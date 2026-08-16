from sherlocked.metadata.metadata_extractor import MetadataExtractor


def test_metadata_extraction(tmp_path):
    test_file = tmp_path / "test.txt"

    test_file.write_text(
        "Sherlocked metadata test",
        encoding="utf-8"
    )

    metadata = MetadataExtractor.extract(test_file)

    assert isinstance(metadata, dict)

    assert metadata["name"] == "test.txt"
    assert metadata["extension"] == ".txt"
    assert metadata["size_bytes"] > 0

    assert "created" in metadata
    assert "modified" in metadata
    assert "accessed" in metadata