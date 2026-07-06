from rich.console import Console

from core.case_manager import CaseManager
from core.evidence_analyzer import EvidenceAnalyzer
from core.logger import logger
from core.ui import show_banner, show_menu
from core.table import display_inventory

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

        logger.info(f"Case created: {current_case.case_id}")

        console.print(
            f"\n[green]✓ Case '{current_case.case_id}' created successfully.[/green]"
        )

    elif choice == "2":

        console.print("[yellow]Open Existing Case - Coming Soon[/yellow]")

    elif choice == "3":

        if current_case is None:
            console.print("[red]No active case.[/red]")

        else:
            console.print(f"\n[bold cyan]Case ID:[/bold cyan] {current_case.case_id}")
            console.print(f"[bold cyan]Investigator:[/bold cyan] {current_case.investigator}")
            console.print(f"[bold cyan]Description:[/bold cyan] {current_case.description}")
            console.print(f"[bold cyan]Evidence:[/bold cyan] {current_case.evidence_path}")
            console.print(f"[bold cyan]Created:[/bold cyan] {current_case.created_at}")

    elif choice == "4":

        if current_case is None:

            console.print("[red]Create a case first![/red]")

        else:

            logger.info(f"Analyzing case {current_case.case_id}")

            current_case = analyzer.analyze(current_case)

            manager.save_case(current_case)

            display_inventory(current_case.metadata)

            console.print(
                "\n[bold green]✓ Evidence analysis completed.[/bold green]"
            )

    elif choice == "5":

        console.print("[yellow]Generate Report - Coming Soon[/yellow]")

    elif choice == "6":

        logger.info("Sherlocked closed")

        console.print("\n[bold green]Thank you for using Sherlocked![/bold green]")

        break

    else:

        console.print("[red]Invalid choice![/red]")