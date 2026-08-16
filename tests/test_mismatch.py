from sherlocked.hashing.mismatch_detector import MismatchDetector


def test_png_matches_png_signature():
    result = MismatchDetector.detect(
        "test.png",
        "PNG image"
    )

    assert result is False


def test_png_with_wrong_signature_is_suspicious():
    result = MismatchDetector.detect(
        "test.png",
        "PDF Document"
    )

    assert result is True


def test_pdf_matches_pdf_signature():
    result = MismatchDetector.detect(
        "test.pdf",
        "PDF document"
    )

    assert result is False


def test_unknown_extension_is_not_flagged():
    result = MismatchDetector.detect(
        "test.xyz",
        "Something"
    )

    assert result is False