from pathlib import Path


class SignatureAnalyzer:
    """
    Detect file types using magic/signature bytes.
    """

    SIGNATURES = {
        b"\x89PNG\r\n\x1a\n": "PNG image",
        b"\xff\xd8\xff": "JPEG image",
        b"GIF87a": "GIF image",
        b"GIF89a": "GIF image",
        b"%PDF": "PDF document",
        b"PK\x03\x04": "ZIP archive / Office document",
        b"Rar!\x1a\x07\x00": "RAR archive",
        b"7z\xbc\xaf\x27\x1c": "7-Zip archive",
        b"\x1f\x8b": "GZIP compressed data",
        b"SQLite format 3\x00": "SQLite database",
        b"RIFF": "RIFF container",
        b"ID3": "MP3 audio",
        b"MZ": "Windows Executable"
    }

    @classmethod
    def detect(cls, file_path):
        """
        Detect a file type using its magic bytes.

        Returns:
            str: Detected file type or 'Unknown'
        """
        file_path = Path(file_path)

        try:
            with file_path.open("rb") as f:
                header = f.read(32)
        except (OSError, PermissionError):
            return "Unreadable"

        for signature, file_type in cls.SIGNATURES.items():
            if header.startswith(signature):
                return file_type

        return "Unknown"

    @classmethod
    def analyze(cls, file_path):
        """
        Return detailed signature-analysis information.
        """
        file_path = Path(file_path)

        try:
            with file_path.open("rb") as f:
                header = f.read(32)
        except (OSError, PermissionError) as exc:
            return {
                "file": str(file_path),
                "detected_type": "Unreadable",
                "signature": None,
                "error": str(exc),
            }

        detected_type = "Unknown"

        for signature, file_type in cls.SIGNATURES.items():
            if header.startswith(signature):
                detected_type = file_type
                break

        return {
            "file": str(file_path),
            "detected_type": detected_type,
            "signature": header.hex(" "),
        }