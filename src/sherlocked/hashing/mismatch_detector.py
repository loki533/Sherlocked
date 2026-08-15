from pathlib import Path


class MismatchDetector:

    @staticmethod
    def detect(file_path, detected_type):

        extension = Path(file_path).suffix.lower()

        mapping = {
            ".jpg": "JPEG image",
            ".jpeg": "JPEG image",
            ".png": "PNG image",
            ".gif": "GIF image",
            ".pdf": "PDF document",
            ".zip": "ZIP archive / Office document",
            ".docx": "ZIP archive / Office document",
            ".xlsx": "ZIP archive / Office document",
            ".pptx": "ZIP archive / Office document",
            ".gz": "GZIP compressed data",
            ".mp3": "MP3 audio",
        }

        expected = mapping.get(extension)

        # Unknown extensions cannot currently be classified
        if expected is None:
            return False

        return expected != detected_type