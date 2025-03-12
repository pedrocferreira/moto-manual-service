# Motorcycle Manual Query System

A comprehensive application for intelligent querying of motorcycle technical manuals using AI. The system combines a Django REST API backend with an Angular frontend that provides a user-friendly interface to access information from motorcycle manuals.

## Features

- Natural language processing for manual queries
- Authentication system with JWT tokens
- PDF document processing and indexing
- Chat-like interface for user queries
- Responsive Angular frontend
- Docker containerization for easy deployment

## Quick Start

### Prerequisites

#### Backend
- Python 3.9
- Docker (recommended)
- Technical manual PDFs

#### Frontend
- Node.js version 18.19.1 or higher
- npm version 8.0.0 or higher
- Angular CLI

### Backend Setup

#### Using Docker (Recommended)

```bash
# Clone the repository
git clone [your-repository]
cd [your-project]

# Create the necessary directories
mkdir -p application/engine/moto_manual_agent/manuals
mkdir -p application/engine/moto_manual_agent/vector_indices

# Add your PDFs to the manuals folder

# Build and run
docker-compose up --build
```

#### Local Installation

```bash
# Create and activate the virtual environment
python -m venv env
source env/bin/activate  # Linux/Mac
env\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
pip install -e .

# Initialize indices
python scripts/initialize_indices.py

# Run the server
python manage.py runserver
```

### Frontend Setup

1. **Install/Update Node.js**
   ```bash
   # Install NVM (Node Version Manager)
   curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
   
   # Reload NVM
   source ~/.bashrc
   
   # Install the correct Node.js version
   nvm install 18.19.1
   nvm use 18.19.1
   ```

2. **Verify installed versions**
   ```bash
   node --version  # Should show v18.19.1
   npm --version   # Should show 8.x.x or higher
   ```

3. **Install Angular CLI globally**
   ```bash
   npm install -g @angular/cli
   ```

4. **Navigate to the frontend directory and install dependencies**
   ```bash
   cd front-temp
   
   # Clean previous installations
   rm -rf node_modules package-lock.json
   
   # Install dependencies
   npm install --legacy-peer-deps
   ```

5. **Start the development server**
   ```bash
   ng serve --proxy-config proxy.conf.json
   ```

6. **Access the application**
   - Open your browser and navigate to: `http://localhost:4200`

## Configuration

### Proxy Configuration

Ensure that your `proxy.conf.json` file in the frontend project contains:

```json
{
  "/ask-manual": {
    "target": "http://localhost:8000",
    "secure": false,
    "changeOrigin": true
  },
  "/api": {
    "target": "http://localhost:8000",
    "secure": false,
    "changeOrigin": true
  }
}
```

### CORS Configuration

The backend's `settings.py` should include CORS settings:

```python
INSTALLED_APPS = [
    # ...
    'corsheaders',
    # ...
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    # ... other middleware
]

# CORS Settings
CORS_ALLOW_ALL_ORIGINS = True  # For development only
CORS_ALLOWED_ORIGINS = [
    "http://localhost:4200",
]
```

## Basic Usage

```bash
# Backend API query example
curl -X POST http://localhost:8000/api/query/ \
  -H "Content-Type: application/json" \
  -d '{"question": "How to adjust clutch?"}'
```

## Project Structure

```
.
├── application/          # Django backend
│   ├── engine/           # NLP processing engine
│   │   └── moto_manual_agent/
│   │       ├── manuals/     # Your PDFs here
│   │       └── vector_indices/
│   ├── views/            # API endpoints
│   └── settings.py       # Django configuration
├── front-temp/           # Angular frontend
│   ├── src/
│   │   ├── app/          # Angular components
│   │   ├── services/     # API services
│   │   └── interceptors/ # HTTP interceptors
│   ├── proxy.conf.json   # Proxy configuration
│   └── angular.json      # Angular configuration
├── scripts/              # Utility scripts
└── docker-compose.yml    # Docker configuration
```

## Common Issues and Troubleshooting

### Backend Issues

1. **Error initializing indices**: Check if there are PDFs in the manuals/ folder
2. **Memory error**: Reduce PDF size or adjust settings
3. **Docker error**: Verify that directories were created correctly

### Dependency Conflicts

This project requires specific library versions that may conflict:

- LangChain 0.0.267 requires OpenAI 0.27.8
- Rakam-systems 0.2.4 is installed via setup.py and typically requires OpenAI 1.37.0+

If you encounter errors related to OpenAI version conflicts:
1. Remove `rakam-systems` from `requirements.txt` (if present)
2. Rebuild the Docker containers

### Frontend Issues

1. **Problems with @angular/router**
   ```bash
   npm install @angular/router@17.3.12 --save --legacy-peer-deps
   ```

2. **General dependency problems**
   ```bash
   npm cache clean --force
   rm -rf node_modules package-lock.json
   npm install --legacy-peer-deps
   ```

3. **Compilation errors**
   ```bash
   npm install --force
   ```

### Authentication Issues

If experiencing 401 Unauthorized errors:
1. Ensure user registration and login work correctly
2. Check that JWT tokens are properly stored
3. Verify the HTTP interceptor adds tokens to all API requests
4. Confirm token format is `Bearer <token>`

### CORS Issues

If experiencing CORS errors in the browser:
1. Check that django-cors-headers is installed
2. Verify CORS settings in Django settings.py
3. Ensure the Angular proxy configuration is correct

## Development Notes

- The OpenAI version (0.27.8) is critical for system functionality
- The project uses JWT tokens for authentication
- Rakam-systems is installed automatically via setup.py
- Always use the proxy configuration when running the Angular frontend
- Keep PDFs out of git (already set up in .gitignore)
- Use branches for new features
- Make small and frequent commits

## Available Scripts

### Backend
- `python scripts/initialize_indices.py`: Initialize vector indices
- `python manage.py runserver`: Start the Django development server

### Frontend  
- `ng serve --proxy-config proxy.conf.json`: Start the Angular development server
- `ng build`: Compile the project
- `ng test`: Run unit tests
- `ng e2e`: Run end-to-end tests

## API Endpoints

- `POST /api/login/` - User authentication
- `POST /ask-manual/` - Query the motorcycle manuals
- `GET /api/user/` - Get user information

## Useful Links

- [Complete Documentation](docs/README.md)
- [Contribution Guide](CONTRIBUTING.md)
- [Changelog](CHANGELOG.md) 