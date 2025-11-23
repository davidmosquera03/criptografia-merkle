
from fastapi import FastAPI, APIRouter, HTTPException, File, Form, UploadFile
from config import collection, challenge_collection, log_collection
from database.schemas import get_logs_schema, individual_merkle_tree_schema, list_merkle_trees_schema
from database.models import merkleTreeModel, challengeModel, logModel
import json
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from merkle_implementation import get_merkle_proof, recompute_merkle_root, get_challenge_blocks_mongo

app = FastAPI()
router = APIRouter()

@router.get("/")
async def get_all_merkle_trees():
    try:

        merkle_trees = collection.find()
        results = list_merkle_trees_schema(merkle_trees)
        return {"merkle_trees": results}
    

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/get_merkle_tree/{id}")
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

@router.post("/challenge")
async def challenge(challenge: challengeModel):
    try:
        doc = challenge.dict()
        resp = challenge_collection.insert_one(doc)
        return {"status": "success", "inserted_id": str(resp.inserted_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/prove")
async def prove_challenge(challenge_id: str):
    try:
        challenge = challenge_collection.find_one({"challenge_id": challenge_id})
        if not challenge:
            raise HTTPException(status_code=404, detail="Challenge not found")
        
        merkle_tree = collection.find_one({"id": challenge.get("file_id", "")})
        if not merkle_tree:
            raise HTTPException(status_code=404, detail="Merkle tree not found")
        
        nonce = challenge.get("nonce", b"")

        tree_json = merkle_tree.get("merkleTreeModel", [])
       
        indexes = challenge.get("indexes", [])
        
        content = merkle_tree.get("content", b"")
       
        challenge_blocks = get_challenge_blocks_mongo(content, indexes, nonce)

        proof = get_merkle_proof(indexes, tree_json)

        recomputed_root = recompute_merkle_root(challenge_blocks, proof, (len(tree_json)+1)//2)

        return {
            "recomputed_root": recomputed_root,
            "nonce": nonce,
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/logs")
async def log_message(log: logModel):
    try:
        doc = log.dict()
        resp = log_collection.insert_one(doc)
        return {"status": "success", "inserted_id": str(resp.inserted_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/logs")
async def get_logs():
    try:
        logs = log_collection.find()
        results = get_logs_schema(logs)
        return {"logs": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
app.include_router(router, prefix="/api")
