from pathlib import Path
from sherlocked.utils.time_utils import filetime_to_datetime


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


class MFTParser:
    """Decode NTFS MFT records and their attributes.

    The parser decodes filesystem structures. It deliberately does not decide
    whether a file is "recovered"; that is the responsibility of higher-level
    analysis and file-data extraction code.
    """

    def __init__(self, image_path, mft_offset, record_size=1024,
                 volume_offset=0, cluster_size=4096):
        self.image_path = Path(image_path)
        self.mft_offset = mft_offset
        self.record_size = record_size
        self.volume_offset = volume_offset
        self.cluster_size = cluster_size

    @classmethod
    def from_ntfs_boot_sector(cls, image_path, partition_offset, boot_sector):
        if len(boot_sector) < 512 or boot_sector[3:11].decode(errors="ignore").strip() != "NTFS":
            raise ValueError("Invalid NTFS boot sector")

        bytes_per_sector = int.from_bytes(boot_sector[11:13], "little")
        sectors_per_cluster = boot_sector[13]
        cluster_size = bytes_per_sector * sectors_per_cluster
        mft_cluster = int.from_bytes(boot_sector[48:56], "little")

        raw_record_size = int.from_bytes(boot_sector[64:65], "little", signed=True)
        if raw_record_size < 0:
            record_size = 2 ** abs(raw_record_size)
        elif raw_record_size > 0:
            record_size = raw_record_size * cluster_size
        else:
            record_size = 1024

        mft_offset = partition_offset + (mft_cluster * cluster_size)
        return cls(
            image_path,
            mft_offset,
            record_size,
            volume_offset=partition_offset,
            cluster_size=cluster_size,
        )

    def decode_flags(self, flags):
        return {
            "in_use": bool(flags & 0x01),
            "directory": bool(flags & 0x02),
        }

    @staticmethod
    def _apply_fixup(record):
        """Validate and restore NTFS Update Sequence Array sector trailers."""
        if len(record) < 24:
            raise ValueError("MFT record is too small")

        usa_offset = int.from_bytes(record[4:6], "little")
        usa_count = int.from_bytes(record[6:8], "little")
        if usa_offset == 0 or usa_count <= 1:
            return record
        if usa_offset + usa_count * 2 > len(record):
            raise ValueError("Invalid Update Sequence Array bounds")

        sequence = record[usa_offset:usa_offset + 2]
        restored = bytearray(record)
        sector_size = 512

        for i in range(1, usa_count):
            trailer_offset = i * sector_size - 2
            if trailer_offset + 2 > len(restored):
                raise ValueError("Invalid MFT sector boundary")
            if restored[trailer_offset:trailer_offset + 2] != sequence:
                raise ValueError("NTFS Update Sequence Array validation failed")
            replacement = usa_offset + i * 2
            restored[trailer_offset:trailer_offset + 2] = record[replacement:replacement + 2]

        return bytes(restored)

    def read_mft_record(self, record_number, record_size=None):
        record_size = record_size or self.record_size
        record_offset = self.mft_offset + record_number * record_size

        with open(self.image_path, "rb") as image:
            image.seek(record_offset)
            record = image.read(record_size)

        if len(record) != record_size or record[0:4] != b"FILE":
            return None

        try:
            record = self._apply_fixup(record)
        except ValueError:
            return None

        sequence_number = int.from_bytes(record[16:18], "little")
        hard_links = int.from_bytes(record[18:20], "little")
        first_attribute = int.from_bytes(record[20:22], "little")
        flags = int.from_bytes(record[22:24], "little")
        used_size = int.from_bytes(record[24:28], "little")
        allocated_size = int.from_bytes(record[28:32], "little")
        base_record = int.from_bytes(record[32:40], "little")
        next_attribute_id = int.from_bytes(record[40:42], "little")

        return {
            "record_number": record_number,
            "record_offset": record_offset,
            "signature": "FILE",
            "sequence_number": sequence_number,
            "hard_links": hard_links,
            "first_attribute_offset": first_attribute,
            "flags": flags,
            "used_size": used_size,
            "allocated_size": allocated_size,
            "base_record": base_record,
            "next_attribute_id": next_attribute_id,
            "raw_record": record,
        }

    def parse_attributes(self, record):
        attributes = []
        offset = int.from_bytes(record[20:22], "little")

        while offset + 16 <= len(record):
            attr_type = int.from_bytes(record[offset:offset + 4], "little")
            if attr_type == 0xFFFFFFFF:
                break

            attr_length = int.from_bytes(record[offset + 4:offset + 8], "little")
            if attr_length < 16 or offset + attr_length > len(record):
                break

            attribute_name = ATTRIBUTE_TYPES.get(attr_type, hex(attr_type))
            non_resident = record[offset + 8] != 0
            attr_id = int.from_bytes(record[offset + 14:offset + 16], "little")
            name_length = record[offset + 9]
            name_offset = int.from_bytes(record[offset + 10:offset + 12], "little")
            attribute_name_value = None
            if name_length:
                name_start = offset + name_offset
                name_end = name_start + name_length * 2
                if name_end <= offset + attr_length:
                    attribute_name_value = record[name_start:name_end].decode(
                        "utf-16le", errors="replace"
                    )
            parsed = None

            if attr_type == 0x10 and not non_resident:
                parsed = self.parse_standard_information(record, offset)
            elif attr_type == 0x30 and not non_resident:
                parsed = self.parse_file_name(record, offset)
            elif attr_type == 0x80:
                parsed = self.parse_data_attribute(record, offset, non_resident)

            attributes.append({
                "type": attribute_name,
                "type_code": attr_type,
                "length": attr_length,
                "resident": not non_resident,
                "id": attr_id,
                "name": attribute_name_value,
                "offset": offset,
                "data": parsed,
            })
            offset += attr_length

        return attributes

    def parse_standard_information(self, record, attribute_offset):
        content_offset = int.from_bytes(record[attribute_offset + 20:attribute_offset + 22], "little")
        start = attribute_offset + content_offset
        if start + 36 > len(record):
            return None

        values = [int.from_bytes(record[start + i:start + i + 8], "little") for i in (0, 8, 16, 24)]
        return {
            "created": filetime_to_datetime(values[0]),
            "modified": filetime_to_datetime(values[1]),
            "mft_modified": filetime_to_datetime(values[2]),
            "accessed": filetime_to_datetime(values[3]),
            "attributes": int.from_bytes(record[start + 32:start + 36], "little"),
        }

    def parse_file_name(self, record, attribute_offset):
        content_offset = int.from_bytes(record[attribute_offset + 20:attribute_offset + 22], "little")
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
        end = start + 66 + name_length * 2
        if end > len(record):
            return None

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
            "filename": record[start + 66:end].decode("utf-16le", errors="replace"),
        }

    def parse_data_attribute(self, record, attribute_offset, non_resident):
        """Decode an NTFS $DATA attribute without reading file content."""
        if not non_resident:
            content_length = int.from_bytes(record[attribute_offset + 16:attribute_offset + 20], "little")
            content_offset = int.from_bytes(record[attribute_offset + 20:attribute_offset + 22], "little")
            start = attribute_offset + content_offset
            end = min(start + content_length, len(record))
            return {
                "resident": True,
                "content_length": content_length,
                "content_hex": record[start:end].hex(),
            }

        #non-resident


        start_vcn = int.from_bytes(record[attribute_offset + 16:attribute_offset + 24], "little") 
        end_vcn = int.from_bytes(record[attribute_offset + 24:attribute_offset + 32], "little")
        mapping_pairs_offset = int.from_bytes(record[attribute_offset + 32:attribute_offset + 34], "little")
        compression_unit = int.from_bytes(record[attribute_offset + 34:attribute_offset + 36], "little")
        allocated_size = int.from_bytes(record[attribute_offset + 40:attribute_offset + 48], "little") 
        #rounded up size to match disk clusters

        real_size = int.from_bytes(record[attribute_offset + 48:attribute_offset + 56], "little")
        initialized_size = int.from_bytes(record[attribute_offset + 56:attribute_offset + 64], "little")

        run_start = attribute_offset + mapping_pairs_offset
        runs = self.parse_data_runs(record[run_start:])
        return {
            "resident": False,
            "start_vcn": start_vcn,
            "end_vcn": end_vcn,
            "compression_unit": compression_unit,
            "allocated_size": allocated_size,
            "real_size": real_size,
            "initialized_size": initialized_size,
            "data_runs": runs,
        }

    @staticmethod
    def parse_data_runs(data):
        """Decode NTFS mapping pairs into (VCN, LCN, cluster_count) runs."""
        runs = []
        pos = 0
        current_lcn = 0
        current_vcn = 0

        while pos < len(data):
            header = data[pos]
            pos += 1
            if header == 0:
                break

            length_size = header & 0x0F
            #bytes representing the run length

            offset_size = (header >> 4) & 0x0F
            #how many bytes represent the starting cluster 
            
            if length_size == 0 or pos + length_size + offset_size > len(data):
                raise ValueError("Invalid NTFS data-run encoding")

            run_length = int.from_bytes(data[pos:pos + length_size], "little", signed=False)
            pos += length_size

            if offset_size == 0:
                lcn = None  # sparse run
            else:
                raw_offset = int.from_bytes(data[pos:pos + offset_size], "little", signed=False)
                sign_bit = 1 << (offset_size * 8 - 1)
                if raw_offset & sign_bit:
                    raw_offset -= 1 << (offset_size * 8)
                current_lcn += raw_offset
                lcn = current_lcn
            pos += offset_size

            runs.append({
                "vcn": current_vcn,
                "lcn": lcn,
                "length": run_length,
                "sparse": lcn is None,
            })
            current_vcn += run_length

        return runs

    def scan_mft(self, max_records=1000):
        records = []
        for record_number in range(max_records):
            record = self.read_mft_record(record_number)
            if record is None:
                continue
            attributes = self.parse_attributes(record["raw_record"])
            record["attributes"] = attributes
            record["flags_decoded"] = self.decode_flags(record["flags"])
            record.pop("raw_record")
            records.append(record)
        return records
