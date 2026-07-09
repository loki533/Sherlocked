from modules.signatures_db import SIGNATURES


class SignatureAnalyzer:

    @staticmethod
    def identify(file_path):

        with open(file_path, "rb") as f:
            header = f.read(32)

        for signature, info in SIGNATURES.items():

            if header.startswith(signature):

                return {
                    "signature": info[0],
                    "category": info[1]
                }

        # Try plain text detection
        try:
            header.decode("utf-8")

            if all(
                (32 <= b <= 126) or b in (9, 10, 13)
                for b in header
            ):
                return {
                    "signature": "Plain Text",
                    "category": "Text"
                }

        except UnicodeDecodeError:
            pass

        return {
            "signature": "Unknown",
            "category": "Unknown"
        }