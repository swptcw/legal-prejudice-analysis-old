#!/usr/bin/env python3

import ftplib
import ssl
import sys
import traceback

# FTP credentials
FTP_HOST = "ftp.legal-prejudice-analysis.com"
FTP_USER = "ninjaai@legal-prejudice-analysis.com"
FTP_PASS = "e0GgBeT1A9E."

print(f"Attempting to connect to {FTP_HOST} with user {FTP_USER}")

try:
    # First try regular FTP
    print("Trying regular FTP...")
    ftp = ftplib.FTP(FTP_HOST)
    ftp.login(FTP_USER, FTP_PASS)
    print("Connected using regular FTP")
except Exception as e:
    print(f"Regular FTP failed: {str(e)}")
    print("Trying FTP with TLS...")
    try:
        # Try FTP with TLS but without certificate verification
        context = ssl._create_unverified_context()
        ftp = ftplib.FTP_TLS(FTP_HOST, context=context)
        ftp.login(FTP_USER, FTP_PASS)
        ftp.prot_p()  # Set up secure data connection
        print("Connected using FTP with TLS")
    except Exception as e:
        print(f"FTP with TLS failed: {str(e)}")
        print("Detailed error information:")
        traceback.print_exc()
        sys.exit(1)

# If we get here, we have a connection
print("Successfully connected to FTP server")

# Try to upload a test file
try:
    with open("test.html", "rb") as file:
        print("Uploading test.html...")
        ftp.storbinary(f"STOR test.html", file)
        print("Successfully uploaded test.html")
except Exception as e:
    print(f"Upload failed: {str(e)}")
    traceback.print_exc()

# Close the connection
try:
    ftp.quit()
except:
    pass

print("FTP session completed")