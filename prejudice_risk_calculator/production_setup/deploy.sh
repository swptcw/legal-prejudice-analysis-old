#!/bin/bash
# Deployment script for Legal Prejudice Risk Calculator API

set -e  # Exit on error

# Print colored messages
print_message() {
    echo -e "\e[1;34m$1\e[0m"
}

print_success() {
    echo -e "\e[1;32m$1\e[0m"
}

print_error() {
    echo -e "\e[1;31m$1\e[0m"
}

print_warning() {
    echo -e "\e[1;33m$1\e[0m"
}

# Check if Docker and Docker Compose are installed
check_dependencies() {
    print_message "Checking dependencies..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    print_success "All dependencies are installed."
}

# Generate environment variables
generate_env_file() {
    print_message "Generating environment variables..."
    
    if [ -f .env ]; then
        print_warning ".env file already exists. Do you want to overwrite it? (y/n)"
        read -r overwrite
        if [ "$overwrite" != "y" ]; then
            print_message "Keeping existing .env file."
            return
        fi
    fi
    
    # Generate random passwords and keys
    DB_PASSWORD=$(openssl rand -base64 32 | tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1)
    SECRET_KEY=$(openssl rand -base64 64 | tr -dc 'a-zA-Z0-9' | fold -w 64 | head -n 1)
    JWT_SECRET_KEY=$(openssl rand -base64 64 | tr -dc 'a-zA-Z0-9' | fold -w 64 | head -n 1)
    
    # Create .env file
    cat > .env << EOF
# Database
DB_PASSWORD=$DB_PASSWORD

# Security
SECRET_KEY=$SECRET_KEY
JWT_SECRET_KEY=$JWT_SECRET_KEY

# CORS
CORS_ORIGINS=*

# Environment
FLASK_ENV=production
FLASK_CONFIG=production
EOF
    
    print_success ".env file generated."
}

# Create SSL certificates for development
generate_ssl_certs() {
    print_message "Generating self-signed SSL certificates for development..."
    
    mkdir -p nginx/ssl
    
    if [ -f nginx/ssl/server.crt ] && [ -f nginx/ssl/server.key ]; then
        print_warning "SSL certificates already exist. Do you want to regenerate them? (y/n)"
        read -r regenerate
        if [ "$regenerate" != "y" ]; then
            print_message "Keeping existing SSL certificates."
            return
        fi
    fi
    
    # Generate self-signed certificate
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout nginx/ssl/server.key -out nginx/ssl/server.crt \
        -subj "/C=US/ST=State/L=City/O=Organization/CN=api.prejudicerisk.example.com"
    
    print_success "Self-signed SSL certificates generated."
    print_warning "Note: These are self-signed certificates for development only. Use proper certificates for production."
}

# Create static files directory
create_static_files() {
    print_message "Creating static files directory..."
    
    mkdir -p static
    
    # Create a simple index.html
    cat > static/index.html << EOF
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Legal Prejudice Risk Calculator API</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            color: #333;
        }
        h1 {
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }
        .api-info {
            background-color: #f8f9fa;
            border-left: 4px solid #3498db;
            padding: 15px;
            margin: 20px 0;
        }
        .footer {
            margin-top: 40px;
            border-top: 1px solid #ddd;
            padding-top: 10px;
            font-size: 0.9em;
            color: #777;
        }
    </style>
</head>
<body>
    <h1>Legal Prejudice Risk Calculator API</h1>
    
    <div class="api-info">
        <p>The API is running and available at <code>/api/v1</code>.</p>
        <p>For API documentation, visit <a href="/api/v1/docs">/api/v1/docs</a>.</p>
    </div>
    
    <p>This API provides endpoints for managing prejudice risk assessments, including:</p>
    
    <ul>
        <li>Creating and managing assessments</li>
        <li>Submitting factor ratings</li>
        <li>Calculating risk scores</li>
        <li>Integrating with case management systems</li>
        <li>Webhook notifications for real-time updates</li>
    </ul>
    
    <p>For more information, please refer to the API documentation.</p>
    
    <div class="footer">
        <p>Legal Prejudice Risk Calculator API &copy; 2025</p>
    </div>
