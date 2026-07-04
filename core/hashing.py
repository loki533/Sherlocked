import hashlib


class HashCalculator:

    @staticmethod
    def calculate_hash(file_path, algorithm):

        hasher = hashlib.new(algorithm)

        with open(file_path, "rb") as file:

            while True:

                chunk = file.read(4096)

                if not chunk:
                    break

                hasher.update(chunk)

        return hasher.hexdigest()