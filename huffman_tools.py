"""
Support code for Project 4.

Students normally do not need to edit this file. It loads packets, rebuilds the
provided Huffman tree, checks decoded pixels, writes local preview files, and
prints compression statistics.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass
import hashlib
import html
import json
from pathlib import Path
import string
from typing import Any


Pixel = tuple[int, int, int]


@dataclass
class Node:
    """One node in the provided Huffman tree."""

    symbol: Pixel | None = None
    left: "Node | None" = None
    right: "Node | None" = None

    def is_leaf(self) -> bool:
        """Return True when this node stores a decoded pixel."""
        return self.symbol is not None


def tree_from_dict(data: dict[str, Any]) -> Node:
    """Convert the packet's nested JSON tree into Node objects."""
    if "symbol" in data:
        return Node(symbol=tuple(data["symbol"]))
    return Node(
        left=tree_from_dict(data["left"]),
        right=tree_from_dict(data["right"]),
    )


def normalize_letter(value: str) -> str:
    """Return one uppercase A-Z packet letter from user input."""
    cleaned = value.strip().upper()
    if not cleaned:
        raise ValueError("Choose a packet letter from A to Z.")

    letter = cleaned[0]
    if letter not in string.ascii_uppercase:
        raise ValueError("Packet letter must be A through Z.")
    return letter


def packet_path_for_letter(letter: str, base_dir: str | Path) -> Path:
    """Return the assigned packet path for a last-name initial."""
    initial = normalize_letter(letter)
    return Path(base_dir) / "packets" / f"{initial}_huffman_image.json"


def load_packet(path: str | Path) -> dict[str, Any]:
    """Load one Huffman image packet and check its required fields."""
    packet = json.loads(Path(path).read_text(encoding="utf-8"))
    required = {"width", "height", "tree", "bits", "decoded_sha256"}
    missing = sorted(required - set(packet))
    if missing:
        raise ValueError(f"Packet is missing required fields: {', '.join(missing)}")
    return packet


def most_common_pixels(counts: dict[Pixel, int], limit: int = 5) -> list[tuple[Pixel, int]]:
    """Return the most common pixels and their counts."""
    return sorted(counts.items(), key=lambda item: item[1], reverse=True)[:limit]


def tree_height(tree: Node) -> int:
    """Return the largest number of edges from the root to any leaf."""
    if tree.is_leaf():
        return 0

    child_heights: list[int] = []
    if tree.left is not None:
        child_heights.append(1 + tree_height(tree.left))
    if tree.right is not None:
        child_heights.append(1 + tree_height(tree.right))
    if not child_heights:
        raise ValueError("Tree has an internal node with no children.")
    return max(child_heights)


def code_lengths(tree: Node, depth: int = 0) -> dict[Pixel, int]:
    """Return each pixel's Huffman code length, measured as tree depth."""
    if tree.is_leaf():
        if tree.symbol is None:
            raise ValueError("Leaf node is missing a symbol.")
        return {tree.symbol: max(depth, 1)}

    lengths: dict[Pixel, int] = {}
    if tree.left is not None:
        lengths.update(code_lengths(tree.left, depth + 1))
    if tree.right is not None:
        lengths.update(code_lengths(tree.right, depth + 1))
    return lengths


def weighted_average_code_length(
    counts: dict[Pixel, int],
    lengths: dict[Pixel, int],
) -> float:
    """Return the average Huffman bits used per decoded pixel."""
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
) -> dict[str, float]:
    """Compute basic compression statistics for the decoded image."""
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
    values: list[int] = []
    for red, green, blue in pixels:
        values.extend([red, green, blue])
    return bytes(values)


def pixel_checksum(pixels: Iterable[Pixel]) -> str:
    """Return a SHA-256 checksum for a pixel sequence.

    Students do not need to know the details of SHA-256 for this project. The
    result is used as an exact-match fingerprint for decoded pixels.
    """
    return hashlib.sha256(pixel_bytes(pixels)).hexdigest()


def write_ppm(path: str | Path, width: int, height: int, pixels: Iterable[Pixel]) -> None:
    """Write pixels to a plain-text P3 PPM image."""
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
    stats: dict[str, float] | None = None,
    top_pixels: list[tuple[Pixel, int]] | None = None,
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


def packet_from_settings(
    base_dir: Path,
    letter: str,
    packet_path: Path | None,
) -> tuple[Path, dict[str, Any]]:
    """Load either PACKET_PATH or the packet matching PACKET_LETTER."""
    if packet_path is not None:
        path = packet_path
        if not path.is_absolute():
            path = base_dir / path
    else:
        path = packet_path_for_letter(letter, base_dir)
    return path, load_packet(path)


def run_project(
    decode_bits: Callable[[str, Node], list[Pixel]],
    count_pixels: Callable[[Iterable[Pixel]], dict[Pixel, int]],
    packet_letter: str,
    packet_path: Path | None,
    base_dir: Path,
) -> int:
    """Run the full local decoder workflow."""
    packet_path, packet = packet_from_settings(base_dir, packet_letter, packet_path)
    tree = tree_from_dict(packet["tree"])
    encoded_bits = "".join(str(packet["bits"]).split())

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

    write_ppm(base_dir / "decoded_image.ppm", width, height, pixels)
    write_preview_html(
        base_dir / "decoded_preview.html",
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
