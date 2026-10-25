# QRCoder

Generate and read QR codes from the terminal. Supports image generation, ASCII printing, and decoding QR codes from images (including multiple codes in one image).

## Dependencies

### System dependencies

`pyzbar` requires the `zbar` shared library. Install it with your package manager:

- **Debian/Ubuntu**: `sudo apt install libzbar0`
- **Fedora**: `sudo dnf install zbar`
- **Arch Linux**: `sudo pacman -S zbar`
- **macOS (Homebrew)**: `brew install zbar`
- **openSUSE**: `sudo zypper install zbar`

### Python dependencies

```bash
pip install qrcode[pil] pyzbar colorist Pillow
```

Or install in editable mode from this repo:

```bash
pip install -e .
```

## Usage

```bash
# Print QR code as ASCII to terminal
qrcoder -p "Hello, world!"

# Generate QR code image
qrcoder -g "Hello, world!" output.png

# Read QR code from image
qrcoder -r image.png
```

## Options

- `-p, --print DATA` - Print QR code ASCII in terminal
- `-g, --generate DATA` - Generate QR code image from data
- `-r, --read` - Read QR code from image (requires image path)
- `-n, --no-color` - Disable colored output
- `NO_COLOR=1` - Also disables colored output

## Exit codes

| Code | Meaning |
|---|---|
| 0 | Success |
| 1 | File does not exist |
| 2 | Invalid/cannot open image or permission error |
| 3 | No valid QR code found |
| 4 | Invalid Unicode in QR data |
| 5 | Output file already exists |
| 6 | Missing image path for -g/-r |
| 7 | Data too long to fit in QR code |
| 8 | Cannot write image |

## Notes

- When piping output, colors are automatically disabled
- Multiple QR codes in one image are all decoded and printed
- QR code generation uses error correction level H by default
