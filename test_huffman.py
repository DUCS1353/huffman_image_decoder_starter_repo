"""
Visible tests for Project 4: Decode Your Huffman Image.

These tests check decoder behavior. Passing them does not prove every case is
correct, but failing them means there is decoder logic to fix.
"""

from pathlib import Path
import tempfile

from huffman_starter import (
    Node,
    code_lengths,
    compression_stats,
    count_pixels,
    decode_bits,
    load_packet,
    most_common_pixels,
    normalize_letter,
    packet_path_for_letter,
    pixel_checksum,
    tree_from_dict,
    tree_height,
    weighted_average_code_length,
    write_ppm,
    write_preview_html,
)


RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)


def small_tree() -> Node:
    # This tiny tree gives red the short code 0, green the code 10,
    # and blue the code 11. Most decoder tests use this tree.
    return Node(
        left=Node(symbol=RED),
        right=Node(
            left=Node(symbol=GREEN),
            right=Node(symbol=BLUE),
        ),
    )


def test_decode_small_tree():
    tree = small_tree()
    # Split the bits as 0 | 10 | 11 | 0.
    assert decode_bits("010110", tree) == [RED, GREEN, BLUE, RED]


def test_decode_empty_bits():
    assert decode_bits("", small_tree()) == []


def test_decode_single_symbol_tree():
    tree = Node(symbol=(8, 16, 32))
    assert decode_bits("00000", tree) == [(8, 16, 32)] * 5


def test_invalid_bit_raises_value_error():
    try:
        decode_bits("012", small_tree())
    except ValueError:
        return
    raise AssertionError("decode_bits should reject non-binary input.")


def test_unfinished_code_raises_value_error():
    try:
        # 0 decodes to red, but the final 1 stops at an internal node.
        decode_bits("01", small_tree())
    except ValueError:
        return
    raise AssertionError("decode_bits should reject an unfinished tree path.")


def test_tree_from_dict():
    data = {
        "left": {"symbol": [255, 0, 0]},
        "right": {
            "left": {"symbol": [0, 255, 0]},
            "right": {"symbol": [0, 0, 255]},
        },
    }
    assert decode_bits("011", tree_from_dict(data)) == [RED, BLUE]


def test_packet_selection_and_loading():
    here = Path(__file__).resolve().parent
    assert normalize_letter("smith") == "S"
    assert normalize_letter(" S ") == "S"
    assert packet_path_for_letter("b", here).name == "B_huffman_image.json"

    packet = load_packet(here / "practice_packet.json")
    assert packet["format"] == "huffman-image-packet-v1"
    assert packet["width"] == 4
    assert packet["height"] == 4
    assert set(["tree", "bits", "decoded_sha256"]).issubset(packet)


def test_pixel_checksum_is_stable():
    pixels = [RED, GREEN, BLUE, RED]
    assert pixel_checksum(pixels) == pixel_checksum(list(pixels))
    assert pixel_checksum(pixels) != pixel_checksum([RED, BLUE, GREEN, RED])


def test_count_pixels_uses_pixel_tuples_as_keys():
    pixels = [RED, GREEN, RED, BLUE, RED, GREEN]
    counts = count_pixels(pixels)

    assert counts[RED] == 3
    assert counts[GREEN] == 2
    assert counts[BLUE] == 1
    assert most_common_pixels(counts, limit=2) == [(RED, 3), (GREEN, 2)]


def test_tree_efficiency_helpers():
    tree = small_tree()
    lengths = code_lengths(tree)
    counts = {RED: 2, GREEN: 1, BLUE: 1}

    # Weighted average = (2 red pixels * 1 bit + 1 green * 2 bits
    # + 1 blue * 2 bits) / 4 total pixels = 1.5 bits per pixel.
    assert tree_height(tree) == 2
    assert lengths[RED] == 1
    assert lengths[GREEN] == 2
    assert lengths[BLUE] == 2
    assert weighted_average_code_length(counts, lengths) == 1.5


def test_compression_stats():
    stats = compression_stats(width=2, height=2, encoded_bit_count=12, bits_per_pixel=24)

    assert stats["original_bits"] == 96
    assert stats["encoded_bits"] == 12
    assert stats["compression_ratio"] == 0.125
    assert stats["percent_saved"] == 87.5


def test_output_files_can_be_written():
    pixels = [RED, GREEN, BLUE, RED]
    with tempfile.TemporaryDirectory() as temp_dir:
        ppm_path = Path(temp_dir) / "out.ppm"
        html_path = Path(temp_dir) / "out.html"
        write_ppm(ppm_path, 2, 2, pixels)
        write_preview_html(html_path, 2, 2, pixels)

        ppm_text = ppm_path.read_text(encoding="utf-8")
        html_text = html_path.read_text(encoding="utf-8")

    assert ppm_text.startswith("P3")
    assert "2 2" in ppm_text
    assert "rgb(255, 0, 0)" in html_text


def run_test(name, test_func):
    try:
        test_func()
    except NotImplementedError as exc:
        print(f"{name}: TODO not implemented yet ({exc})")
        return False
    except AssertionError as exc:
        print(f"{name}: failed ({exc})")
        return False

    print(f"{name}: passed")
    return True


def main():
    tests = [
        ("decode small tree", test_decode_small_tree),
        ("decode empty bits", test_decode_empty_bits),
        ("decode single-symbol tree", test_decode_single_symbol_tree),
        ("invalid bit raises ValueError", test_invalid_bit_raises_value_error),
        ("unfinished code raises ValueError", test_unfinished_code_raises_value_error),
        ("tree from dict", test_tree_from_dict),
        ("packet selection and loading", test_packet_selection_and_loading),
        ("pixel checksum", test_pixel_checksum_is_stable),
        ("count pixels", test_count_pixels_uses_pixel_tuples_as_keys),
        ("tree efficiency helpers", test_tree_efficiency_helpers),
        ("compression stats", test_compression_stats),
        ("output files", test_output_files_can_be_written),
    ]

    passed = 0
    for name, test_func in tests:
        if run_test(name, test_func):
            passed += 1

    print(f"{passed}/{len(tests)} tests passed")
    return 0 if passed == len(tests) else 1


if __name__ == "__main__":
    raise SystemExit(main())
