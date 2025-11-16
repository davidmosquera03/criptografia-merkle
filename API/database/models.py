from pydantic import BaseModel

class merkleTreeModel(BaseModel):
    _id: str
    id: str
    merkleTreeModel: list

    class Config:
        orm_mode = True

