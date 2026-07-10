import pycdlib
from pathlib import Path

Path('local_secret.txt').write_text("This is a secret forensic test file.")
Path('local_notes.pdf').write_text("Dummy PDF content for testing.")
Path('payload.exe').touch()

# 1. Initialize the ISO object
iso = pycdlib.PyCdlib()

# 2. Open a new ISO9660 target (interchange level 1)
iso.new(interchange_level=1)

# 3. Add a file from your hard drive into the ISO
# Arguments: local_file_path, iso_path
iso.add_file('local_secret.txt', '/SECRET.TXT;1')
iso.add_file('payload.exe','/PAYLOAD.EXE;1')

# 4. Add a directory
iso.add_directory('/DOCS')

# 5. Add a file inside that directory
iso.add_file('local_notes.pdf', '/DOCS/NOTES.PDF;1')

# 6. Write the data to a file and close it
iso.write('evidence/test_evidence.iso')
iso.close()