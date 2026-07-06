from pathlib import Path

class SignatureAnalyzer:
    SIGNATURES = {
        b"\xFF\xD8\xFF": "JPEG Image",
        b"\x89PNG\r\n\x1a\n": "PNG Image",
        b"%PDF": "PDF Document",
        b"PK\x03\x04": "ZIP Archive",
        b"MZ": "Windows Executable",
    }

    @staticmethod
    def identify(file_path):
        file_path = Path(file_path)
        
        # 1. Check for binary magic bytes
        with open(file_path, "rb") as file:
            header = file.read(16)
            
        for signature, filetype in SignatureAnalyzer.SIGNATURES.items():
            if header.startswith(signature):
                return filetype
                
        # check for valid text
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                file.read(1024) # Try reading the beginning as string , since text files dont have a signature
            return "Plain Text"
        except (UnicodeDecodeError, OSError):
            return "Unknown"

    @staticmethod
    def is_suspicious(file_path, detected_type):
        extension = Path(file_path).suffix.lower()
        mapping = {
            ".jpg": "JPEG Image",
            ".jpeg": "JPEG Image",
            ".png": "PNG Image",
            ".pdf": "PDF Document",
            ".zip": "ZIP Archive",
            ".exe": "Windows Executable",
            ".txt": "Plain Text"  
        }
        
        expected = mapping.get(extension)
        if expected is None:
            return False
        return expected != detected_type