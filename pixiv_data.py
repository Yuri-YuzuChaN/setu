from hoshino.typing import MessageSegment
from typing import List

import random

from .config import pixiv, Group_Config
from .data import *
from .download import b2b64, Img_Download

token_error = 'Error occurred at the OAuth process. Please check your Access Token to fix this. Error Message: invalid_grant'

async def pixiv_img(info: dict, group: Group_Config) -> Union[List[str], str]:
    data = PixivIllustDetail(**info)
    if data.restrict == 1 and not group.pixiv_r18:
        return '插画为R18类型，该群Pixiv模块未开启R18，不给予发送'
    user = PixivUser(**data.user)
    if data.page_count == 1:
        url = data.meta_single_page['original_image_url'].replace('i.pximg.net', 'i.pixiv.re')
    else:
        url = data.meta_pages[0]['image_urls']['original'].replace('i.pximg.net', 'i.pixiv.re')
    img = await Img_Download('pixiv', url, data.id)
    imgb64 = b2b64(img)
    setu = MessageSegment.image(imgb64)
    tags = [i['name'] for i in data.tags]
    msg = f'''{setu}
Pid: {data.id}
Author: {user.name}
Title: {data.title}
Tags: {' | '.join(tags)}'''
    result = [msg, setu]
    return result

async def illust_detail(pid: int, group: Group_Config) -> list:
    info = await pixiv.aapi.illust_detail(pid)
    if 'error' in info:
        if info['error']['message'] == token_error:
            await pixiv.reload()
            return await illust_detail(pid, group)
        else:
            msg = '未找到该ID作品'
    else:
        msg = await pixiv_img(info['illust'], group)
    return msg

async def user_detail(uid: int) -> str:
    info = await pixiv.aapi.user_detail(uid)
    if 'error' in info:
        if info['error']['message'] == token_error:
            await pixiv.reload()
            return await user_detail(uid)
        else:
            msg = '未找到该用户'
    else:
        data = PixivUser(**info['user'])
        url = data.profile_image_urls['medium'].replace('i.pximg.net', 'i.pixiv.re')
        setu = MessageSegment.image(url)
        msg = f'''{setu}
Id: {data.id}
Name: {data.name}'''
    return msg

async def user_illusts(uid: int, num: int = 0, group: Group_Config = ...) -> list:
    info = await pixiv.aapi.user_illusts(uid)
    if 'error' in info:
        if info['error']['message'] == token_error:
            await pixiv.reload()
            return await user_illusts(uid, num, group)
        else:
            msg = '未找到该用户'
    else:
        rdnum = random.randint(0, len(info['illusts']))
        error_len: list[str] = []
        if num != 0 and num < len(info['illusts']):
            rdnum = num - 1
            error_len.append('超出数量，随机发送一张该画师作品：\n')
        data = await pixiv_img(info['illusts'][rdnum], group)
        if isinstance(data, str) or not error_len:
            msg = data
        else:
            msg = error_len + data
    return msg

async def search_illusts(word: str, duration: Optional[str] = None, group: Group_Config = ...) -> list:
    info = await pixiv.aapi.search_illust(word, duration=duration)
    if 'error' in info:
        if info['error']['message'] == token_error:
            await pixiv.reload()
            return await search_illusts(word, duration=duration, group=group)
        else:
            msg = '未找到相关作品'
    else:
        rdnum = random.randint(0, len(info['illusts']))
        msg = await pixiv_img(info['illusts'][rdnum], group)
    return msg

async def illust_ranking(mode: str, num: int = 0, group: Group_Config = ...) -> list:
    info = await pixiv.aapi.illust_ranking(mode)
    if 'error' in info:
        if info['error']['message'] == token_error:
            await pixiv.reload()
            return await illust_ranking(mode, num, group)
        else:
            msg = '未知'
    else:
        if num != 0:
            rdnum = num - 1
        else:
            rdnum = random.randint(0, len(info['illusts']))
        msg = await pixiv_img(info['illusts'][rdnum], group)
    return msg

async def illust_related(pid: int, num: int = 0, group: Group_Config = ...) -> list:
    info = await pixiv.aapi.illust_related(pid)
    if 'error' in info:
        if info['error']['message'] == token_error:
            await pixiv.reload()
            return await illust_related(pid, group)
        else:
            msg = '未找到该ID相关作品'
    else:
        if num != 0:
            num -= 1
        msg = await pixiv_img(info['illusts'][num], group)
    return msg
