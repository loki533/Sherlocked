import hashlib
from io import BytesIO
from pathlib import Path
import struct
import pycdlib

class MFTParser:

    def __init__(self,image_path,mft_offset,record_size=1024):


        self.image_path = Path(image_path)

        self.mft_offset = mft_offset

        self.record_size = record_size

    def decode_flags(self,flags):
        return{
            "in_use" : bool(flags & 0x01), #performing bitwise marking , if 0 it has been deleted , 1 means allocated
            "directory" : bool(flags & 0x02) #indication of whether a directory or file , 1 - directory / 0 - standard file
        }

    def read_mft_record(self,record_number,mft_offset,record_size=1024):#mft_offset is calculated from NTFS boot sector

        record_offset = (mft_offset)+(record_number*record_size)

        try:
            with open(self.image_path,"rb") as image:
                image.seek(record_offset)
                record = image.read(record_size)

            if len(record)!= record_size:
                return None

            signature = record[0:4]

            if signature!=b"FILE":
                return None

            sequence_number = int.from_bytes(record[16:18],"little")
            hard_links =int.from_bytes(record[18:20],"little")
            first_attribute = int.from_bytes(record[20:22],"little")
            flags =int.from_bytes(record[22:24],"little")
            used_size=int.from_bytes(record[24:28],"little")
            allocated_size =int.from_bytes(record[28:32],"little")
            base_record=int.from_bytes(record[32:40],"little")
            next_attribute_id =int.from_bytes(record[40:42],"little")

            return{
                "record_number " : record_number,
                "record_offset " : record_offset,
                "signature " : "FILE",
                "sequence_number" : sequence_number,
                "hard_links" : hard_links,
                "first_attribute_offset" : first_attribute,
                "flags" : self.decode_flags(flags),
                "used_size" : used_size,
                "allocatted size " : allocated_size,
                "base_record " : base_record,
                "next_attribute id " : next_attribute_id,
                "raw_record " : record
            }

        except OSError:
            return None

    def parse_attributes(self,record):

        attributes = []

        offset = int.from_bytes(record[20:22],"little")

        while offset< len(record):
            attr_type = int.from_bytes(record[offset:offset+4],"little")

            if attr_type == "0xFFFFFFFF":
                break

            attr_length = int.from_bytes(record[offset + 4 : offset + 8], "little")
            resident = record[offset + 8] #0 if resident , 1 if non-resident
            attr_id = int.from_bytes(record[offset + 14 : offset + 16], "little")

            attributes.append(
                {
                    "type":attr_type,
                    "length":attr_length,
                    "resident":resident==0,
                    "id":attr_id,
                    "offset" : offset
                }
            )

            if (attr_length == 0):
                break

            offset+=attr_length #to get the next record

            return attributes