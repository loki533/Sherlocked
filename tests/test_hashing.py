from sherlocked.hashing.hash_calculator import HashCalculator


def test_hash_calculation(tmp_path):
    test_file = tmp_path / "test.txt"

    test_file.write_text(
        "Sherlocked forensic test",
        encoding="utf-8"
    )

    hashes = HashCalculator.calculate_all(test_file)

    assert isinstance(hashes, dict)

    assert "md5" in hashes
    assert "sha1" in hashes
    assert "sha256" in hashes

    assert len(hashes["md5"]) == 32
    assert len(hashes["sha1"]) == 40
    assert len(hashes["sha256"]) == 64