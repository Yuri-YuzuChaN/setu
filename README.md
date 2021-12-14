# setu

自用基于HoshinoBotV2的setu插件

项目地址：https://github.com/Yuri-YuzuChaN/setu

# 使用方法

1. 将该项目放在HoshinoBot插件目录 `modules` 下，或者clone本项目 `git clone https://github.com/Yuri-YuzuChaN/setu`
2. pip以下依赖：`aiohttp`，`traceback`，`pydantics`
3. 在`config/__bot__.py`模块列表中添加`setu`

# 全局配置文件 `config.json`

1. `user_config`为用户配置，`daily_max`：每日上限，`freq_limit`：冷却时间，`send_max`：单次发送上限
2. `group_config`为群配置，用于bot加入新群时初始化群配置
3. `lolicon`为lolicon api的设置，`pixiv_proxy`目前为本地代理的开关，`r18`：全局r18开关，如果关闭，即使群配置为开都视作为关闭
4. `proxy`目前仅为本地代理地址，即代理工具的本地地址，一般为`http://127.0.0.1:8080`
5. `banner`黑名单用户
6. `whitelist`白名单用户

# 群配置文件 `group_config.json`

1. `withdraw`：撤回时间
2. `r18`：r18开关
3. `only_r18`：只发送r18
4. `mode`：发送模式，[0]正常，[1]转发，[2]大图

# 指令

| 指令              | 可选参数              | 说明                            |
| :---------------- | :-------------------- | :------------------------------ |
| 涩图，来份涩图，来两份涩图     | 无                 | 获取一张或多张随机涩图                                       |
| 搜涩图百合涩图，搜两份百合涩图 | 无                 | 获取一张或多张关键词的涩图                                   |
| setu                           | help               | 获取setu插件使用方法                                         |
|                                | me                 | 获取今日剩余次数                                             |
|                                | get                | 获取群配置                                                   |
|                                | set [模块] [值]    | 修改群配置，仅允许群主和白名单用户设置                       |
|                                | su [模块] [值]     | 修改全局配置，仅限BOT管理员                                  |
| susetu                         | [群号] [模块] [值] | 修改指定群组配置，模块与`setu set`一致，该指令为私聊指令，仅限BOT管理员 |

# setu set 模块

| 模块     | 说明                                      |
| :------- | ----------------------------------------- |
| withdraw | 撤回时间，值为秒                          |
| r18      | 是否发送r18，`on`或`true`，`off`或`false` |
| only_r18 | 只发送r18，`on`或`true`，`off`或`false`   |
| mode     | 发送方式，`0`正常，`1`转发，`2`大图       |

# setu su 模块

| 模块         | 说明                                                         |
| ------------ | ------------------------------------------------------------ |
| daily        | 修改每日获取涩图的次数                                       |
| freq         | 修改涩图发送冷却时间                                         |
| max          | 修改单次获取涩图的次数                                       |
| r18          | 是否开启全局r18，如果关闭则所有群组的r18模块都关闭，不影响每个群配置，`on`或`true`，`off`或`false` |
| proxy        | 是否使用本地代理8，`on`或`true`，`off`或`false`              |
| ban/dban     | 添加/移除黑名单用户                                          |
| admin/dadmin | 添加/移除白名单用户                                          |