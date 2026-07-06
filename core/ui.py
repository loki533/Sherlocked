from rich.console import Console
from rich.panel import Panel

console = Console()


def show_banner():

    console.print(
        Panel.fit(
            "[bold cyan]SHERLOCKED[/bold cyan]\n"
            "[white]Digital Forensics Investigation Toolkit[/white]",
            border_style="cyan",
            padding=(1, 8)
        )
    )


def show_menu():

    console.print("\n[bold yellow]Main Menu[/bold yellow]\n")

    console.print("[green]1.[/green] 📁 Create New Case")
    console.print("[green]2.[/green] 📂 Open Existing Case")
    console.print("[green]3.[/green] 🔍 Analyze Evidence")
    console.print("[green]4.[/green] ♻ Recover Deleted Files")
    console.print("[green]5.[/green] 📑 Generate Report")
    console.print("[green]6.[/green] 🚪 Exit")

    return input("\nChoice: ")