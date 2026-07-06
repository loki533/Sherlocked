from rich.console import Console
from rich.table import Table

console = Console()


def display_inventory(files):

    table = Table(title="Evidence Inventory")

    table.add_column("File", style="cyan")
    table.add_column("Category")
    table.add_column("Size")
    table.add_column("Signature")
    table.add_column("Suspicious")

    for item in files:

        suspicious = "⚠ YES" if item["suspicious"] else "No"

        table.add_row(
            item["name"],
            item["category"],
            str(item["size_bytes"]),
            item["signature"],
            suspicious
        )

    console.print(table)