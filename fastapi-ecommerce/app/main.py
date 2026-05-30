#import fastapi httpexpection query are classes we import from fastapi
from fastapi import FastAPI , HTTPException , Query , Path
# since i have python version < 3.10 it doesnt support union type syntax(|) 
from typing import Optional
# to connect product.py to main.py so we can call the functions written in other file 
from service.product import getAllProducts , addProducts , removeProduct , changeProduct
from schemas.product import Product , ProductUpdate
from uuid import uuid4 , UUID
from datetime import datetime

# create an instance(object - app) from FastAPI class
app = FastAPI()

# what happens in url ends with / simplest get request
@app.get("/")
def root():
    return {"message" :" welcome to fastapi"}

# returns all products
# @app.get("/products")
# def getProducts():
#     return getAllProducts()

#path parameter dynamic + validation using Path
@app.get("/products/{product_id}")
def getProductById(product_id:str = Path(...,
 min_length = 36 ,
 max_length= 36 ,
 description = "uuid of the product", 
 example = "8095d920-3554-49b8-b8f3-906c3b934dbe"
 )
):
    products = getAllProducts()
    for product in products :
        if product["id"] == product_id :
            return product 
    raise HTTPException(status_code = 404 , detail = "product not found")



#GET OPERATIONS
# using query we will filter the products on basis on name , by category(self) sort by order , limit & offset
@app.get("/products")
def listProducts(
    # name filter query
    name : Optional[str] = Query(
        default = None ,
        min_length = 1 ,
        max_length = 50,
        description ="search for product name (case insensitive)",
    ),
    #category filter query
    category : Optional[str] = Query(
        default = None ,
        max_length = 50 ,
        description=" search for the product by category ",
    ),
    # sort query if sortByPrice = true
    sortByPrice : bool = Query(
        default = False,
        description = "sort product by price",
    ),
    # if upper true then order specify - asc ,desc
    order : str = Query(
        default = 'asc',
        pattern = "^(asc|desc)$",
        description = "sort product by sortByPrice is true (asc,desc)",
    ),
    # limit of products shown in display
    limit : int = Query(
        default = 10 ,
        ge = 1 ,
        le = 100,
        description = "no. of items to return "
    ),
    # how many products visible in one page
    offset : int = Query(
        default = 0 , 
        ge = 0 ,
        description = "pagination"
    )
):
    products = getAllProducts()
    # name =filter specified then normalise to make it case non case sensitive
    if name :
        nameNormalized = name.strip().lower()
        products = [p for p in products if nameNormalized in p.get("name","").lower()]
    if category:
        categoryNormalized = category.strip().lower() # case insensitive
        products = [p for p in products if categoryNormalized in p.get("category","").lower()]
     # if not found then exception handeling for both name and cateogory combined
    if (name or category) and not products:
        raise HTTPException(
            status_code = 404 , detail = "no product found matching filters"
        )
    # sort functionn
    if sortByPrice :
        reverse =  order == "desc"
        products = sorted(products,key=lambda p : p.get("price",0),reverse = reverse)
    total = len(products)
    # limit + offset
    products = products[offset: offset+limit]
    return {"total" : total,"limit" : limit , "items" : products}

#POST OPERATIONS 
@app.post("/products",status_code=201)
def createProducts(product:Product):
    product_dict = product.model_dump(mode="json")
    product_dict["id"] = str(uuid4())
    product_dict["created_at"] = datetime.utcnow().isoformat() + "Z"
    try :
        addProducts(product_dict)
    except ValueError as e :
        raise HTTPException(status_code = 400 , detail = str(e))
    return product.model_dump(mode = "json") 

# DELETE OPERATIONS 
@app.delete("/products/{product_id}")
def deleteProduct(
    product_id: UUID = Path(...,description="product uuid")):
    try : 
        res = removeProduct(str(product_id))
        return res
    except Exception as e :
        raise HTTPException(status_code = 400 , detail = str(e))

#UPDATE OPERATIONS 
@app.put("/products/{product_id}")
def updateProduct(
    product_id : UUID = Path(...,description= "product UUID"),
    payload : ProductUpdate = ...
):
    try:
        updatedProduct = changeProduct(
            str(product_id),
            payload.model_dump(
                mode= "json",
                exclude_unset = True
            )
        )
        return updatedProduct
    except ValueError as e:
        raise HTTPException(
            status_code = 404,
            detail=str(e)
        )


