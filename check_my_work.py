"""
Friendly checks for Project 4.

Run this file while you work:

    python check_my_work.py

You do not need to edit this file. The checks import your functions from
huffman_starter.py and report which pieces are working.
"""

from pathlib import Path

from huffman_starter import count_pixels, decode_bits
from huffman_tools import (
    Node,
    load_packet,
    packet_path_for_letter,
    pixel_checksum,
    tree_from_dict,
)


RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)


def small_tree() -> Node:
    """Return a tiny tree where red=0, green=10, and blue=11."""
    return Node(
        left=Node(symbol=RED),
        right=Node(
            left=Node(symbol=GREEN),
            right=Node(symbol=BLUE),
        ),
    )


def check_decode_small_tree() -> None:
    assert decode_bits("010110", small_tree()) == [RED, GREEN, BLUE, RED]


def check_decode_empty_bits() -> None:
    assert decode_bits("", small_tree()) == []


def check_decode_single_symbol_tree() -> None:
    tree = Node(symbol=(8, 16, 32))
    assert decode_bits("00000", tree) == [(8, 16, 32)] * 5


def check_invalid_bit_raises_value_error() -> None:
    try:
        decode_bits("012", small_tree())
    except ValueError:
        return
    raise AssertionError("decode_bits should reject non-binary input.")


def check_unfinished_code_raises_value_error() -> None:
    try:
        decode_bits("01", small_tree())
    except ValueError:
        return
    raise AssertionError("decode_bits should reject an unfinished tree path.")


def check_count_pixels_uses_dict() -> None:
    counts = count_pixels([RED, GREEN, RED, BLUE, RED, GREEN])
    assert isinstance(counts, dict)
    assert counts[RED] == 3
    assert counts[GREEN] == 2
    assert counts[BLUE] == 1


def check_packet_files_are_available() -> None:
    here = Path(__file__).resolve().parent
    assert packet_path_for_letter("s", here).name == "S_huffman_image.json"

    packet = load_packet(here / "practice_packet.json")
    assert packet["format"] == "huffman-image-packet-v1"
    assert packet["width"] == 4
    assert packet["height"] == 4
    assert {"tree", "bits", "decoded_sha256"}.issubset(packet)


def check_practice_packet_decodes_exactly() -> None:
    here = Path(__file__).resolve().parent
    packet = load_packet(here / "practice_packet.json")
    tree = tree_from_dict(packet["tree"])
    pixels = decode_bits(packet["bits"], tree)

    assert len(pixels) == packet["width"] * packet["height"]
    assert pixel_checksum(pixels) == packet["decoded_sha256"]


def run_check(name, check_func) -> bool:
    """Run one check and print a beginner-friendly result."""
    try:
        check_func()
    except NotImplementedError as exc:
        print(f"{name}: not finished yet ({exc})")
        return False
    except AssertionError as exc:
        detail = f" ({exc})" if str(exc) else ""
        print(f"{name}: check failed{detail}")
        return False
    except Exception as exc:
        print(f"{name}: error ({type(exc).__name__}: {exc})")
        return False

    print(f"{name}: passed")
    return True


def main() -> int:
    checks = [
        ("small tree decoding", check_decode_small_tree),
        ("empty bit string", check_decode_empty_bits),
        ("single-symbol tree", check_decode_single_symbol_tree),
        ("invalid bit handling", check_invalid_bit_raises_value_error),
        ("unfinished code handling", check_unfinished_code_raises_value_error),
        ("pixel hashmap counting", check_count_pixels_uses_dict),
        ("packet files", check_packet_files_are_available),
        ("practice packet exact decode", check_practice_packet_decodes_exactly),
    ]

    passed = 0
    for name, check_func in checks:
        if run_check(name, check_func):
            passed += 1

    print(f"{passed}/{len(checks)} checks passed")
    return 0 if passed == len(checks) else 1


if __name__ == "__main__":
    raise SystemExit(main())
