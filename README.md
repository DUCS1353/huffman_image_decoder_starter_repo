# Huffman Image Decoder Starter Guide

This folder contains the starter files for Project 4.

## Files
- `huffman_starter.py`: TODO-based Python starter code.
- `test_huffman.py`: visible tests for the decoding functions.
- `practice_packet.json`: a tiny packet for inspecting the packet format.
- `packets/`: assigned image packets from `A_huffman_image.json` through `Z_huffman_image.json`.
- `huffman_visualizer.html`: a local visualizer for a Huffman tree walk.
- `.vscode/`: recommended VS Code Python extensions and settings.
- `.gitignore`: ignores generated output files and Python cache files.

Choose the packet whose filename starts with the first letter of your last name. For example, a student with the last name `Stevens` should use `packets/S_huffman_image.json`.

Keep these files together while you work. You will use the starter files and packet files locally, but you will submit only one `.py` file to Canvas.

## Opening the Project
If you are using the GitHub template, make your own copy from the template link and open that project folder in VS Code.

If you downloaded the files directly, open the folder that contains `huffman_starter.py`. Do not move `huffman_starter.py` away from the `packets` folder.

VS Code may ask whether you want to install recommended Python extensions. Installing them is helpful, but the project does not require any third-party Python packages.

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
