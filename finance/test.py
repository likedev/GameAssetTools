from fastapi import FastAPI
from pydantic import BaseModel, Field
import time
import asyncio

app = FastAPI()


# 定义请求模型
class Item(BaseModel):
    name: str = Field(..., max_length=3)
    description: str = None
    price: float
    tax: float = None


# 异步函数示例
@app.post("/async")
async def async_endpoint(item: Item):
    await asyncio.sleep(2)  # 模拟一个耗时的异步操作
    return {"message": "Finished async", "item": item}


# 同步函数示例
@app.post("/sync")
def sync_endpoint(item: Item):
    time.sleep(2)  # 模拟一个耗时的同步操作
    return {"message": "Finished sync", "item": item}


# 运行应用程序
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
