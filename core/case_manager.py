import json

from core.case import Case
from config import CASES_DIR
from core.logger import logger
import os


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
        logger.info(f"Case {case.case_id} created")

        return case

    def save_case(self, case):

        folder = CASES_DIR / case.case_id

        with open(folder / "case.json", "w") as file:

            json.dump(case.to_dict(), file, indent=4)
            
        logger.info(f"Case {case.case_id} saved")
    
    def open_case(self):

        if not CASES_DIR.exists():

            print("No cases found.")
            return None

        cases = []

        for folder in CASES_DIR.iterdir():

            if folder.is_dir():
                cases.append(folder)

        if not cases:

            print("No existing cases.")
            return None

        print("\nExisting Cases")

        for i, folder in enumerate(cases, start=1):

            print(f"{i}. {folder.name}")

        try:
            choice = int(input("\nSelect case: "))

        except ValueError:

            print("Invalid input.")
            return None

        if choice < 1 or choice > len(cases):

            print("Invalid selection.")
            return None

        selected_folder = cases[choice - 1]

        with open(selected_folder / "case.json", "r") as file:

            data = json.load(file)

        case = Case.from_dict(data)

        logger.info(f"Opened case {case.case_id}")

        print(f"\n✅ Opened Case: {case.case_id}")

        return case