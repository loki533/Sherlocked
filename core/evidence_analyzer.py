from modules.scanner import EvidenceScanner
from modules.metadata import MetadataExtractor
from modules.hashing import HashCalculator
from modules.signature import SignatureAnalyzer

from core.logger import logger


class EvidenceAnalyzer:

    def analyze(self, case):

        logger.info("Scanning evidence folder")

        files = EvidenceScanner.scan(case.evidence_path)
        info = MetadataExtractor.extract(file)

        info["hashes"] = HashCalculator.calculate_all(file)
        info["signature"] = SignatureAnalyzer.identify(file)


        metadata = []

        for file in files:

            logger.info(f"Analyzing {file}")

            info = MetadataExtractor.extract(file)

            info["hashes"] = HashCalculator.calculate_all(file)

            metadata.append(info)

        case.metadata = metadata

        logger.info("Evidence analysis finished")

        return case