from pathlib import Path
import webbrowser

from rich.console import Console

from sherlocked.core.case_manager import CaseManager
from sherlocked.core.evidence_analyzer import EvidenceAnalyzer
from sherlocked.core.logger import logger

from sherlocked.cli.ui import show_banner, show_menu
from sherlocked.cli.table import display_inventory
from sherlocked.cli.timeline_table import display_timeline
from sherlocked.cli.browser_table import display_history
from sherlocked.cli.download_table import display_downloads

from sherlocked.reporting.report_generator import ReportGenerator
from sherlocked.reporting.timeline_generator import TimelineGenerator

from sherlocked.artifacts.chrome import ChromeArtifacts

from sherlocked.filesystem.image_analysis import RawImageAnalyzer


def main():
    """
    Main entry point for the Sherlocked CLI application.
    """

    console = Console()

    manager = CaseManager()
    evidence_analyzer = EvidenceAnalyzer()

    current_case = None

    logger.info("Sherlocked started")

    show_banner()

    while True:

        choice = show_menu()
        
        if choice == "1":

            current_case = manager.create_case()


        elif choice == "2":

            current_case = manager.open_case()

            if current_case:

                console.print(
                    f"[bold green]"
                    f"Opened Case: {current_case.case_id}"
                    f"[/bold green]"
                )


        elif choice == "3":

            if current_case is None:

                console.print(
                    "[bold red]"
                    "Create or open a case first!"
                    "[/bold red]"
                )

            else:

                logger.info(
                    f"Analyzing case {current_case.case_id}"
                )

                current_case = evidence_analyzer.analyze(
                    current_case
                )

                manager.save_case(current_case)

                # Display evidence inventory
                display_inventory(
                    current_case.metadata
                )

                # Generate timeline
                timeline = TimelineGenerator.build(
                    current_case.metadata
                )

                # Display timeline
                display_timeline(timeline)

                console.print(
                    "\n[bold green]"
                    "✓ Evidence analysis completed."
                    "[/bold green]"
                )

        elif choice == "4":

            if current_case is None:

                console.print(
                    "[bold red]"
                    "Create or open a case first!"
                    "[/bold red]"
                )

            else:

                current_case = evidence_analyzer.analyze(
                    current_case
                )

                manager.save_case(current_case)

                console.print(
                    "[bold green]"
                    "✓ Case analysis saved."
                    "[/bold green]"
                )


        elif choice == "5":

            print("\nBrowser Artifacts")

            logger.info(
                "Extracting Chrome browser history"
            )

            history_path = (
                Path.home()
                / "AppData"
                / "Local"
                / "Google"
                / "Chrome"
                / "User Data"
                / "Default"
                / "History"
            )

            if not history_path.exists():

                console.print(
                    "[bold red]"
                    f"Chrome History database not found: "
                    f"{history_path}"
                    "[/bold red]"
                )

                continue

            try:

                history = ChromeArtifacts.extract(
                    history_path
                )

                display_history(history)

            except Exception as exc:

                logger.exception(
                    "Chrome history extraction failed"
                )

                console.print(
                    f"[bold red]"
                    f"Browser history extraction failed: {exc}"
                    f"[/bold red]"
                )


        elif choice == "6":

            logger.info(
                "Extracting Chrome browser downloads"
            )

            history_path = (
                Path.home()
                / "AppData"
                / "Local"
                / "Google"
                / "Chrome"
                / "User Data"
                / "Default"
                / "History"
            )

            if not history_path.exists():

                console.print(
                    "[bold red]"
                    f"Chrome History database not found: "
                    f"{history_path}"
                    "[/bold red]"
                )

                continue

            try:

                downloads = (
                    ChromeArtifacts.extract_downloads(
                        history_path
                    )
                )

                display_downloads(downloads)

            except Exception as exc:

                logger.exception(
                    "Chrome download extraction failed"
                )

                console.print(
                    f"[bold red]"
                    f"Download extraction failed: {exc}"
                    f"[/bold red]"
                )


        elif choice == "7":

            image_path = Path(
                "evidence/windows_disk.dd"
            )

            if not image_path.exists():

                console.print(
                    "[bold red]"
                    f"[!] Target evidence file not found:\n"
                    f"    {image_path}"
                    "[/bold red]"
                )

                console.print(
                    "Place the disk image inside the "
                    "'evidence' directory and try again."
                )

                continue

            try:

                logger.info(
                    f"Started disk image analysis: "
                    f"{image_path}"
                )

                console.print(
                    f"[*] Loading image data from: "
                    f"{image_path.name}"
                )

                image_analyzer = RawImageAnalyzer(
                    image_path
                )

                report = image_analyzer.analyze()


                console.print(
                    "\n[bold green]"
                    "[+] Image Information:"
                    "[/bold green]"
                )

                print(
                    f"    Name:       "
                    f"{report['image_name']}"
                )

                print(
                    f"    File Size:  "
                    f"{report['image_size']:,} bytes"
                )

                print(
                    f"    Signature:  "
                    f"{report['boot_signature']} "
                    f"(Valid MBR Marker)"
                )

                print(
                    f"    Layout:     "
                    f"{report['partition_scheme']}"
                )

                print("-" * 50)

                console.print(
                    "[bold green]"
                    "[+] Parsed MBR Partition Table Map:"
                    "[/bold green]"
                )

                partitions = report.get(
                    "partitions",
                    []
                )

                if not partitions:

                    print(
                        "    No active primary partitions "
                        "found (Empty structural slots)."
                    )

                else:

                    for part in partitions:

                        boot_marker = (
                            "(*) ACTIVE/BOOTABLE"
                            if part.get("bootable")
                            else "INACTIVE"
                        )

                        print(
                            f"\n    [Slot "
                            f"#{part.get('partition')}] "
                            f"Partition Metadata:"
                        )

                        print(
                            f"    └── Type:          "
                            f"{part.get('type')}"
                        )

                        print(
                            f"    └── Status:        "
                            f"{boot_marker}"
                        )

                        print(
                            f"    └── Starting LBA:  "
                            f"{part.get('start_lba')}"
                        )

                        print(
                            f"    └── Total Sectors: "
                            f"{part.get('total_sectors')}"
                        )

                        print(
                            f"    └── Computed Size: "
                            f"{part.get('size_gb')} GB"
                        )

                print("\n" + "=" * 50)

            except Exception as exc:

                logger.exception(
                    "Disk image analysis failed"
                )

                console.print(
                    f"[bold red]"
                    f"[!] Critical processing failure: {exc}"
                    f"[/bold red]"
                )
        elif choice == "8":

            if current_case is None:

                console.print(
                    "[bold red]"
                    "Create or open a case first!"
                    "[/bold red]"
                )

            else:

                try:

                    logger.info(
                        f"Generating report for case "
                        f"{current_case.case_id}"
                    )

                    report = ReportGenerator.generate(
                        current_case
                    )

                    console.print(
                        "\n[bold green]"
                        f"✓ Report generated successfully:"
                        f"[/bold green]"
                    )

                    console.print(
                        str(report)
                    )

                    # Open generated report
                    if report.exists():

                        webbrowser.open(
                            report.resolve().as_uri()
                        )

                except Exception as exc:

                    logger.exception(
                        "Report generation failed"
                    )

                    console.print(
                        f"[bold red]"
                        f"Report generation failed: {exc}"
                        f"[/bold red]"
                    )

        # ---------------------------------------------------------
        # 9. EXIT
        # ---------------------------------------------------------

        elif choice == "9":

            logger.info(
                "Sherlocked application closed"
            )

            console.print(
                "\n[bold cyan]"
                "Sherlocked closed."
                "[/bold cyan]"
            )

            break

        # ---------------------------------------------------------
        # INVALID OPTION
        # ---------------------------------------------------------

        else:

            console.print(
                "[bold red]"
                "Invalid option."
                "[/bold red]"
            )


if __name__ == "__main__":
    main()