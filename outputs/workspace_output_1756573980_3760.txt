# DNS Configuration Guide for Legal Prejudice Analysis Website

## Overview

This guide provides the DNS configuration needed to set up the subdomains for the Legal Prejudice Analysis website. These subdomains will be used to host different components of the website, providing a clean and organized structure.

## Required DNS Records

Please add the following DNS records to your domain configuration:

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

## Explanation

1. **A Records for Root Domain**
   - These point your root domain (legal-prejudice-analysis.org) to GitHub Pages' IP addresses
   - GitHub Pages uses multiple IP addresses for redundancy

2. **CNAME for www Subdomain**
   - Points www.legal-prejudice-analysis.org to your root domain

3. **CNAMEs for Feature Subdomains**
   - All subdomains (docs, demo, api, downloads, forum) point to GitHub Pages
   - Each will be configured with a specific branch or directory in your GitHub repository

## GitHub Pages Configuration

After adding these DNS records, you'll need to:

1. Create a CNAME file in each subdomain's directory in your GitHub repository
2. Configure GitHub Pages to serve content from these directories
3. Wait for DNS propagation (can take up to 48 hours)

## Verification

After DNS propagation, you can verify your configuration using:

```bash
dig docs.legal-prejudice-analysis.org
dig demo.legal-prejudice-analysis.org
```

You should see the CNAME records pointing to GitHub Pages.

## Next Steps

Once DNS is configured:

1. Create the directory structure in your GitHub repository
2. Add CNAME files to each directory
3. Enable GitHub Pages for each subdomain
4. Deploy your content to each subdomain

## Support

If you encounter any issues with DNS configuration, please check:
- DNS propagation using online tools
- GitHub Pages documentation for custom domains
- Your domain registrar's specific DNS configuration interface