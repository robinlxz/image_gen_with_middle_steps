import multiprocessing

# Bind to all interfaces (for ECS)
# Using 8080 as verified it works now
bind = "0.0.0.0:8080"

# Worker processes (usually 2 * CPU + 1)
# For a small ECS instance (2 vCPU), 3-4 workers is good.
workers = 3

# Timeout for long-running image generation tasks
# Image generation can take time, so we increase this from default 30s
timeout = 120

# Logging
accesslog = "-"  # Log to stdout
errorlog = "-"   # Log to stderr
loglevel = "info"
