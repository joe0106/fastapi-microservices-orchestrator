from fastapi import FastAPI

app = FastAPI()

@app.get("/order/{path}")
async def get_order(path: str):
    return {
        "path": f"path",
        "order_id": ["test001", "test002", "test003", "test004"],
    }

@app.post("/order")
async def new_order():
    return {
        "msg": "new order placed"
    }