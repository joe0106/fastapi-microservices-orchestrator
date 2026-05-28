from fastapi import FastAPI, Request, Body
from fastapi.responses import JSONResponse
from http import HTTPMethod, HTTPStatus
from settings.config import settings as config
import httpx

settings = config
client = httpx.AsyncClient()

app = FastAPI()

@app.get("/info")
def sysinfo():
    return JSONResponse(content={"app_mode": settings.app_mode})

async def proxy_request(request: Request, url: str, body: any = None):
    exclude_headers = ["host", "content-length"]
    headers = {k: v for k, v in request.headers.items() if k.lower() not in exclude_headers}
    
    try:
        response = await client.request(
                method=request.method,
                url=url,
                headers=headers,
                content= await request.body() if not body else None,
                json=body if isinstance(body, dict) else None,
                timeout=10
            )
        return JSONResponse(content=response.json(), status_code=response.status_code, headers=response.headers)
    except Exception as e:
        return JSONResponse(content={"exception": str(e)}, status_code=HTTPStatus.INTERNAL_SERVER_ERROR)

@app.get("/{service}/{path:path}")
async def generic_handler(request: Request, service: str, path: str):
    if service in settings.service_map().keys():
        url = settings.build_url(service, path)
        try:
            return await proxy_request(request, url)
        except Exception as e:
            return JSONResponse(content={"exception": str(e)}, status_code=HTTPStatus.INTERNAL_SERVER_ERROR)
    else:
        return JSONResponse(content={"unknown service": f"{service}"}, status_code=HTTPStatus.BAD_REQUEST)
    
@app.post("/{service}/{path:path}")
async def generic_handler(request: Request, service: str, path: str, body: dict = Body(None)):
    if service in settings.service_map().keys():
        url = settings.build_url(service, path)
        try:
            return await proxy_request(request, url, body)
        except Exception as e:
            return JSONResponse(content={"exception": str(e)}, status_code=HTTPStatus.INTERNAL_SERVER_ERROR)
    else:
        return JSONResponse(content={"unknown service": f"{service}"}, status_code=HTTPStatus.BAD_REQUEST)