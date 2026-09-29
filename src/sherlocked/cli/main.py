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
from sherlocked.filesystem.mft_parser import MFTParser


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
                    "[bold red]Create or open a case first![/bold red]"
                )
                continue

            image_path = Path(current_case.evidence_path)
            if image_path.is_dir():
                image_path = image_path / "windows_disk.dd"

            if not image_path.exists():
                console.print(
                    f"[bold red]Disk image not found: {image_path}[/bold red]"
                )
                continue

            try:
                image_report = RawImageAnalyzer(image_path).analyze()
                ntfs_partitions = [
                    p for p in image_report.get("partitions", [])
                    if "NTFS" in p.get("type", "")
                ]

                if not ntfs_partitions:
                    console.print(
                        "[bold red]No NTFS partition was detected.[/bold red]"
                    )
                    continue

                console.print("\n[bold cyan]NTFS Partitions[/bold cyan]")
                for p in ntfs_partitions:
                    console.print(
                        f"{p['partition']}. LBA={p['start_lba']} | "
                        f"Size={p['size_gb']} GB | {p['type']}"
                    )

                if len(ntfs_partitions) == 1:
                    partition = ntfs_partitions[0]
                else:
                    selected = int(input("Select partition number: "))
                    partition = next(
                        p for p in ntfs_partitions
                        if p["partition"] == selected
                    )

                partition_offset = partition["start_lba"] * 512
                boot_sector = RawImageAnalyzer(
                    image_path
                ).read_ntfs_boot_sector(partition["start_lba"])

                if boot_sector[3:11].decode(
                    errors="ignore"
                ).strip() != "NTFS":
                    console.print(
                        "[bold red]Selected partition does not contain "
                        "an NTFS boot sector.[/bold red]"
                    )
                    continue

                parser = MFTParser.from_ntfs_boot_sector(
                    image_path,
                    partition_offset,
                    boot_sector,
                )

                console.print(
                    f"\n[cyan]MFT offset:[/cyan] {parser.mft_offset:,} bytes"
                )
                console.print(
                    f"[cyan]MFT record size:[/cyan] {parser.record_size} bytes"
                )

                max_records = int(
                    input("Records to scan [default 1000]: ") or "1000"
                )

                records = parser.scan_mft(max_records=max_records)
                current_case.mft_records = records
                manager.save_case(current_case)

                deleted = [
                    r for r in records
                    if not r["flags_decoded"]["in_use"]
                ]

                console.print(
                    f"\n[bold green]✓ Parsed {len(records)} MFT records[/bold green]"
                )
                console.print(
                    f"[yellow]Unused/deleted records: {len(deleted)}[/yellow]"
                )

                for record in records[:25]:
                    names = record.get("file_names", [])
                    name = names[0]["filename"] if names else "<unnamed>"
                    state = (
                        "ALLOC"
                        if record["flags_decoded"]["in_use"]
                        else "DELETED"
                    )
                    console.print(
                        f"#{record['record_number']:>6} | "
                        f"{state:<7} | {name}"
                    )

                if len(records) > 25:
                    console.print(
                        f"... {len(records) - 25} more records saved to the case."
                    )

            except (ValueError, StopIteration) as exc:
                console.print(
                    f"[bold red]Invalid MFT selection/input: {exc}[/bold red]"
                )
            except Exception as exc:
                logger.exception("MFT parsing failed")
                console.print(
                    f"[bold red]MFT parsing failed: {exc}[/bold red]"
                )

        elif choice == "9":

            if current_case is None:
                console.print(
                    "[bold red]Create or open a case first![/bold red]"
                )
            else:
                try:
                    report = ReportGenerator.generate(current_case)

                    console.print(
                        "\n[bold green]"
                        "✓ Report generated successfully:"
                        "[/bold green]"
                    )
                    console.print(str(report))

                    if report.exists():
                        webbrowser.open(report.resolve().as_uri())

                except Exception as exc:
                    logger.exception("Report generation failed")
                    console.print(
                        f"[bold red]Report generation failed: {exc}[/bold red]"
                    )

        # ---------------------------------------------------------
        # 10. EXIT
        # ---------------------------------------------------------

        elif choice == "10":

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