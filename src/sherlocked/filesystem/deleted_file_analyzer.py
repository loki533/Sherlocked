"""Higher-level analysis of unused NTFS MFT records.

The MFT parser is intentionally responsible for decoding NTFS structures.
This module turns those decoded structures into forensic *candidates*.

Important distinction:
    An unused MFT record is evidence that a record is no longer marked in use.
    It is not proof that the file's contents are recoverable.
"""

from collections import defaultdict


class DeletedFileAnalyzer:
    """Identify potentially deleted files from parsed MFT records."""

    def analyze(self, mft_records):
        """Return normalized deleted-file candidates.

        Only records whose NTFS ``in_use`` flag is false are considered.
        Directory records are retained, but marked as directories so callers
        can decide whether to display or investigate them differently.
        """
        candidates = []

        for record in mft_records:
            flags = record.get("flags_decoded", {})

            if flags.get("in_use", True):
                continue

            names = record.get("file_names", [])
            if not names:
                candidates.append(self._build_candidate(record, None))
                continue

            # A record can contain more than one $FILE_NAME attribute because
            # NTFS supports multiple namespaces / hard-link names. Preserve
            # them rather than silently throwing information away.
            for name in names:
                if name:
                    candidates.append(self._build_candidate(record, name))

        return candidates

    def _build_candidate(self, record, file_name):
        flags = record.get("flags_decoded", {})
        is_directory = bool(flags.get("directory"))

        candidate = {
            "record_number": record.get("record_number"),
            "sequence_number": record.get("sequence_number"),
            "record_offset": record.get("record_offset"),
            "status": "deleted_or_unused",
            "is_directory": is_directory,
            "type": "directory" if is_directory else "file",
            "filename": None,
            "parent_record": None,
            "created": None,
            "modified": None,
            "mft_modified": None,
            "accessed": None,
            "allocated_size": None,
            "real_size": None,
            "namespace": None,
            "evidence": ["MFT record is not marked in use"],
        }

        if file_name:
            candidate.update({
                "filename": file_name.get("filename"),
                "parent_record": file_name.get("parent_record"),
                "created": file_name.get("created"),
                "modified": file_name.get("modified"),
                "mft_modified": file_name.get("mft_modified"),
                "accessed": file_name.get("accessed"),
                "allocated_size": file_name.get("allocated_size"),
                "real_size": file_name.get("real_size"),
                "namespace": file_name.get("namespace"),
            })

            if file_name.get("filename"):
                candidate["evidence"].append(
                    "$FILE_NAME attribute contains a filename"
                )

            if file_name.get("parent_record") is not None:
                candidate["evidence"].append(
                    "$FILE_NAME attribute contains a parent record reference"
                )

            if file_name.get("real_size") is not None:
                candidate["evidence"].append(
                    "$FILE_NAME attribute contains a file size"
                )

        return candidate

    @staticmethod
    def summary(candidates):
        """Return useful counts for CLI/report presentation."""
        files = [c for c in candidates if not c.get("is_directory")]
        directories = [c for c in candidates if c.get("is_directory")]

        return {
            "total": len(candidates),
            "files": len(files),
            "directories": len(directories),
        }

    @staticmethod
    def unique_files(candidates):
        """Deduplicate candidates by MFT record and filename.

        This is useful when an MFT record contains multiple hard-link names.
        It intentionally does not discard different names from the main
        ``analyze`` result.
        """
        seen = set()
        unique = []

        for candidate in candidates:
            key = (
                candidate.get("record_number"),
                candidate.get("filename"),
            )
            if key in seen:
                continue
            seen.add(key)
            unique.append(candidate)

        return unique
