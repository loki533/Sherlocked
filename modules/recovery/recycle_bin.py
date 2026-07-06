from pathlib import Path
from core.logger import logger
import shutil  #shell utilites

#when a user deletes a file
#the recycle bin stores it as 2 components
    #with #I index, the metadata index
    #with #R index, the content

class RecycleBinRecovery:

    RECYCLE_BIN = Path("C:/$Recycle.Bin")

    @staticmethod
    def find_deleted_files():

        deleted = []

        if not RecycleBinRecovery.RECYCLE_BIN.exists():
            return deleted

        for sid in RecycleBinRecovery.RECYCLE_BIN.iterdir():

            if not sid.is_dir():
                continue

            try:

                for item in sid.iterdir():

                    if item.name.startswith("$R"):
                        deleted.append(item)

            except PermissionError:
                # Skip system-owned recycle bin folders
                logger.warning(f"Permission denied: {sid}")
                continue


        return deleted

    @staticmethod
    def recover(file_path, destination):

        destination = Path(destination)

        destination.mkdir(parents=True, exist_ok=True)

        shutil.copy2(file_path, destination / file_path.name)
        #.copy2() , attempts to preserve the original metadata, instead of creating a new file