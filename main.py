import uvicorn
from web.fastapi_app import app
from common.config.config import settings

if __name__ == "__main__":
    uvicorn.run(app, host=settings.server_host, port=settings.server_port)
