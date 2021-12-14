from hoshino import Service, priv, new_logger
from hoshino.service import sucmd
from hoshino.typing import CQEvent, CommandSession
from typing import Optional, Union
from re import Match
import asyncio

from .config import config, Group_Config
from .download import get_random_setu, get_serach_setu

help = '''[涩图|来份涩图|来两份涩图] 随机涩图
[搜涩图百合|来两份百合涩图] 搜索关键词的涩图
----------------------
setu help setu帮助说明
setu me  获取今日剩余次数
setu get 获取群配置
setu set [模块] [值] 修改群配置，仅允许群主和白名单用户设置
模块：
[withdraw] 撤回时间，值为秒
[r18] 是否发送r18，on|true 或 off|false
[only_r18] 只发送r18，on|true 或 off|false
[mode] 发送方式，[0]正常，[1]转发，[2]大图
----------------------
setu su [模块] [值] 修改全局配置，仅限BOT管理员
模块：
[daily] 修改每日获取涩图的次数
[freq] 修改涩图发送冷却时间
[max] 修改单次获取涩图的次数
[r18] 是否开启全局r18，如果关闭则所有群组的r18模块都关闭，不影响每个群配置
[proxy] 是否使用本地代理，on|true 或 off|false
[ban/dban] 添加/移除黑名单用户
[admin/dadmin] 添加/移除白名单用户
----------------------
susetu [群号] [模块] [值] 修改指定群组配置，模块与setu set指令一致
----------------------
*susetu指令为私聊指令，仅限BOT管理员
*开启r18需要联系BOT管理员
*建议将发送模式更改为转发模式，发送多张图片不容易刷屏'''

sv = Service('setu', manage_priv=priv.OWNER, enable_on_default=False, help_=help)
log = new_logger('setu')

chinese = {'一': 1, '二': 2, '两': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9, '十': 10}
dailymax = config.dailymax
freqlimit = config.freqlimit

def TodayLimiter(user_id: int, num: Optional[int] = 1) -> Union[str, bool]:
    if user_id in config.banner:
        msg = f'您已被拉黑'
    elif not dailymax.check(user_id):
        msg = f'您今天已经冲过{config.daily}次了，请明天再来'
    elif dailymax.leave_num(user_id, num):
        msg = f'您今天的剩余次数为{dailymax.leave}，不足{num}次'
    elif not freqlimit.check(user_id):
        msg = f'您冲的太快了，请等待{round(freqlimit.left_time(user_id))}秒'
    else:
        freqlimit.start_cd(user_id)
        msg = False
    return msg

def forward_msg(info: list, self_id: int) -> list:
    forward_msg_list = []
    for _ in info:
        data = {
            "type": "node",
            "data": {
                "name": "Bot",
                "uin": str(self_id),
                "content": _[0] + '\n' + _[1]
                }
        }
        forward_msg_list.append(data)
    return forward_msg_list

async def setu_send(bot, ev: CQEvent, img: list, mode: int, withdraw: int):
    imglist: list = []
    if mode == 0:
        for _ in img:
            await bot.send(ev, _[0])
            imglist.append(await bot.send(ev, _[1]))
            await asyncio.sleep(1)
    elif mode == 1:
        forward_msg_list = forward_msg(img, ev.self_id)
        try:
            await bot.send_group_forward_msg(group_id=ev.group_id, messages=forward_msg_list)
        except:
            log.error('转发模式发送失败')
            await bot.finish(ev, '转发模式发送失败，请切换其它发送模式')
        return
    else:
        for _ in img:
            try:
                imglist.append(await bot.send(ev, f'[CQ:cardimage,file={_[1]},source={_[0]},icon={_[1]}]'))
            except:
                log.error('大图模式发送失败')
                await bot.finish(ev, '大图模式发送失败，请切换其它发送模式')
                break
            await asyncio.sleep(1)

    if withdraw != 0:
        await asyncio.sleep(withdraw)
        for i in range(len(imglist)):
            try:
                await bot.delete_msg(self_id=ev.self_id, message_id=imglist[i]['message_id'])
            except:
                log.error('涩图撤回失败')
            await asyncio.sleep(1)

