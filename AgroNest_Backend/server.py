import uvicorn
from core.settings import settings
from core.app import get_app

def main() -> None:
    """Entrypoint of the application."""
    app = get_app()  # Get the FastAPI app instance
    uvicorn.run(
        "core.app:get_app",  # Use the import string of the app
        workers=settings.WORKERS_COUNT,
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
        factory=True,
    )

if __name__ == "__main__":
    main()
