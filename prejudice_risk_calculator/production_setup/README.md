# Legal Prejudice Risk Calculator API
## Production Setup Guide

This guide provides instructions for deploying the Legal Prejudice Risk Calculator API in a production environment using Docker and Docker Compose.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Directory Structure](#directory-structure)
3. [Deployment Steps](#deployment-steps)
4. [Manual Configuration](#manual-configuration)
5. [Monitoring and Maintenance](#monitoring-and-maintenance)
6. [Backup and Recovery](#backup-and-recovery)
7. [Troubleshooting](#troubleshooting)

## Prerequisites

Before deploying the API, ensure you have the following:

- A server with at least 2GB RAM and 1 CPU core
- Docker (version 20.10.0 or later)
- Docker Compose (version 2.0.0 or later)
- Domain name configured to point to your server (for production use)
- SSL certificates (for production use)

## Directory Structure

The production setup has the following structure:

```
production_setup/
├── app.py                 # Main application file
├── config.py              # Configuration settings
├── deploy.sh              # Deployment script
├── docker-compose.yml     # Docker Compose configuration
├── Dockerfile             # Docker image definition
├── migrations/            # Database migrations
├── models.py              # Database models
├── nginx/                 # Nginx configuration
│   └── conf.d/            # Nginx site configuration
│       └── default.conf   # Default site configuration
├── README.md              # This file
├── requirements.txt       # Python dependencies
├── routes/                # API routes
│   ├── assessments.py     # Assessment routes
│   ├── auth.py            # Authentication routes
│   ├── cms.py             # CMS integration routes
│   ├── factors.py         # Factor routes
│   ├── results.py         # Results routes
│   └── webhooks.py        # Webhook routes
└── utils/                 # Utility functions
    ├── auth.py            # Authentication utilities
    ├── events.py          # Event handling utilities
    └── validation.py      # Validation utilities
```

## Deployment Steps

### Automated Deployment

The easiest way to deploy the API is using the provided deployment script:

```bash
./deploy.sh
```

This script will:

1. Check for required dependencies
2. Generate environment variables
3. Create self-signed SSL certificates (for development)
4. Create static files and error pages
5. Build and start the Docker containers
6. Initialize the database
7. Create an initial admin API key

### Manual Deployment

If you prefer to deploy manually, follow these steps:

1. **Create environment variables**

   Create a `.env` file with the following variables:

   ```
   # Database
   DB_PASSWORD=<strong-password>

   # Security
   SECRET_KEY=<random-string>
   JWT_SECRET_KEY=<random-string>

   # CORS
   CORS_ORIGINS=*
   ```

2. **Configure SSL certificates**

   For production, place your SSL certificates in the `nginx/ssl` directory:
   - `server.crt`: SSL certificate
   - `server.key`: SSL private key

   For development, you can generate self-signed certificates:

   ```bash
   mkdir -p nginx/ssl
   openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
       -keyout nginx/ssl/server.key -out nginx/ssl/server.crt \
       -subj "/C=US/ST=State/L=City/O=Organization/CN=api.prejudicerisk.example.com"
   ```

3. **Create static files directory**

   ```bash
   mkdir -p static
   # Create index.html and error pages
   ```

4. **Create logs directory**

   ```bash
   mkdir -p logs
   ```

5. **Build and start containers**

   ```bash
   docker-compose build
   docker-compose up -d
   ```

6. **Initialize database**

   ```bash
   # Wait for database to be ready
   sleep 10
   
   # Run migrations
   docker-compose exec api flask db upgrade
   
   # Seed initial data
   docker-compose exec api python -c "from app import create_app, db; from models import FactorDefinition; app = create_app(); with app.app_context(): db.create_all()"
   ```

7. **Create initial admin API key**

   ```bash
   # Generate API key
   API_KEY=$(docker-compose exec api python -c "import secrets; print(f'prfk_{secrets.token_urlsafe(32)}')")
   
   # Create API key in database
   docker-compose exec api python -c "from app import create_app, db; from models import APIKey; import hashlib, datetime, uuid; app = create_app(); with app.app_context(): key = APIKey(key_id=str(uuid.uuid4()), key_hash=hashlib.sha256('$API_KEY'.encode()).hexdigest(), name='Initial Admin Key', description='Created during deployment', created_by='manual', is_active=True, created_at=datetime.datetime.utcnow(), updated_at=datetime.datetime.utcnow()); db.session.add(key); db.session.commit()"
   
   echo "Initial admin API key created: $API_KEY"
   ```

## Manual Configuration

### Domain Configuration

Update the Nginx configuration in `nginx/conf.d/default.conf` to use your domain name:

```nginx
server_name your-domain.com;
```

### SSL Certificates

For production, replace the self-signed certificates with proper ones:

1. Obtain SSL certificates from a certificate authority (e.g., Let's Encrypt)
2. Place the certificate and key files in `nginx/ssl/`
3. Update the Nginx configuration if necessary

### CORS Configuration

Update the CORS configuration in the `.env` file:

```
CORS_ORIGINS=https://your-app-domain.com,https://another-domain.com
```

### Rate Limiting

Adjust the rate limiting configuration in `nginx/conf.d/default.conf`:

```nginx
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
```

## Monitoring and Maintenance

### Logs

Logs are stored in the `logs` directory and can be accessed as follows:

- **API logs**: `docker-compose logs api`
- **Nginx access logs**: `docker-compose exec nginx cat /var/log/nginx/api_access.log`
- **Nginx error logs**: `docker-compose exec nginx cat /var/log/nginx/api_error.log`
- **Database logs**: `docker-compose logs db`

### Health Check

The API provides a health check endpoint at `/health` that returns the status of the API and its dependencies.

### Updating the API

To update the API to a new version:

1. Pull the latest changes
2. Rebuild and restart the containers:

   ```bash
   docker-compose build
   docker-compose up -d
   ```

3. Run database migrations if needed:

   ```bash
   docker-compose exec api flask db upgrade
   ```

## Backup and Recovery

### Database Backup

To backup the database:

```bash
docker-compose exec db pg_dump -U prejudice prejudice_risk > backup_$(date +%Y%m%d).sql
```

### Database Restore

To restore the database from a backup:

```bash
cat backup_file.sql | docker-compose exec -T db psql -U prejudice prejudice_risk
```

### Volume Backup

To backup the Docker volumes:

```bash
docker run --rm -v prejudice_risk_calculator_postgres_data:/volume -v $(pwd):/backup alpine tar -czvf /backup/postgres_data_$(date +%Y%m%d).tar.gz /volume
docker run --rm -v prejudice_risk_calculator_redis_data:/volume -v $(pwd):/backup alpine tar -czvf /backup/redis_data_$(date +%Y%m%d).tar.gz /volume
```

## Troubleshooting

### Common Issues

1. **API not starting**
   - Check logs: `docker-compose logs api`
   - Verify environment variables in `.env` file
   - Ensure database is running: `docker-compose ps db`

2. **Database connection issues**
   - Check database logs: `docker-compose logs db`
   - Verify database password in `.env` file
   - Ensure database container is running: `docker-compose ps db`

3. **Nginx not serving requests**
   - Check Nginx logs: `docker-compose logs nginx`
   - Verify SSL certificates in `nginx/ssl/`
   - Ensure Nginx container is running: `docker-compose ps nginx`

4. **Rate limiting issues**
   - Adjust rate limiting configuration in `nginx/conf.d/default.conf`
   - Restart Nginx: `docker-compose restart nginx`

### Getting Help

If you encounter issues not covered in this guide, please:

1. Check the detailed logs for error messages
2. Consult the API documentation
3. Contact support at support@prejudicerisk.example.com

## Security Considerations

- Regularly update all components (Docker, containers, dependencies)
- Rotate API keys periodically
- Monitor logs for suspicious activity
- Use proper SSL certificates from trusted authorities
- Implement network security measures (firewall, VPN, etc.)
- Perform regular security audits