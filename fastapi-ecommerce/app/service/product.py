import json 
from pathlib import Path
from typing import List,Dict
DATA_FILE = Path(__file__).parent.parent / "data"/ "products.json"

# functions to read products

def loadProducts()-> List[Dict] :
    if not DATA_FILE.exists():
        return []
    with open(DATA_FILE,"r",encoding ="utf-8") as file :
        return json.load(file)

def getAllProducts()->List[Dict]:
    return loadProducts()

#functions to help create products

def saveProducts(products:List[Dict])->None:
    with open(DATA_FILE , "w" , encoding ="utf-8") as f :
        json.dump(products , f ,indent = 2 , ensure_ascii = False)

def addProducts(product : Dict)->Dict :
    products = getAllProducts()
    if any (p["sku"] == product["sku"] for p in products):
        raise ValueError("SKU already exists")
    products.append(product)
    saveProducts(products)
    return product
 
# function to delete product

def removeProduct(id :str)->str:
    products = getAllProducts()
    for idx , p in enumerate(products):
        if p["id"] == str(id):
            deleted = products.pop(idx)
            saveProducts(products)
            return{"message" : "product deleted successfully", "data" : deleted}
        raise ValueError("Product not found")
    
# functions to update products
def changeProduct(product_id : str , updateData : dict) -> dict:
    products = getAllProducts();
    #find product 
    for idx , p in enumerate(products):
        if p["id"] == str(product_id):
            for key , value in updateData.items():
                if value is None :
                    continue 
                #nested dictionary field update
                if isinstance(value , dict) and isinstance(p.get(key),dict):
                    p[key].update(value)
                #normal field update
                else:
                    p[key]= value
            #replace old product with new updated
            products[idx]= p
            #save back to json files
            saveProducts(products)
            return p 
        #not found raise error
        raise ValueError(" the product you want to update wasnt found")

  