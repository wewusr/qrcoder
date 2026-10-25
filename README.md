# QRCoder

Generate and read QR codes directly from the terminal. Supports image generation, terminal ASCII/color rendering, and decoding single or multiple QR codes from images.

## Features

- **Terminal Rendering**: Print high-contrast ASCII QR codes with rich color support (automatically respects `NO_COLOR` and non-TTY redirection).
- **Image Generation**: Generate and save QR code images with error correction level H.
- **Image Decoding**: Read and decode one or multiple QR codes from an image file.
- **Robust Error Handling**: Comprehensive exit codes and error messages for file access, data overflow, and invalid formats.

---

## Dependencies

### System Dependencies

`pyzbar` requires the native `zbar` shared library. Install it using your system package manager:

- **Debian / Ubuntu**: `sudo apt install libzbar0`
- **Fedora**: `sudo dnf install zbar`
- **Arch Linux**: `sudo pacman -S zbar`
- **macOS (Homebrew)**: `brew install zbar`
- **openSUSE**: `sudo zypper install zbar`

### Python Dependencies

Install the required Python packages:

```bash
pip install qrcode[pil] pyzbar rich Pillow
```

Or install the package in editable mode from the repository:

```bash
pip install -e .
```

---

## Usage

```bash
# Print QR code as ASCII / color in the terminal
python main.py -p "Hello, world!"

# Generate a QR code image
python main.py -g "Hello, world!" output.png

# Read a QR code from an image
python main.py -r image.png

# Disable color output explicitly
python main.py -p "Hello, world!" --no-color
```

---

## Options

| Flag | Argument | Description |
| :--- | :--- | :--- |
| `-p`, `--print` | `DATA` | Print QR code ASCII in the terminal. |
| `-g`, `--generate` | `DATA` | Generate QR code image from data (requires output path). |
| `-r`, `--read` | None | Read QR code from image (requires input path). |
| `-n`, `--no-color` | None | Disable colored output. |
| `-h`, `--help` | None | Show help message and exit. |

*Note:* `image_path` is positional and required when using `-g` (output path) or `-r` (input path). It is not used with `-p`.

---

## Exit Codes

| Code | Description |
| :---: | :--- |
| **0** | Success |
| **1** | File does not exist |
| **2** | Invalid image, image too large, permission error, directory passed, or cannot access image |
| **3** | No valid QR code found in the image |
| **4** | Invalid Unicode in QR data |
| **5** | Output file already exists |
| **6** | Missing image path for `--generate` or `--read` |
| **7** | Data too long to fit in a QR code (Data overflow) |
| **8** | Cannot write image file |

---

## Notes

- **Color Support**: Colors are enabled by default in interactive terminals (TTY) and automatically disabled when piping output or when the `NO_COLOR` environment variable is set.
- **Multi-QR Decoding**: If an image contains multiple QR codes, all of them are decoded and printed sequentially.
- **Error Correction**: QR codes are generated using error correction level H (High) by default for maximum reliability.
