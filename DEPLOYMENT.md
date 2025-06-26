# Railway Deployment Guide

## Overview
This Flask application is configured for deployment on Railway with Docker. The app provides file conversion services using Pandoc and supports various input/output formats.

## Configuration Files

### Dockerfile
- Uses Python 3.9 slim image
- Installs Pandoc and LaTeX dependencies for PDF support
- Uses Railway's `$PORT` environment variable
- Binds to `0.0.0.0` for production deployment

### railway.json
- Uses Dockerfile builder
- Configures health check endpoint (`/health`)
- Sets restart policy for reliability
- Uses Railway's `$PORT` environment variable

### Procfile
- Alternative deployment method (not used with Dockerfile)
- Uses Gunicorn WSGI server

## Deployment Steps

1. **Push to Railway**: Connect your repository to Railway
2. **Automatic Build**: Railway will use the Dockerfile to build the container
3. **Environment Variables**: Railway automatically sets the `PORT` environment variable
4. **Health Check**: Railway monitors the `/health` endpoint

## Troubleshooting

### Common Issues

1. **Port Binding Issues**
   - Ensure the app uses `$PORT` environment variable
   - Bind to `0.0.0.0` not `127.0.0.1`

2. **Missing Dependencies**
   - Pandoc and LaTeX are installed in the Dockerfile
   - Check `/health` endpoint for dependency status

3. **File Upload Issues**
   - Ensure `uploads` and `output` directories exist
   - Check file permissions

### Testing Deployment

Run the test script locally to verify configuration:
```bash
cd backend
python deploy_test.py
```

### Health Check Endpoint

The `/health` endpoint provides:
- Application status
- Pandoc availability
- Pandoc version information

### Logs

Check Railway logs for:
- Application startup messages
- Gunicorn worker status
- Error messages

## Environment Variables

- `PORT`: Set by Railway automatically
- `FLASK_ENV`: Set to "production" in Railway

## Supported Formats

### Input Formats
- Document: docx, doc, odt, rtf
- Web: html, htm
- Text: txt, md, markdown
- Technical: tex, latex, rst, asciidoc
- E-book: epub, mobi, fb2
- Other: opml, org, mediawiki, dokuwiki, textile, man, ms

### Output Formats
- Markdown: gfm, markdown
- Web: html
- Document: docx, odt, rtf
- Technical: latex, pdf
- E-book: epub

## API Endpoints

- `GET /`: Basic status message
- `GET /health`: Health check with dependency status
- `POST /convert`: File conversion endpoint
  - Accepts multipart form data with files
  - Returns ZIP file with converted documents 