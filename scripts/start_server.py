#!/usr/bin/env python3
import sys
import subprocess
from pathlib import Path


def main():
    """Start the Cursor Clone service"""
    # Add project root to Python path
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))

    # Import and run
    try:
        from src.main import app
        import uvicorn
        from config.settings import settings

        print(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
        print(f"Server running on http://{settings.HOST}:{settings.PORT}")

        uvicorn.run(
            "src.main:app",
            host=settings.HOST,
            port=settings.PORT,
            workers=settings.WORKERS if not settings.DEBUG else 1,
            reload=settings.DEBUG,
            log_level=settings.LOG_LEVEL.lower()
        )

    except KeyboardInterrupt:
        print("\nShutting down server...")
    except Exception as e:
        print(f"Failed to start server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
