from pathlib import Path


class FileClassifier:

    CATEGORIES = {

        "Images": [
            ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff"
        ],

        "Documents": [
            ".pdf", ".doc", ".docx",
            ".xls", ".xlsx",
            ".ppt", ".pptx",
            ".txt"
        ],

        "Archives": [
            ".zip", ".rar", ".7z", ".tar", ".gz"
        ],

        "Executables": [
            ".exe", ".dll", ".msi", ".bat", ".cmd"
        ],

        "Videos": [
            ".mp4", ".avi", ".mov", ".mkv"
        ],

        "Audio": [
            ".mp3", ".wav", ".aac"
        ]
    }

    @staticmethod
    def classify(file_path):

        extension = Path(file_path).suffix.lower()

        for category, extensions in FileClassifier.CATEGORIES.items():

            if extension in extensions:
                return category

        return "Unknown"