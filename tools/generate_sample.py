import os

with open("testdata/sample.bin", "wb") as out:

    # Random bytes
    out.write(os.urandom(5000))

    # First image
    with open("testdata/image1.jpg", "rb") as img:
        out.write(img.read())

    # More random bytes
    out.write(os.urandom(8000))

    # Second image
    with open("testdata/image2.jpg", "rb") as img:
        out.write(img.read())

    # Ending random bytes
    out.write(os.urandom(5000))

print("Sample binary created!")