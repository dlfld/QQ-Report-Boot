import json

import requests
from nonebot import on_command
from nonebot.typing import T_State
from nonebot.adapters import Bot, Event

frend_status = on_command("研友统计", priority=5)


@frend_status.handle()
async def frend_status_(bot: Bot, event: Event, state: T_State):
    res = requests.get("http://10.23.71.70:5700/get_group_member_list?group_id=343659014").text
    res_j = json.loads(res)
    # print(res_j)
    count = 0
    res_data = {
        "计算机": 0,
        "网安": 0,
        "软工": 0,
        "电子信息": 0,
        "22级群友总共": 0
    }
    for member in res_j['data']:
        if "22" in member['card']:
            count += 1
            if "计算机" in member['card'] or "计科" in member['card'] or "计专" in member['card']:
                res_data['计算机'] += 1
            if "软工" in member['card'] or "软件工程" in member['card'] or "软" in member['card']:
                res_data['软工'] += 1
            if "网" in member['card'] or "网安" in member['card']:
                res_data['网安'] += 1
            if "电子信息" in member['card']:
                res_data['电子信息'] += 1
            if "22" in member['card']:
                res_data['22级群友总共'] += 1
            # print(member['card'])

    await frend_status.finish(str(res_data))
