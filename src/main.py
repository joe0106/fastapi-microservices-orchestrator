from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from http import HTTPMethod

METHODS = [HTTPMethod.GET, HTTPMethod.POST, HTTPMethod.PUT, HTTPMethod.DELETE]

app = FastAPI()

@app.get("/")
def hello_world():
    return {"Hello": "world"}

@app.api_route("/{service}/{path}", methods=METHODS)
async def generic_handler(service: str, path: str):
    if service == "service-a":
        return RedirectResponse(url=f"/service-a/auth/{path}")
    return {
        "unknown service": f"/{service}/{path}"
    }

@app.get("/service-a/auth/{path}")
def service_a(path: str):
    return {
        "service_a path": f"{path}"
    }