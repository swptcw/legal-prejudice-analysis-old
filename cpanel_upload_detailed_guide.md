# Comprehensive cPanel File Manager Upload Guide
## Legal Prejudice Analysis Project

This detailed guide will walk you through the process of uploading the Legal Prejudice Analysis Project files using cPanel File Manager, with specific instructions for each component.

## Table of Contents
1. [Accessing cPanel File Manager](#accessing-cpanel-file-manager)
2. [Preparing Your Local Files](#preparing-your-local-files)
3. [Creating the Directory Structure](#creating-the-directory-structure)
4. [Uploading the Main Landing Page](#uploading-the-main-landing-page)
5. [Uploading the Documentation Files](#uploading-the-documentation-files)
6. [Uploading the Enhanced Calculator](#uploading-the-enhanced-calculator)
7. [Uploading the Risk Calculator API](#uploading-the-risk-calculator-api)
8. [Uploading Markdown Documentation](#uploading-markdown-documentation)
9. [Setting File Permissions](#setting-file-permissions)
10. [Verifying the Upload](#verifying-the-upload)
11. [Troubleshooting Common Issues](#troubleshooting-common-issues)

## Accessing cPanel File Manager

1. Open your web browser and navigate to your cPanel login page
   - Typically at: `https://yourdomain.com/cpanel` or `https://your-hosting-provider.com/cpanel`

2. Log in with your cPanel username and password
   - These credentials should have been provided by your hosting provider

3. Find and click on the "File Manager" icon in the Files section
   - It usually has a folder icon and is labeled "File Manager"

4. In the dialog that appears, select:
   - "Web Root (public_html/www)"
   - Check "Show Hidden Files (dotfiles)"
   - Click "Go"

## Preparing Your Local Files

Before uploading, organize your local files according to the project structure:

```
legal-prejudice-analysis/
│
├── index.html                      # Main landing page
├── README.md                       # Project readme
├── LICENSE                         # License information
├── CODE_OF_CONDUCT.md              # Code of conduct
├── CONTRIBUTING.md                 # Contribution guidelines
│
├── docs/                           # Documentation directory
│   ├── index.html                  # Documentation home page
│   ├── assets/                     # Documentation assets
│   ├── css/                        # Documentation styles
│   └── js/                         # Documentation scripts
│
├── enhanced-calculator/            # Enhanced risk calculator
│   ├── index.html                  # Calculator main page
│   ├── assets/                     # Calculator assets
│   ├── css/                        # Calculator styles
│   └── js/                         # Calculator scripts
│
├── prejudice_risk_calculator/      # Risk calculator API
│   ├── README.md                   # API documentation
│   └── [other API files]           # Various API implementation files
│
└── legal_prejudice_*.md            # Various markdown documentation files
```

## Creating the Directory Structure

1. Navigate to your website's root directory (usually public_html)

2. Create the main project directories:
   - Click the "New Folder" button in the top menu
   - Enter "docs" and click "Create New Folder"
   - Repeat for "enhanced-calculator"
   - Repeat for "prejudice_risk_calculator"

3. Create subdirectories within each main directory:
   - Navigate into "docs"
   - Create subdirectories: "assets", "css", "js"
   - Navigate back to root
   - Navigate into "enhanced-calculator"
   - Create subdirectories: "assets", "css", "js"
   - Navigate back to root
   - Navigate into "prejudice_risk_calculator"
   - Create necessary subdirectories based on your local structure

## Uploading the Main Landing Page

1. Navigate to your website's root directory (public_html)

2. Upload the main index.html file:
   - Click the "Upload" button in the top menu
   - In the upload interface, click "Select File"
   - Browse to your local index.html file
   - Select it and click "Open"
   - Wait for the upload to complete
   - Click "Go Back to /public_html" when done

3. Upload the supporting files:
   - Click "Upload" again
   - Select README.md, LICENSE, CODE_OF_CONDUCT.md, and CONTRIBUTING.md
   - Click "Open" to upload them
   - Wait for the upload to complete
   - Click "Go Back to /public_html" when done

## Uploading the Documentation Files

1. Navigate to the "docs" directory:
   - Click on the "docs" folder in the file list

2. Upload the documentation index.html:
   - Click the "Upload" button
   - Select your local docs/index.html file
   - Click "Open" to upload
   - Wait for the upload to complete
   - Click "Go Back to /public_html/docs" when done

3. Upload assets:
   - Navigate to the "docs/assets" directory
   - Click the "Upload" button
   - Select all files from your local docs/assets directory
   - Click "Open" to upload them
   - Wait for the upload to complete
   - Click "Go Back to /public_html/docs/assets" when done

4. Upload CSS files:
   - Navigate to the "docs/css" directory
   - Click the "Upload" button
   - Select all files from your local docs/css directory
   - Click "Open" to upload them
   - Wait for the upload to complete

5. Upload JavaScript files:
   - Navigate to the "docs/js" directory
   - Click the "Upload" button
   - Select all files from your local docs/js directory
   - Click "Open" to upload them
   - Wait for the upload to complete

## Uploading the Enhanced Calculator

1. Navigate to the "enhanced-calculator" directory:
   - Return to the root directory
   - Click on the "enhanced-calculator" folder

2. Upload the calculator index.html:
   - Click the "Upload" button
   - Select your local enhanced-calculator/index.html file
   - Click "Open" to upload
   - Wait for the upload to complete
   - Click "Go Back to /public_html/enhanced-calculator" when done

3. Upload assets:
   - Navigate to the "enhanced-calculator/assets" directory
   - Click the "Upload" button
   - Select all files from your local enhanced-calculator/assets directory
   - Click "Open" to upload them
   - Wait for the upload to complete

4. Upload CSS files:
   - Navigate to the "enhanced-calculator/css" directory
   - Click the "Upload" button
   - Select all files from your local enhanced-calculator/css directory
   - Click "Open" to upload them
   - Wait for the upload to complete

5. Upload JavaScript files:
   - Navigate to the "enhanced-calculator/js" directory
   - Click the "Upload" button
   - Select all files from your local enhanced-calculator/js directory
   - Click "Open" to upload them
   - Wait for the upload to complete

## Uploading the Risk Calculator API

1. Navigate to the "prejudice_risk_calculator" directory:
   - Return to the root directory
   - Click on the "prejudice_risk_calculator" folder

2. Upload the API files:
   - Click the "Upload" button
   - Select all files from your local prejudice_risk_calculator directory
   - Click "Open" to upload them
   - Wait for the upload to complete

3. Create and upload to any subdirectories as needed:
   - Follow the same process as above for any subdirectories

## Uploading Markdown Documentation

1. Navigate to your website's root directory (public_html)

2. Upload the markdown documentation files:
   - Click the "Upload" button
   - Select all legal_prejudice_*.md files from your local directory
   - Click "Open" to upload them
   - Wait for the upload to complete
   - Click "Go Back to /public_html" when done

## Setting File Permissions

1. Set permissions for HTML, CSS, JS, and MD files:
   - In the root directory, select all .html, .css, .js, and .md files
   - Click "Permissions" in the top menu
   - Set numeric value to 644 (rw-r--r--)
   - Check "Apply to all files"
   - Click "Change Permissions"

2. Set permissions for directories:
   - Select all directories (docs, enhanced-calculator, etc.)
   - Click "Permissions" in the top menu
   - Set numeric value to 755 (rwxr-xr-x)
   - Check "Apply to all directories"
   - Click "Change Permissions"

## Verifying the Upload

1. Test the main landing page:
   - Open a new browser tab
   - Navigate to your website (e.g., https://legal-prejudice-analysis.com)
   - Verify that the main page loads correctly with all styles and images

2. Test the documentation:
   - Click on the documentation link from the main page
   - Verify that the documentation loads correctly
   - Check that all links within the documentation work

3. Test the enhanced calculator:
   - Click on the calculator link from the main page
   - Verify that the calculator loads correctly
   - Test the calculator functionality by completing an assessment
   - Check that all visualizations render properly

4. Test the API documentation:
   - Navigate to the API documentation
   - Verify that all documentation files are accessible

## Troubleshooting Common Issues

### 404 Not Found Errors
- Verify that the file exists in the correct location
- Check the file name for typos
- Ensure the file path in links is correct (case-sensitive)

### Missing Styles or Images
- Check that CSS files are in the correct directories
- Verify that image paths are correct
- Ensure file permissions are set correctly

### JavaScript Not Working
- Check browser console for errors
- Verify that JS files are in the correct directories
- Ensure file permissions are set correctly

### Permission Denied Errors
- Check file permissions (644 for files, 755 for directories)
- Contact your hosting provider if you need higher permissions

### Broken Links
- Verify that all links use relative paths correctly
- Check for typos in link URLs
- Ensure target pages exist in the correct locations

## Additional Resources

- [cPanel Documentation](https://docs.cpanel.net/cpanel/files/file-manager/)
- [Web File Permissions Guide](https://www.webhostface.com/kb/knowledgebase/file-permissions/)
- [HTML5 Validation Tool](https://validator.w3.org/)