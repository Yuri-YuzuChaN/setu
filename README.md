# setu

自用基于HoshinoBotV2的setu插件

项目地址：https://github.com/Yuri-YuzuChaN/setu

## 使用方法

1. 将该项目放在HoshinoBot插件目录 `modules` 下，或者clone本项目 `git clone https://github.com/Yuri-YuzuChaN/setu`
2. pip以下依赖：`aiohttp`，`traceback`，`pydantics`, `pixivpy-async[socks]`
3. 获取 `refresh_token`：https://gist.github.com/ZipFile/c9ebedb224406f4f11845ab700124362
4. 在 `config.json` 填入 `refresh_token`
4. 在`config/__bot__.py`模块列表中添加`setu`

**插件默认为关闭状态，若发现BOT无反应，请手动开启插件**

## 说明

1. pixiv的推荐内容根据登陆的账号决定，可能会泄露XP（
2. 请根据您的服务器IP修改 `pixiv_direct` 和 `proxy`
3. 如果服务器不能访问Pixiv，必须开启代理，将 `pixiv` 模块的 `proxy` 设置为 `true`，并填写 `proxy_url` 地址，否则无法启动bot

## 全局配置文件 `config.json`

- `user_config`：用户配置
    - `daily_max`：每日上限
    - `freq_limit`：冷却时间
    - `send_max`：单次发送上限
- `group_config`：群配置，用于bot加入新群时初始化群配置
- `lolicon`：lolicon模块设置
    - `pixiv_direct`：是否使用Pixiv原生地址
    - `proxy`：本地代理的开关
    - `r18`：全局r18开关，如果关闭，即使群配置为开都视作为关闭
- `pixiv`：pixiv模块设置
    - `pixiv_direct`：是否使用Pixiv原生地址
    - `proxy`：本地代理的开关
    - `refresh_token`：账号TOKEN，用于登陆Pixiv
- `proxy_url`：本地代理地址，即代理工具的本地地址，一般为：`http://127.0.0.1:8080`，根据自身环境填入
- `banner`：黑名单用户
- `whitelist`：白名单用户

## 群配置文件 `group_config.json`

- `lolicon`：群lolicon模块配置
    - `switch`：该模块开关
    - `withdraw`：撤回时间
    - `r18`：r18开关
    - `only_r18`：只发送r18
- `pixiv`：群pixiv模块配置
    - `switch`：该模块开关
    - `withdraw`：撤回时间
    - `r18`：r18开关
- `mode`：发送模式，[0]正常，[1]转发，[2]大图

## 指令

| 指令              | 可选参数              | 说明                            |
| :---------------- | :-------------------- | :------------------------------ |
| 涩图，来份涩图，来两份涩图     | 无                 | 获取一张或多张随机涩图      |
| 搜涩图百合涩图，搜两份百合涩图 | 无                 | 获取一张或多张关键词的涩图    |
| pvid           | [pid]              | 查看指定ID插画      |
| pvuid          | [uid]              | 查看指定UID用户 |
| pvimg          | [uid]              | 随机一张该用户插画   |
|                | [uid] [num]        | 查看该用户的一张插画，`num`为第几张 |
| pvrank         | [mode]             | 随机一张排行榜的插画 |
|                | [mode] [num]       | 查看排行榜的一张插画，`num`为第几张 |
| pvre           | [pid]              | 随机一张该插画ID的相关插画作品 |
|                | [pid] [num]        | 查看一张该插画ID的相关插画作品，`num`为第几张 |
| pvse           | [word]             | 搜索该标签的相关作品 |
|                | [word] [duration]  | 搜索该标签的相关作品，`duration`: `day`， `week`， `month` |
| setu           | help               | 获取setu插件使用方法    |
|                | me                 | 获取今日剩余次数    |
|                | get                | 获取群配置   |
|                | set [模块] [单项]或[值]    | 修改群配置，仅允许群主和白名单用户设置  |
|                | su [模块] [单项]或[值]     | 修改全局配置，仅限BOT管理员  |
| susetu         | [群号] [模块] [单项]或[值] | 修改指定群组配置，模块与`setu set`一致，该指令为私聊指令，仅限BOT管理员 |

- pvrank mode:
    - 默认: day | week | month | day_male | day_female | week_original | day_manga | week_rookie
    - r18 : day_r18 | day_male_r18 | day_female_r18 | week_r18 | week_r18g
## setu set 模块

- `lolicon`:
    - `on/off`：该模块开关，例如：`setu set lolicon on`
    - `withdraw`：撤回时间，值为秒，例如：`setu set lolicon withdraw 60`
    - `r18`：是否发送r18，on|true 或 off|false，例如：`setu set lolicon r18 on`
    - `only_r18`：只发送r18，on|true 或 off|false，例如：`setu set lolicon only_r18 on`
- `pixiv`:
    - `on/off`：该模块开关，例如：`setu set lolicon on`
    - `withdraw`：撤回时间，值为秒，例如：`setu set lolicon withdraw 60`
    - `r18`：是否发送r18，on|true 或 off|false，例如：`setu set lolicon r18 on`
- `mode`：发送方式，[0]正常，[1]转发，[2]大图，例如：`setu set mode 1`

## setu su 模块

- `daily`：每日获取涩图次数，例如：`setu su daily 50`
- `freq`：发送冷却时间，例如：`setu su freq 10`
- `max`：单次获取涩图的次数，例如：`setu su max 10`
- `lolicon`:
    - `r18`：全局r18，例如：`setu su lolicon r18 off`
    - `direct`：Pixiv原生地址，例如：`setu su lolicon direct on`
    - `proxy`：本地代理，例如：`setu su lolicon proxy on`
- `pixiv`:
    - `reload`：重新登陆Pixiv，例如：`setu su pixiv reload`
    - `direct`：使用Pixiv原生地址，例如：`setu su pixiv direct on`
    - `proxy`：是否使用本地代理，例如：`setu su pixiv proxy on`
- `ban/dban`：添加/移除黑名单用户，例如：`setu su ban 445621534`
- `admin/dadmin`：添加/移除白名单用户，例如：`setu su dadmin 445621534`
- `config`：重新加载全局配置，适用于手动修改配置，例如：`setu su config reload`
