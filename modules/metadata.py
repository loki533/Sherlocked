import mimetypes
import os
from datetime import datetime


class MetadataExtractor:

    @staticmethod
    def extract(file_path):

        stat = os.stat(file_path)

        mime, _ = mimetypes.guess_type(file_path)

        return {

            "name": os.path.basename(file_path),

            "path": file_path,

            "extension": os.path.splitext(file_path)[1],

            "mime_type": mime,

            "size_bytes": stat.st_size,

            "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),

            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),

            "accessed": datetime.fromtimestamp(stat.st_atime).isoformat()

        }