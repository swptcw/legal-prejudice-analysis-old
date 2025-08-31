# Legal Prejudice Analysis Documentation Hub Deployment Guide

## Overview

This guide provides instructions for deploying the Legal Prejudice Analysis documentation hub and its subdomains to GitHub Pages. The documentation hub consists of the following components:

- **Main Documentation Hub**: docs.legal-prejudice-analysis.org
- **Demo Site**: demo.legal-prejudice-analysis.org
- **API Documentation**: api.legal-prejudice-analysis.org
- **Downloads Portal**: downloads.legal-prejudice-analysis.org
- **Community Forum**: forum.legal-prejudice-analysis.org

## Prerequisites

- GitHub account with access to the repository
- Git installed on your local machine
- DNS access to configure the domain records

## Deployment Steps

### 1. GitHub Repository Setup

1. Create a new branch in the repository for the documentation hub:

```bash
git checkout -b docs-deployment
```

2. Copy the contents of the `docs_new` directory to the appropriate location in the repository:

```bash
# If deploying to the main branch
cp -r docs_new/* docs/

# If deploying to a gh-pages branch
git checkout gh-pages
cp -r docs_new/* ./
```

3. Commit and push the changes:

```bash
git add .
git commit -m "Deploy documentation hub and subdomains"
git push origin docs-deployment
```

4. Create a pull request to merge the changes into the main branch.

### 2. GitHub Pages Configuration

1. Go to the repository settings on GitHub.
2. Navigate to the "Pages" section.
3. Configure the source branch (main or gh-pages) and directory (/docs or root).
4. Enable "Enforce HTTPS" for secure connections.
5. Add the custom domain "docs.legal-prejudice-analysis.org".
6. Save the settings and wait for GitHub Pages to build and deploy the site.

### 3. DNS Configuration

Ensure the following DNS records are configured for the domain:

| Type | Name | Value | TTL |
|------|------|-------|-----|
| A | @ | 185.199.108.153 | 3600 |
| A | @ | 185.199.109.153 | 3600 |
| A | @ | 185.199.110.153 | 3600 |
| A | @ | 185.199.111.153 | 3600 |
| CNAME | www | legal-prejudice-analysis.org. | 3600 |
| CNAME | docs | swptcw.github.io. | 3600 |
| CNAME | demo | swptcw.github.io. | 3600 |
| CNAME | api | swptcw.github.io. | 3600 |
| CNAME | downloads | swptcw.github.io. | 3600 |
| CNAME | forum | swptcw.github.io. | 3600 |

### 4. Verify Deployment

1. Wait for DNS propagation (can take up to 48 hours).
2. Verify that the main documentation hub is accessible at https://docs.legal-prejudice-analysis.org.
3. Verify that each subdomain is accessible:
   - https://demo.legal-prejudice-analysis.org
   - https://api.legal-prejudice-analysis.org
   - https://downloads.legal-prejudice-analysis.org
   - https://forum.legal-prejudice-analysis.org

### 5. Set Up GitHub Actions for Automated Deployment

Create a GitHub Actions workflow file at `.github/workflows/deploy-docs.yml`:

```yaml
name: Deploy Documentation

on:
  push:
    branches:
      - main
    paths:
      - 'docs/**'
      - 'docs_new/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '16'

      - name: Copy documentation files
        run: |
          mkdir -p build
          cp -r docs_new/* build/

      - name: Deploy to GitHub Pages
        uses: JamesIves/github-pages-deploy-action@v4
        with:
          branch: gh-pages
          folder: build
          clean: true
```

### 6. Implement Analytics

1. Create a Google Analytics account if you don't have one.
2. Add the Google Analytics tracking code to all HTML files:

```html
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'GA_MEASUREMENT_ID');
</script>
```

3. Replace `GA_MEASUREMENT_ID` with your actual Google Analytics measurement ID.

## Maintenance and Updates

### Regular Updates

1. Make changes to the documentation files in the `docs_new` directory.
2. Test the changes locally if possible.
3. Commit and push the changes to the repository.
4. The GitHub Actions workflow will automatically deploy the changes to GitHub Pages.

### Troubleshooting

- **404 Errors**: Ensure that all file paths are correct and that the CNAME files are present in each subdomain directory.
- **DNS Issues**: Verify that the DNS records are correctly configured and that enough time has passed for propagation.
- **HTTPS Issues**: Ensure that "Enforce HTTPS" is enabled in the GitHub Pages settings.
- **Broken Links**: Use a link checker tool to identify and fix broken links in the documentation.

## Future Enhancements

- Implement a documentation search engine using Algolia or similar service.
- Set up monitoring for the documentation site using Uptime Robot or similar service.
- Create a feedback mechanism for users to report issues or suggest improvements.
- Implement versioning for the documentation to support multiple versions of the framework.