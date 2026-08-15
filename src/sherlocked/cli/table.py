from rich.console import Console
from rich.table import Table

console = Console()


def display_inventory(files):

    table = Table(title="Evidence Inventory")

    table.add_column("File", style="cyan")
    table.add_column("Category")
    table.add_column("Size (Bytes)")
    table.add_column("Signature")
    table.add_column("Suspicious")

    for item in files:

        suspicious = "⚠ YES" if item.get("suspicious", False) else "No"

        table.add_row(
            item.get("name", "Unknown"),
            item.get("category", "Unknown"),
            str(item.get("size_bytes", 0)),
            item.get("signature", "Unknown"),
            suspicious
        )

    console.print(table)