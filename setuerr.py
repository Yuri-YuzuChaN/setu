err_num = {
    '-1': 'lolicon模块错误，请联系bot管理员',
    '-2': 'pixiv模块错误，请联系bot管理员',
    '-3': '未找到涩图',
    '-4': 'setu下载失败'
}

class SetuLoliconError(Exception):

    def __init__(self, num: str):
        self.err = err_num[num]

class SetuPixivError(Exception):

    def __init__(self):
        self.err = err_num['-2']

class SetuDownloadError(Exception):

    def __init__(self):
        self.err = err_num['-4']