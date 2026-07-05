import os
from datetime import datetime


class MetadataExtractor:

    @staticmethod
    def extract(file_path):

        stat = os.stat(file_path) #python lib which returns every info of the specific file

        return {
            "name": os.path.basename(file_path),
            "path": file_path,
            "extension": os.path.splitext(file_path)[1],    #return the extension
            "size": stat.st_size,
            "created": datetime.fromtimestamp(stat.st_ctime).strftime("%Y-%m-%d %H:%M:%S"),
            "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
            "accessed": datetime.fromtimestamp(stat.st_atime).strftime("%Y-%m-%d %H:%M:%S")
        }