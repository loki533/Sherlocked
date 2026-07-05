import os


class EvidenceScanner:

    @staticmethod
    def scan(folder):

        files = []

        #scans the entire folder
        #scans each directory recursivley

        for root, dirs, filenames in os.walk(folder):               
            for filename in filenames:

                files.append(
                    os.path.join(root, filename)
                )

        return files