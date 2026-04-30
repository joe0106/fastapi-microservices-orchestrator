from fastapi import FastAPI
from fastapi.responses import JSONResponse
from http import HTTPMethod, HTTPStatus
from .settings.config import settings as config
import httpx

settings = config
client = httpx.AsyncClient()

app = FastAPI()

@app.get("/info")
def sysinfo():
    return JSONResponse(content={"app_mode": settings.app_mode})

@app.api_route("/{service}/{path}", methods=[HTTPMethod.GET])
async def generic_handler(service: str, path: str):
    if service == "service-a":
        url = f"{settings.order_service_url}/order/{path}"
        try:
            response = await client.get(url=url)
            return JSONResponse(content=response.json(), status_code=response.status_code)
        except Exception as e:
            return JSONResponse(content={"exception": str(e)}, status_code=HTTPStatus.INTERNAL_SERVER_ERROR)
    else:
        return JSONResponse(content={"unknown service": f"{service}"}, status_code=HTTPStatus.BAD_REQUEST)