</body>
</html>
EOF
    
    # Create error pages
    cat > static/404.html << EOF
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>404 - Page Not Found</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            color: #333;
            text-align: center;
        }
        h1 {
            color: #e74c3c;
            font-size: 3em;
            margin-bottom: 10px;
        }
        .error-container {
            background-color: #f8f9fa;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
        }
        .back-link {
            display: inline-block;
            margin-top: 20px;
            padding: 10px 20px;
            background-color: #3498db;
            color: white;
            text-decoration: none;
            border-radius: 4px;
        }
        .back-link:hover {
            background-color: #2980b9;
        }
    </style>
</head>
<body>
    <div class="error-container">
        <h1>404</h1>
        <h2>Page Not Found</h2>
        <p>The page you are looking for does not exist or has been moved.</p>
        <a href="/" class="back-link">Go to Homepage</a>
    </div>
</body>
</html>
EOF
    
    cat > static/50x.html << EOF
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Server Error</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            color: #333;
            text-align: center;
        }
        h1 {
            color: #e74c3c;
            font-size: 3em;
            margin-bottom: 10px;
        }
        .error-container {
            background-color: #f8f9fa;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
        }
        .back-link {
            display: inline-block;
            margin-top: 20px;
            padding: 10px 20px;
            background-color: #3498db;
            color: white;
            text-decoration: none;
            border-radius: 4px;
        }
        .back-link:hover {
            background-color: #2980b9;
        }
    </style>
</head>
<body>
    <div class="error-container">
        <h1>500</h1>
        <h2>Server Error</h2>
        <p>Something went wrong on our end. Please try again later.</p>
        <a href="/" class="back-link">Go to Homepage</a>
    </div>
</body>
</html>
EOF
    
    print_success "Static files created."
}

# Create logs directory
create_logs_directory() {
    print_message "Creating logs directory..."
    mkdir -p logs
    print_success "Logs directory created."
}

# Build and start containers
start_services() {
    print_message "Building and starting services..."
    docker-compose build
    docker-compose up -d
    print_success "Services started."
}

# Initialize database
initialize_database() {
    print_message "Initializing database..."
    
    # Wait for database to be ready
    print_message "Waiting for database to be ready..."
    sleep 10
    
    # Run migrations
    print_message "Running database migrations..."
    docker-compose exec api flask db upgrade
    
    # Seed initial data
    print_message "Seeding initial data..."
    docker-compose exec api python -c "from app import create_app, db; from models import FactorDefinition; app = create_app(); with app.app_context(): db.create_all()"
    
    print_success "Database initialized."
}

# Create initial admin API key
create_admin_api_key() {
    print_message "Creating initial admin API key..."
    
    # Generate API key
    API_KEY=$(docker-compose exec api python -c "import secrets; print(f'prfk_{secrets.token_urlsafe(32)}')")
    
    # Create API key in database
    docker-compose exec api python -c "from app import create_app, db; from models import APIKey; import hashlib, datetime, uuid; app = create_app(); with app.app_context(): key = APIKey(key_id=str(uuid.uuid4()), key_hash=hashlib.sha256('$API_KEY'.encode()).hexdigest(), name='Initial Admin Key', description='Created during deployment', created_by='deploy.sh', is_active=True, created_at=datetime.datetime.utcnow(), updated_at=datetime.datetime.utcnow()); db.session.add(key); db.session.commit()"
    
    print_success "Initial admin API key created: $API_KEY"
    print_warning "Make sure to save this API key as it won't be shown again."
}

# Show deployment info
show_info() {
    print_message "Deployment completed successfully!"
    print_message "API is available at: https://api.prejudicerisk.example.com/api/v1"
    print_message "Health check endpoint: https://api.prejudicerisk.example.com/health"
    print_message "API documentation: https://api.prejudicerisk.example.com/api/v1/docs"
    
    print_warning "Note: You need to configure your DNS to point api.prejudicerisk.example.com to your server."
    print_warning "For production use, replace the self-signed SSL certificates with proper ones."
}

# Main deployment process
main() {
    print_message "Starting deployment of Legal Prejudice Risk Calculator API..."
    
    check_dependencies
    generate_env_file
    generate_ssl_certs
    create_static_files
    create_logs_directory
    start_services
    initialize_database
    create_admin_api_key
    show_info
}

# Run the main function
main