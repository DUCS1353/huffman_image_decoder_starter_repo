"""
Starter code for Project 4: Decode Your Huffman Image.

Fill in decode_bits, then run:

    python test_huffman.py
    python huffman_starter.py --letter A

Use the packet whose letter matches the first letter of your last name. The
provided packet contains the Huffman tree, compressed bits, image dimensions,
and checksum needed to reconstruct the image.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import html
import json
from pathlib import Path
import string
from typing import Any, Dict, Iterable, List, Optional, Tuple


Pixel = Tuple[int, int, int]


# A Pixel is an RGB color written as (red, green, blue).
# Each value is an integer from 0 to 255.
@dataclass
class Node:
    """A node in a provided Huffman tree."""

    symbol: Optional[Pixel] = None
    left: Optional["Node"] = None
    right: Optional["Node"] = None

    def is_leaf(self) -> bool:
        return self.symbol is not None


def tree_from_dict(data: Dict[str, Any]) -> Node:
    """Convert the provided JSON tree into Node objects."""
    # Packet files store trees as nested dictionaries because JSON cannot store
    # Python objects directly. This helper rebuilds the tree into Node objects.
    if "symbol" in data:
        return Node(symbol=tuple(data["symbol"]))
    return Node(
        left=tree_from_dict(data["left"]),
        right=tree_from_dict(data["right"]),
    )


def normalize_letter(value: str) -> str:
    """Return the first A-Z letter from a student's last-name initial."""
    cleaned = value.strip().upper()
    if not cleaned:
        raise ValueError("Choose a packet letter from A to Z.")

    letter = cleaned[0]
    if letter not in string.ascii_uppercase:
        raise ValueError("Packet letter must be A through Z.")
    return letter


def packet_path_for_letter(letter: str, base_dir: str | Path) -> Path:
    """Return the packet path for a last-name initial."""
    initial = normalize_letter(letter)
    return Path(base_dir) / "packets" / f"{initial}_huffman_image.json"


def load_packet(path: str | Path) -> Dict[str, Any]:
    """Load one Huffman image packet from JSON."""
    packet = json.loads(Path(path).read_text(encoding="utf-8"))
    required = {"width", "height", "tree", "bits", "decoded_sha256"}
    missing = sorted(required - set(packet))
    if missing:
        raise ValueError(f"Packet is missing required fields: {', '.join(missing)}")
    return packet


def load_tree(path: str | Path) -> Node:
    """Load a Huffman tree from a JSON file."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return tree_from_dict(data)


def load_bits(path: str | Path) -> str:
    """Load encoded bits from a text file, ignoring whitespace."""
    return "".join(Path(path).read_text(encoding="utf-8").split())


def load_metadata(path: str | Path) -> Dict[str, Any]:
    """Load image metadata from JSON."""
    return json.loads(Path(path).read_text(encoding="utf-8"))


def decode_bits(encoded_bits: str, tree: Node) -> List[Pixel]:
    """Decode a string of 0 and 1 characters using a provided Huffman tree."""
    # Each bit moves one level down the tree. Decoding one pixel takes work
    # proportional to that pixel leaf's depth.
    #
    # You only need to edit this function for the main decoding logic. The
    # helper functions below are already written so you can focus on the tree
    # walk itself.
    # TODO:
    # 1. Start at the root of the tree.
    # 2. For each bit, move left for "0" and right for "1".
    # 3. If the bit is not "0" or "1", raise ValueError.
    # 4. When you reach a leaf, append that leaf's pixel to decoded_pixels.
    # 5. After each leaf, jump back to the root.
    # 6. If the bit string ends while you are not at the root, raise ValueError.
    #
    # Special case: if the tree itself is one leaf, each bit represents that
    # same symbol.
    raise NotImplementedError("decode_bits")


def count_pixels(pixels: Iterable[Pixel]) -> Dict[Pixel, int]:
    """Count decoded pixels using Python's dict as a hashmap."""
    # The keys are pixel tuples, and the values are how many times each color
    # appears. This is the hashmap part of the project.
    counts: Dict[Pixel, int] = {}
    for pixel in pixels:
        counts[pixel] = counts.get(pixel, 0) + 1
    return counts


def most_common_pixels(counts: Dict[Pixel, int], limit: int = 5) -> List[Tuple[Pixel, int]]:
    """Return the most common pixels and their counts."""
    return sorted(counts.items(), key=lambda item: item[1], reverse=True)[:limit]


def tree_height(tree: Node) -> int:
    """Return the largest number of edges from the root to a leaf."""
    # A single leaf has height 0 because no edges are needed to reach it.
    if tree.is_leaf():
        return 0

    child_heights: List[int] = []
    if tree.left is not None:
        child_heights.append(1 + tree_height(tree.left))
    if tree.right is not None:
        child_heights.append(1 + tree_height(tree.right))
    if not child_heights:
        raise ValueError("Tree has an internal node with no children.")
    return max(child_heights)


