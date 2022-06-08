import json, os, traceback, time, pytz, aiohttp
from typing import Any, List, Union
from collections import defaultdict
from datetime import datetime, timedelta
from pixivpy_async import AppPixivAPI, PixivAPI
from hoshino.log import new_logger

setu_logger = new_logger('setu_config')
pixiv_logger = new_logger('pixiv_logger')

class DailyNumberLimiter:

    tz = pytz.timezone('Asia/Shanghai')
    
    def __init__(self, max_num: int):
        self.today = -1
        self.count = defaultdict(int)
        self.max = max_num

    def check(self, key: int) -> bool:
        now = datetime.now(self.tz)
        day = (now - timedelta(hours=0)).day
        if day != self.today:
            self.today = day
            self.count.clear()
        return bool(self.count[key] < self.max)

    def get_num(self, key: int) -> int:
        return self.count[key]

    def leave_num(self, key: int, num: int) -> int:
        self._leave = config.daily - self.count[key]
        return bool(config.daily - self.count[key] < num)

    def increase(self, key: int, num: int = 1):
        self.count[key] += num

    def reset(self, key: int):
        self.count[key] = 0

    def update_max(self, max_num: int):
        self.max = max_num

    @property
    def leave(self) -> int:
        return self._leave

class FreqLimiter:

    def __init__(self, default_cd_seconds: int):
        self.next_time = defaultdict(float)
        self.default_cd = default_cd_seconds

    def check(self, key: int) -> bool:
        return bool(time.time() >= self.next_time[key])

    def start_cd(self, key: int, cd_time: int = 0):
        self.next_time[key] = time.time() + (cd_time if cd_time > 0 else self.default_cd)

    def left_time(self, key: int) -> float:
        return self.next_time[key] - time.time()

    def update_time(self, key: int):
        self.default_cd = key

class Config:

    config_json = os.path.join(os.path.dirname(__file__), 'config.json')
    group_json = os.path.join(os.path.dirname(__file__), 'group_config.json')

    def __init__(self):
        '''加载全局配置'''
        self.config: dict[str, Union[dict[str, Union[int, bool]], list[int]]] = json.load(open(self.config_json, 'r', encoding='utf-8'))
        self.group_config: dict[str, Union[dict[str, Union[int, bool]], int]] = json.load(open(self.group_json, 'r', encoding='utf-8'))
        
        self.dailymax = DailyNumberLimiter(self.config['user_config']['daily_max'])
        self.freqlimit = FreqLimiter(self.config['user_config']['freq_limit'])

    def set_config(self, project: str, item: str, data: Union[str, int, bool]) -> str:
        '''修改全局配置'''
        self.config[project][item] = data
        self.save_config(self.config_json, self.config)
        if item == 'daily_max':
            self.new_dailymax()
        elif item == 'freq_limit':
            self.new_freqlimit()
        elif project == 'pixiv' and item == 'proxy':
            pixiv.proxy()
        
        return f'已将模块 [{item}] 修改为 [{data}]'

    def update_token(self, access_token: str, refresh_token: str):
        '''更新pixiv Token'''
        self.config['pixiv']['access_token'] = access_token
        self.config['pixiv']['refresh_token'] = refresh_token
        self.save_config(self.config_json, self.config)

    def new_dailymax(self):
        '''更新当天最高次数'''
        self.dailymax.update_max(self.config['user_config']['daily_max'])

    def new_freqlimit(self):
        '''更新发送冷却时间'''
        self.freqlimit.update_time(self.config['user_config']['freq_limit'])

    def save_config(self, file: str, data: Any):
        '''保存配置'''
        try:
            with open(file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            traceback.print_exc()
            setu_logger.error(f'Save Setu Config File Error: {e}')

    def add_user(self, item: str, user_id: int) -> str:
        '''添加黑/白名单'''
        if item == 'ban':
            data = '黑'
            self.banner.append(user_id)
        else:
            data = '白'
            self.whitelist.append(user_id)
        self.save_config(self.config_json, self.config)

        return f'已将 [{user_id}] 添加为{data}名单'

    def del_user(self, item: str, user_id: int) -> str:
        '''移除黑/白名单'''
        if item == 'ban':
            data = '黑'
            self.banner.remove(user_id)
        else:
            data = '白'
            self.whitelist.remove(user_id)
        self.save_config(self.config_json, self.config)

        return f'已将 [{user_id}] 移出{data}名单'

    def get_user(self, item: str, user_id: int) -> bool:
        '''获取黑/白名单'''
        if item == 'ban':
            args = bool(user_id in self.banner)
        else:
            args = bool(user_id in self.whitelist)
        return args

    def reload(self) -> str:
        self.config: dict[str, Union[dict[str, Union[int, bool]], list[int]]] = json.load(open(self.config_json, 'r', encoding='utf-8'))
        return '已重新加载全局配置文件'

    @property
    def default(self) -> dict:
        '''群默认配置'''
        return self.config['group_config']

    @property
    def daily(self) -> int:
        '''每日上限'''
        return self.config['user_config']['daily_max']

    @property
    def freq(self) -> int:
        '''发送冷却时间'''
        return self.config['user_config']['freq_limit']

    @property
    def max(self) -> int:
        '''单此发送上限'''
        return self.config['user_config']['send_max']

    @property
    def r18(self) -> bool:
        '''全局r18'''
        return self.config['lolicon']['r18']

    @property
    def lolicon_direct(self) -> bool:
        '''lolicon pixiv开关'''
        return self.config['lolicon']['pixiv_direct']

    @property
    def lolicon_proxy(self) -> bool:
        '''lolicon代理开关'''
        return self.config['lolicon']['proxy']

    @property
    def pixiv_direct(self) -> bool:
        '''pixiv 原生地址开关'''
        return self.config['pixiv']['pixiv_direct']

    @property
    def pixiv_proxy(self) -> bool:
        '''pixiv代理开关'''
        return self.config['pixiv']['proxy']

    @property
    def token(self) -> str:
        '''pixiv Token'''
        return self.config['pixiv']['refresh_token']

    @property
    def proxy_url(self) -> str:
        '''代理地址'''
        return self.config['proxy_url']

    @property
    def banner(self) -> list:
        return self.config['banner']

    @property
    def whitelist(self) -> list:
        return self.config['whitelist']

config = Config()

class Pixiv:

    AUTH_TOKEN_URL = 'https://oauth.secure.pixiv.net/auth/token'
    USER_AGENT = 'PixivIOSApp/7.13.3 (iOS 14.6; iPhone13,2)'
    CLIENT_ID = 'MOBrBDS8blbauoSck0ZfDbtuzpyT'
    CLIENT_SECRET = 'lsACyCD94FhDUtGTXi3QzcFE2uU1hqtDaKeqrdwj'

    def __init__(self):
        '''加载Pixiv模块'''
        self.proxy()
        self._APixiv = AppPixivAPI(proxy=self._proxy)
        self._PPixiv = PixivAPI(proxy=self._proxy)

    async def reload(self):
        '''重新加载新的Token并重新登陆'''
        self._APixiv = AppPixivAPI(proxy=self._proxy)
        self._PPixiv = PixivAPI(proxy=self._proxy)
        await self.Login()
        return '已重新登陆Pixiv'

    async def Login(self) -> List[dict]:
        '''登陆Pixiv'''
        try:
            Aapi = await self._APixiv.login(refresh_token=config.token)
            Papi = await self._PPixiv.login(refresh_token=config.token)
        except:
            await self.refresh()
            await self.Login()
        return [Aapi, Papi]

    def proxy(self):
        '''更新代理开关'''
        if config.pixiv_proxy:
            self._proxy = config.proxy_url
        else:
            self._proxy = None

    async def refresh(self):
        '''刷新 `refresh_token`'''
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.AUTH_TOKEN_URL,
                data = {
                    'client_id': self.CLIENT_ID,
                    'client_secret': self.CLIENT_SECRET,
                    'grant_type': 'refresh_token',
                    'include_policy': 'true',
                    'refresh_token': config.token,
                },
                headers = {
                    'user-agent': self.USER_AGENT,
                    'app-os-version': '14.6',
                    'app-os': 'ios',
                }) as req:
                response = await req.json()
        access_token = response['access_token']
        refresh_toekn = response['refresh_token']
        config.update_token(access_token, refresh_toekn)

    @property
    def aapi(self) -> AppPixivAPI:
        return self._APixiv

    @property
    def papi(self) -> PixivAPI:
        return self._PPixiv

