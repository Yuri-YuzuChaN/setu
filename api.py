from typing import Union
from hoshino.log import new_logger
import aiohttp

lolicon = 'https://api.lolicon.app/setu/v2'
logger = new_logger('setu_api')

async def Get_Random_Imginfo(r18: int, num: int = 1) -> Union[dict, bool]:
    async with aiohttp.ClientSession() as session:
        async with session.get(lolicon + f'?r18={r18}&num={num}') as req:
            if req.status != 200:
                data = False
            else:
                data = await req.json()
    return data

async def Get_Imginfo(r18: int, keyword: list, num: int = 1, noimg: bool = False) -> Union[dict, bool]:
    if noimg:
        url = lolicon + f'?r18={r18}&num={num}&keyword={"&keyword=".join(keyword)}'
        se = True
    else:
        url = lolicon + f'?r18={r18}&num={num}&tag={"&tag=".join(keyword)}'
        se = False
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as req:
            if req.status != 200:
                data = False
            else:
                data = await req.json()
                if not data['data'] and not se:
                    data = await Get_Imginfo(r18, keyword, num, True)
        return data