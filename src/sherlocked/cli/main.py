from rich.console import Console
from pathlib import Path
import webbrowser

from core.case_manager import CaseManager
from core.evidence_analyzer import EvidenceAnalyzer
from core.logger import logger
from core.ui import show_banner, show_menu
from core.table import display_inventory
from core.timeline_table import display_timeline
from core.browser_table import display_history
from core.download_table import display_downloads
from core.report_generator import ReportGenerator

from modules.timeline import TimelineGenerator
from modules.browser.chrome import ChromeArtifacts
from modules.image_analysis import ISOAnalyzer
from modules.image_analysis import RawImageAnalyzer




console = Console()
manager = CaseManager()
analyzer = EvidenceAnalyzer()

current_case = None

logger.info("Sherlocked started")

show_banner()


iso_tester = ISOAnalyzer("evidence/test_evidence.iso")
image_path = Path("evidence/windows_disk.dd")

report = iso_tester.analyze()

print("Image:", report["image_name"])
print("Files:", report["total_files"])
print("Directories:", report["total_directories"])

print("\nExecutables:")

for file in report["executables"]:
    print(file)

print("\nHidden Files:")
for file in report["hidden_files"]:
    print(file)

print("\nSuspicious:")
for file in report["suspicious_files"]:
    print(file)

print("\nLargest Files:")
for file in report["largest_files"]:
    print(file)

while True:

    choice = show_menu()

    if choice == "1":

        current_case = manager.create_case()

    elif choice == "2":

        current_case = manager.open_case()

        if current_case:

            console.print(
                f"[bold green]Opened Case: {current_case.case_id}[/bold green]"
            )

    elif choice == "3":

        if current_case is None:

            console.print("[bold red]Create a case first![/bold red]")

        else:

            logger.info(f"Analyzing case {current_case.case_id}")

            current_case = analyzer.analyze(current_case)

            manager.save_case(current_case)

            # Display inventory
            display_inventory(current_case.metadata)

            # Generate timeline
            timeline = TimelineGenerator.build(current_case.metadata)

            # Display timeline
            display_timeline(timeline)

            console.print(
                "\n[bold green]✓ Evidence analysis completed.[/bold green]"
            )
            
    elif choice == "4":

        if current_case is None:

            print("Create/Open a case first.")

        else:

            analyzer.analyze(current_case)

            manager.save_case(current_case)

    elif choice == "5":

        print("Browser Artifacts")

        logger.info("Extraction of Browser History")

        history = ChromeArtifacts.extract(Path.home() /
        "AppData/Local/Google/Chrome/User Data/Default/History")

        display_history(history)

    elif choice == "6":

        logger.info("Extraced Browser Downloads")
        history_path = Path.home() / "AppData/Local/Google/Chrome/User Data/Default/History"
        
        downloads = ChromeArtifacts.extract_downloads(history_path)
        display_downloads(downloads)

    elif choice == "7":
        if not image_path.exists():
            print(f"[!] Error: Target evidence file not found at: {image_path}")
            print("    Please verify the path and try again.")

            break
        
        try:
            logger.info("Started Disk image analysing")

            # 2. Instantiate y module dispatcher
            print(f"[*] Loading image data from: {image_path.name}")
            analyzer = RawImageAnalyzer(image_path)
            
            # 3. Execute the structural breakdown
            report = analyzer.analyze()
            
            # 4. Display Core Image Metadata
            print("\n[+] Image Information:")
            print(f"    Name:       {report['image_name']}")
            print(f"    File Size:  {report['image_size']:,} bytes")
            print(f"    Signature:  {report['boot_signature']} (Valid MBR Marker)")
            print(f"    Layout:     {report['partition_scheme']}")
            print("-" * 50)
            
            # 5. Display Parsed Partition Map Entries
            print("[+] Parsed MBR Partition Table Map:")
            if not report["partitions"]:
                print("    No active primary partitions found (Empty structural slots).")
            else:
                for part in report["partitions"]:
                    boot_marker = "(*) ACTIVE/BOOTABLE" if part["bootable"] else "INACTIVE"
                    
                    print(f"\n    [Slot #{part['partition']}] Partition Metadata:")
                    print(f"    └── Type:          {part['type']}")
                    print(f"    └── Status:        {boot_marker}")
                    print(f"    └── Starting LBA:  {part['start_lba']}")
                    print(f"    └── Total Sectors: {part['total_sectors']}")
                    print(f"    └── Computed Size: {part['size_gb']} GB")
                    
        except Exception as e:
            print(f"\n[!] Critical processing failure: {e}")
            
        print("\n" + "=" * 50)
                
    elif choice == "8":

        if current_case is None:

            print("Create/Open a case first.")

        else:

            report = ReportGenerator.generate(current_case)

            print(f"\nReport generated at {report}")

            webbrowser.open(report.resolve().as_uri())


        

    elif choice == "9":
        logger.info("Application Closed")
        break

    else:

        print("Invalid option.")