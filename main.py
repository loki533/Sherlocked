from core.case_manager import CaseManager
from core.evidence_analyzer import EvidenceAnalyzer
from core.ui import show_banner, show_menu
from core.logger import logger

manager = CaseManager()
analyzer = EvidenceAnalyzer()

current_case = None

logger.info("Sherlocked started")

show_banner()

while True:

    choice = show_menu()

    if choice == "1":

        current_case = manager.create_case()

    elif choice == "2":

        print("Coming Soon")

    elif choice == "3":

        print("Coming Soon")

    elif choice == "4":

        if current_case is None:

            print("Create/Open a case first.")

        else:

            analyzer.analyze(current_case)

            manager.save_case(current_case)

    elif choice == "5":

        print("Coming Soon")

    elif choice == "6":

        logger.info("Application closed")

        break

    else:

        print("Invalid option.")