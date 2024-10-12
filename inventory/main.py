from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from redis_om import get_redis_connection, HashModel

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import redis

# Connect to Redis
redis = get_redis_connection(
  host="redis-17946.c305.ap-south-1-1.ec2.redns.redis-cloud.com",
  port=17946,
  password="vOYX1FzuG85IHXXPfBnPI4uPqcfwCA2C")

# Define a Redis-OM Product model
class ProductModel(HashModel):
    name: str
    price: float
    quantity: int

    class Meta:
        database = redis  # Connect to the Redis client


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:3000'],
    allow_methods=['*'],
    allow_headers=['*']
)


class Product(BaseModel):
    name: str
    price: float
    quantity: int


@app.post("/product")
async def create_product(product: Product):
    # Create a new ProductModel instance from the request body
    new_product = ProductModel(
        name=product.name,
        price=product.price,
        quantity=product.quantity,
    )

    # Save the product to Redis
    try:
        return new_product.save()
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving product: {e}")
    

@app.get('/products')
def all():
    return [pk for pk in ProductModel.all_pks()]

@app.get('/products/{pk}')
def get(pk: str):
  try:
    return ProductModel.get(pk)
  except Exception as e:
    raise HTTPException(status_code=404, detail=f"Product with id {pk} not found. Error: {str(e)}")



@app.delete('/products/{pk}')
def delete(pk: str):
  return ProductModel.delete(pk)

