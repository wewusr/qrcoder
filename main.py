# Imports
import argparse
import os
import sys
from pathlib import Path

import PIL
import qrcode
from PIL import Image
from pyzbar.pyzbar import decode
from rich import print

# Class


class QRCodeError(Exception):
    def __init__(self, message: str, code: int):
        super().__init__(message)
        self.message = message
        self.code = code

    def __str__(self) -> str:
        return super().__str__()


# Helper Functions


def terminal_supports_color() -> bool:
    return sys.stdout.isatty() and "NO_COLOR" not in os.environ


def read_qr_image(image_path: Path) -> list[str]:
    if not image_path.exists():
        raise QRCodeError("Error: File does not exist", 1)
    try:
        with Image.open(image_path) as img:
            res = [r for r in decode(img) if r.type == "QRCODE"]

    except PIL.UnidentifiedImageError:
        raise QRCodeError("Error: Invalid image", 2)

    except Image.DecompressionBombError:
        raise QRCodeError("Error: Image is too large", 2)

    except PermissionError:
        raise QRCodeError("Error: Permission error", 2)

    except IsADirectoryError:
        raise QRCodeError("Error: Directory passed, not an image. Pass an image.", 2)

    except OSError:
        raise QRCodeError("Error: Cannot access image", 2)

    if not res:
        raise QRCodeError("Error: Did not find a valid QR code in image", 3)

    data = [r.data for r in res]

    try:
        return [d.decode("utf-8") for d in data]
    except UnicodeError:
        raise QRCodeError("Error: Invalid Unicode", 4)


def gen_qr_image(data: str, image_path: Path):
    if image_path.exists():
        raise QRCodeError("Error: File already exists", 5)

    qr = qrcode.QRCode(
        error_correction=qrcode.constants.ERROR_CORRECT_H,
    )
    qr.add_data(data=data)
    try:
        qr.make(fit=True)
    except (ValueError, qrcode.exceptions.DataOverflowError):
        raise QRCodeError("Error: Too much data to fit in a QR code", 7)

    img = qr.make_image(fill_color=(0, 0, 0), back_color=(255, 255, 255))

    try:
        img.save(image_path)

    except OSError:
        raise QRCodeError("Error: Cannot write image", 8)


def render_qr_ascii(data: str, use_color: bool):
    qr = qrcode.QRCode(
        error_correction=qrcode.constants.ERROR_CORRECT_H,
    )
    qr.add_data(data=data)
    try:
        qr.make(fit=True)
    except (ValueError, qrcode.exceptions.DataOverflowError):
        raise QRCodeError("Error: Too much data to fit in a QR code", 7)

    matrix = qr.get_matrix()

    for i in matrix:
        if use_color:
            row = ["[black]██[/black]" if j else "[white]██[/white]" for j in i]
        else:
            row = ["██" if j else "  " for j in i]
        print("".join(row))


# Argument Parser


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="QRCoder", description="Generate and read QRCodes from the terminal"
    )

    parser.add_argument(
        "image_path",
        nargs="?",
        help="Input image path (--read) or output image path (--generate). Not used with --print.",
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-g", "--generate", help="Generate QR code image from this data")
    group.add_argument("-p", "--print", help="Print QR code ASCII in terminal from this data")
    group.add_argument("-r", "--read", action="store_true", help="Read QR code from image")
    parser.add_argument("-n", "--no-color", action="store_true", help="Disable colored output")
    return parser


parser = build_parser()

# Main Execution


def main(argv=None) -> int:
    try:
        args = parser.parse_args(argv)
        use_color = terminal_supports_color() and not args.no_color

        if args.print is not None:
            render_qr_ascii(args.print, use_color)
            return 0

        if not args.image_path:
            raise QRCodeError("Error: image_path is required for --generate and --read", 6)

        if args.generate is not None:
            gen_qr_image(args.generate, Path(args.image_path))
        else:
            res = read_qr_image(Path(args.image_path))
            if len(res) == 1:
                print(res[0])
            else:
                for i, r in enumerate(res):
                    if use_color:
                        print(f"[bold green]---------- QR Code {i + 1} ----------[/bold green]")
                    else:
                        print(f"---------- QR Code {i + 1} ----------")
                    print(r)
    except QRCodeError as e:
        print(e.message, file=sys.stderr)
        return e.code
    return 0


if __name__ == "__main__":
    sys.exit(main())
