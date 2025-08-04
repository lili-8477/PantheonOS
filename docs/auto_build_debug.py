#!/usr/bin/env python
"""
Debug version of auto_build.py to diagnose file watching issues.
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
    from watchdog.events import FileSystemEventHandler
    from watchdog.observers.polling import PollingObserver
except ImportError:
    print("Installing watchdog...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "watchdog"])
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    from watchdog.observers.polling import PollingObserver


class DebugDocBuilder(FileSystemEventHandler):
    def __init__(self):
        self.last_build_time = 0
        self.build_lock = threading.Lock()
        self.pending_build = False
        self.min_build_interval = 1.0
        self.event_count = 0
        print("🔍 Debug mode enabled - will log all events")
        
    def on_any_event(self, event):
        """Log all events for debugging."""
        self.event_count += 1
        print(f"📌 Event #{self.event_count}: {event.event_type} on {event.src_path}")
        print(f"   Is directory: {event.is_directory}")
        
        # Call specific handler
        if hasattr(self, f'on_{event.event_type}'):
            getattr(self, f'on_{event.event_type}')(event)
    
    def on_modified(self, event):
        """Only respond to actual file modifications."""
        if event.is_directory:
            print("   → Ignoring directory modification")
            return
        self._handle_change(event)
    
    def on_created(self, event):
        """Respond to new files being created."""
        if event.is_directory:
            print("   → Ignoring directory creation")
            return
        self._handle_change(event)
    
    def on_deleted(self, event):
        """Respond to files being deleted."""
        if event.is_directory:
            print("   → Ignoring directory deletion")
            return
        self._handle_change(event)
    
    def _handle_change(self, event):
        """Common handler for file changes."""
        path = Path(event.src_path)
        print(f"   → Processing change for: {path}")
        print(f"   → File suffix: {path.suffix}")
        
        # Check file extension
        valid_extensions = ['.rst', '.md', '.py', '.css', '.js', '.yml', '.yaml']
        if path.suffix not in valid_extensions:
            print(f"   → Ignoring due to extension (not in {valid_extensions})")
            return
            
        # Ignore certain paths
        ignore_patterns = ['__pycache__', '.git', 'build', '.pyc', '.pyo', '~', '.swp', '.tmp', '.doctrees']
        for pattern in ignore_patterns:
            if pattern in str(path):
                print(f"   → Ignoring due to pattern: {pattern}")
                return
            
        # Ignore build directory changes
        if 'build' in path.parts:
            print("   → Ignoring build directory change")
            return
            
        print(f"✅ Valid change detected: {event.event_type} - {path}")
        self.schedule_build()
        
    def schedule_build(self):
        print("📅 Scheduling build...")
        self.pending_build = True
        threading.Timer(0.5, self.build_if_needed).start()
        
    def build_if_needed(self):
        if not self.pending_build:
            print("❌ Build cancelled - no pending build")
            return
            
        with self.build_lock:
            if not self.pending_build:
                print("❌ Build cancelled - no pending build (after lock)")
                return
                
            self.pending_build = False
            self.build()
            
    def build(self):
        # Check if enough time has passed since last build
        current_time = time.time()
        time_since_last = current_time - self.last_build_time
        if time_since_last < self.min_build_interval:
            print(f"⏳ Skipping build - only {time_since_last:.2f}s since last build")
            return
            
        self.last_build_time = current_time
        print("🔨 Building documentation...")
        start_time = time.time()
        
        try:
            # Try different sphinx commands
            sphinx_commands = [
                [sys.executable, '-m', 'sphinx.cmd.build'],
                [sys.executable, '-m', 'sphinx'],
                ['sphinx-build']
            ]
            
            result = None
            for cmd in sphinx_commands:
                try:
                    full_cmd = cmd + ['-b', 'html', '-d', 'build/doctrees', 'source', 'build/html']
                    print(f"   → Trying command: {' '.join(full_cmd)}")
                    result = subprocess.run(full_cmd, capture_output=True, text=True)
                    if result.returncode == 0:
                        break
                except FileNotFoundError:
                    continue
            
            elapsed = time.time() - start_time
            
            if result and result.returncode == 0:
                print(f"✅ Build successful! ({elapsed:.2f}s)")
            else:
                print(f"❌ Build failed! ({elapsed:.2f}s)")
                if result:
                    if result.stderr:
                        print("Errors:")
                        print(result.stderr)
                    if result.stdout:
                        print("Output:")
                        print(result.stdout)
                    
        except Exception as e:
            print(f"❌ Build error: {e}")
            import traceback
            traceback.print_exc()


def run_server(directory, port=8080):
    """Run a simple HTTP server in a separate thread."""
    handler = partial(SimpleHTTPRequestHandler, directory=directory)
    httpd = HTTPServer(('127.0.0.1', port), handler)
    print(f"🌐 Serving docs at http://127.0.0.1:{port}")
    httpd.serve_forever()


def main():
    # Print current working directory
    print(f"📁 Current directory: {os.getcwd()}")
    
    # Change to docs directory if needed
    if Path('source').exists() and Path('Makefile').exists():
        print("✅ Already in docs directory")
    elif Path('docs/source').exists():
        os.chdir('docs')
        print(f"📁 Changed to docs directory: {os.getcwd()}")
    else:
        print("❌ Cannot find documentation source directory")
        print(f"   Looking for 'source' in: {os.getcwd()}")
        print(f"   Directory contents: {list(Path('.').iterdir())}")
        sys.exit(1)
        
    print("🚀 Pantheon Documentation Auto-Builder (Debug Mode)")
    print("=" * 50)
    
    # Check if source directory exists and list contents
    source_path = Path('source')
    if source_path.exists():
        print(f"📂 Source directory contents: {len(list(source_path.rglob('*')))} files")
        print("   Sample files:")
        for i, f in enumerate(source_path.rglob('*.rst')):
            if i >= 5:
                break
            print(f"     - {f}")
    
    # Initial build
    builder = DebugDocBuilder()
    builder.build()
    
    # Start web server in background
    server_thread = threading.Thread(
        target=run_server, 
        args=('build/html', 8080),
        daemon=True
    )
    server_thread.start()
    
    # Try different observer types
    print("\n🔍 Setting up file watching...")
    
    # Check if we're on a network filesystem or Docker
    use_polling = False
    if os.environ.get('FORCE_POLLING_OBSERVER', '').lower() in ('1', 'true', 'yes'):
        use_polling = True
        print("⚠️  Forcing polling observer due to environment variable")
    elif Path('/proc/mounts').exists():
        with open('/proc/mounts', 'r') as f:
            mounts = f.read()
            if 'nfs' in mounts or 'cifs' in mounts:
                use_polling = True
                print("⚠️  Detected network filesystem, using polling observer")
    
    if use_polling:
        observer = PollingObserver()
        print("📊 Using PollingObserver (slower but more reliable)")
    else:
        observer = Observer()
        print("📊 Using standard Observer")
    
    # Watch source directory
    watch_path = str(source_path.absolute())
    observer.schedule(builder, watch_path, recursive=True)
    print(f"👀 Watching: {watch_path}")
    
    # Watch Python source if available
    pantheon_path = Path('../pantheon')
    if pantheon_path.exists():
        watch_path2 = str(pantheon_path.absolute())
        observer.schedule(builder, watch_path2, recursive=True)
        print(f"👀 Watching: {watch_path2}")
        
    observer.start()
    
    print("\n✨ Ready! The docs will rebuild automatically on changes.")
    print("💡 Debug mode: All file system events will be logged")
    print("Press Ctrl+C to stop\n")
    
    # Create a test file to verify watching works
    test_file = source_path / '_test_watch.rst'
    print("🧪 Creating test file to verify file watching...")
    test_file.write_text("Test")
    time.sleep(1)
    test_file.unlink()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 Stopping...")
        observer.stop()
        
    observer.join()


if __name__ == '__main__':
    main()