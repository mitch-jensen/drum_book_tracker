from pathlib import Path

from PIL import Image

from book_tracker.ocr import _extract_audiveris_detail, _prepare_notation_image_for_ocr


def test_prepare_notation_image_upscales_low_resolution_image(tmp_path: Path) -> None:
    input_path = tmp_path / "tiny.png"
    output_dir = tmp_path / "out"

    Image.new("RGB", (264, 116), color="white").save(input_path, format="PNG")

    prepared_path = _prepare_notation_image_for_ocr(str(input_path), str(output_dir))

    assert prepared_path != str(input_path)
    prepared_file = Path(prepared_path)
    assert prepared_file.exists()

    with Image.open(prepared_file) as prepared:
        assert prepared.width >= 1000
        assert prepared.height >= 400
        dpi = prepared.info.get("dpi", (0, 0))
        assert dpi[0] >= 299
        assert dpi[1] >= 299


def test_prepare_notation_image_keeps_adequate_image_unchanged(tmp_path: Path) -> None:
    input_path = tmp_path / "good_scan.png"
    output_dir = tmp_path / "out"

    Image.new("RGB", (2400, 3200), color="white").save(input_path, format="PNG", dpi=(300, 300))

    prepared_path = _prepare_notation_image_for_ocr(str(input_path), str(output_dir))

    assert prepared_path == str(input_path)


def test_extract_audiveris_detail_prefers_resolution_warning() -> None:
    output = """
INFO  [sample] SheetStub 1194 | Sheet sample flagged as invalid.
WARN  [sample] ScaleBuilder 1166 | With a too low interline value of 7 pixels, either this sheet contains no multi-line staves, or the picture resolution is too low (try 300 DPI).
"""

    detail = _extract_audiveris_detail(output)

    assert "too low interline" in detail


def test_extract_audiveris_detail_includes_stub_cause_line() -> None:
    output = """
ERROR [sample] Book 320 | Error processing stub
Caused by: java.lang.IllegalStateException: Invalid image geometry for system detection
    at org.audiveris.omr.sheet.SystemManager.buildSystems(SystemManager.java:421)
"""

    detail = _extract_audiveris_detail(output)

    assert "Error processing stub" in detail
    assert "Invalid image geometry" in detail


def test_extract_audiveris_detail_skips_book_storing_noise() -> None:
    output = """
ERROR [sample] Book 320 | Error processing stub
INFO  [sample] Book 555 | Book{Screenshot_2026-04-20_223015} storing
Caused by: java.lang.IllegalArgumentException: No system candidates found
"""

    detail = _extract_audiveris_detail(output)

    assert "Error processing stub" in detail
    assert "No system candidates found" in detail
    assert "storing" not in detail


def test_extract_audiveris_detail_skips_stored_bookxml_noise() -> None:
    output = """
ERROR [sample] Book 320 | Error processing stub
INFO  [sample] ExportPattern 101 | Stored /book.xml
Caused by: java.lang.IllegalStateException: Could not detect valid staff systems
"""

    detail = _extract_audiveris_detail(output)

    assert "Error processing stub" in detail
    assert "Could not detect valid staff systems" in detail
    assert "Stored /book.xml" not in detail


def test_extract_audiveris_detail_skips_book_stored_as_omr_noise() -> None:
    output = """
ERROR [sample] Book 320 | Error processing stub
INFO  [sample] Book 221 | Book stored as /tmp/tmpd8f4jaeg/Screenshot_2026-04-20_223015.omr
WARN  [sample] ScaleBuilder 1166 | With a too low interline value of 7 pixels, either this sheet contains no multi-line staves, or the picture resolution is too low (try 300 DPI).
"""

    detail = _extract_audiveris_detail(output)

    assert "too low interline" in detail
    assert "Book stored as" not in detail
