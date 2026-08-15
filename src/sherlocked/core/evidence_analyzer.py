from sherlocked.scanner.evidence_scanner import EvidenceScanner
from sherlocked.metadata.metadata_extractor import MetadataExtractor
from sherlocked.hashing.hash_calculator import HashCalculator
from sherlocked.recovery.signatures import SignatureAnalyzer
from sherlocked.hashing.mismatch_detector import MismatchDetector

from sherlocked.core.logger import logger


class EvidenceAnalyzer:

    def analyze(self, case):

        logger.info("Scanning evidence folder")

        files = EvidenceScanner.scan(case.evidence_path)

        metadata = []

        for file in files:

            info = MetadataExtractor.extract(file)

            info["hashes"] = HashCalculator.calculate_all(file)

            signature = SignatureAnalyzer.analyze(file)

            # Store the raw magic/signature bytes
            info["signature"] = signature["signature"]

            # Store the detected file type
            info["category"] = signature["detected_type"]

            # Compare file extension against detected file type
            info["suspicious"] = MismatchDetector.detect(
                file,
                signature["detected_type"]
            )

            metadata.append(info)

        case.metadata = metadata

        logger.info("Evidence analysis finished")

        return case