@sv.on_rex(r'^[色涩瑟]图$|^不够[色涩瑟]$|^[色涩瑟]图就这[?？]?$|^[在再]?来?(\d*|\w*)?[点份张][色涩瑟]图$')
async def random_setu(bot, ev:CQEvent):
    group_id = ev.group_id
    user_id = ev.user_id
    args: Match[str] = ev['match']
    group = Group_Config(group_id)
    limit = 1
    try:
        num = args.group(1)
        if num in chinese:
            limit = chinese[num]
        else:
            limit = int(num)
    except:
        log.info('Pass Num')
    if limit > config.max:
        await bot.finish(ev, f'仅允许同时发送{config.max}张', at_sender=True)
    info = TodayLimiter(user_id, limit)
    if isinstance(info, str):
        await bot.finish(ev, info, at_sender=True)
    img = await get_random_setu(group.r18_num, limit, group.mode)
    if not img:
        await bot.finish(ev, '无')
    dailymax.increase(user_id, limit if group.mode == 1 else len(img))
    await setu_send(bot, ev, img, group.mode, group.withdraw)

def Msg2list(args: str) -> list:
    if ',' in args:
        liststr = ','
    elif '，' in args:
        liststr = '，'
    else:
        liststr = ' '
    keyword = args.split(liststr)
    return keyword

@sv.on_rex(r'^[搜来]?(\d*|\w*)?[点份张](.*)[色涩瑟]图$|^搜索?(\d*|\w*)?[点份张]?[色涩瑟]图(.*)$')
async def serach_setu(bot, ev:CQEvent):
    group_id = ev.group_id
    user_id = ev.user_id
    args: Match[str] = ev['match']
    group = Group_Config(group_id)
    limit = 1
    try:
        num = args.group(1) or args.group(3)
        if num in chinese:
            limit = chinese[num]
        else:
            limit = int(num)
    except:
        log.info('Pass Num')
    if limit > config.max:
        await bot.finish(ev, f'仅允许同时发送{config.max}张', at_sender=True)
    info = TodayLimiter(user_id, limit)
    if isinstance(info, str):
        await bot.finish(ev, info, at_sender=True)
    word = args.group(2) or args.group(4)
    if not word:
        await bot.finish(ev, '请输入关键词')
    keyword = Msg2list(word.strip())
    await bot.send(ev, '正在搜索涩图...')
    img = await get_serach_setu(group.r18_num, limit, keyword, group.mode)
    if isinstance(img, bool):
        await bot.finish(ev, '未找到涩图')
    elif isinstance(img, str):
        await bot.finish(ev, f'error: {img}')
    elif len(img) != limit:
        await bot.send(ev, f'找到{len(img)}份该关键词的涩图')
    dailymax.increase(user_id, limit if group.mode == 1 else len(img))
    await setu_send(bot, ev, img, group.mode, group.withdraw)

def args2data(args: str) -> Union[int, bool, str]:
    try:
        if args.isdigit():
            data = int(args)
        elif args.lower() == 'on' or args.lower() == 'true':
            data = True
        elif args.lower() == 'off' or args.lower() == 'false':
            data = False
        else:
            data = '指令错误'
    except:
        data = '指令错误'
    return data

