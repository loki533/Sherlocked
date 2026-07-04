from rich.console import Console
from core.case_manager import CaseManager
from core.hashing import HashCalculator

console = Console()

console.print("[bold green]Welcome to Sherlocked[/bold green]")
console.print("[cyan]Digital Forensics Investigation Toolkit[/cyan]")


print(HashCalculator.calculate_hash(
    "evidence/hello.txt",
    "md5"
))

print(HashCalculator.calculate_hash(
    "evidence/hello.txt",
    "sha1"
))

print(HashCalculator.calculate_hash(
    "evidence/hello.txt",
    "sha256"
))

manager = CaseManager()      # Create ONE object

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
    

