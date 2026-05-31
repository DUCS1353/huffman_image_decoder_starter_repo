# Huffman Image Decoder Starter Guide

This folder contains the starter files for Project 4.

## Files
- `huffman_starter.py`: TODO-based Python starter code.
- `test_huffman.py`: visible tests for the decoding functions.
- `practice_packet.json`: a tiny packet for inspecting the packet format.
- `packets/`: assigned image packets from `A_huffman_image.json` through `Z_huffman_image.json`.
- `huffman_visualizer.html`: a local visualizer for a Huffman tree walk.
- `requirements.txt`: confirms that no third-party Python packages are required.
- `.vscode/`: recommended VS Code Python extensions and settings.
- `.gitignore`: ignores generated output files and Python cache files.

Choose the packet whose filename starts with the first letter of your last name. For example, a student with the last name `Stevens` should use `packets/S_huffman_image.json`.

Keep these files together while you work. You will use the starter files and packet files locally, but you will submit only one `.py` file to Canvas.

## Opening the Project
If you are viewing the GitHub template repository, choose **Use this template** to make your own copy. Then open your copied project folder in VS Code.

If you downloaded the files directly, open the folder that contains `huffman_starter.py`. Do not move `huffman_starter.py` away from the `packets` folder.

VS Code may ask whether you want to install recommended Python extensions. Installing them is helpful, but the project does not require any third-party Python packages.

## Packages and Libraries
Use Python 3 and the Python standard library only.

You should use:

- `pathlib.Path` for file paths;
- `json` to read the packet files;
- a simple `Node` class or the provided `@dataclass` for tree nodes;
- a Python `dict` as a hashmap for color counts;
- the starter's existing `hashlib` code to check your decoded pixels.

Do not use:

- Pillow/PIL, OpenCV, imageio, matplotlib, or other image libraries;
- NumPy, pandas, or other array/dataframe libraries;
- compression or Huffman libraries such as `zlib`, `gzip`, `bz2`, `lzma`, `bitarray`, `bitstring`, or `dahuffman`;
- network, AI, or API packages;
- code that hard-codes the decoded image instead of walking the Huffman tree.

The `requirements.txt` file is intentionally empty except for comments. You do not need to install anything with `pip`. VS Code extensions are allowed because they help you edit code; they are not Python packages used by your program.

### Standard-Library Module Guide
The starter uses only modules that come with Python.

- `argparse` reads command-line options such as `--letter S`.
- `dataclasses` creates the small `Node` class without writing a long constructor.
- `hashlib` computes the SHA-256 checksum used to verify the decoded pixels.
- `html` escapes text that is inserted into `decoded_preview.html`.
- `json` reads the packet files, which store the tree, bit string, dimensions, and checksum.
- `pathlib.Path` builds file paths that work on different computers.
- `string` provides `ascii_uppercase`, which is used to check packet letters from `A` to `Z`.
- `typing` provides type hints such as `List[Pixel]` and `Dict[Pixel, int]`.

You do not need to memorize these modules. Use this list when you want to understand why an import is present.

## Overview
You are building a Huffman decoder for an image.

You do not need to build the tree. You do not need a priority queue. The tree is already provided in your assigned packet.

The packet images are color-binned before Huffman coding. That binning step is lossy because nearby RGB colors are rounded together. Huffman decoding is still lossless for the binned pixels: if your decoder is correct, it reconstructs the exact binned image stored in the packet.

The decoder reads bits from left to right:

1. Start at the root of the tree.
2. Read one bit.
3. Go left for `0`.
4. Go right for `1`.
5. When you reach a leaf, output that leaf's pixel.
6. Return to the root.
7. Continue until all bits are decoded.

Each leaf stores one RGB pixel tuple, such as:

```python
(128, 64, 0)
```

After decoding, use a Python `dict` as a hashmap to count how many times each pixel color appears. Huffman coding works best when some symbols are much more common than others.

## Why This Works
Huffman codes are prefix-free. That means no complete pixel code is the beginning of another complete pixel code.

Because of that, the decoder does not need commas or spaces between codes. Reaching a leaf means exactly one pixel has been decoded.

Tree depth is the runtime idea to notice. If a pixel is stored at depth 3, your decoder follows 3 bits to reach it. The worst single pixel takes time proportional to the height of the tree, because height is the deepest path from the root to a leaf.

Efficiency is the compression idea to notice. Common colors usually have shorter paths. Your script reports the tree height, average Huffman bits per pixel, compression ratio, and percent saved.

## Tree Format
The packet stores the tree as nested JSON.

An internal node has `left` and `right` children:

```json
{
  "left": { "...": "..." },
  "right": { "...": "..." }
}
```

A leaf has a `symbol`, which is one RGB pixel:

```json
{"symbol": [255, 0, 0]}
```

Here is a complete small tree:

```json
{
  "left": {"symbol": [255, 0, 0]},
  "right": {
    "left": {"symbol": [0, 255, 0]},
    "right": {"symbol": [0, 0, 255]}
  }
}
```

This means red has code `0`, green has code `10`, and blue has code `11`.

The starter code already converts this JSON into `Node` objects with `tree_from_dict`. After that, your decoder should use `current.left`, `current.right`, and `current.is_leaf()`.

