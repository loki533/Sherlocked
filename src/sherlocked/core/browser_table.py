from rich.console import Console
from rich.table import Table

console = Console()


def display_history(history):

    table = Table(title="Chrome History")

    table.add_column("Visited")
    table.add_column("Title")
    table.add_column("URL")

    for item in history:

        table.add_row(
            str(item["timestamp"]),
            item["title"][:40],
            item["url"][:70]
        )

    console.print(table)