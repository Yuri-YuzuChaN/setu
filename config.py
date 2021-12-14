import json, os, traceback, time, pytz
from typing import Any, List, Union
from collections import defaultdict
from datetime import datetime, timedelta
from hoshino import new_logger

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
        self. default_cd = key
        
class Config:

    config_json = os.path.join(os.path.dirname(__file__), 'config.json')
    group_json = os.path.join(os.path.dirname(__file__), 'group_config.json')

    def __init__(self):
        self.config: dict[str, Union[dict[str, Union[int, bool]], list[int]]] = json.load(open(self.config_json, 'r', encoding='utf-8'))
        self.group_config: dict[str, Union[int, bool]] = json.load(open(self.group_json, 'r', encoding='utf-8'))

        self.user_config = self.config['user_config']
        self.lolicon = self.config['lolicon']
        
        self.dailymax = DailyNumberLimiter(self.user_config['daily_max'])
        self.freqlimit = FreqLimiter(self.user_config['freq_limit'])

    def set_config(self, project: str, item: str, data: Union[str, int, bool]) -> str:
        '''修改全局配置'''
        self.config[project][item] = data
        self.save_config(self.config_json, self.config)
        if item == 'daily_max':
            self.new_dailymax()
        elif item == 'freq_limit':
            self.new_freqlimit()
        
        return f'已将该群模块 [{item}] 修改为 [{data}]'

    def update_token(self, token: str):
        '''更新pixiv Token'''
        self.config['pixiv']['refresh_token'] = token
        self.save_config(self.config_json, self.config)

    def new_dailymax(self):
        '''更新当天最高次数'''
        self.dailymax.update_max(self.user_config['daily_max'])

    def new_freqlimit(self):
        '''更新发送冷却时间'''
        self.freqlimit.update_time(self.user_config['freq_limit'])

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
        self.save_config(self.config, self.group_config)

        return f'已将 [{user_id}] 添加为{data}名单'

    def del_user(self, item: str, user_id: int) -> str:
        '''移除黑/白名单'''
        if item == 'ban':
            data = '黑'
            self.banner.remove(user_id)
        else:
            data = '白'
            self.whitelist.remove(user_id)
        self.save_config(self.config, self.group_config)

        return f'已将 [{user_id}] 移出{data}名单'

    def get_user(self, item: str, user_id: int) -> bool:
        '''获取黑/白名单'''
        if item == 'ban':
            args = bool(user_id in self.banner)
        else:
            args = bool(user_id in self.whitelist)
        return args

    @property
    def default(self) -> dict:
        '''群默认配置'''
        return self.config['group_config']

    @property
    def r18(self) -> bool:
        '''全局r18'''
        return self.lolicon['r18']

    @property
    def token(self) -> str:
        '''pixiv Token'''
        return self.config['pixiv']['refresh_token']

    @property
    def daily(self) -> int:
        '''每日上限'''
        return self.user_config['daily_max']

    @property
    def freq(self) -> int:
        '''发送冷却时间'''
        return self.user_config['freq_limit']

    @property
    def max(self) -> int:
        '''单此发送上限'''
        return self.user_config['send_max']

    @property
    def pixiv_proxy(self) -> bool:
        '''代理开关'''
        return self.lolicon['pixiv_proxy']

    @property
    def proxy(self) -> str:
        '''代理地址'''
        return self.config['proxy']

    @property
    def banner(self) -> list:
        return self.config['banner']

    @property
    def whitelist(self) -> list:
        return self.config['whitelist']

config = Config()

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

    def set_group_config(self, project: str, data: Union[int, bool]):
        '''修改群配置'''
        config.group_config[self.group_id][project] = data
        config.save_config(config.group_json, config.group_config)

    def get_group_config(self) -> str:
        '''获取群配置'''
        msg = f'''
withdraw: {self.withdraw}
r18: {self.r18}
only_r18: {self.only_r18}
mode: {self.mode}'''
        return msg

    @property
    def r18(self) -> bool:
        '''是否开启r18'''
        return config.group_config[self.group_id]['r18']

    @property
    def only_r18(self) -> bool:
        '''是否只开启r18'''
        return config.group_config[self.group_id]['only_r18']

    @property
    def mode(self) -> int:
        '''发送模式'''
        return config.group_config[self.group_id]['mode']

    @property
    def withdraw(self) -> int:
        '''撤回时间'''
        return config.group_config[self.group_id]['withdraw']

    @property
    def r18_num(self) -> int:
        '''是否开启r18或只开启r18'''
        if config.r18:
            if self.r18:
                r18 = 1 if self.only_r18 else 2
            else:
                r18 = 0
        else:
            r18 = 0

        return r18