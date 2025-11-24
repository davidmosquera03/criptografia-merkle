from pydantic import BaseModel

class merkleTreeModel(BaseModel):
    _id: str
    id: str
    merkleTreeModel: list

    class Config:
        orm_mode = True

class challengeModel(BaseModel):
    challenge_id: str
    file_id: str
    nonce: bytes
    indexes: list[int]

    class Config:
        orm_mode = True

class corruptChallengeModel(BaseModel):
    challenge_id: str
    file_id: str
    nonce: str  # Change to str
    indexes: list[int]
    percentage: float

class logModel(BaseModel):
    challenge_id: str
    result: str

    class Config:
        orm_mode = True