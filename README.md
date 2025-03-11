# Motorcycle Manual Query API

REST API in Django for intelligent querying of motorcycle technical manuals using AI.

## Quick Start

### Prerequisites
- Python 3.9
- Docker (optional)
- Technical manual PDFs

### Quick Installation with Docker

```bash
# Clone the repository
git clone [your-repository]
cd [your-project]

# Create the necessary directories
mkdir -p application/engine/moto_manual_agent/manuals
mkdir -p application/engine/moto_manual_agent/vector_indices

# Add your PDFs to the manuals folder/

# Build and run
docker build -t moto-manual-api .
docker run -p 8000:8000 moto-manual-api
```

### Local Installation

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

## Basic Structure

```
.
├── application/
│   └── engine/
│       └── moto_manual_agent/
│           ├── manuals/     # Your PDFs here
│           └── vector_indices/
└── scripts/
```

## Basic Usage

```bash
# Query example
curl -X POST http://localhost:8000/api/query/ \
  -H "Content-Type: application/json" \
  -d '{"question": "How to adjust clutch?"}'
```

## Development Tips

1. Keep PDFs out of git (already set up in .gitignore)
2. Use branches for new features
3. Make small and frequent commits
4. Keep dependencies updated

## Common Issues

1. **Error initializing indices**: Check if there are PDFs in the manuals/ folder
2. **Memory error**: Reduce PDF size or adjust settings
3. **Docker error**: Verify that directories were created correctly

## Useful Links

- [Complete Documentation](docs/README.md)
- [Contribution Guide](CONTRIBUTING.md)
- [Changelog](CHANGELOG.md) 