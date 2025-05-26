#!/usr/bin/env python3
"""
Worker with HTTP health check server for Cloud Run compatibility.
Runs both Celery worker and a simple HTTP server for health checks.
"""
import asyncio
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
import structlog
from celery import Celery
from apps.workers.celery_app import celery_app

logger = structlog.get_logger()

class HealthHandler(BaseHTTPRequestHandler):
    """Simple HTTP handler for health checks."""
    
    def do_GET(self):
        if self.path in ['/health', '/healthz', '/']:
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status": "healthy", "service": "worker"}')
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        # Suppress default HTTP server logs
        pass

def run_health_server(port=8080):
    """Run a simple HTTP health check server."""
    server = HTTPServer(('0.0.0.0', port), HealthHandler)
    logger.info(f"Health server starting on port {port}")
    server.serve_forever()

def run_celery_worker():
    """Run the Celery worker."""
    logger.info("Starting Celery worker")
    # Run celery worker with proper arguments
    celery_app.worker_main([
        'worker',
        '--loglevel=info',
        '--concurrency=2',
        '--queues=default,ingestion,ai'
    ])

def main():
    """Main entry point that runs both HTTP server and Celery worker."""
    logger.info("Starting worker with health server")
    
    # Start health server in a separate thread
    health_thread = threading.Thread(target=run_health_server, daemon=True)
    health_thread.start()
    
    # Give the health server a moment to start
    time.sleep(1)
    
    # Run Celery worker in the main thread
    try:
        run_celery_worker()
    except KeyboardInterrupt:
        logger.info("Worker shutting down")

if __name__ == "__main__":
    main() 