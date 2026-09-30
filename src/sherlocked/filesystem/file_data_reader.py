from pathlib import Path


class FileDataReader:
    """Read file content described by an NTFS MFT record.

    This class consumes decoded $DATA attributes. It does not infer whether
    a file is deleted; it simply reconstructs bytes from the supplied runs.
    """

    def __init__(self, image_path, volume_offset, cluster_size):
        self.image_path = Path(image_path)
        self.volume_offset = volume_offset
        self.cluster_size = cluster_size

    def read_attribute(self, data_attribute):
        if not data_attribute:
            return b""
        if data_attribute.get("resident"):
            if "content_hex" in data_attribute:
                content = bytes.fromhex(data_attribute["content_hex"])
            else:
                content = data_attribute.get("content", b"") #if in bytes
            return content[:data_attribute.get("content_length", len(content))]

        target_size = data_attribute.get("real_size")
        output = bytearray()
        with self.image_path.open("rb") as image:
            for run in data_attribute.get("data_runs", []):
                run_bytes = run["length"] * self.cluster_size
                if run.get("sparse"):
                    output.extend(b"\x00" * run_bytes)
                else:
                    offset = self.volume_offset + run["lcn"] * self.cluster_size  
                    #lcn * clustersize gives distance from start of partition
                    #adding volume offset gives exct distnce from start of disk
                    image.seek(offset)
                    chunk = image.read(run_bytes)
                    if len(chunk) != run_bytes:
                        raise IOError("NTFS data run extends beyond the image")
                    output.extend(chunk)

                if target_size is not None and len(output) >= target_size:
                    break

        if target_size is not None:
            return bytes(output[:target_size])
        return bytes(output)

    @staticmethod
    def data_attributes(record):
        return [
            attribute for attribute in record.get("attributes", [])
            if attribute.get("type") == "$DATA"
            and attribute.get("data") is not None
        ]

    def read_record(self, record):
        """Read the unnamed/default $DATA stream from an MFT record."""
        data_attrs = self.data_attributes(record)
        if not data_attrs:
            return None

        # Named streams are not the primary file content stream. The current
        # milestone intentionally selects the unnamed/default $DATA attribute.
        for attribute in data_attrs:
            name = attribute.get("name")
            if not name:
                return self.read_attribute(attribute["data"])

        return self.read_attribute(data_attrs[0]["data"])
