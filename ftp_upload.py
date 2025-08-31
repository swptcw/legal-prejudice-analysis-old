#!/usr/bin/env python3

import ftplib
import os
import ssl

# FTP credentials
FTP_HOST = "ftp.legal-prejudice-analysis.com"
FTP_USER = "ninjaai@legal-prejudice-analysis.com"
FTP_PASS = "e0GgBeT1A9E."

# Create a secure FTP connection
context = ssl._create_unverified_context()
ftp = ftplib.FTP_TLS(FTP_HOST, FTP_USER, FTP_PASS, context=context)
ftp.prot_p()  # Set up secure data connection

print("Connected to FTP server")

# Upload main documentation files
main_files = ["README.md", "LICENSE", "CODE_OF_CONDUCT.md", "CONTRIBUTING.md"]
for file in main_files:
    if os.path.exists(file):
        with open(file, 'rb') as f:
            print(f"Uploading {file}...")
            ftp.storbinary(f'STOR {file}', f)
            print(f"Uploaded {file}")

# Create and navigate to docs directory
try:
    ftp.mkd("docs")
except:
    pass  # Directory might already exist
ftp.cwd("docs")

# Upload index.html to docs directory
if os.path.exists("docs/index.html"):
    with open("docs/index.html", 'rb') as f:
        print("Uploading docs/index.html...")
        ftp.storbinary('STOR index.html', f)
        print("Uploaded docs/index.html")

# Return to root directory
ftp.cwd("/")

# Close the connection
ftp.quit()
print("FTP upload completed")