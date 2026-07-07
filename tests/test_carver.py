from modules.recovery.carver import FileCarver

files = FileCarver.carve(
    "testdata/sample.bin",
    "recovered"
)

print("\nRecovered Files")

for file in files:
    print(file)