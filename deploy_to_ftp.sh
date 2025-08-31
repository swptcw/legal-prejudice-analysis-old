#!/bin/bash

# FTP Deployment Script for Legal Prejudice Analysis Project
# This script uploads the project files to the FTP server

# FTP credentials
FTP_USER="ninjaai@legal-prejudice-analysis.com"
FTP_PASS="e0GgBeT1A9E."
FTP_HOST="ftp.legal-prejudice-analysis.com"

# LFTP command with SSL verification disabled
LFTP_CMD="lftp -u &quot;$FTP_USER,$FTP_PASS&quot; $FTP_HOST -e &quot;set ssl:verify-certificate no;"

# Upload main documentation files
echo "Uploading main documentation files..."
$LFTP_CMD put README.md; put LICENSE; put CODE_OF_CONDUCT.md; put CONTRIBUTING.md; exit&quot;"

# Upload docs directory
echo "Uploading docs directory..."
$LFTP_CMD mirror -R docs docs; exit&quot;"

# Upload landing page
echo "Uploading landing page..."
$LFTP_CMD mirror -R landing-page landing-page; exit&quot;"

# Upload enhanced calculator
echo "Uploading enhanced calculator..."
$LFTP_CMD mirror -R enhanced-calculator enhanced-calculator; exit&quot;"

# Upload prejudice risk calculator
echo "Uploading prejudice risk calculator..."
$LFTP_CMD mirror -R prejudice_risk_calculator prejudice_risk_calculator; exit&quot;"

# Upload markdown files
echo "Uploading markdown documentation files..."
$LFTP_CMD cd /; mput legal_prejudice_*.md; exit&quot;"

echo "Deployment completed successfully!"