from modules.recovery.carver import FileCarver

count = FileCarver.carve_jpegs(
    "testdata/sample.bin",
    "recovered"
)

print(f"{count} images recovered")