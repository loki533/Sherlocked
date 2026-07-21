import hashlib
from io import BytesIO
from pathlib import Path
import struct
import pycdlib

"""
+-----------------------------------------------------------+
| Sector 0                                                   |
| Master Boot Record (MBR)                                  |
+-----------------------------------------------------------+
| Partition Entry 1                                         |
| Partition Entry 2                                         |
| Partition Entry 3                                         |
| Partition Entry 4                                         |
+-----------------------------------------------------------+
| Sector 1 ...                                               |
| Filesystem starts (NTFS/FAT32/etc.)                       |
+-----------------------------------------------------------+

"""

#inside each MBR

"""
Offset      Size

0x000       446 bytes    Bootloader

0x1BE       16 bytes     Partition Entry 1

0x1CE       16 bytes     Partition Entry 2

0x1DE       16 bytes     Partition Entry 3

0x1EE       16 bytes     Partition Entry 4

0x1FE       2 bytes      Signature (55 AA)

"""

PARTITION_TYPES = {
    0x00: "Unused",
    0x01: "FAT12",
    0x04: "FAT16",
    0x05: "Extended",
    0x06: "FAT16B",
    0x07: "NTFS / exFAT",
    0x0B: "FAT32",
    0x0C: "FAT32 LBA",
    0x0E: "FAT16 LBA",
    0x0F: "Extended LBA",
    0x82: "Linux Swap",
    0x83: "Linux",
    0x8E: "Linux LVM",
    0xAF: "macOS HFS",
    0xEE: "GPT Protective",
}

class ISOAnalyzer:
    """
    Analyze ISO9660 images without mounting them.
    """

    EXECUTABLE_EXTENSIONS = (
        ".exe",
        ".dll",
        ".bat",
        ".cmd",
        ".ps1",
        ".msi",
        ".com",
        ".scr",
    )

    SUSPICIOUS_KEYWORDS = (
        "hack",
        "crack",
        "keygen",
        "loader",
        "patch",
        "payload",
        "inject",
        "trojan",
        "virus",
        "malware",
        "backdoor",
        "exploit",
        "miner",
        "ransom",
    )

    def __init__(self, iso_path):

        self.iso_path = Path(iso_path)

        self.files = []
        self.directories = []

        self.executables = []
        self.hidden = []
        self.suspicious = []

        self.hashes = []


    def analyze(self):

        iso = pycdlib.PyCdlib()
        iso.open(str(self.iso_path))

        try:
            self.walk_directory(iso, "/")

        finally:
            iso.close()

        #sorts the first 10 files based on their size
        largest = sorted(
            self.hashes,
            key=lambda x: x["size"],
            reverse=True,
        )[:10]

        return {
            "image_name": self.iso_path.name,
            "image_size": self.iso_path.stat().st_size,
            "total_files": len(self.files),
            "total_directories": len(self.directories),
            "executables": self.executables,
            "hidden_files": self.hidden,
            "suspicious_files": self.suspicious,
            "largest_files": largest,
            "hashes": self.hashes,
        }

    #recursive function call , to traverse through the entire directory

    def walk_directory(self, iso, path):

        try:
            children = list(iso.list_children(iso_path=path))#lists the children of the CD

        except Exception:
            return

        for child in children:
            try:
                name = child.file_identifier().decode(
                    errors="ignore"
                ).rstrip(";1")

            except Exception:
                continue

            if name in (".", "..", ""):#to prevent the CD, and the parent -> to avoid loops
                continue

            full_path = path + name

            if child.is_dir():

                self.directories.append(full_path)
                self.walk_directory(
                    iso,
                    full_path + "/",
                )

            else:     #if the child is a file , check for the extensions.

                self.files.append(full_path)
                lower = name.lower()

                if lower.startswith("."):
                    self.hidden.append(full_path)

                if lower.endswith(self.EXECUTABLE_EXTENSIONS):
                    self.executables.append(full_path)

                if any(
                    keyword in lower
                    for keyword in self.SUSPICIOUS_KEYWORDS
                ):
                    self.suspicious.append(full_path)

                info = self.hash_file(
                    iso,
                    full_path,
                )

                if info:
                    self.hashes.append(info)

    def hash_file(self, iso, iso_path):

        try:

            buffer = BytesIO() #creates a virtual file , instead of actually downloadin it.
            iso.get_file_from_iso_fp(
                buffer,
                iso_path=iso_path,
            )

            data = buffer.getvalue()
            sha256 = hashlib.sha256(data).hexdigest()

            return {
                "file": iso_path,
                "size": len(data),
                "sha256": sha256,
            }

        except Exception:

            return None
        
