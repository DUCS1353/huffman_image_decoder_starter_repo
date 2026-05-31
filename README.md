# Huffman Image Decoder Starter Guide

This folder contains the starter files for Project 4.

## What You Edit
Edit and submit only this file:

- `huffman_starter.py`

That file is intentionally short. It contains:

- `PACKET_LETTER`, where you choose your assigned image packet;
- `decode_bits(encoded_bits, tree)`, where you walk the Huffman tree;
- `count_pixels(pixels)`, where you use a Python `dict` as a hashmap;
- `main()`, which runs the project.

## What You Do Not Edit
These files support your work:

- `huffman_tools.py`: loads packets, builds tree nodes, checks the decoded image, writes the preview, and prints statistics.
- `check_my_work.py`: runs friendly checks on your functions.
- `practice_packet.json`: a tiny packet for debugging.
- `packets/`: assigned image packets from `A_huffman_image.json` through `Z_huffman_image.json`.
- `huffman_visualizer.html`: a local visualizer for a Huffman tree walk.
- `requirements.txt`: confirms that no third-party Python packages are required.
- `.vscode/`: recommended VS Code Python extensions and settings.

Keep these files together while you work. You will use the full folder locally, but you will submit only `huffman_starter.py` to Canvas.

## Opening the Project
If you are viewing the GitHub template repository, choose **Use this template** to make your own copy. Then open your copied project folder in VS Code.

If you downloaded the files directly, open the folder that contains `huffman_starter.py`. Do not move `huffman_starter.py` away from the other starter files.

VS Code may ask whether you want to install recommended Python extensions. Installing them is helpful, but the project does not require any third-party Python packages.

## Choose Your Packet
Open `huffman_starter.py` and set `PACKET_LETTER` to the first letter of your last name.

For example, a student with the last name `Stevens` should use:

```python
PACKET_LETTER = "S"
```

That setting uses:

```text
packets/S_huffman_image.json
```

## Run the Checks
From this folder, run:

```sh
python check_my_work.py
```

At first, the checks will say that functions are not finished yet. That is expected. Keep working until all checks pass.

You do not need to read or edit `check_my_work.py`. It is there so you can quickly see whether your two functions are working.

## Run the Decoder
After the checks pass, run:

```sh
python huffman_starter.py
```

Your script should create:

- `decoded_image.ppm`
- `decoded_preview.html`

Open `decoded_preview.html` in your browser to inspect your decoded image, compression statistics, tree facts, and most common colors.

## Packages and Libraries
Use Python 3 and the Python standard library only.

The file you edit uses:

- `pathlib.Path`, so local files are found relative to the project folder;
- `collections.abc.Iterable`, as a type hint for a sequence of pixels;
- `huffman_tools`, the provided support module for this project.

The support module uses standard-library tools such as `json`, `dataclasses`, `hashlib`, and `html`. These are helper details. Your main work is still the tree walk in `decode_bits` and the hashmap count in `count_pixels`.

Do not use:

- Pillow/PIL, OpenCV, imageio, matplotlib, or other image libraries;
- NumPy, pandas, or other array/dataframe libraries;
- compression or Huffman libraries such as `zlib`, `gzip`, `bz2`, `lzma`, `bitarray`, `bitstring`, or `dahuffman`;
- network, AI, or API packages;
- code that hard-codes the decoded image instead of walking the Huffman tree.

The `requirements.txt` file is intentionally empty except for comments. You do not need to install anything with `pip`.

## The Packet Format
Each packet is one JSON object. The important fields are:

- `width` and `height`: the decoded image size.
- `tree`: the provided Huffman tree.
- `bits`: the compressed bit string.
- `decoded_sha256`: an exact-match checksum for the decoded pixels.
- `bits_per_pixel_before_huffman`: the uncompressed RGB size used for compression statistics.

The checksum is mostly there for testing and debugging. It is like a fingerprint of the correct decoded image. The support code computes a checksum from your decoded pixels and compares it to `decoded_sha256`.

You do not decode `decoded_sha256`, and you do not need to understand the details of SHA-256. The project is about walking the Huffman tree.

## The Tree Format
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

The support code converts this JSON into `Node` objects. Your decoder should use:

- `current.left`
- `current.right`
- `current.is_leaf()`
- `current.symbol`

## Decoding Algorithm
The decoder reads bits from left to right:

1. Start at the root of the tree.
2. Read one bit.
3. Go left for `0`.
4. Go right for `1`.
5. When you reach a leaf, output that leaf's pixel.
6. Return to the root.
7. Continue until all bits are decoded.

Huffman codes are prefix-free. That means reaching a leaf tells you that one complete pixel has been decoded.

## Counting Pixels
After decoding, use a Python `dict` as a hashmap to count how many times each pixel color appears.

The pixel tuple is the key. The count is the value.

```python
counts[pixel] = counts.get(pixel, 0) + 1
```

This matters because Huffman coding works best when some symbols are much more common than others.

## Local Visualizer
Open this file in your browser:

```text
huffman_visualizer.html
```

It shows an example of Huffman decoding. Watch how each bit moves through the tree. Whenever the walk reaches a leaf, one pixel is emitted and the decoder returns to the root.

## Checklist
- `PACKET_LETTER` is set to your last-name initial.
- `python check_my_work.py` passes all checks.
- `python huffman_starter.py` runs without errors.
- The printed checksum matches the packet.
- `decoded_preview.html` shows a decoded image.
- Your output includes compression statistics and most common colors.
- You submit only `huffman_starter.py` to Canvas.

## Submission
Submit one `.py` file to Canvas:

- `huffman_starter.py`

Do not submit the whole starter folder, the packet JSON files, `decoded_image.ppm`, or `decoded_preview.html`.
