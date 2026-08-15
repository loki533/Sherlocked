from datetime import datetime
from pathlib import Path


class Case:
    def __init__(
        self,
        case_id,
        investigator,
        description,
        evidence_path
    ):
        self.case_id = case_id
        self.investigator = investigator
        self.description = description
        self.evidence_path = evidence_path
        self.created_at = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        # Forensic data
        self.hashes = {}
        self.metadata = []
        self.timeline = []
        self.recovered_files = []

    @staticmethod
    def _serialize(value):
        """
        Convert objects that are not natively JSON serializable
        into JSON-compatible representations.
        """

        if isinstance(value, Path):
            return str(value)

        if isinstance(value, dict):
            return {
                key: Case._serialize(val)
                for key, val in value.items()
            }

        if isinstance(value, list):
            return [
                Case._serialize(item)
                for item in value
            ]

        if isinstance(value, tuple):
            return [
                Case._serialize(item)
                for item in value
            ]

        return value

    def to_dict(self):
        """
        Convert the Case object into a JSON-serializable dictionary.
        """

        return self._serialize({
            "case_id": self.case_id,
            "investigator": self.investigator,
            "description": self.description,
            "evidence_path": self.evidence_path,
            "created_at": self.created_at,

            # Forensic investigation data
            "hashes": self.hashes,
            "metadata": self.metadata,
            "timeline": self.timeline,
            "recovered_files": self.recovered_files,
        })

    @staticmethod
    def from_dict(data):
        """
        Reconstruct a Case object from a dictionary.
        """

        case = Case(
            data["case_id"],
            data["investigator"],
            data["description"],
            data["evidence_path"]
        )

        case.created_at = data.get(
            "created_at",
            case.created_at
        )

        case.hashes = data.get(
            "hashes",
            {}
        )

        case.metadata = data.get(
            "metadata",
            []
        )

        case.timeline = data.get(
            "timeline",
            []
        )

        case.recovered_files = data.get(
            "recovered_files",
            []
        )

        return case