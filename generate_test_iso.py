from pathlib import Path
import pycdlib


OUTPUT = Path("evidence/test_evidence.iso")


def create_test_iso():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    iso = pycdlib.PyCdlib()

    # Create a new ISO
    iso.new(
    interchange_level=3,
    joliet=True)

    # ---------------------------------------------------------
    # Create directories
    # ---------------------------------------------------------

    iso.add_directory(
        "/EVIDENCE"
    )

    iso.add_directory(
        "/EVIDENCE/DOCUMENTS"
    )

    iso.add_directory(
        "/EVIDENCE/IMAGES"
    )

    # ---------------------------------------------------------
    # Create test files
    # ---------------------------------------------------------

    document = Path("iso_test_document.txt")

    document.write_text(
        "Sherlocked Digital Forensics Test Evidence\n"
        "===========================================\n"
        "This file was generated for ISO analysis testing.\n"
        "Case: TEST-ISO-001\n"
        "Purpose: Validate ISO filesystem enumeration.\n",
        encoding="utf-8"
    )

    image_data = (
        b"\x89PNG\r\n\x1a\n"
        b"SHERLOCKED_TEST_IMAGE"
    )

    test_image = Path("iso_test.png")
    test_image.write_bytes(image_data)

    # ---------------------------------------------------------
    # Add files to ISO
    # ---------------------------------------------------------

    iso.add_file(
        str(document),
        "/EVIDENCE/DOCUMENTS/TEST.TXT;1"
    )

    iso.add_file(
        str(test_image),
        "/EVIDENCE/IMAGES/TEST.PNG;1"
    )

    # ---------------------------------------------------------
    # Add another text file
    # ---------------------------------------------------------

    notes = Path("iso_notes.txt")

    notes.write_text(
        "Forensic test notes\n"
        "-------------------\n"
        "ISO created specifically for Sherlocked.\n"
        "Contains a text document and a PNG-signature test file.\n",
        encoding="utf-8"
    )

    iso.add_file(
        str(notes),
        "/EVIDENCE/NOTES.TXT;1"
    )

    # ---------------------------------------------------------
    # Write ISO
    # ---------------------------------------------------------

    iso.write(str(OUTPUT))

    # Close ISO
    iso.close()

    # Remove temporary source files
    document.unlink(missing_ok=True)
    test_image.unlink(missing_ok=True)
    notes.unlink(missing_ok=True)

    print("[+] Test ISO created successfully")
    print(f"[+] Location: {OUTPUT.resolve()}")
    print(f"[+] Size: {OUTPUT.stat().st_size:,} bytes")


if __name__ == "__main__":
    create_test_iso()