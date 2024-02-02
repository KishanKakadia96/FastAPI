from fastapi import FastAPI, Path, Query
from typing import Optional
from pydantic import BaseModel
import uvicorn
import json

app = FastAPI()

class Item(BaseModel):
    name: str
    price: float
    brand: Optional[str] = None

class UpdateItem(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    brand: Optional[str] = None

# Function to load data from JSON file
def load_data():
    try:
        with open("inventory.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

# Function to save data to JSON file
def save_data(data):
    with open("inventory.json", "w") as file:
        json.dump(data, file, indent=2)

inventory = load_data()

@app.get("/get-item/{item_id}")
def get_item(item_id: int = Path(..., title="Item ID", description="The ID of the item you want to view")):
    if item_id not in inventory:
        return {"Error": "Item ID not found"}
    return inventory[item_id]

@app.get("/get-by-name/")
def get_item_by_name(name: str = Query(..., title="Name", description="Name of item.", max_length=10)):
    for item_id, item in inventory.items():
        if item["name"] == name:
            return {"ItemID": item_id, "ItemData": item}
    return {"Data": "Not found"}

@app.post("/create-item/{item_id}")
def create_item(item_id: int, item: Item):
    if item_id in inventory:
        return {"Error": "Item ID already exists."}

    inventory[item_id] = item.model_dump()
    save_data(inventory)
    return inventory[item_id]

@app.put("/update-item/{item_id}")
def update_item(item_id: int, item: UpdateItem):
    if item_id not in inventory:
        return {"Error": "Item ID does not exist."}

    existing_item = inventory[item_id]
    updated_item = existing_item.copy()

    update_data = item.model_dump(exclude_unset=True)

    updated_item.update(update_data)

    inventory[item_id] = updated_item
    save_data(inventory)

    return updated_item

@app.delete("/delete-item/{item_id}")
def delete_item(item_id: int = Path(..., title="Item ID", description="The ID of the item to delete", ge=0)):
    if item_id not in inventory:
        return {"Error": "Item ID does not exist."}

    deleted_item = inventory.pop(item_id)
    save_data(inventory)
    
    return {"success": "Item deleted", "deleted_item": deleted_item}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
