from typing import Optional, List
from pydantic import BaseModel

class Data(BaseModel):
    
    pid: Optional[int]
    p: Optional[int]
    uid: Optional[int]
    title: Optional[str]
    author: Optional[str]
    r18: Optional[bool]
    width: Optional[int]
    height: Optional[int]
    tags: Optional[List[str]]
    ext: Optional[str]
    uploadDate: Optional[int]
    urls: Optional[dict]