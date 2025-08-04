#!/usr/bin/env python
"""
Fixed automatic documentation builder with reliable file watching.
Uses polling observer for better compatibility across different file systems.
"""

import os
import sys
import time
import subprocess
import threading
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
from functools import partial
import hashlib
import json

try:
    from watchdog.observers.polling import PollingObserver
    from watchdog.events import FileSystemEventHandler
except ImportError:
    print("Installing watchdog...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "watchdog"])
    from watchdog.observers.polling import PollingObserver
    from watchdog.events import FileSystemEventHandler


class FileHashCache:
    """Cache file hashes to detect real changes."""
    def __init__(self, cache_file='.build_cache.json'):
        self.cache_file = cache_file
        self.hashes = self.load_cache()
    
    def load_cache(self):
        """Load hash cache from file."""
        if Path(self.cache_file).exists():
            try:
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {}
    
    def save_cache(self):
        """Save hash cache to file."""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.hashes, f)
        except:
            pass
    
    def get_file_hash(self, filepath):
        """Calculate hash of file contents."""
        try:
            with open(filepath, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except:
            return None
    
    def has_changed(self, filepath):
        """Check if file has actually changed."""
        filepath = str(filepath)
        current_hash = self.get_file_hash(filepath)
        if current_hash is None:
            return False
        
        old_hash = self.hashes.get(filepath)
        if old_hash != current_hash:
            self.hashes[filepath] = current_hash
            self.save_cache()
            return True
        return False


class ReliableDocBuilder(FileSystemEventHandler):
    def __init__(self):
        self.last_build_time = 0
        self.build_lock = threading.Lock()
        self.pending_files = set()
        self.min_build_interval = 2.0  # Increased for stability
        self.hash_cache = FileHashCache()
        self.build_timer = None
        print("🔧 Initialized with reliable file watching")
        
    def on_modified(self, event):
        """Handle file modifications."""
        if event.is_directory:
            return
        self._handle_change(event)
    
    def on_created(self, event):
        """Handle file creation."""
        if event.is_directory:
            return
        self._handle_change(event)
    
    def _handle_change(self, event):
        """Process file changes with proper filtering."""
        path = Path(event.src_path)
        
        # Check file extension
        valid_extensions = {'.rst', '.md', '.py', '.css', '.js', '.yml', '.yaml', '.html'}
        if path.suffix not in valid_extensions:
            return
            
        # Ignore patterns
        ignore_patterns = {
            '__pycache__', '.git', 'build', '.pyc', '.pyo', 
            '~', '.swp', '.tmp', '.doctrees', '_build', '.cache'
        }
        
        path_str = str(path).lower()
        if any(pattern in path_str for pattern in ignore_patterns):
            return
        
        # Check if file actually changed (content-based)
        if not self.hash_cache.has_changed(path):
            return
            
        print(f"📝 Change detected: {path.name}")
        self.pending_files.add(str(path))
        self.schedule_build()
        
    def schedule_build(self):
        """Schedule a build with debouncing."""
        # Cancel existing timer
        if self.build_timer:
            self.build_timer.cancel()
        
        # Schedule new build
        self.build_timer = threading.Timer(1.0, self.build_if_needed)
        self.build_timer.start()
        
    def build_if_needed(self):
        """Build if there are pending changes."""
        if not self.pending_files:
            return
            
        with self.build_lock:
            if not self.pending_files:
                return
            
            # Get list of changed files
            changed_files = list(self.pending_files)
            self.pending_files.clear()
            
            print(f"📋 Building due to {len(changed_files)} file change(s)")
            self.build()
            
    def build(self):
        """Execute the documentation build."""
        current_time = time.time()
        if current_time - self.last_build_time < self.min_build_interval:
            remaining = self.min_build_interval - (current_time - self.last_build_time)
            print(f"⏳ Waiting {remaining:.1f}s before next build...")
            time.sleep(remaining)
            
        self.last_build_time = time.time()
        print("🔨 Building documentation...")
        start_time = time.time()
        
        # Clear terminal for cleaner output
        print("\033[2J\033[H")  # Clear screen and move cursor to top
        print("🔨 Building documentation...")
        
        try:
            # Find sphinx-build command
            sphinx_cmd = None
            for cmd in ['sphinx-build', 'python -m sphinx', f'{sys.executable} -m sphinx']:
                if subprocess.run(cmd.split() + ['--version'], 
                                capture_output=True).returncode == 0:
                    sphinx_cmd = cmd.split()
                    break
            
            if not sphinx_cmd:
                print("❌ Could not find sphinx-build command")
                return
            
            # Build command
            cmd = sphinx_cmd + [
                '-b', 'html',
                '-d', 'build/doctrees',
                '-W', '--keep-going',  # Warnings as errors but continue
                'source',
                'build/html'
            ]
            
            # Run build
            result = subprocess.run(cmd, capture_output=True, text=True)
            elapsed = time.time() - start_time
            
            if result.returncode == 0:
                print(f"✅ Build successful! ({elapsed:.2f}s)")
                print(f"📁 Docs available at: http://127.0.0.1:8080")
            else:
                print(f"⚠️  Build completed with warnings ({elapsed:.2f}s)")
                if result.stderr:
                    print("\nWarnings/Errors:")
                    # Only show first few lines of errors
                    error_lines = result.stderr.strip().split('\n')[:10]
                    for line in error_lines:
                        print(f"  {line}")
                    if len(result.stderr.strip().split('\n')) > 10:
                        print("  ... (more warnings hidden)")
                        
        except Exception as e:
            print(f"❌ Build error: {e}")


def run_server(directory, port=8080):
    """Run HTTP server silently."""
    class QuietHTTPHandler(SimpleHTTPRequestHandler):
        def log_message(self, format, *args):
            pass  # Suppress request logs
    
    handler = partial(QuietHTTPHandler, directory=directory)
    httpd = HTTPServer(('127.0.0.1', port), handler)
    print(f"🌐 Serving docs at http://127.0.0.1:{port}")
    httpd.serve_forever()


def main():
    # Change to docs directory if needed
    if Path('source').exists() and Path('Makefile').exists():
        pass
    elif Path('docs/source').exists():
        os.chdir('docs')
    else:
        print("❌ Cannot find documentation source directory")
        sys.exit(1)
        
    print("🚀 Pantheon Documentation Auto-Builder")
    print("=" * 50)
    
    # Initial build
    builder = ReliableDocBuilder()
    builder.build()
    
    # Start web server
    server_thread = threading.Thread(
        target=run_server, 
        args=('build/html', 8080),
        daemon=True
    )
    server_thread.start()
    
    # Use polling observer for reliability
    observer = PollingObserver()
    observer.timeout = 1  # Poll every second
    
    # Watch directories
    observer.schedule(builder, 'source', recursive=True)
    print("👀 Watching: source/")
    
    # Also watch static files
    if Path('source/_static').exists():
        observer.schedule(builder, 'source/_static', recursive=True)
    
    observer.start()
    
    print("\n✨ Ready! Docs will rebuild automatically on file changes.")
    print("💡 Tip: Make a change to any .rst, .md, or .py file to test")
    print("Press Ctrl+C to stop\n")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 Stopping...")
        observer.stop()
        
    observer.join()


if __name__ == '__main__':
    main()