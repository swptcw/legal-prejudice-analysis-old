# Website Structure Guide for Legal Prejudice Analysis Project

This guide provides detailed information about the structure of the Legal Prejudice Analysis Project website and how the files should be organized on your web server.

## Main Website Structure

```
public_html/ (or your web root directory)
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
│   ├── api_server.py               # API server implementation
│   ├── cms_integration_example.py  # CMS integration example
│   ├── cms_integration_guide.md    # CMS integration guide
│   ├── production_setup/           # Production deployment files
│   ├── server.py                   # Simple server implementation
│   └── webhook_implementation_spec.md # Webhook specifications
│
└── legal_prejudice_*.md            # Various markdown documentation files
```

## Key Files and Their Purposes

### Main Landing Page (index.html)

The main landing page serves as the entry point to the website. It provides:
- Project overview
- Key components description
- Links to documentation and tools
- Contact information

This file should be placed in the root directory of your website.

### Enhanced Calculator (enhanced-calculator/index.html)

The enhanced calculator is a web-based tool that allows users to:
- Assess legal prejudice risk factors
- Calculate risk scores based on likelihood and impact
- Visualize risk through interactive matrices
- Generate recommendations based on risk levels

The calculator requires its CSS and JavaScript files to function properly.

### Documentation (docs/index.html)

The documentation section provides comprehensive information about:
- The legal prejudice analysis framework
- Risk assessment methodologies
- Practical guides for legal practitioners
- Case studies and examples
- API integration instructions

### Risk Calculator API (prejudice_risk_calculator/)

The API implementation allows integration with other systems:
- RESTful endpoints for assessments and results
- CMS integration capabilities
- Webhook implementation for notifications
- Production deployment configurations

## File Relationships and Dependencies

- The main index.html links to the documentation and calculator
- The enhanced calculator depends on its CSS and JS files
- The documentation pages reference each other through relative links
- The API documentation references implementation files

## Important Notes for Upload

1. **Maintain Directory Structure**: Keep the directory structure intact to ensure all relative links work correctly
2. **File Permissions**: Set appropriate permissions as outlined in the cPanel upload guide
3. **Index Files**: Make sure index.html files are present in each directory to enable proper navigation
4. **Asset Paths**: Verify that all asset paths (images, CSS, JS) use relative paths
5. **Testing**: After upload, test all links and functionality to ensure everything works as expected