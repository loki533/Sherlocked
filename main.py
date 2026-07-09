from rich.console import Console
from pathlib import Path

from core.case_manager import CaseManager
from core.evidence_analyzer import EvidenceAnalyzer
from core.logger import logger
from core.ui import show_banner, show_menu
from core.table import display_inventory
from core.timeline_table import display_timeline
from core.browser_table import display_history
from core.download_table import display_downloads

from modules.timeline import TimelineGenerator
from modules.browser.chrome import ChromeArtifacts




console = Console()
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

        current_case = manager.open_case()

        if current_case:

            console.print(
                f"[bold green]Opened Case: {current_case.case_id}[/bold green]"
            )

    elif choice == "3":

        if current_case is None:

            console.print("[bold red]Create a case first![/bold red]")

        else:

            logger.info(f"Analyzing case {current_case.case_id}")

            current_case = analyzer.analyze(current_case)

            manager.save_case(current_case)

            # Display inventory
            display_inventory(current_case.metadata)

            # Generate timeline
            timeline = TimelineGenerator.build(current_case.metadata)

            # Display timeline
            display_timeline(timeline)

            console.print(
                "\n[bold green]✓ Evidence analysis completed.[/bold green]"
            )
            
    elif choice == "4":

        if current_case is None:

            print("Create/Open a case first.")

        else:

            analyzer.analyze(current_case)

            manager.save_case(current_case)

    elif choice == "5":

        print("Browser Artifacts")

        logger.info("Extraction of Browser History")

        history = ChromeArtifacts.extract(Path.home() /
        "AppData/Local/Google/Chrome/User Data/Default/History")

        display_history(history)

    elif choice == "6":

        logger.info("Extraced Browser Downloads")
        history_path = Path.home() / "AppData/Local/Google/Chrome/User Data/Default/History"
        
        downloads = ChromeArtifacts.extract_downloads(history_path)
        display_downloads(downloads)



    elif choice == "7":

        logger.info("Application closed")

        break

    else:

        print("Invalid option.")