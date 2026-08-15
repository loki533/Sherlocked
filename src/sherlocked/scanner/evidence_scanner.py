from pathlib import Path


class EvidenceScanner:
    """
    Scans an evidence directory and returns all files recursively.
    """

    @staticmethod
    def scan(evidence_path):
        """
        Recursively scans the given directory and returns
        a list of all file paths.

        Args:
            evidence_path (str | Path): Path to the evidence directory.

        Returns:
            list[Path]: List of file paths.
        """

        evidence_path = Path(evidence_path)

        if not evidence_path.exists():
            raise FileNotFoundError(
                f"Evidence path '{evidence_path}' does not exist."
            )

        if not evidence_path.is_dir():
            raise NotADirectoryError(
                f"'{evidence_path}' is not a directory."
            )

        files = []

        for file in evidence_path.rglob("*"):
            if file.is_file():
                files.append(file)

        return files