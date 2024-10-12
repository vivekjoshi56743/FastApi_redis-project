from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from redis_om import get_redis_connection, HashModel

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import redis



from fastapi.background import BackgroundTasks

from starlette.requests import Request
import time,requests

# Connect to Redis
redis = get_redis_connection(
  host="redis-17946.c305.ap-south-1-1.ec2.redns.redis-cloud.com",
  port=17946,
  password="vOYX1FzuG85IHXXPfBnPI4uPqcfwCA2C")

# Define a Redis-OM Product model
class OrderModel(HashModel):
    product_id: str
    price: float
    fee: float
    total: float
    quantity: int
    status: str  # pending, completed, refunded

    class Meta:
        database = redis  # Connect to the Redis client


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:3000'],
    allow_methods=['*'],
    allow_headers=['*']
)


class Order(BaseModel):
    product_id: str
    price: float
    fee: float
    total: float
    quantity: int
    status: str  # pending, completed, refunded

@app.get('/orders/{pk}')
def get(pk: str):
    return OrderModel.get(pk)


@app.post('/orders')
async def create(request: Request, background_tasks: BackgroundTasks):  # id, quantity
    body = await request.json()

    req = requests.get('http://localhost:8000/products/%s' % body['id'])
    product = req.json()

    order = OrderModel(
        product_id=body['id'],
        price=product['price'],
        fee=0.2 * product['price'],
        total=1.2 * product['price'],
        quantity=body['quantity'],
        status='pending'
    )
    order.save()

    background_tasks.add_task(order_completed, order)

    return order


def order_completed(order: OrderModel):
    time.sleep(5)
    order.status = 'completed'
    order.save()
    redis.xadd('order_completed', order.model_dump(), '*') 