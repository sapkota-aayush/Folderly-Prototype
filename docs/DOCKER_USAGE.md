# 🐳 Docker Usage Guide for Folderly

## Quick Start

### 1. Build the Docker Image
```bash
docker build -t folderly .
```

### 2. Run with Docker Compose (Recommended)
```bash
docker-compose up --build
```

### 3. Run Individual Container
```bash
docker run -it --rm \
  -v ${USERPROFILE}/Desktop:/workspace/Desktop \
  -v ${USERPROFILE}/Documents:/workspace/Documents \
  -e OPENAI_API_KEY=your_api_key \
  folderly
```

## 🚀 Development Workflow

### Using Docker Compose
```bash
# Start the service
docker-compose up

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the service
docker-compose down
```

### Interactive Mode
```bash
# Access container shell
docker-compose exec folderly bash

# Run Folderly CLI
docker-compose exec folderly python -m src.cli.cli
```

## 📁 Volume Mounts

The container mounts these directories from your system:
- **Desktop**: `/workspace/Desktop`
- **Documents**: `/workspace/Documents` 
- **Downloads**: `/workspace/Downloads`
- **Pictures**: `/workspace/Pictures`
- **Music**: `/workspace/Music`
- **Videos**: `/workspace/Videos`

## 🔧 Environment Variables

Create a `.env` file in your project root:
```env
OPENAI_API_KEY=your_openai_api_key_here
LOG_LEVEL=INFO
```

## 🐛 Troubleshooting

### Permission Issues
```bash
# Fix file permissions
docker-compose exec folderly chown -R folderly:folderly /workspace
```

### Rebuild After Code Changes
```bash
docker-compose up --build
```

### Check Container Status
```bash
docker-compose ps
docker-compose logs folderly
```

## 🎯 Poetry Integration

- **Dependencies**: Automatically installed from `pyproject.toml`
- **Build**: Multi-stage Dockerfile optimizes Poetry installation
- **Production**: Only production dependencies included in final image

## 📦 Production Deployment

```bash
# Build production image
docker build -t folderly:latest .

# Run production container
docker run -d \
  --name folderly-prod \
  -v /path/to/files:/workspace \
  -e OPENAI_API_KEY=prod_key \
  folderly:latest
```

## 🔍 Useful Commands

```bash
# List running containers
docker ps

# View container resources
docker stats folderly-app

# Access container filesystem
docker exec -it folderly-app ls /workspace

# Copy files to/from container
docker cp folderly-app:/workspace/Desktop ./local-desktop
```
