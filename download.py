from typing import Union, List, Dict
from nonebot import MessageSegment
from hoshino.log import new_logger
import base64, aiohttp, traceback

from .data import Data
from .config import config
from .setuerr import SetuDownloadError, SetuLoliconError
from .api import Get_Random_Imginfo, Get_Imginfo

logger = new_logger('setu_download')

def b2b64(bytes: bytes) -> str:
    base64_str = 'base64://' + base64.b64encode(bytes).decode()
    return base64_str

async def Img_Download(project: str, url: str, pid: int) -> Union[bytes, bool]:
    try:
        headers = None
        proxy = None
        msg = f'Start Downloading Image With Pixiv.re -> PID: {pid}'
        if project == 'lolicon' and config.lolicon_direct:
            headers = {
                'referer': f'https://www.pixiv.net/member_illust.php?mode=medium&illust_id={pid}'
            }
            proxy = config.proxy_url if config.lolicon_proxy else None
            msg = f'Start Downloading Image With Pixiv.net -> PID: {pid}'
        elif project == 'pixiv' and config.pixiv_direct:
            headers = {
                'referer': f'https://www.pixiv.net/member_illust.php?mode=medium&illust_id={pid}'
            }
            proxy = config.proxy_url if config.pixiv_proxy else None
            msg = f'Start Downloading Image With Pixiv.net -> PID: {pid}'
        logger.info(msg)
        async with aiohttp.request('GET', url, headers=headers, proxy=proxy) as req:
            data = await req.read() if req.status == 200 else False
        return data
    except:
        logger.error(traceback.format_exc())
        raise SetuDownloadError

async def get_random_setu(r18: int, limit: int, mode: int) -> Union[List[MessageSegment], bool]:
    msg: list[MessageSegment] = []
    setu = await Get_Random_Imginfo(r18, limit)
    if setu['error']:
        raise SetuLoliconError('-1')
    elif not setu['data']:
        return False
    for data in setu['data']:
        msg.append(await img_data(Data(**data), mode))
    return msg

async def get_serach_setu(r18: int, limit: int, keyword: list, mode: int) -> Union[Dict[str, MessageSegment], bool]:
    msg: list[MessageSegment] = []
    setu = await Get_Imginfo(r18, keyword, limit)
    if setu['error']:
        raise SetuLoliconError('-1')
    elif not setu['data']:
        raise SetuLoliconError('-3')
    for data in setu['data']:
        setuinfo = await img_data(Data(**data), mode)
        msg.append(setuinfo)
    return msg

async def img_data(data: Data, mode: int) -> Union[bool, list, str]:
    url = data.urls['original'].replace('i.pixiv.cat', 'i.pixiv.re')
    if mode != 2:
        img = await Img_Download('lolicon', url, data.pid)
        imgb64 = b2b64(img)
        msg = f'''Title: {data.title}
Author: {data.author}
PixivID: {data.pid}'''
        setu = MessageSegment.image(imgb64)
        setuinfo = [msg, setu]
    else:
        setuinfo = [data.pid, url]
    return setuinfo