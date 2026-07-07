from pathlib import Path

from modules.recovery.signatures import FILE_SIGNATURES
from core.logger import logger


class FileCarver:

    @staticmethod
    def carve(source_file, output_folder):

        source_file = Path(source_file)
        output_folder = Path(output_folder)

        output_folder.mkdir(parents=True, exist_ok=True)

        with open(source_file, "rb") as f:
            data = f.read()

        recovered = []
        logger.info(f"Searching for {extension.upper()} files...")

        for extension, signature in FILE_SIGNATURES.items():

            header = signature["header"]
            footer = signature["footer"]

            position = 0
            count = 0

            while True:

                start = data.find(header, position)

                if start == -1:
                    break

                # Footer-based formats
                if footer is not None:

                    end = data.find(footer, start)

                    if end == -1:
                        break

                    end += len(footer)

                else:
                    # Temporary limit for formats without footer
                    end = min(start + 5_000_000, len(data))

                recovered_data = data[start:end]

                filename = output_folder / f"{extension}_{count}.{extension}"

                with open(filename, "wb") as out:
                    out.write(recovered_data)

                recovered.append(filename)

                count += 1
                position = end

        logger.info(f"Recovered {filename}")

        return recovered