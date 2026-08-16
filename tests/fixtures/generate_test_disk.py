from pathlib import Path
import struct


OUTPUT = Path("evidence/windows_disk.dd")

SECTOR_SIZE = 512
TOTAL_SECTORS = 10000


def create_partition_entry(
    bootable,
    partition_type,
    start_lba,
    total_sectors
):
    """
    Create one 16-byte MBR partition table entry.
    """

    entry = bytearray(16)

    # Boot flag
    entry[0] = 0x80 if bootable else 0x00

    # CHS fields.
    # For our controlled test image these are not important.
    entry[1:4] = b"\x00\x02\x00"

    # Partition type
    entry[4] = partition_type

    # Ending CHS fields
    entry[5:8] = b"\x00\x00\x00"

    # Starting LBA
    struct.pack_into(
        "<I",
        entry,
        8,
        start_lba
    )

    # Number of sectors
    struct.pack_into(
        "<I",
        entry,
        12,
        total_sectors
    )

    return entry


def create_test_disk():

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    # ---------------------------------------------------------
    # Create empty disk image
    # ---------------------------------------------------------

    disk = bytearray(
        TOTAL_SECTORS * SECTOR_SIZE
    )

    # ---------------------------------------------------------
    # MBR
    # ---------------------------------------------------------

    mbr = bytearray(512)

    # ---------------------------------------------------------
    # Partition 1
    #
    # Type 0x07 = NTFS / exFAT
    # Starts at LBA 2048
    # Size = 4000 sectors
    # ---------------------------------------------------------

    partition1 = create_partition_entry(
        bootable=True,
        partition_type=0x07,
        start_lba=2048,
        total_sectors=4000
    )

    mbr[446:462] = partition1

    # ---------------------------------------------------------
    # Partition 2
    #
    # Type 0x83 = Linux
    # Starts at LBA 6048
    # Size = 2000 sectors
    # ---------------------------------------------------------

    partition2 = create_partition_entry(
        bootable=False,
        partition_type=0x83,
        start_lba=6048,
        total_sectors=2000
    )

    mbr[462:478] = partition2

    # ---------------------------------------------------------
    # MBR boot signature
    # ---------------------------------------------------------

    mbr[510:512] = b"\x55\xAA"

    # Put MBR into disk
    disk[0:512] = mbr

    # ---------------------------------------------------------
    # Add a fake NTFS boot sector to partition 1
    # ---------------------------------------------------------

    ntfs_sector = bytearray(512)

    # Jump instruction
    ntfs_sector[0:3] = b"\xEB\x52\x90"

    # NTFS OEM identifier
    ntfs_sector[3:11] = b"NTFS    "

    # Bytes per sector = 512
    struct.pack_into(
        "<H",
        ntfs_sector,
        11,
        512
    )

    # Sectors per cluster = 8
    ntfs_sector[13] = 8

    # Total sectors
    struct.pack_into(
        "<Q",
        ntfs_sector,
        40,
        4000
    )

    # MFT cluster
    struct.pack_into(
        "<Q",
        ntfs_sector,
        48,
        4
    )

    # NTFS boot signature
    ntfs_sector[510:512] = b"\x55\xAA"

    # Put NTFS boot sector at partition start
    partition_start = 2048 * SECTOR_SIZE

    disk[
        partition_start:
        partition_start + SECTOR_SIZE
    ] = ntfs_sector

    # ---------------------------------------------------------
    # Write image
    # ---------------------------------------------------------

    OUTPUT.write_bytes(disk)

    print("[+] Test disk image created")
    print(f"[+] Location : {OUTPUT.resolve()}")
    print(f"[+] Size     : {OUTPUT.stat().st_size:,} bytes")
    print()
    print("[+] MBR:")
    print("    Signature       : 55 AA")
    print()
    print("[+] Partition 1:")
    print("    Type            : 0x07 (NTFS / exFAT)")
    print("    Bootable        : Yes")
    print("    Starting LBA    : 2048")
    print("    Total sectors   : 4000")
    print()
    print("[+] Partition 2:")
    print("    Type            : 0x83 (Linux)")
    print("    Bootable        : No")
    print("    Starting LBA    : 6048")
    print("    Total sectors   : 2000")


if __name__ == "__main__":
    create_test_disk()