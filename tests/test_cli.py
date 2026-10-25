from unittest.mock import patch

import pytest
from PIL import Image

import main

# Argument parsing & falsy values


def test_cli_print_empty_string(capsys):
    code = main.main(["-p", ""])
    out, err = capsys.readouterr()
    assert code == 0
    assert err == ""
    assert "█" in out


def test_cli_generate_empty_string_needs_path(capsys):
    code = main.main(["-g", ""])
    out, err = capsys.readouterr()
    assert code == 6
    assert "Error: image_path is required for --generate and --read" in err


def test_cli_generate_empty_string_with_path(tmp_path, capsys):
    code = main.main(["-g", "", str(tmp_path / "img.png")])
    out, err = capsys.readouterr()
    assert code == 0
    assert err == ""


def test_cli_read_needs_path(capsys):
    code = main.main(["-r", ""])
    out, err = capsys.readouterr()
    assert code == 6
    assert "Error: image_path is required for --generate and --read" in err


def test_cli_generate_file_exists(tmp_path, capsys):
    img_path = tmp_path / "img.png"
    img_path.write_text("data")
    code = main.main(["-g", "data", str(img_path)])
    out, err = capsys.readouterr()
    assert code == 5
    assert "Error: File already exists" in err


def test_cli_print_data_overflow(capsys):
    code = main.main(["-p", "data" * (10**5)])
    out, err = capsys.readouterr()
    assert "Error: Too much data to fit in a QR code" in err
    assert code == 7


def test_cli_generate_data_overflow(tmp_path, capsys):
    code = main.main(["-g", "data" * (10**5), str(tmp_path / "img.png")])
    out, err = capsys.readouterr()
    assert "Error: Too much data to fit in a QR code" in err
    assert code == 7


def test_cli_generate_then_read(tmp_path, capsys):
    img_path = tmp_path / "img.png"
    code1 = main.main(["-g", "data", str(img_path)])
    out, err = capsys.readouterr()
    assert code1 == 0
    assert out == ""

    code2 = main.main(["-r", str(img_path)])
    out, err = capsys.readouterr()
    assert code2 == 0
    assert out.strip() == "data"


def test_cli_without_flags(capsys):
    with pytest.raises(SystemExit) as exc_info:
        main.main([])

    out, err = capsys.readouterr()
    assert exc_info.value.code != 0
    assert err != ""


def test_cli_read_nonexistent_file(tmp_path, capsys):
    code = main.main(["-r", str(tmp_path / "missing.png")])
    out, err = capsys.readouterr()
    assert code == 1
    assert "Error: File does not exist" in err


def test_cli_read_invalid_image(tmp_path, capsys):
    img_path = tmp_path / "invalid.png"
    img_path.write_text("not an image")
    code = main.main(["-r", str(img_path)])
    out, err = capsys.readouterr()
    assert code == 2
    assert "Error: Invalid image" in err


def test_cli_read_no_qr_code(tmp_path, capsys):
    img_path = tmp_path / "blank.png"
    img = Image.new("RGB", (50, 50), "white")
    img.save(img_path)
    code = main.main(["-r", str(img_path)])
    out, err = capsys.readouterr()
    assert code == 3
    assert "Error: Did not find a valid QR code in image" in err


def test_cli_write_error(tmp_path, capsys):
    img_path = tmp_path / "out.png"
    with patch("PIL.Image.Image.save", side_effect=OSError):
        code = main.main(["-g", "hello", str(img_path)])
    out, err = capsys.readouterr()
    assert code == 8
    assert "Error: Cannot write image" in err


def test_cli_print_no_color(capsys):
    code = main.main(["-p", "hello", "-n"])
    out, err = capsys.readouterr()
    assert code == 0
    assert err == ""
    assert "██" in out
    assert "[" not in out
