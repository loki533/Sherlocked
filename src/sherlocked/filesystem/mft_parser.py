from pathlib import Path

from sherlocked.utils.time_utils import filetime_to_datetime


class MFTParser:
    """Read and decode NTFS Master File Table records from a raw image."""

    ATTRIBUTE_TYPES = {
        0x10: "$STANDARD_INFORMATION",
        0x20: "$ATTRIBUTE_LIST",
        0x30: "$FILE_NAME",
        0x40: "$OBJECT_ID",
        0x50: "$SECURITY_DESCRIPTOR",
        0x60: "$VOLUME_NAME",
        0x70: "$VOLUME_INFORMATION",
        0x80: "$DATA",
        0x90: "$INDEX_ROOT",
        0xA0: "$INDEX_ALLOCATION",
    }

    def __init__(self, image_path, mft_offset, record_size=1024):
        self.image_path = Path(image_path)
        self.mft_offset = mft_offset
        self.record_size = record_size

    @classmethod
    def from_ntfs_boot_sector(cls, image_path, partition_offset, boot_sector):
        """Build a parser from an NTFS volume boot sector."""
        bytes_per_sector = int.from_bytes(boot_sector[11:13], "little")
        sectors_per_cluster = boot_sector[13]
        cluster_size = bytes_per_sector * sectors_per_cluster
        mft_cluster = int.from_bytes(boot_sector[48:56], "little")

        raw_record_size = int.from_bytes(
            boot_sector[64:65], "little", signed=True           
        )
        if raw_record_size > 0:
            record_size = raw_record_size * cluster_size
        else:
            record_size = 1 << abs(raw_record_size)

        mft_offset = (
            partition_offset + mft_cluster * cluster_size
        )

        return cls(image_path, mft_offset, record_size)

    def decode_flags(self, flags):
        return {
            "in_use": bool(flags & 0x01),
            "directory": bool(flags & 0x02),
        }

    def _apply_fixup(self, record):
        """Apply the NTFS Update Sequence Array to a FILE record."""
        if len(record) < 48 or record[:4] != b"FILE":
            return record

        usa_offset = int.from_bytes(record[4:6], "little")
        usa_count = int.from_bytes(record[6:8], "little")

        if usa_offset + usa_count * 2 > len(record) or usa_count < 2:
            return record

        sequence = record[usa_offset:usa_offset + 2]
        fixed = bytearray(record)

        for i in range(1, usa_count):
            sector_end = i * 512 - 2
            if sector_end + 2 > len(fixed):
                break

            if fixed[sector_end:sector_end + 2] != sequence:
                # Do not silently repair a record whose sector trailer
                # does not contain the expected update sequence number.
                
                #USA -> Update Sequence array , used to check for torn disks such as in the case of power failure
                #easy check is that , the last 2 bytes of the sectors are moved onto usa , therefore incase of a power failure ... they wont match
                return record

            replacement_start = usa_offset + i * 2
            fixed[sector_end:sector_end + 2] = record[
                replacement_start:replacement_start + 2
            ]

        return bytes(fixed)

    def read_mft_record(self, record_number):
        record_offset = self.mft_offset + record_number * self.record_size

        with self.image_path.open("rb") as image:
            image.seek(record_offset)
            record = image.read(self.record_size)

        if len(record) != self.record_size or record[:4] != b"FILE":
            return None

        record = self._apply_fixup(record)

        return {
            "record_number": record_number,
            "record_offset": record_offset,
            "signature": "FILE",
            "sequence_number": int.from_bytes(record[16:18], "little"),
            "hard_links": int.from_bytes(record[18:20], "little"),
            "first_attribute_offset": int.from_bytes(record[20:22], "little"),
            "flags": int.from_bytes(record[22:24], "little"),
            "used_size": int.from_bytes(record[24:28], "little"),
            "allocated_size": int.from_bytes(record[28:32], "little"),
            "base_record": int.from_bytes(record[32:40], "little"),
            "next_attribute_id": int.from_bytes(record[40:42], "little"),
            "raw_record": record,
        }

    def parse_attributes(self, record):
        attributes = []
        offset = int.from_bytes(record[20:22], "little")

        while offset + 8 <= len(record):
            attr_type = int.from_bytes(record[offset:offset + 4], "little")

            if attr_type == 0xFFFFFFFF:
                break

            attr_length = int.from_bytes(
                record[offset + 4:offset + 8], "little"
            )
            if attr_length < 24 or offset + attr_length > len(record):
                break

            resident = record[offset + 8] == 0 

            #NTFS allows 1kb of data to be stored directly 
            #if larger than 1kb , the clusters pointing to the actual data is stored i.e non resident data

            attr_id = int.from_bytes(record[offset + 14:offset + 16], "little")

            parsed = None
            if attr_type == 0x10 and resident:
                parsed = self.parse_standard_information(record, offset)
            elif attr_type == 0x30 and resident:
                parsed = self.parse_file_name(record, offset)

            attributes.append({
                "type": self.ATTRIBUTE_TYPES.get(attr_type, hex(attr_type)),
                "length": attr_length,
                "resident": resident,
                "id": attr_id,
                "offset": offset,
                "data": parsed,
            })

            offset += attr_length

        return attributes

    def parse_standard_information(self, record, attribute_offset):
        content_offset = int.from_bytes(
            record[attribute_offset + 20:attribute_offset + 22], "little"
        )
        start = attribute_offset + content_offset

        if start + 36 > len(record):
            return None

        created = int.from_bytes(record[start:start + 8], "little")
        modified = int.from_bytes(record[start + 8:start + 16], "little")
        mft_modified = int.from_bytes(record[start + 16:start + 24], "little")
        accessed = int.from_bytes(record[start + 24:start + 32], "little")
        attributes = int.from_bytes(record[start + 32:start + 36], "little")

        return {
            "created": filetime_to_datetime(created),
            "modified": filetime_to_datetime(modified),
            "mft_modified": filetime_to_datetime(mft_modified),
            "accessed": filetime_to_datetime(accessed),
            "attributes": attributes,
        }

    def parse_file_name(self, record, attribute_offset):
        content_offset = int.from_bytes(
            record[attribute_offset + 20:attribute_offset + 22], "little"
        )
        start = attribute_offset + content_offset

        if start + 66 > len(record):
            return None

        parent_reference = int.from_bytes(record[start:start + 8], "little")
        created = int.from_bytes(record[start + 8:start + 16], "little")
        modified = int.from_bytes(record[start + 16:start + 24], "little")
        mft_modified = int.from_bytes(record[start + 24:start + 32], "little")
        accessed = int.from_bytes(record[start + 32:start + 40], "little")
        allocated_size = int.from_bytes(record[start + 40:start + 48], "little")
        real_size = int.from_bytes(record[start + 48:start + 56], "little")
        flags = int.from_bytes(record[start + 56:start + 60], "little")
        name_length = record[start + 64]
        namespace = record[start + 65]

        name_end = start + 66 + name_length * 2
        if name_end > len(record):
            return None

        file_name = record[start + 66:name_end].decode(
            "utf-16le", errors="replace"
        )

        return {
            "parent_record": parent_reference & 0x0000FFFFFFFFFFFF,
            "created": filetime_to_datetime(created),
            "modified": filetime_to_datetime(modified),
            "mft_modified": filetime_to_datetime(mft_modified),
            "accessed": filetime_to_datetime(accessed),
            "allocated_size": allocated_size,
            "real_size": real_size,
            "flags": flags,
            "namespace": namespace,
            "filename": file_name,
        }

    def scan_mft(self, max_records=1000):
        records = []

        for record_number in range(max_records):
            record = self.read_mft_record(record_number)
            if record is None:
                continue

            record["attributes"] = self.parse_attributes(record["raw_record"])
            record["flags_decoded"] = self.decode_flags(record["flags"])
            record.pop("raw_record")

            #can have multiple file names , windows keeps a POSIX case-name ,win32 name and sometimes a DOS8.3 name
            file_names = [
                attr["data"]
                for attr in record["attributes"]
                if attr["type"] == "$FILE_NAME" and attr["data"]
            ]
            record["file_names"] = file_names
            records.append(record)

        return records
