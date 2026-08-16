from pathlib import Path


class MismatchDetector:

    @staticmethod
    def detect(file_path, detected_signature):

        extension = Path(file_path).suffix.lower()

        mapping = {
            ".jpg": "JPEG image",
            ".jpeg": "JPEG image",
            ".png": "PNG image",
            ".pdf": "PDF document",
            ".exe": "Windows Executable",
            ".zip": "ZIP archive / Office document",
            ".docx": "ZIP archive / Office document",
        }

        expected = mapping.get(extension)

        if expected is None:
            return False

        return expected != detected_signature