from fastapi import FastAPI, Request, Body
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

@app.api_route("/{service}/{path:path}", methods=[HTTPMethod.GET, HTTPMethod.POST])
async def generic_handler(request: Request, service: str, path: str):
    if service == "service-a":
        url = f"{settings.order_service_url}/order/{path}"
        try:
            body = await request.body()
            response = await client.request(
                method=request.method,
                url=url,
                headers=dict(request.headers),
                content=body
            )
            return JSONResponse(content=response.json(), status_code=response.status_code)
        except Exception as e:
            return JSONResponse(content={"exception": str(e)}, status_code=HTTPStatus.INTERNAL_SERVER_ERROR)
    else:
        return JSONResponse(content={"unknown service": f"{service}"}, status_code=HTTPStatus.BAD_REQUEST)