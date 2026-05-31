"""
Project 4: Decode Your Huffman Image.

This is the file you should edit and submit.

Before running the project, set PACKET_LETTER to the first letter of your last
name. Then run:

    python check_my_work.py
    python huffman_starter.py

The Huffman tree is already provided. Your job is to walk that tree to decode
the compressed bits, then use a Python dict as a hashmap to count colors.
"""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from huffman_tools import Node, Pixel, run_project


# Change this to the first letter of your last name.
# Example: "S" uses packets/S_huffman_image.json.
PACKET_LETTER = "A"

# Leave this as None for the assigned A-Z packet.
# If your instructor gives you a different packet, you can use:
# PACKET_PATH = Path("practice_packet.json")
PACKET_PATH = None


def decode_bits(encoded_bits: str, tree: Node) -> list[Pixel]:
    """Decode 0s and 1s by walking the provided Huffman tree.

    Return a list of RGB pixel tuples.

    Huffman decoding rule:
    - Start at the root of the tree.
    - A 0 means move left.
    - A 1 means move right.
    - When you reach a leaf, append that leaf's pixel.
    - After a leaf, jump back to the root for the next pixel.
    """
    # TODO:
    # 1. Create an empty list named decoded_pixels.
    # 2. Keep track of the current node. It should start at tree.
    # 3. Loop over encoded_bits one bit at a time.
    # 4. Move left for "0" and right for "1".
    # 5. Raise ValueError if a bit is not "0" or "1".
    # 6. Raise ValueError if a bit asks you to move to a missing child.
    # 7. When current is a leaf, append current.symbol and reset to tree.
    # 8. After the loop, make sure you are back at the root.
    # 9. Return decoded_pixels.
    #
    # Hint: current.is_leaf() tells you whether the current node is a leaf.
    # Hint: a leaf stores its RGB pixel in current.symbol.
    #
    # Special case: if tree itself is a leaf, each valid bit decodes to that
    # same pixel.
    raise NotImplementedError("decode_bits")


def count_pixels(pixels: Iterable[Pixel]) -> dict[Pixel, int]:
    """Count RGB pixels using a Python dict as a hashmap."""
    # TODO:
    # 1. Create an empty dict named counts.
    # 2. Loop over the pixels.
    # 3. For each pixel, increase its count in the dict.
    # 4. Return counts.
    #
    # A useful pattern is:
    # counts[pixel] = counts.get(pixel, 0) + 1
    raise NotImplementedError("count_pixels")


def main() -> int:
    """Run the local decoder workflow."""
    return run_project(
        decode_bits=decode_bits,
        count_pixels=count_pixels,
        packet_letter=PACKET_LETTER,
        packet_path=PACKET_PATH,
        base_dir=Path(__file__).resolve().parent,
    )


if __name__ == "__main__":
    raise SystemExit(main())
