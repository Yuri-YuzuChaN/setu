from typing import Union, List, Dict
from nonebot import MessageSegment
from hoshino.log import new_logger
import base64, aiohttp, traceback

from .data import Data
from .config import config
from .api import Get_Random_Imginfo, Get_Imginfo

logger = new_logger('setu_download')

def b2b64(bytes: bytes) -> str:
    base64_str = 'base64://' + base64.b64encode(bytes).decode()
    return base64_str

async def Img_Download(url: str, pid: int) -> Union[bytes, bool]:
    try:
        if config.pixiv_proxy:
            headers = {
                'referer': f'https://www.pixiv.net/member_illust.php?mode=medium&illust_id={pid}'
            }
            proxy = config.proxy
            msg = f'Start Downloading Image With Pixiv.net -> PID: {pid}'
        else:
            headers = None
            proxy = None
            msg = f'Start Downloading Image With Pixiv.re -> PID: {pid}'
        logger.info(msg)
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url, proxy=proxy) as req:
                if req.status != 200:
                    data = False
                else:
                    data = await req.read()
    except:
        logger.error(traceback.print_exc())
    return data

async def get_random_setu(r18: int, limit: int, mode: int) -> Union[List[MessageSegment], bool]:
    msg: list[MessageSegment] = []
    setu = await Get_Random_Imginfo(r18, limit)
    if setu['error']:
        return setu['error']
    elif not setu['data']:
        return False
    for data in setu['data']:
        msg.append(await img_data(Data(**data), mode))
    return msg

async def get_serach_setu(r18: int, limit: int, keyword: list, mode: int) -> Union[Dict[str, MessageSegment], bool]:
    msg: list[MessageSegment] = []
    setu = await Get_Imginfo(r18, keyword, limit)
    if setu['error']:
        return setu['error']
    elif not setu['data']:
        return False
    for data in setu['data']:
        msg.append(await img_data(Data(**data), mode))
    return msg

async def img_data(data: Data, mode: int) -> Union[bool, list]:
    url = data.urls.get('original').replace('i.pixiv.cat', 'i.pixiv.re')
    if mode != 2:
        img = await Img_Download(url, data.pid)
        if not img:
            logger.error('Image Download Fail')
            return img
        imgb64 = b2b64(img)
        msg = f'''Title: {data.title}
Author: {data.author}
PixivID: {data.pid}'''
        setu = MessageSegment.image(imgb64)
        data = [msg, setu]
    else:
        data = [data.pid, url]
    return data