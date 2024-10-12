from main import redis,ProductModel
import time
from fastapi import HTTPException

key="order_completed"
group="inventory-group"

try:
    redis.xgroup_create(key,group)
except:
    print("group alreday exits")

while True:
    try:
        results=redis.xreadgroup(group,key,{key: '>'},None)
        print(results)
        if results != []:
            for result in results:
                obj = result[1][0][1]
                print(obj)
                try:
                    product = ProductModel.get(obj['product_id'])
                    product.quantity = product.quantity - int(obj['quantity'])
                    product.save()
                except Exception as e:
                    raise HTTPException(status_code=404, detail=f"Error: {str(e)}")
                    
    except Exception as e:
        print(e)
    time.sleep(2)

