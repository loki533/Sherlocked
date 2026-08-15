from rich.console import Console
from rich.table import Table

console = Console()


def display_timeline(events):

    table = Table(title="Forensic Timeline")

    table.add_column("Timestamp", style="cyan")
    table.add_column("Event")
    table.add_column("File")

    for event in events:

        table.add_row(
            event["time"],
            event["event"],
            event["file"]
        )

    console.print(table)