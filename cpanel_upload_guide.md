# cPanel File Manager Upload Guide for Legal Prejudice Analysis Project

This guide provides step-by-step instructions for uploading the Legal Prejudice Analysis Project files using cPanel File Manager.

## Accessing cPanel File Manager

1. Log in to your cPanel account (typically at https://yourdomain.com/cpanel)
2. Find and click on the "File Manager" icon in the Files section
3. Make sure you're in the public_html directory (or the directory where your website files should be stored)

## Creating Directory Structure

Create the following directory structure for the project:

1. Click the "New Folder" button at the top
2. Create these main directories:
   - docs
   - landing-page
   - enhanced-calculator
   - prejudice_risk_calculator

## Uploading Main Files

### Uploading index.html (Main Landing Page)

1. Navigate to the root directory (public_html)
2. Click the "Upload" button at the top
3. Select the index.html file from your computer
4. Click "Open" to upload

### Uploading Documentation Files

1. Navigate to the docs directory
2. Click the "Upload" button
3. Select all files from the docs directory on your computer
4. Click "Open" to upload
5. If there are subdirectories in docs, create them manually and upload their contents

### Uploading Enhanced Calculator

1. Navigate to the enhanced-calculator directory
2. Click the "Upload" button
3. Select all files from the enhanced-calculator directory on your computer
4. Click "Open" to upload
5. Make sure to create and upload to any subdirectories (css, js, assets)

### Uploading Risk Calculator

1. Navigate to the prejudice_risk_calculator directory
2. Click the "Upload" button
3. Select all files from the prejudice_risk_calculator directory on your computer
4. Click "Open" to upload
5. Make sure to create and upload to any subdirectories

### Uploading Markdown Documentation

1. Navigate to the root directory (public_html)
2. Click the "Upload" button
3. Select all legal_prejudice_*.md files from your computer
4. Click "Open" to upload

## Setting File Permissions

After uploading, you may need to set proper file permissions:

1. For HTML, CSS, JS, and MD files: 644 (read and write for owner, read for group and others)
2. For directories: 755 (read, write, and execute for owner, read and execute for group and others)

To set permissions:
1. Select the file or directory
2. Click "Permissions" at the top
3. Enter the numeric value (644 for files, 755 for directories)
4. Click "Change Permissions"

## Verifying the Upload

1. Visit your website in a browser (https://legal-prejudice-analysis.com)
2. Check that the main page loads correctly
3. Test links to ensure they navigate to the proper pages
4. Verify that the enhanced calculator and other interactive elements work properly

## Troubleshooting Common Issues

- **404 Not Found errors**: Check file paths and ensure files are in the correct directories
- **Broken links**: Verify that all links use relative paths correctly
- **Missing styles or scripts**: Make sure all CSS and JS files are uploaded to the correct locations
- **Permission issues**: Ensure files have the correct permissions as outlined above