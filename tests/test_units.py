import os
from unittest.mock import patch

import pytest
from PIL import Image

import main

# Reading QR codes


def test_read_missing_file(tmp_path):
    img_path = tmp_path / "img.png"

    with pytest.raises(main.QRCodeError) as exc_info:
        main.read_qr_image(img_path)

    assert exc_info.value.code == 1
    assert "Error: File does not exist" in str(exc_info.value)


def test_read_invalid_img(tmp_path):
    img_path = tmp_path / "invalid_img.png"
    img_path.write_text("not image data")

    with pytest.raises(main.QRCodeError) as exc_info:
        main.read_qr_image(img_path)

    assert exc_info.value.code == 2
    assert "Error: Invalid image" in str(exc_info.value)


def test_read_image_too_large(tmp_path):
    img_path = tmp_path / "img.png"
    img = Image.new("RGB", (20, 20), "red")
    img.save(img_path)

    original_max = Image.MAX_IMAGE_PIXELS
    Image.MAX_IMAGE_PIXELS = 100

    try:
        with pytest.raises(main.QRCodeError) as exc_info:
            main.read_qr_image(img_path)

        assert "Error: Image is too large" in str(exc_info.value)
        assert exc_info.value.code == 2

    finally:
        Image.MAX_IMAGE_PIXELS = original_max


def test_read_permission_error(tmp_path):
    img_path = tmp_path / "img.png"
    img_path.write_text("some data")
    os.chmod(img_path, 0o200)

    try:
        with pytest.raises(main.QRCodeError) as exc_info:
            main.read_qr_image(img_path)

        assert exc_info.value.code == 2
        assert "Error: Permission error" in str(exc_info.value)

    finally:
        os.chmod(img_path, 0o700)


def test_read_dir(tmp_path):
    with pytest.raises(main.QRCodeError) as exc_info:
        main.read_qr_image(tmp_path)

    assert exc_info.value.code == 2
    assert "Error: Directory passed, not an image. Pass an image." in str(exc_info.value)


def test_read_os_error(tmp_path):
    img_path = tmp_path / "img.png"
    img_path.write_text("dummy")
    with patch("PIL.Image.open", side_effect=OSError):
        with pytest.raises(main.QRCodeError) as exc_info:
            main.read_qr_image(img_path)
        assert exc_info.value.code == 2
        assert "Error: Cannot access image" in str(exc_info.value)


def test_read_found_no_valid_qr_code(tmp_path):
    img_path = tmp_path / "img.png"
    img = Image.new("RGB", (50, 50), "white")
    img.save(img_path)

    with pytest.raises(main.QRCodeError) as exc_info:
        main.read_qr_image(img_path)

    assert exc_info.value.code == 3
    assert "Error: Did not find a valid QR code in image" in str(exc_info.value)


# QR Generation Tests


def test_gen_qr_image_success(tmp_path):
    img_path = tmp_path / "qr_out.png"
    main.gen_qr_image("Hello world", img_path)
    assert img_path.exists()
    assert img_path.stat().st_size > 0


def test_gen_qr_image_already_exists(tmp_path):
    img_path = tmp_path / "existing.png"
    img_path.write_text("existing content")

    with pytest.raises(main.QRCodeError) as exc_info:
        main.gen_qr_image("data", img_path)

    assert exc_info.value.code == 5
    assert "Error: File already exists" in str(exc_info.value)


def test_gen_qr_image_data_overflow(tmp_path):
    img_path = tmp_path / "overflow.png"
    with pytest.raises(main.QRCodeError) as exc_info:
        main.gen_qr_image("data" * (10**5), img_path)

    assert exc_info.value.code == 7
    assert "Error: Too much data to fit in a QR code" in str(exc_info.value)


def test_gen_qr_image_write_error(tmp_path):
    img_path = tmp_path / "error.png"
    with patch("PIL.Image.Image.save", side_effect=OSError):
        with pytest.raises(main.QRCodeError) as exc_info:
            main.gen_qr_image("hello", img_path)

        assert exc_info.value.code == 8
        assert "Error: Cannot write image" in str(exc_info.value)


# ASCII Print Tests


def test_print_qr_ascii_success():
    # Verify both color modes execute cleanly without raising errors
    main.render_qr_ascii("Hello world", use_color=True)
    main.render_qr_ascii("Hello world", use_color=False)


def test_render_qr_ascii_data_overflow():
    with pytest.raises(main.QRCodeError) as exc_info:
        main.render_qr_ascii("data" * (10**5), use_color=True)

    assert exc_info.value.code == 7
    assert "Error: Too much data to fit in a QR code" in str(exc_info.value)
