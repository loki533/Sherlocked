import os
import json

from core.case import Case

class CaseManager:
    CASE_DIRECTORY = "cases"
    def create_case(self):

        case_id = input("Case ID: ")
        investigator = input("Investigator: ")
        description = input("Description: ")
        evidence_path = input("Evidence Path: ")

        case=Case(
            case_id,
            investigator,
            description,
            evidence_path
        )

        folder = os.path.join(self.CASE_DIRECTORY,case.case_id)

        os.makedirs(folder, exist_ok=True)

        with open(os.path.join(folder, "case.json"), "w") as file:
            json.dump(case.to_dict(), file, indent=4)

        with open(os.path.join(folder, "notes.txt"), "w") as file:
            file.write("Investigation Notes\n")

        print("\nCase created successfully.")