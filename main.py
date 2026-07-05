from rich.console import Console
from core.case_manager import CaseManager
from modules.hashing import HashCalculator
from core.evidence_scanner import EvidenceScanner
from modules.metadata import MetadataExtractor

console = Console()

console.print("[bold green]Welcome to Sherlocked[/bold green]")
console.print("[cyan]Digital Forensics Investigation Toolkit[/cyan]")



manager = CaseManager()      # Create ONE object
case = manager.create_case()
files = EvidenceScanner.scan(case.evidence_path)
metadata = []

for file in files:
    metadata.append(MetadataExtractor.extract(file))


case.metadata = metadata
print(case.metadata)



while True:

    print("\n========================")
    print("      SHERLOCKED")
    print("========================")
    print("1. Create New Case")
    print("2. Exit")

    choice = input("\nChoice: ")

    if choice == "1":
        manager.create_case()

    elif choice == "2":
        break

    else:
        print("Invalid option.")
    

