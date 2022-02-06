from typing import Optional, Union, List, Dict
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
    urls: Optional[Dict[str, str]]

class PixivIllustDetail(BaseModel):
    
    id: Optional[int]
    title: Optional[str]
    type: Optional[str]
    image_urls: Optional[Dict[str, str]]
    caption: Optional[str]
    restrict: Optional[int]
    user: Optional[Dict[str, Union[int, str, dict, bool]]]
    tags: Optional[List[Dict[str, Optional[str]]]]
    create_date: Optional[str]
    page_count: Optional[int]
    meta_single_page: Optional[Dict[str, str]]
    meta_pages: Optional[List[Dict[str, Dict[str, str]]]]

class PixivUser(BaseModel):

    id: Optional[int]
    name: Optional[str]
    account: Optional[str]
    profile_image_urls: Optional[Dict[str, str]]
    comment: Optional[str]
    is_followed: Optional[bool]