def code_lengths(tree: Node, depth: int = 0) -> Dict[Pixel, int]:
    """Return each pixel's Huffman code length, measured as tree depth."""
    # In a Huffman tree, a symbol's code length is the depth of its leaf.
    # This mirrors the same recursive tree walk used for decoding.
    if tree.is_leaf():
        if tree.symbol is None:
            raise ValueError("Leaf node is missing a symbol.")
        return {tree.symbol: max(depth, 1)}

    lengths: Dict[Pixel, int] = {}
    if tree.left is not None:
        lengths.update(code_lengths(tree.left, depth + 1))
    if tree.right is not None:
        lengths.update(code_lengths(tree.right, depth + 1))
    return lengths


def weighted_average_code_length(counts: Dict[Pixel, int], lengths: Dict[Pixel, int]) -> float:
    """Return the average Huffman bits used per decoded pixel."""
    # Weighted average means common pixels matter more than rare pixels.
    # Formula: sum(count * code_length) / total_pixel_count.
    total_pixels = sum(counts.values())
    if total_pixels == 0:
        return 0.0

    total_bit_steps = 0
    for pixel, count in counts.items():
        if pixel not in lengths:
            raise ValueError(f"Decoded pixel has no code length: {pixel!r}")
        total_bit_steps += count * lengths[pixel]
    return total_bit_steps / total_pixels


def compression_stats(
    width: int,
    height: int,
    encoded_bit_count: int,
    bits_per_pixel: int = 24,
) -> Dict[str, float]:
    """Compute basic compression statistics for the decoded image."""
    # Before Huffman coding, a normal RGB image uses 24 bits per pixel:
    # 8 bits for red, 8 bits for green, and 8 bits for blue.
    original_bits = width * height * bits_per_pixel
    if original_bits == 0:
        ratio = 0.0
        percent_saved = 0.0
    else:
        ratio = encoded_bit_count / original_bits
        percent_saved = (1.0 - ratio) * 100.0

    return {
        "original_bits": float(original_bits),
        "encoded_bits": float(encoded_bit_count),
        "compression_ratio": ratio,
        "percent_saved": percent_saved,
    }


def pixel_bytes(pixels: Iterable[Pixel]) -> bytes:
    """Pack RGB pixels into bytes for checksum verification."""
    values: List[int] = []
    for red, green, blue in pixels:
        values.extend([red, green, blue])
    return bytes(values)


def pixel_checksum(pixels: Iterable[Pixel]) -> str:
    """Return a SHA-256 checksum for a pixel sequence."""
    return hashlib.sha256(pixel_bytes(pixels)).hexdigest()


def write_ppm(path: str | Path, width: int, height: int, pixels: Iterable[Pixel]) -> None:
    """Write pixels to a plain-text P3 PPM image."""
    # PPM is intentionally used here because it is a very simple image format.
    # It lets us write a viewable image without installing an image library.
    pixels = list(pixels)
    if len(pixels) != width * height:
        raise ValueError("Pixel count does not match width * height.")

    lines = ["P3", f"{width} {height}", "255"]
    for red, green, blue in pixels:
        lines.append(f"{red} {green} {blue}")
    Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_preview_html(
    path: str | Path,
    width: int,
    height: int,
    pixels: Iterable[Pixel],
    stats: Optional[Dict[str, float]] = None,
    top_pixels: Optional[List[Tuple[Pixel, int]]] = None,
    packet_name: str = "assigned packet",
) -> None:
    """Write a local HTML preview of the decoded image."""
    pixels = list(pixels)
    if len(pixels) != width * height:
        raise ValueError("Pixel count does not match width * height.")

    cells = []
    for red, green, blue in pixels:
        cells.append(
            '<span class="pixel" '
            f'style="background-color: rgb({red}, {green}, {blue})"></span>'
        )

    stats_html = ""
    if stats:
        tree_items = ""
        if "tree_height" in stats and "average_code_length" in stats:
            tree_items = f"""
      <li>Tree height: {int(stats["tree_height"])}</li>
      <li>Average Huffman bits per pixel: {stats["average_code_length"]:.2f}</li>
"""
        stats_html = f"""
  <section>
    <h2>Compression Stats</h2>
    <ul>
      <li>Original bits: {int(stats["original_bits"])}</li>
      <li>Encoded bits: {int(stats["encoded_bits"])}</li>
      <li>Compression ratio: {stats["compression_ratio"]:.3f}</li>
      <li>Space saved: {stats["percent_saved"]:.1f}%</li>
      {tree_items}
    </ul>
  </section>
"""

    top_pixels_html = ""
    if top_pixels:
        rows = []
        for pixel, count in top_pixels:
            red, green, blue = pixel
            rows.append(
                "<li>"
                f'<span class="swatch" style="background-color: rgb({red}, {green}, {blue})"></span>'
                f" rgb({red}, {green}, {blue}): {count} pixels"
                "</li>"
            )
        top_pixels_html = f"""
  <section>
    <h2>Most Common Colors</h2>
    <ul class="colors">
      {''.join(rows)}
    </ul>
  </section>
"""

    title = "Decoded Huffman Image"
    safe_packet_name = html.escape(packet_name)
    document = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{html.escape(title)}</title>
  <style>
    body {{
      margin: 24px;
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: #f6f3ee;
      color: #1f2933;
    }}
    .preview {{
      display: grid;
      grid-template-columns: repeat({width}, 8px);
      grid-template-rows: repeat({height}, 8px);
      width: max-content;
      border: 1px solid #25313d;
      background: white;
      image-rendering: pixelated;
    }}
    .pixel {{
      width: 8px;
      height: 8px;
      display: block;
    }}
    .colors {{
      list-style: none;
      padding-left: 0;
    }}
    .colors li {{
      display: flex;
      align-items: center;
      gap: 8px;
      margin: 6px 0;
      font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
    }}
    .swatch {{
      width: 22px;
      height: 22px;
      border: 1px solid #25313d;
      display: inline-block;
    }}
  </style>