@sv.on_prefix('setu')
async def change_config(bot, ev:CQEvent):
    group_id = ev.group_id
    group = Group_Config(group_id)
    args: list[str] = ev.message.extract_plain_text().strip().split()
    super = priv.check_priv(ev, priv.SUPERUSER)
    if not args:
        msg = '指令错误，请输入参数'
    elif args[0] == 'help':
        msg = '\n' + help
    elif args[0] == 'me':
        if not super:
            num = dailymax.get_num(ev.user_id)
            dailymax.leave_num(ev.user_id, num)
            msg = f'您今日的涩图获取次数剩余[{dailymax.leave}]次'
        else:
            msg = '涩图无上限'
    elif args[0] == 'get':
        group_info = await bot.get_group_info(group_id=group_id)
        group_config_info = group.get_group_config()
        msg = f'\n[{group_info["group_name"]}]({group_id})配置:' + group_config_info
    elif args[0] == 'su':
        if not super:
            return
        try:
            data = args2data(args[2])
        except IndexError:
            await bot.finish(ev, '指令错误')
        if isinstance(data, str):
            msg = '指令错误'
        elif args[1] == 'daily':
            msg = config.set_config('user_config', 'daily_max', data)
        elif args[1] == 'freq':
            msg = config.set_config('user_config', 'freq_limit', data)
        elif args[1] == 'max':
            msg = config.set_config('user_config', 'send_max', data)
        elif args[1] == 'r18':
            msg = config.set_config('lolicon', args[1], data)
        elif args[1] == 'proxy':
            msg = config.set_config('lolicon', 'pixiv_proxy', data)
        elif args[1] == 'ban' or args[1] == 'admin':
            msg = config.add_user(args[1], data)
        elif args[1] == 'dban' or args[1] == 'dadmin':
            msg = config.del_user('ban' if len(args[1]) == 4 else 'admin', data)
        else:
            msg = '指令错误'
    elif args[0] == 'set':
        if not priv.check_priv(ev, priv.OWNER) or ev.user_id in config.whitelist:
            msg = '仅允许群主以及白名单用户修改群配置'
        elif args[1] == 'withdraw':
            try:
                data = args2data(args[2])
            except IndexError:
                await bot.finish(ev, '指令错误，请输入该模块的值')
            if not isinstance(data, int):
                msg = '指令错误，仅允许整数'
            elif not 0 <= data <= 120:
                msg = '指令错误，撤回时间不得为负数且超过120秒'
            else:
                if data == 0:
                    msg = '已取消该群涩图撤回'
                else:
                    msg = f'已将该群涩图撤回时间修改为 {data}s'
                group.set_group_config(args[1], data)
        elif args[1] == 'r18' or args[1] == 'only_r18':
            if not super:
                await bot.finish(ev, 'r18仅允许BOT管理员修改')
            try:
                data = args2data(args[2])
            except IndexError:
                await bot.finish(ev, '指令错误，请输入该模块的值')
            if isinstance(data, bool):
                group.set_group_config(args[1], data)
                msg = f'已将该群模块 [{args[1]}] 修改为 {data}'
            else:
                msg = '指令错误，值为 on|true 或 off|false'
        elif args[1] == 'mode':
            try:
                data = args2data(args[2])
            except IndexError:
                await bot.finish(ev, '指令错误，请输入该模块的值')
            if not isinstance(data, int):
                msg = '指令错误，请输入值 0-2'
            elif not 0 <= data < 3:
                msg = '指令错误，发送模式仅三种\n0：正常，1：转发，2：大图'
            else:
                group.set_group_config(args[1], data)
                msg = f'已将该群模块 [{args[1]}] 修改为 [{data}]'
        else:
            msg = '指令错误，请输入正确的模块'
    else:
        msg = '指令错误，请输入 setu get 或 setu set [模块] [值]'

    await bot.send(ev, msg, at_sender=True)

@sucmd('susetu')
async def superuser_setu(session: CommandSession):
    args: list[str] = session.current_arg.strip().split()
    group_id = int(args[0])
    group = Group_Config(group_id)
    group_list = await session.bot.get_group_list()
    gl = [ gid['group_id'] for gid in group_list ]
    if group_id not in gl:
        await session.finish(f'未找到群组: {group_id}')
    group_info = await session.bot.get_group_info(group_id=group_id)
    if not args[2].isdigit():
        data = bool(args[2] == 'on')
    else:
        data = int(args[2])
    group.set_group_config(args[1], data)
    await session.bot.send_group_msg(group_id=group_id, message=f'已将该群模块 [{args[1]}] 修改为 [{data}]')
    await session.send(f'已成功将群：{group_info["group_name"]}({group_id})\n模块 [{args[1]}] 修改为 [{data}]')