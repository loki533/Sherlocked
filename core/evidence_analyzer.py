from modules.scanner import EvidenceScanner
from modules.metadata import MetadataExtractor
from modules.hashing import HashCalculator
from modules.signatures import SignatureAnalyzer
from modules.mismatch_detector import MismatchDetector

from core.logger import logger


class EvidenceAnalyzer:

    def analyze(self, case):

        logger.info("Scanning evidence folder")

        files = EvidenceScanner.scan(case.evidence_path)

        metadata = []

        for file in files:

            info = MetadataExtractor.extract(file)

            info["hashes"] = HashCalculator.calculate_all(file)

            signature = SignatureAnalyzer.identify(file)

            info["signature"] = signature["signature"]
            info["category"] = signature["category"]

            info["suspicious"] = MismatchDetector.detect(file,info["signature"])

            metadata.append(info)

        case.metadata = metadata

        logger.info("Evidence analysis finished")

        return case