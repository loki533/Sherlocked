import json

from core.case import Case
from config import CASES_DIR


class CaseManager:

    def create_case(self):
        """
        Creates a new investigation case and stores it on disk.
        """

        case_id = input("Case ID: ").strip()
        investigator = input("Investigator: ").strip()
        description = input("Description: ").strip()
        evidence_path = input("Evidence Path: ").strip()

        case = Case(
            case_id=case_id,
            investigator=investigator,
            description=description,
            evidence_path=evidence_path
        )

        case_folder = CASES_DIR / case.case_id
        case_folder.mkdir(parents=True, exist_ok=True)

        with open(case_folder / "case.json", "w") as file:
            json.dump(case.to_dict(), file, indent=4)

        with open(case_folder / "notes.txt", "w") as file:
            file.write("=== Investigation Notes ===\n")

        print(f"\n✅ Case '{case.case_id}' created successfully.")

        return case