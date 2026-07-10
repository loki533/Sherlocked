import hashlib
from io import BytesIO
from pathlib import Path

import pycdlib


class ISOAnalyzer:
    """
    Analyze ISO9660 images without mounting them.
    """

    EXECUTABLE_EXTENSIONS = (
        ".exe",
        ".dll",
        ".bat",
        ".cmd",
        ".ps1",
        ".msi",
        ".com",
        ".scr",
    )

    SUSPICIOUS_KEYWORDS = (
        "hack",
        "crack",
        "keygen",
        "loader",
        "patch",
        "payload",
        "inject",
        "trojan",
        "virus",
        "malware",
        "backdoor",
        "exploit",
        "miner",
        "ransom",
    )

    def __init__(self, iso_path):

        self.iso_path = Path(iso_path)

        self.files = []
        self.directories = []

        self.executables = []
        self.hidden = []
        self.suspicious = []

        self.hashes = []


    def analyze(self):

        iso = pycdlib.PyCdlib()
        iso.open(str(self.iso_path))

        try:
            self.walk_directory(iso, "/")

        finally:
            iso.close()

        #sorts the first 10 files based on their size
        largest = sorted(
            self.hashes,
            key=lambda x: x["size"],
            reverse=True,
        )[:10]

        return {
            "image_name": self.iso_path.name,
            "image_size": self.iso_path.stat().st_size,
            "total_files": len(self.files),
            "total_directories": len(self.directories),
            "executables": self.executables,
            "hidden_files": self.hidden,
            "suspicious_files": self.suspicious,
            "largest_files": largest,
            "hashes": self.hashes,
        }

    #recursive function call , to traverse through the entire directory

    def walk_directory(self, iso, path):

        try:
            children = list(iso.list_children(iso_path=path))#lists the children of the CD

        except Exception:
            return

        for child in children:
            try:
                name = child.file_identifier().decode(
                    errors="ignore"
                ).rstrip(";1")

            except Exception:
                continue

            if name in (".", "..", ""):#to prevent the CD, and the parent -> to avoid loops
                continue

            full_path = path + name

            if child.is_dir():

                self.directories.append(full_path)
                self.walk_directory(
                    iso,
                    full_path + "/",
                )

            else:     #if the child is a file , check for the extensions.

                self.files.append(full_path)
                lower = name.lower()

                if lower.startswith("."):
                    self.hidden.append(full_path)

                if lower.endswith(self.EXECUTABLE_EXTENSIONS):
                    self.executables.append(full_path)

                if any(
                    keyword in lower
                    for keyword in self.SUSPICIOUS_KEYWORDS
                ):
                    self.suspicious.append(full_path)

                info = self.hash_file(
                    iso,
                    full_path,
                )

                if info:
                    self.hashes.append(info)

    def hash_file(self, iso, iso_path):

        try:

            buffer = BytesIO() #creates a virtual file , instead of actually downloadin it.
            iso.get_file_from_iso_fp(
                buffer,
                iso_path=iso_path,
            )

            data = buffer.getvalue()
            sha256 = hashlib.sha256(data).hexdigest()

            return {
                "file": iso_path,
                "size": len(data),
                "sha256": sha256,
            }

        except Exception:

            return None