from pathlib import Path

from sherlocked.recovery.signatures import SignatureAnalyzer


def test_png_signature(tmp_path):
    test_file = tmp_path / "test.png"

    test_file.write_bytes(
        b"\x89PNG\r\n\x1a\n"
        b"test data"
    )

    result = SignatureAnalyzer.detect(test_file)

    assert result == "PNG image"


def test_pdf_signature(tmp_path):
    test_file = tmp_path / "test.pdf"

    test_file.write_bytes(
        b"%PDF-1.7\n"
        b"test"
    )

    result = SignatureAnalyzer.detect(test_file)

    assert result == "PDF document"


def test_unknown_signature(tmp_path):
    test_file = tmp_path / "unknown.bin"

    test_file.write_bytes(
        b"THIS IS NOT A KNOWN FILE FORMAT"
    )

    result = SignatureAnalyzer.detect(test_file)

    assert result == "Unknown"


def test_analyze_returns_details(tmp_path):
    test_file = tmp_path / "test.png"

    test_file.write_bytes(
        b"\x89PNG\r\n\x1a\n"
        b"test data"
    )

    result = SignatureAnalyzer.analyze(test_file)

    assert isinstance(result, dict)

    assert result["file"] == str(test_file)
    assert result["detected_type"] == "PNG image"
    assert result["signature"] is not None


def test_missing_file():
    result = SignatureAnalyzer.analyze(
        Path("this_file_does_not_exist.bin")
    )

    assert result["detected_type"] == "Unreadable"
    assert result["signature"] is None
    assert "error" in result