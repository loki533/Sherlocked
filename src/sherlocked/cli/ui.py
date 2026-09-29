from rich.console import Console
from rich.panel import Panel
from rich.align import Align

console = Console()


def show_banner():

    banner = """
███████╗██╗  ██╗███████╗██████╗ ██╗      ██████╗  ██████╗██╗  ██╗███████╗██████╗
██╔════╝██║  ██║██╔════╝██╔══██╗██║     ██╔═══██╗██╔════╝██║ ██╔╝██╔════╝██╔══██╗
███████╗███████║█████╗  ██████╔╝██║     ██║   ██║██║     █████╔╝ █████╗  ██║  ██║
╚════██║██╔══██║██╔══╝  ██╔══██╗██║     ██║   ██║██║     ██╔═██╗ ██╔══╝  ██║  ██║
███████║██║  ██║███████╗██║  ██║███████╗╚██████╔╝╚██████╗██║  ██╗███████╗██████╔╝
╚══════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝ ╚═════╝  ╚═════╝╚═╝  ╚═╝╚══════╝╚═════╝
"""

    console.print(
        Panel(
            Align.center(f"[bold cyan]{banner}[/bold cyan]"),
            title="[green]v1.0[/green]",
            subtitle="[yellow]Digital Forensics Framework[/yellow]",
            border_style="cyan"
        )
    )


def show_menu():

    console.print("\n[bold yellow]Main Menu[/bold yellow]\n")

    console.print("[green]1.[/green] 📁 Create New Case")
    console.print("[green]2.[/green] 📂 Open Existing Case")
    console.print("[green]3.[/green] 📊 View Case Information")
    console.print("[green]4.[/green] 🔍 Analyze Evidence")
    console.print("[green]5.[/green] 📑 Extract Browser history")
    console.print("[green]6.[/green] 📑 Extract Browser Downloads")
    console.print("[green]7.[/green] 🔍 Scan Disk Image")
    console.print("[green]8.[/green] 🧬 Parse Master File Table (MFT)")
    console.print("[green]9.[/green] 📑 Generate Report")
    console.print("[green]10.[/green] 🚪 Exit")

    return input("\nChoice: ")
