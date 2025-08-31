#!/bin/bash

# Set verbose output
set -x

# FTP credentials
FTP_USER="ninjaai@legal-prejudice-analysis.com"
FTP_PASS="e0GgBeT1A9E."
FTP_HOST="ftp.legal-prejudice-analysis.com"

# Try to upload a test file
echo "Attempting to upload test.html..."
lftp -d -u "$FTP_USER,$FTP_PASS" $FTP_HOST << EOF
set ssl:verify-certificate no
set ftp:ssl-allow true
set ftp:ssl-force true
set ftp:ssl-protect-data true
debug 3
put test.html
bye
EOF

echo "Upload attempt completed"