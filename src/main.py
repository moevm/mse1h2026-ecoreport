import asyncio

from uvicorn import Config, Server

from reports.app import create_app
from reports.core.config import settings

app = create_app()

async def main():
    config = Config(
        "main:app",
        host="0.0.0.0",
        port=settings.APP_PORT,
        reload=True
    )

    server = Server(config)
    await server.serve()

if __name__ == "__main__":
    asyncio.run(main())
