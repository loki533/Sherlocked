from rich.console import Console

from core.case_manager import CaseManager
from core.evidence_analyzer import EvidenceAnalyzer
from core.logger import logger
from core.ui import show_banner, show_menu
from core.table import display_inventory

from modules.recovery.recycle_bin import RecycleBinRecovery

console = Console()

manager = CaseManager()
analyzer = EvidenceAnalyzer()

current_case = None

logger.info("Sherlocked started")

show_banner()

while True:

    choice = show_menu()

    # -------------------------------
    # CREATE NEW CASE
    # -------------------------------
    if choice == "1":

        current_case = manager.create_case()

        logger.info(f"Case created: {current_case.case_id}")

        console.print(
            f"\n[bold green]✓ Case '{current_case.case_id}' created.[/bold green]"
        )

    # -------------------------------
    # OPEN CASE (Coming Soon)
    # -------------------------------
    elif choice == "2":

        console.print("[yellow]Open Existing Case - Coming Soon[/yellow]")

    # -------------------------------
    # ANALYZE EVIDENCE
    # -------------------------------
    elif choice == "3":

        if current_case is None:

            console.print("[bold red]Create a case first![/bold red]")

        else:

            logger.info(f"Analyzing case {current_case.case_id}")

            current_case = analyzer.analyze(current_case)

            manager.save_case(current_case)

            display_inventory(current_case.metadata)

            console.print(
                "\n[bold green]✓ Evidence analysis completed.[/bold green]"
            )

    # -------------------------------
    # RECOVER DELETED FILES
    # -------------------------------
    elif choice == "4":

        console.print("\n[bold cyan]Searching Recycle Bin...[/bold cyan]")

        deleted_files = RecycleBinRecovery.find_deleted_files()

        if not deleted_files:

            console.print("[yellow]No deleted files found.[/yellow]")

        else:

            console.print(
                f"\n[green]{len(deleted_files)} deleted file(s) found.[/green]\n"
            )

            for index, file in enumerate(deleted_files, start=1):
                console.print(f"{index}. {file.name}")

            recover = input("\nRecover all files? (y/n): ")

            if recover.lower() == "y":

                destination = input(
                    "Destination folder (e.g. recovered_files): "
                )

                for file in deleted_files:

                    RecycleBinRecovery.recover(
                        file,
                        destination
                    )

                console.print(
                    "\n[bold green]✓ Recovery completed.[/bold green]"
                )

    # -------------------------------
    # GENERATE REPORT
    # -------------------------------
    elif choice == "5":

        console.print("[yellow]Generate Report - Coming Soon[/yellow]")

    # -------------------------------
    # EXIT
    # -------------------------------
    elif choice == "6":

        logger.info("Sherlocked closed")

        console.print(
            "\n[bold green]Thank you for using Sherlocked![/bold green]"
        )

        break

    else:

        console.print("[bold red]Invalid choice![/bold red]")