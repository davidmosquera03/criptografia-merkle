from pydantic import BaseModel

class merkleTreeModel(BaseModel):
    id: str
    merkleTreeModel: list

    class Config:
        orm_mode = True

