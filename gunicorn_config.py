import multiprocessing

# Bind to all interfaces (for ECS)
# Using 80 as requested to bypass potential firewall issues on 8080
bind = "0.0.0.0:80"

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
