# GitHub Repository Structure for Legal Prejudice Analysis

This document outlines the recommended structure for the GitHub repository to support the Legal Prejudice Analysis website and its subdomains.

## Repository Organization

```
legal-prejudice-analysis/
├── .github/                    # GitHub-specific files
│   ├── workflows/              # GitHub Actions workflows
│   │   ├── deploy-main.yml     # Deploy main website
│   │   ├── deploy-docs.yml     # Deploy documentation
│   │   ├── deploy-demo.yml     # Deploy demo
│   │   ├── deploy-api.yml      # Deploy API docs
│   │   └── deploy-downloads.yml # Deploy downloads portal
│   ├── ISSUE_TEMPLATE/         # Issue templates
│   └── PULL_REQUEST_TEMPLATE.md # PR template
├── www/                        # Main website files
│   ├── index.html              # Main landing page
│   ├── assets/                 # Website assets
│   │   ├── css/                # CSS files
│   │   ├── js/                 # JavaScript files
│   │   └── images/             # Images
│   ├── CNAME                   # Contains "legal-prejudice-analysis.org"
│   └── README.md               # Main website README
├── docs/                       # Documentation site
│   ├── index.html              # Documentation home
│   ├── assets/                 # Documentation assets
│   ├── framework/              # Framework documentation
│   ├── risk-analysis/          # Risk analysis documentation
│   ├── practical-guide/        # Practical implementation guide
│   ├── case-studies/           # Case studies
│   ├── api/                    # API documentation
│   ├── integration/            # Integration guides
│   ├── CNAME                   # Contains "docs.legal-prejudice-analysis.org"
│   └── README.md               # Documentation README
├── demo/                       # Interactive demo
│   ├── index.html              # Demo landing page
│   ├── assets/                 # Demo assets
│   ├── js/                     # Demo JavaScript
│   │   ├── calculator.js       # Calculator logic
│   │   ├── visualization.js    # Visualization components
│   │   └── data.js             # Sample data
│   ├── data/                   # Demo data files
│   ├── CNAME                   # Contains "demo.legal-prejudice-analysis.org"
│   └── README.md               # Demo README
├── api-docs/                   # API documentation site
│   ├── index.html              # API docs home
│   ├── assets/                 # API docs assets
│   ├── overview/               # API overview
│   ├── authentication/         # Authentication docs
│   ├── endpoints/              # Endpoints documentation
│   ├── integration/            # Integration guides
│   ├── examples/               # Code examples
│   ├── CNAME                   # Contains "api.legal-prejudice-analysis.org"
│   └── README.md               # API docs README
├── downloads/                  # Downloads portal
│   ├── index.html              # Downloads home
│   ├── assets/                 # Downloads assets
│   ├── calculator/             # Calculator downloads
│   ├── api-server/             # API server downloads
│   ├── documentation/          # Documentation downloads
│   ├── templates/              # Templates & worksheets
│   ├── CNAME                   # Contains "downloads.legal-prejudice-analysis.org"
│   └── README.md               # Downloads README
├── forum/                      # Forum configuration
│   ├── index.html              # Forum redirect page
│   ├── config/                 # Forum configuration files
│   ├── CNAME                   # Contains "forum.legal-prejudice-analysis.org"
│   └── README.md               # Forum README
├── src/                        # Source code
│   ├── calculator/             # Calculator source code
│   ├── api-server/             # API server source code
│   └── shared/                 # Shared components
├── scripts/                    # Utility scripts
│   ├── build.sh                # Build script
│   ├── deploy.sh               # Deployment script
│   └── update-docs.sh          # Documentation update script
├── .gitignore                  # Git ignore file
├── LICENSE                     # Project license
├── CODE_OF_CONDUCT.md          # Code of conduct
├── CONTRIBUTING.md             # Contributing guidelines
└── README.md                   # Main project README
```

## Branch Strategy

### Main Branches
- `main` - Production-ready code, deployed to the main website
- `develop` - Development branch for integration of features

### Feature Branches
- `feature/feature-name` - For new features
- `bugfix/bug-name` - For bug fixes
- `docs/topic-name` - For documentation updates
- `release/version` - For release preparation

### Deployment Branches
- `deploy/www` - Deployment branch for main website
- `deploy/docs` - Deployment branch for documentation
- `deploy/demo` - Deployment branch for demo
- `deploy/api` - Deployment branch for API docs
- `deploy/downloads` - Deployment branch for downloads portal

## GitHub Pages Configuration

### Repository Settings
- Enable GitHub Pages for the repository
- Configure custom domains for each subdomain
- Enable HTTPS for all domains
- Set up branch protection rules

### GitHub Actions Workflows

#### Main Website Deployment
```yaml
name: Deploy Main Website

on:
  push:
    branches:
      - main
    paths:
      - 'www/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Build and Deploy
        uses: JamesIves/github-pages-deploy-action@4.1.4
        with:
          branch: deploy/www
          folder: www
          clean: true
```

#### Documentation Deployment
```yaml
name: Deploy Documentation

on:
  push:
    branches:
      - main
    paths:
      - 'docs/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Build and Deploy
        uses: JamesIves/github-pages-deploy-action@4.1.4
        with:
          branch: deploy/docs
          folder: docs
          clean: true
```

Similar workflows would be created for demo, API docs, and downloads portal.

## Repository Management

### Issue Templates
- Bug report template
- Feature request template
- Documentation improvement template
- Question template

### Pull Request Template
- Description of changes
- Related issue
- Type of change
- Checklist of completed items
- Testing instructions

### Branch Protection Rules
- Require pull request reviews
- Require status checks to pass
- Require linear history
- Include administrators in restrictions

## Documentation

### Main README
- Project overview
- Repository structure
- Setup instructions
- Development workflow
- Deployment instructions
- Contributing guidelines

### Component READMEs
- Component-specific documentation
- Setup instructions
- Development guidelines
- Testing instructions
- Deployment notes

## Continuous Integration

### Build Checks
- Code linting
- Unit tests
- Integration tests
- Build verification

### Deployment Checks
- Link checking
- HTML validation
- Accessibility testing
- Performance testing

## Release Management

### Version Tagging
- Semantic versioning (MAJOR.MINOR.PATCH)
- Release notes in tag description
- Automated changelog generation

### Release Assets
- Pre-built packages
- Documentation PDFs
- Release notes