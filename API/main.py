from fastapi import FastAPI, APIRouter, HTTPException, File, Form, UploadFile
from config import collection
from database.schemas import individual_merkle_tree_schema
from database.models import merkleTreeModel
from typing import List
import json

app = FastAPI()
router = APIRouter()

@router.get("/")
async def get_merkle_tree(id: str):
    try:
        # Use a filter dict when querying MongoDB
        merkle_tree = collection.find_one({"id": id})
        if not merkle_tree:
            raise HTTPException(status_code=404, detail="Merkle tree not found")
        # Schema expects (id, merkle_tree)
        result = individual_merkle_tree_schema(merkle_tree.get("id", id), merkle_tree)
        return {"merkle_trees": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload")
async def upload_tree(data: str = Form(...), 
                      file: UploadFile = File(...)):
    try:
        content = await file.read()
        tree = merkleTreeModel(**json.loads(data))

        doc = {
            **tree.dict(),
            "filename": file.filename,
            "content": content
        }   

        resp = collection.insert_one(doc)


        return {"status": "success", "inserted_id": str(resp.inserted_id), "filename": file.filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


app.include_router(router, prefix="/api")
