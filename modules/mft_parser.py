import hashlib
from io import BytesIO
from pathlib import Path
import struct
import pycdlib
from datetime import datetime, timedelta

def filetime_to_datetime(filetime):

    if filetime == 0:
        return None

    return datetime(1601, 1, 1) + timedelta(
        microseconds=filetime / 10
    )

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

        attributes = []

        offset = int.from_bytes(record[20:22],"little")

        while offset< len(record):
            attr_type = int.from_bytes(record[offset:offset+4] , "little")
            attribute_name = ATTRIBUTE_TYPES.get(attr_type,hex(attr_type))

            if attr_type == 0xFFFFFFFF:
                break

            attr_length = int.from_bytes(record[offset + 4 : offset + 8], "little")
            resident = record[offset + 8] #0 if resident , 1 if non-resident
            attr_id = int.from_bytes(record[offset + 14 : offset + 16], "little")

           

            if (attr_length == 0):
                break

            if (attr_type == 0x10):
                parsed = self.parse_standard_information(record,offset)

            elif(attr_type == 0x30):
                parsed = self.parse_file_name(record,offset)

            else:
                parsed = None

            attributes.append(
                    {
                        "type":attribute_name,
                        "length":attr_length,
                        "resident":resident==0,
                        "id":attr_id,
                        "offset" : offset

                    }
                )

            offset+=attr_length #to get the next record

        return attributes

    def parse_standard_information(self,record,attribute_offset):
        content_offset = int.from_bytes(record[attribute_offset+20:attribute_offset+22],"little")
        start = attribute_offset + content_offset

        if start + 36 > len(record):
            return None
        
        #0x00 -> creation
        #0x08 -> modified
        #0x10 -> MFT modified
        #0x18 -> accessed
        created = int.from_bytes(record[start:start+8],"little")
        modified = int.from_bytes(record[start+8 : start+16],"little")
        mft_modified = int.from_bytes(record[start+16 : start+24],"little")
        accessed = int.from_bytes(record[start+24 : start+32],"little")

        #0x20 -> File attributes start
        attributes = int.from_bytes(record[start+32 : start+36],"little")

        return{
            "created" : filetime_to_datetime(created),
            "modified" : filetime_to_datetime(modified),
            "mft_modified" : filetime_to_datetime(mft_modified),
            "accessed" : filetime_to_datetime(accessed),
            "attributes" : attributes
        }

    def parse_file_name(self,record,attribute_offset):

        content_offset = int.from_bytes(record[attribute_offset+20 : attribute_offset+22],"little")
        start = attribute_offset + content_offset

        parent_reference = int.from_bytes(record[start:start+8],"little")

        created = filetime_to_datetime(int.from_bytes(record[start+8:start+16],"little"))
        modified = filetime_to_datetime(int.from_bytes(record[start+16 : start+24],"little"))
        mft_modified = filetime_to_datetime(int.from_bytes(record[start+24 : start+32],"little"))
        accessed = filetime_to_datetime(int.from_bytes(record[start+32 : start+40],"little"))

        allocated_size = int.from_bytes(record[start+40 : start+48],"little")
        real_size = int.from_bytes(record[start+48 : start+56],"little")
        flags = int.from_bytes(record[start+56 : start+60] ,"little")
        name_length = record[start+64]

        namespace = record[start+65]
        #0 -> POSIX , 1 -> Win32 , 2 -> DOS ,3 -> Win32 + DOS

        name_bytes = record[start+66:start+66+(name_length*2)]
        file_name = name_bytes.decode("utf-16le",errors = "ignore")

        return {

            "parent_record": parent_reference,
            "created": filetime_to_datetime(created),
            "modified": filetime_to_datetime(modified),
            "mft_modified": filetime_to_datetime(mft_modified),
            "accessed": filetime_to_datetime(accessed),
            "allocated_size": allocated_size,
            "real_size": real_size,
            "flags": flags,
            "namespace": namespace,
            "filename": file_name
        }

    def scan_mft(self,max_records=1000):

        records=[]

        for record_number in range(max_records):

            record = self.read_mft_record(record_number)

            if record is None:
                continue

            attributes = self.parse_attributes(record["raw_record"])
            record["attributes"] = attributes
            record.pop("raw_record")

            records.append(record)

        return records








