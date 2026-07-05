from rich.console import Console
from rich.panel import Panel

from core.case_manager import CaseManager
from core.evidence_analyzer import EvidenceAnalyzer
from core.logger import logger

console = Console()

manager = CaseManager()
analyzer = EvidenceAnalyzer()

logger.info("Sherlocked started")


console.print(
    Panel.fit(
        "[bold cyan]SHERLOCKED[/bold cyan]\n"
        "[white]Digital Forensics Investigation Toolkit[/white]",
        border_style="cyan"
    )
)

while True:

    console.print("\n[bold]Main Menu[/bold]")
    console.print("1. Create New Case")
    console.print("2. Exit")

    choice = input("\nChoice: ")

    if choice == "1":

        case = manager.create_case()

        logger.info(f"Case created: {case.case_id}")

        analyzer.analyze(case)

        manager.save_case(case)

        logger.info(f"Evidence analysis completed for {case.case_id}")

        console.print(
            f"\n[green]Analysis completed for {case.case_id}[/green]"
        )

    elif choice == "2":

        logger.info("Sherlocked closed")

        console.print("\nGoodbye!")

        break

    else:

        console.print("[red]Invalid option[/red]")