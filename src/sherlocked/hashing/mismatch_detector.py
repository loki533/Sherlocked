from pathlib import Path


class MismatchDetector:

    @staticmethod
    def detect(file_path, detected_signature):

        extension = Path(file_path).suffix.lower()

        mapping = {
            ".jpg": "JPEG Image",
            ".jpeg": "JPEG Image",
            ".png": "PNG Image",
            ".pdf": "PDF Document",
            ".exe": "Windows Executable",
            ".zip": "ZIP Archive / DOCX / XLSX",
            ".docx": "ZIP Archive / DOCX / XLSX",
        }

        expected = mapping.get(extension)

        if expected is None:
            return False

        return expected != detected_signature