import json 
from pathlib import Path
from typing import List,Dict
DATA_FILE = Path(__file__).parent.parent / "data"/ "dummy.json"

def loadProducts()-> List[Dict] :
    if not DATA_FILE.exists():
        return []
    with open(DATA_FILE,"r",encoding ="utf-8") as file :
        return json.load(file)

def getAllProducts()->List[Dict]:
    return loadProducts()

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
