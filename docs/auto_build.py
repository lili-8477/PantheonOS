#!/usr/bin/env python
"""
Automatic documentation builder with file watching.
Fixed version with reliable file watching using polling observer.
"""

import os
import sys
import time
import subprocess
import threading
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
from functools import partial

try:
    from watchdog.observers import Observer
    from watchdog.observers.polling import PollingObserver
    from watchdog.events import FileSystemEventHandler
except ImportError:
    print("Installing watchdog...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "watchdog"])
    from watchdog.observers import Observer
    from watchdog.observers.polling import PollingObserver
    from watchdog.events import FileSystemEventHandler


class DocBuilder(FileSystemEventHandler):
    def __init__(self):
        self.last_build_time = 0
        self.build_lock = threading.Lock()
        self.pending_build = False
        self.min_build_interval = 2.0  # Minimum seconds between builds
        self.build_timer = None
        
    def on_modified(self, event):
        """Only respond to actual file modifications."""
        if event.is_directory:
            return
        self._handle_change(event)
    
    def on_created(self, event):
        """Respond to new files being created."""
        if event.is_directory:
            return
        self._handle_change(event)
    
    def on_deleted(self, event):
        """Respond to files being deleted."""
        if event.is_directory:
            return
        self._handle_change(event)
    
    def _handle_change(self, event):
        """Common handler for file changes."""
        # Check file extension
        path = Path(event.src_path)
        valid_extensions = {'.rst', '.md', '.py', '.css', '.js', '.yml', '.yaml'}
        if path.suffix not in valid_extensions:
            return
            
        # Ignore certain paths
        ignore_patterns = {
            '__pycache__', '.git', 'build', '.pyc', '.pyo', 
            '~', '.swp', '.tmp', '.doctrees', '_build'
        }
        
        path_str = str(path).lower()
        if any(pattern in path_str for pattern in ignore_patterns):
            return
            
        print(f"📝 Change detected: {event.event_type} - {path.name}")
        self.schedule_build()
        
    def schedule_build(self):
        """Schedule a build with debouncing."""
        # Cancel any existing timer
        if self.build_timer:
            self.build_timer.cancel()
            
        self.pending_build = True
        self.build_timer = threading.Timer(1.0, self.build_if_needed)
        self.build_timer.start()
        
    def build_if_needed(self):
        if not self.pending_build:
            return
            
        with self.build_lock:
            if not self.pending_build:
                return
                
            self.pending_build = False
            self.build()
            
    def build(self):
        # Check if enough time has passed since last build
        current_time = time.time()
        if current_time - self.last_build_time < self.min_build_interval:
            return
            
        self.last_build_time = current_time
        print("🔨 Building documentation...")
        start_time = time.time()
        
        try:
            # Try to find sphinx-build
            sphinx_cmd = None
            
            # Try direct sphinx-build command first
            try:
                result = subprocess.run(['sphinx-build', '--version'], 
                                      capture_output=True)
                if result.returncode == 0:
                    sphinx_cmd = ['sphinx-build']
            except FileNotFoundError:
                pass
            
            # Try Python module
            if not sphinx_cmd:
                try:
                    result = subprocess.run([sys.executable, '-m', 'sphinx', '--version'], 
                                          capture_output=True)
                    if result.returncode == 0:
                        sphinx_cmd = [sys.executable, '-m', 'sphinx']
                except:
                    pass
            
            if not sphinx_cmd:
                print("❌ Could not find sphinx-build. Please install sphinx.")
                return
            
            # Build command
            cmd = sphinx_cmd + [
                '-b', 'html',
                '-d', 'build/doctrees',
                'source',
                'build/html'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            elapsed = time.time() - start_time
            
            if result.returncode == 0:
                print(f"✅ Build successful! ({elapsed:.2f}s)")
            else:
                print(f"❌ Build failed! ({elapsed:.2f}s)")
                if result.stderr:
                    print("Errors:")
                    print(result.stderr)
                if result.stdout and 'warning' in result.stdout.lower():
                    print("Warnings:")
                    # Show only first few warnings
                    lines = result.stdout.split('\n')
                    warning_lines = [l for l in lines if 'warning' in l.lower()][:5]
                    for line in warning_lines:
                        print(f"  {line}")
                    
        except Exception as e:
            print(f"❌ Build error: {e}")


def run_server(directory, port=8080):
    """Run a simple HTTP server in a separate thread."""
    class QuietHandler(SimpleHTTPRequestHandler):
        def log_message(self, format, *args):
            pass  # Suppress logs
            
    handler = partial(QuietHandler, directory=directory)
    httpd = HTTPServer(('127.0.0.1', port), handler)
    print(f"🌐 Serving docs at http://127.0.0.1:{port}")
    httpd.serve_forever()


def main():
    # Change to docs directory if needed
    if Path('source').exists() and Path('Makefile').exists():
        pass  # Already in docs directory
    elif Path('docs/source').exists():
        os.chdir('docs')
    else:
        print("❌ Cannot find documentation source directory")
        sys.exit(1)
        
    print("🚀 Pantheon Documentation Auto-Builder")
    print("=" * 50)
    
    # Initial build
    builder = DocBuilder()
    builder.build()
    
    # Start web server in background
    server_thread = threading.Thread(
        target=run_server, 
        args=('build/html', 8080),
        daemon=True
    )
    server_thread.start()
    
    # Detect if we should use polling observer
    # Use polling for Docker, WSL, network filesystems, or if explicitly requested
    use_polling = (
        os.environ.get('FORCE_POLLING', '').lower() in ('1', 'true', 'yes') or
        os.path.exists('/.dockerenv') or  # Docker
        'microsoft' in os.uname().release.lower() or  # WSL
        os.environ.get('USE_POLLING_OBSERVER', '').lower() in ('1', 'true', 'yes')
    )
    
    # Set up file watching
    if use_polling:
        print("📊 Using polling observer (more reliable for virtual filesystems)")
        observer = PollingObserver()
        observer.timeout = 1  # Poll every second
    else:
        print("📊 Using native file system observer")
        observer = Observer()
    
    # Watch source directory
    observer.schedule(builder, 'source', recursive=True)
    print("👀 Watching: source/")
    
    # Watch Python source if available
    if Path('../pantheon').exists():
        observer.schedule(builder, '../pantheon', recursive=True)
        print("👀 Watching: ../pantheon/")
        
    observer.start()
    
    print("\n✨ Ready! The docs will rebuild automatically on changes.")
    print("💡 Tip: Edit any .rst or .md file to trigger a rebuild")
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