</head>
<body>
  <h1>{html.escape(title)}</h1>
  <p>Packet: {safe_packet_name}</p>
  <p>{width} x {height} pixels</p>
  <div class="preview">
    {''.join(cells)}
  </div>
  {stats_html}
  {top_pixels_html}
</body>
</html>
"""
    Path(path).write_text(document, encoding="utf-8")


def packet_from_args(base_dir: Path, letter: Optional[str], packet_path: Optional[Path]) -> Tuple[Path, Dict[str, Any]]:
    """Load either an explicit packet path or the packet matching a letter."""
    if packet_path is not None:
        path = packet_path
    else:
        path = packet_path_for_letter(letter or "A", base_dir)
    return path, load_packet(path)


def main(argv: Optional[List[str]] = None) -> int:
    here = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description="Decode one assigned Huffman image packet.")
    parser.add_argument(
        "--letter",
        default="A",
        help="First letter of your last name. Example: --letter S",
    )
    parser.add_argument(
        "--packet",
        type=Path,
        help="Optional direct path to a packet JSON file.",
    )
    args = parser.parse_args(argv)

    packet_path, packet = packet_from_args(here, args.letter, args.packet)
    tree = tree_from_dict(packet["tree"])
    encoded_bits = "".join(str(packet["bits"]).split())

    # Student work begins in decode_bits. Everything after this line assumes
    # that decode_bits returns the correct list of RGB pixel tuples.
    pixels = decode_bits(encoded_bits, tree)
    width = int(packet["width"])
    height = int(packet["height"])
    expected_count = width * height

    if len(pixels) != expected_count:
        raise ValueError(f"Expected {expected_count} pixels, decoded {len(pixels)}.")

    checksum = pixel_checksum(pixels)
    checksum_matches = checksum == packet["decoded_sha256"]
    counts = count_pixels(pixels)
    top_pixels = most_common_pixels(counts)
    height_value = tree_height(tree)
    lengths = code_lengths(tree)
    average_code_length = weighted_average_code_length(counts, lengths)
    stats = compression_stats(
        width,
        height,
        len(encoded_bits),
        int(packet.get("bits_per_pixel_before_huffman", 24)),
    )
    stats["tree_height"] = float(height_value)
    stats["average_code_length"] = average_code_length

    write_ppm(here / "decoded_image.ppm", width, height, pixels)
    write_preview_html(
        here / "decoded_preview.html",
        width,
        height,
        pixels,
        stats,
        top_pixels,
        packet_name=packet_path.name,
    )

    print(f"Packet: {packet_path}")
    print(f"Decoded pixels: {len(pixels)}")
    print(f"Unique colors: {len(counts)}")
    print(f"Tree height: {height_value}")
    print(f"Average Huffman bits per pixel: {average_code_length:.2f}")
    print(f"Original bits: {int(stats['original_bits'])}")
    print(f"Encoded bits: {int(stats['encoded_bits'])}")
    print(f"Compression ratio: {stats['compression_ratio']:.3f}")
    print(f"Space saved: {stats['percent_saved']:.1f}%")
    print(f"Checksum: {checksum}")
    print(f"Checksum matches packet: {checksum_matches}")
    print("Most common colors:")
    for pixel, count in top_pixels:
        print(f"  {pixel}: {count}")
    print("Wrote decoded_image.ppm")
    print("Wrote decoded_preview.html")
    return 0 if checksum_matches else 1


if __name__ == "__main__":
    raise SystemExit(main())
