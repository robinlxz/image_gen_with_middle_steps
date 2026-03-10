import os
import time
import requests
import uuid
import socket
import ipaddress
from urllib.parse import urlparse
from datetime import datetime

class StorageManager:
    def __init__(self, storage_type='local', base_dir='static/gallery', max_files=2000):
        self.storage_type = storage_type
        self.base_dir = base_dir
        self.max_files = max_files
        
        # Ensure the directory exists for local storage
        if self.storage_type == 'local':
            os.makedirs(self.base_dir, exist_ok=True)

    def save_image(self, image_url, metadata=None):
        """
        Downloads an image from a URL and saves it.
        Returns the public URL/path to access the saved image.
        """
        try:
            # Security Check: Prevent SSRF
            if not self._is_safe_url(image_url):
                print(f"Security Alert: Unsafe URL blocked: {image_url}")
                return None

            # Download the image
            # Set a timeout to prevent hanging
            response = requests.get(image_url, stream=True, timeout=10)
            response.raise_for_status()
            
            # Verify Content-Type is an image
            content_type = response.headers.get('Content-Type', '')
            if not content_type.startswith('image/'):
                print(f"Security Alert: Invalid Content-Type: {content_type}")
                return None
            
            # Generate a unique filename
            # Format: YYYYMMDD_HHMMSS_uuid.png
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_id = str(uuid.uuid4())[:8]
            filename = f"{timestamp}_{unique_id}.png"
            
            if self.storage_type == 'local':
                file_path = os.path.join(self.base_dir, filename)
                
                with open(file_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                # Cleanup old images if needed
                self._cleanup_local_storage()
                
                # Return the relative path for frontend use
                # Note: This assumes the base_dir is inside 'static/'
                return f"/{self.base_dir}/{filename}"
            
            elif self.storage_type == 'tos':
                # TODO: Implement TOS upload logic here
                # e.g., s3_client.upload_fileobj(...)
                # return s3_url
                pass
                
        except Exception as e:
            print(f"Error saving image: {e}")
            return None

    def _is_safe_url(self, url):
        """
        Validates the URL to prevent SSRF (Server-Side Request Forgery).
        Checks:
        1. Scheme is http or https
        2. Hostname resolves to a public IP address (not private/loopback)
        """
        try:
            parsed = urlparse(url)
            if parsed.scheme not in ('http', 'https'):
                return False
            
            hostname = parsed.hostname
            if not hostname:
                return False
                
            # Resolve hostname to IP addresses
            # This handles both IPv4 and IPv6
            try:
                # Use getaddrinfo to get all IPs associated with the hostname
                addr_info = socket.getaddrinfo(hostname, None)
            except socket.gaierror:
                return False # DNS resolution failed

            for res in addr_info:
                ip_str = res[4][0]
                try:
                    ip = ipaddress.ip_address(ip_str)
                    # Block private, loopback, and link-local addresses
                    if ip.is_private or ip.is_loopback or ip.is_link_local:
                        return False
                except ValueError:
                    continue # Skip invalid IPs
                    
            return True
            
        except Exception as e:
            print(f"URL validation error: {e}")
            return False

    def _cleanup_local_storage(self):
        """
        Maintains the number of files within the limit by deleting the oldest ones.
        """
        try:
            files = [os.path.join(self.base_dir, f) for f in os.listdir(self.base_dir) 
                     if f.endswith(('.png', '.jpg', '.jpeg'))]
            
            if len(files) > self.max_files:
                # Sort files by modification time (oldest first)
                files.sort(key=os.path.getmtime)
                
                # Delete excess files
                num_to_delete = len(files) - self.max_files
                for i in range(num_to_delete):
                    os.remove(files[i])
                    print(f"Deleted old image: {files[i]}")
                    
        except Exception as e:
            print(f"Error during cleanup: {e}")