pixiv = Pixiv()

class Group_Config():

    def __init__(self, group_id: int):
        '''加载群配置'''
        self.group_id = str(group_id)
        if self.group_id not in config.group_config:
            self.new_group_config()

    def new_group_config(self):
        '''创建群配置'''
        config.group_config[self.group_id] = config.default
        config.save_config(config.group_json, config.group_config)

    def set_group_config(self, project: str, item: str, data: Union[int, bool]):
        '''修改群配置'''
        if item:
            config.group_config[self.group_id][project][item] = data
        else:
            config.group_config[self.group_id][project] = data
        config.save_config(config.group_json, config.group_config)

    def get_group_config(self) -> str:
        '''获取群配置'''
        msg = f'''
lolicon:
    switch: {self.lolicon_switch}
    withdraw: {self.lolicon_withdraw}
    r18: {self.lolicon_r18}
    only_r18: {self.only_r18}
pixiv:
    switch: {self.pixiv_switch}
    withdraw: {self.pixiv_withdraw}
    r18: {self.pixiv_r18}
mode: {self.mode}'''
        return msg

    @property
    def lolicon_switch(self) -> bool:
        '''lolicon 开关'''
        return config.group_config[self.group_id]['lolicon']['switch']

    @property
    def lolicon_withdraw(self) -> int:
        '''lolicon 撤回时间'''
        return config.group_config[self.group_id]['lolicon']['withdraw']

    @property
    def lolicon_r18(self) -> bool:
        '''lolicon 是否开启r18'''
        return config.group_config[self.group_id]['lolicon']['r18']

    @property
    def only_r18(self) -> bool:
        '''lolicon 是否只开启r18'''
        return config.group_config[self.group_id]['lolicon']['only_r18']

    @property
    def pixiv_switch(self) -> bool:
        '''Pixiv 开关'''
        return config.group_config[self.group_id]['pixiv']['switch']

    @property
    def pixiv_withdraw(self) -> int:
        '''pixiv 撤回时间'''
        return config.group_config[self.group_id]['pixiv']['withdraw']

    @property
    def pixiv_r18(self) -> bool:
        '''pixiv 是否开启r18'''
        return config.group_config[self.group_id]['pixiv']['r18']

    @property
    def mode(self) -> int:
        '''发送模式'''
        return config.group_config[self.group_id]['mode']

    @property
    def r18_num(self) -> int:
        '''是否开启r18或只开启r18'''
        if config.r18:
            if self.lolicon_r18:
                r18 = 1 if self.only_r18 else 2
            else:
                r18 = 0
        else:
            r18 = 0

        return r18