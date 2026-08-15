from rich.console import Console
from rich.table import Table

console = Console()


def display_downloads(downloads):

    table = Table(title="Chrome Downloads")

    table.add_column("Time")
    table.add_column("Filename")
    table.add_column("Size")
    table.add_column("Source")

    for item in downloads:

        filename = item["path"].split("\\")[-1]

        table.add_row(
            str(item["time"]),
            filename,
            str(item["size"]),
            item["url"][:60]
        )

    console.print(table)