class RawImageAnalyzer:
    
    def __init__(self,image_path):
        self.image_path = Path(image_path)

    def analyze(self):
        with open(self.image_path,"rb") as f:

            #Read the master boot record(first 512 bytes)
            #MBR is responsible for BIOS,Partition table

            boot_sector = f.read(512)
            f.seek(512)
            gpt_header=f.read(8)
            partitions = self.parse_partition_table(boot_sector)


        return{
            "image_name":self.image_path.name,
            "image_size":self.image_path.stat().st_size,
            "boot_signature":self.get_boot_signature(boot_sector),
            "partition_scheme":self.detect_partition_scheme(gpt_header),
            "file_system":self.detect_filesystem(boot_sector),
            "boot_info":self.parse_boot_sector(boot_sector),
            "partitions":partitions,
        }   
    
    def get_boot_signature(self,boot_sector):
        #valid boot sectors must end with 0x55A at offsets 510-512
        sig = boot_sector[510:512]
        return sig.hex().upper()
    

    def detect_partition_scheme(self,gpt_header):
        #GPT disks stores "EFI PART" the header at the begining
        if (gpt_header==b"EFI PART"):
            return "GPT"
        
        return "MBR"

    def detect_file_system(self,boot_sector):
        #File system striing is usually at 3-10th bytes
        fs = boot_sector[3:11].decode(errors="ignore").strip()

        if "NTFS" in fs:
            return "NTFS"
        
        elif "FAT32" in fs:
            return "FAT32"

        elif "EXFAT" in fs.upper():
            return "EXFAT"

        return "Unknown or Raw MBR"
    
    def parse_boot_sector(self,boot_sector):
        
        """
        Parses the BIOS Parameter Block (BPB) for NTFS volumes.
        Uses Little-Endian format (<) to unpack binary data types:
        H = unsigned short (2 bytes), Q = unsigned long long (8 bytes)
        """
        try:
            # Only attempt to parse if it looks like an NTFS filesystem boot sector
            fs = boot_sector[3:11].decode(errors="ignore").strip()
            if "NTFS" not in fs:
                return None
                
            bytes_per_sector = struct.unpack("<H", boot_sector[11:13])[0]
            sectors_per_cluster = boot_sector[13]
            total_sectors = struct.unpack("<Q", boot_sector[40:48])[0]
            mft_cluster = struct.unpack("<Q", boot_sector[48:56])[0]

            return {
                "bytes_per_sector": bytes_per_sector,
                "sectors_per_cluster": sectors_per_cluster,
                "cluster_size": bytes_per_sector * sectors_per_cluster,
                "total_sectors": total_sectors,
                "mft_cluster": mft_cluster,
            }
        except Exception:
            return {"error": "Failed to parse BPB metadata"}
        
    def parse_partition_table(self,boot_sector):

        partitions = []
        partition_offset = 446
            
        for i in range (4): #read the 4 partitions
            entry = boot_sector[
            partition_offset:partition_offset + 16]

            partition_offset += 16
        
            boot_flag = entry[0] #decides if its bootable , if 0x00 -> not bootable
            partition_type = entry[4] #0x83 -> LINUX,0x07 -> NTFS/exFAT 

            start_lba = int.from_bytes(entry[8:12],"little") #tells us the start of the logical byte address
            """important to calculate , so that prog knows how many bytes to skip to reach the start of the filesystem"""

            total_sectors = int.from_bytes(entry[12:16],"little" )

            if partition_type == 0:
                continue

            ptype = PARTITION_TYPES.get(partition_type,f"Unknown (0x{partition_type:02X})")

            # Calculate sizing based on standard 512 bytes per sector
            size_bytes = total_sectors * 512
            size_gb = size_bytes / (1024**3)

            # Append structured metadata to our results list
            partitions.append({
                "partition": i + 1,
                "bootable": boot_flag == 0x80,
                "type": ptype,
                "start_lba": start_lba,
                "total_sectors": total_sectors,
                "size_gb": round(size_gb, 2),
            })
                
        return partitions

    def read_ntfs_boot_sector(self,start_lba):

        with open (self.image_path,"rb") as f:

            f.seek(start_lba*512) #skips the MFT , and jumpts to the NTFS
            return f.read(512)  

    def parse_ntfs_boot_sector(self,boot_sector):

        signature = boot_sector[3:11].decode(errors="ignore").strip()
        





class ImageAnalyzer:

    @staticmethod
    def analyze(path):

        ext = Path(path).suffix.lower()

        if ext == "iso":
            return ISOAnalyzer(path).analyze()

        elif ext in (".img",".dd",".raw"):
            return RawImageAnalyzer(path).analyze()
        
        else:
            raise ValueError(f"Unsupported Format : {ext}")
        
    