## Code Map
The main file is `huffman_starter.py`. It is organized so that the decoding task stays small.

### Data Representation
- `Pixel` is a type hint for an RGB color tuple: `(red, green, blue)`.
- `Node` represents one Huffman tree node. A leaf node has a `symbol`. An internal node has `left` and `right` children.
- `Node.is_leaf()` tells you whether the current tree node stores a pixel.

### Packet Loading
- `normalize_letter(value)` turns a last-name initial into an uppercase packet letter.
- `packet_path_for_letter(letter, base_dir)` builds the path to the matching packet in `packets/`.
- `load_packet(path)` reads one packet JSON file and checks that the required fields are present.
- `tree_from_dict(data)` converts the packet's nested JSON tree into `Node` objects.

### Your Main Function
- `decode_bits(encoded_bits, tree)` is the main function you complete.
- It should return a list of RGB pixel tuples.
- It should not build a new tree, use a compression library, or look up a precomputed answer.

### Analysis Helpers
- `count_pixels(pixels)` uses a Python `dict` as a hashmap to count colors.
- `most_common_pixels(counts)` finds the most frequent colors.
- `tree_height(tree)` finds the longest root-to-leaf path.
- `code_lengths(tree)` records each color's Huffman code length.
- `weighted_average_code_length(counts, lengths)` computes the average number of Huffman bits per decoded pixel.
- `compression_stats(...)` compares the encoded bit count with the original 24-bit RGB size.

### Output Helpers
- `pixel_checksum(pixels)` checks whether your decoded pixels match the packet.
- `write_ppm(...)` writes `decoded_image.ppm` without using an image library.
- `write_preview_html(...)` writes `decoded_preview.html` so you can inspect the image in a browser.
- `main(...)` connects the command-line arguments, packet loading, decoding, analysis, and output.

## Test File Map
The file `test_huffman.py` is meant to be readable. Each test focuses on one behavior.

- The first decoding tests use a tiny tree where red is `0`, green is `10`, and blue is `11`.
- The invalid-input tests check that your decoder raises `ValueError` when the bit string cannot be decoded cleanly.
- The packet-loading test checks that the local files are in the expected place.
- The counting, checksum, tree, and compression tests check helper functions that are already provided.
- The output-file test checks that the starter can write a PPM image and HTML preview.

## Suggested Path
Use these checkpoints:

1. Open `huffman_visualizer.html` and click through a few steps.
2. Run `python test_huffman.py` once before editing anything.
3. Open your assigned packet JSON and inspect the `tree` and `bits` fields.
4. Make `decode_bits("", tree)` return an empty list.
5. Decode one short path, such as `0`.
6. Decode multi-bit paths, such as `10` and `11`.
7. Reset back to the root after every leaf.
8. Raise `ValueError` for invalid bits.
9. Raise `ValueError` if the bit string ends before reaching a leaf.
10. Count decoded pixel colors with a Python `dict`.
11. Print the compression ratio, tree height, average Huffman bits per pixel, and most common colors.
12. Run `python huffman_starter.py --letter X`, replacing `X` with your last-name initial.
13. Open `decoded_preview.html`.

If the project feels large, do not start with the image packet. Start with the small visible tests in `test_huffman.py`. The image packet only works after the same small tree-walk idea works.

## Running the Tests
From this folder, run:

```sh
python test_huffman.py
```

At first, the tests will report TODO functions because `huffman_starter.py` is incomplete. As you implement the decoder, more tests should pass.

## Running the Decoder
After the tests pass, run:

```sh
python huffman_starter.py --letter X
```

Replace `X` with the first letter of your last name.

Your script should create:

- `decoded_image.ppm`
- `decoded_preview.html`

Open `decoded_preview.html` in your browser to check your decoded image, compression stats, tree facts, and most common colors.

## Local Visualizer
Open this file in your browser:

```text
huffman_visualizer.html
```

It shows an example of Huffman decoding. Watch how each bit moves through the tree. Whenever the walk reaches a leaf, one pixel is emitted and the decoder returns to the root.

## Checklist
- All visible tests pass.
- The checksum printed by `huffman_starter.py` matches the packet.
- `decoded_image.ppm` exists.
- `decoded_preview.html` shows the decoded image.
- Your output includes original bits, encoded bits, compression ratio, percent saved, tree height, average Huffman bits per pixel, and most common colors.
- Your submitted file is one `.py` file.

## Debugging Hints
- If the output has too many or too few pixels, check whether you reset to the root after every leaf.
- If invalid input is accepted, check that every bit is exactly `"0"` or `"1"`.
- If unfinished input is accepted, check where the decoder is after the loop ends.
- If file loading fails, use `Path(__file__).resolve().parent` so paths are relative to your script.

## Submission Checklist
Submit one `.py` file. Do not submit a zip file.

Your script should include:

- `decode_bits(encoded_bits, tree)`;
- `count_pixels(pixels)` using a Python `dict`;
- compression statistics from `main`;
- tree height and average Huffman bits per pixel;
- a `main` function or command-line runner;
- a top-of-file comment explaining the tree walk;
- your checksum result;
- a short note describing the decoded image and compression results.
