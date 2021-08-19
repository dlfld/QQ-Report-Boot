import requests
from nonebot import on_command
from nonebot.typing import T_State
from nonebot.adapters import Bot, Event
from scrapy import Selector
import time
from bs4 import BeautifulSoup

from qqRobot.utils.MySqlConn import MyPymysqlPool

clock_report_ = on_command("打卡",priority=5)

@clock_report_.handle()
async def handle_first_receive(bot: Bot, event: Event, state: T_State):
    args = str(event.get_message()).strip()
    res = "请输入   打卡 学号#密码\n或者是 申请出校 学号#密码#事由#地点\n默认地点为双流，事由为学习"
    if args:
        args = args.replace('#', '#')
        state['number'] = args.split('#')[0]
        state['password'] = args.split('#')[1]
        number = state['number']
        password = state['password']
        sql = "replace into student value(%s,%s,%s)"
        param = (event.get_user_id(), number, password)
        MyPymysqlPool().insert(sql=sql, param=param)
        reason = ""
        location = ""
        if len(list(args.split('#'))) > 2:
            reason = args.split('#')[2]
            location = args.split('#')[3]
        res = clock_report(number, password, location, reason)
        print(res)
    else:
        sql = "select * from  student where qq = %s"
        param = (event.get_user_id(),)
        stu = MyPymysqlPool().getOne(sql=sql, param=param)
        if stu is False:
            res = "请输入   打卡 学号#密码 首次输入需要输入学号密码 后面使用时只需要发送命令：打卡"
        else:
            reason = ""
            location = ""
            res = clock_report(bytes.decode(stu['number']), bytes.decode(stu['password']), location, reason)
        print(res)
    await clock_report_.finish(str(res))

def clock_report(number, password, location, reason):
    flag = True
    try:
        params = ClockHandle().login(str(number), str(password))
    except:
        res = "密码错误"
        flag = False
        return res
    if flag:
        response = ClockHandle().clock(params, location, reason)
        res = str(response['result'])
        if "您今天已经打过卡了,不用再重复打了~" in res:
            res = res
        else:
            res = "声明：\n本程序只用于学习交流使用，如果身体感到不适，请前往教务处，如实填写异常信息。谎报身体状况，后果自行承担哦~\n" + res
    return res


class ClockMsg:
    cookie = ""
    url = ""


class ClockHandle:

    def login(self, txtId, txtMM):
        print(txtId + "\t" + txtMM)
        postData = {
            "txtId": txtId,
            "txtMM": txtMM,
            "WinW": 1536,
            "WinH": 824,
            "codeKey": 692032,
            "Login": "Check",
            "IbtnEnter.x": 49,
            "IbtnEnter.y": 49
        }
        print(postData)
        res1 = requests.get(
            url="http://login.cuit.edu.cn/Login/xLogin/Login.asp")
        res1.encoding = 'GBK'
        print(res1.headers)
        cookie = res1.headers['Set-Cookie']
        cookie = str(cookie).split(';')[0]
        # print(cookie)
        sel = Selector(text=res1.text)
        result = sel.css('#userlogin_body script ::text').extract_first()
        codeKey = str(result).split('\'')[1]
        postData['codeKey'] = int(codeKey)
        # print(postData)
        header2 = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:75.0) Gecko/20100101 Firefox/75.0",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
            "Connection": "keep-alive",
            "Host": "login.cuit.edu.cn",
            "Upgrade-Insecure-Requests": "1",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Origin": "http://login.cuit.edu.cn",
            "Referer": "http://login.cuit.edu.cn/Login/xLogin/Login.asp",
            "Cookie": str(cookie),
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        res2 = requests.post(url="http://login.cuit.edu.cn/Login/xLogin/Login.asp", data=postData, headers=header2,
                             allow_redirects=False)
        res2.encoding = 'GBK'
        # print(res2.text)
        # print("res2")
        # print(res2.headers)

        header3 = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:75.0) Gecko/20100101 Firefox/75.0",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
            "Connection": "keep-alive",
            "Host": "login.cuit.edu.cn",
            "Upgrade-Insecure-Requests": "1",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Referer": "http://login.cuit.edu.cn/Login/xLogin/Login.asp",
            "Cookie": str(cookie),
            "Cache-Control": "no-cache",
            "Pragma": "no-cache"
        }
        res3 = requests.get(url="http://login.cuit.edu.cn/Login/qqLogin.asp", headers=header3, allow_redirects=False)
        res3.encoding = "GBK"
        # print(res3.text)
        # print(res3.headers)

        header4 = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:75.0) Gecko/20100101 Firefox/75.0",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
            "Connection": "keep-alive",
            "Host": "jxgl.cuit.edu.cn",
            "Upgrade-Insecure-Requests": "1",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Referer": "http://login.cuit.edu.cn/Login/xLogin/Login.asp",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache"

        }
        res4 = requests.get(url="http://jxgl.cuit.edu.cn/jkdk", headers=header4)
        res4.encoding = "GBK"
        # print(res4.headers)
        # print(res4.text)

        header5 = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:75.0) Gecko/20100101 Firefox/75.0",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
            "Connection": "keep-alive",
            "Host": "jszx-jxpt.cuit.edu.cn",
            "Upgrade-Insecure-Requests": "1",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Referer": "http://jxgl.cuit.edu.cn/jkdk/",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "Cookie": str(cookie)

        }
        res5 = requests.get(url="http://jszx-jxpt.cuit.edu.cn/jxgl/xs/netks/sj.asp?jkdk=Y", headers=header5,
                            allow_redirects=False)
        res5.encoding = "GBK"
        # print(res5.headers)
        # print(res5.text)
        cookieN = res5.headers['Set-Cookie']
        cookieN = str(cookieN).split(';')[0]
        # print(cookieN)

        header6 = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:75.0) Gecko/20100101 Firefox/75.0",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
            "Connection": "keep-alive",
            "Host": "login.cuit.edu.cn",
            "Upgrade-Insecure-Requests": "1",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            # "Referer": "http://jszx-jxpt.cuit.edu.cn/Jxgl/Login/tyLogin.asp",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            # "Cookie": str(cookie)
        }
        res6 = requests.get(url="http://jszx-jxpt.cuit.edu.cn/Jxgl/UserPub/Login.asp?UTp=Xs", headers=header6,
                            allow_redirects=False)
        res6.encoding = "GBK"
        # print(res6.headers)
        # print(res6.text)

        #
        #
        header7 = {

            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
            "Connection": "keep-alive",
            "Host": "jszx-jxpt.cuit.edu.cn",
            "Accept": "text/html, application/xhtml+xml, image/jxr, */*",
            # "Cache-Control": "no-cache",
            # "Pragma": "no-cache",
            "Cookie": str(cookieN)
        }
        res7 = requests.get("http://jszx-jxpt.cuit.edu.cn/Jxgl/Login/tyLogin.asp", headers=header7)
        res7.encoding = "GBK"
        # print(res7.headers)
        # print(res7.text)
        sel = Selector(text=res7.text)
        osidV = sel.css('meta').extract()[1]
        sel2 = Selector(text=str(osidV))
        osidV = sel2.css('meta::attr(content)').extract_first()
        osidV = str(osidV).split('=')
        # print(str(osidV))
        url7 = str(osidV[1]) + "=" + str(osidV[2]) + "=" + str(osidV[3])
        # print(url7)
        header8 = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:75.0) Gecko/20100101 Firefox/75.0",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
            "Connection": "keep-alive",
            "Host": "login.cuit.edu.cn",
            "Upgrade-Insecure-Requests": "1",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",

            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "Cookie": str(cookie)
        }
        res8 = requests.get(url=url7, headers=header8, allow_redirects=False)
        res8.encoding = "GBK"
        # print(res8.headers)
        # print(res8.text)

        header9 = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:75.0) Gecko/20100101 Firefox/75.0",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
            "Connection": "keep-alive",
            "Host": "jszx-jxpt.cuit.edu.cn",
            "Upgrade-Insecure-Requests": "1",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",

            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "Cookie": str(cookieN)
        }
        res9 = requests.get(
            url="http://jszx-jxpt.cuit.edu.cn/Jxgl/Login/tyLogin.asp",
            headers=header9, allow_redirects=False)
        res9.encoding = "GBK"
        # print(res9.headers)

        header10 = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:75.0) Gecko/20100101 Firefox/75.0",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
            "Connection": "keep-alive",
            "Host": "login.cuit.edu.cn",
            "Upgrade-Insecure-Requests": "1",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Referer": "http://jszx-jxpt.cuit.edu.cn/Jxgl/Login/tyLogin.asp",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "Cookie": str(cookieN)
        }
        res10 = requests.get(url="http://jszx-jxpt.cuit.edu.cn/Jxgl/Login/syLogin.asp", headers=header10,
                             allow_redirects=False)
        res10.encoding = "GBK"
        # print(res10.headers)
        # print(res10.text)

        header11 = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:75.0) Gecko/20100101 Firefox/75.0",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
            "Connection": "keep-alive",
            "Host": "jszx-jxpt.cuit.edu.cn",
            "Upgrade-Insecure-Requests": "1",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",

            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "Cookie": str(cookieN)
        }
        res11 = requests.get(url="http://jszx-jxpt.cuit.edu.cn/Jxgl/UserPub/Login.asp?UTp=Xs&Func=Login",
                             headers=header11,
                             allow_redirects=False)
        res11.encoding = "GBK"
        # print(res11.headers)
        # print(res11.text)

        header12 = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:75.0) Gecko/20100101 Firefox/75.0",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
            "Connection": "keep-alive",
            "Host": "jszx-jxpt.cuit.edu.cn",
            "Upgrade-Insecure-Requests": "1",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",

            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "Cookie": str(cookieN)
        }
        res12 = requests.get(url="http://jszx-jxpt.cuit.edu.cn/Jxgl/Xs/MainMenu.asp", headers=header12,
                             allow_redirects=False)
        res12.encoding = "GBK"
        # print(res12.headers)
        # print(res12.text)

        header13 = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:75.0) Gecko/20100101 Firefox/75.0",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
            "Connection": "keep-alive",
            "Host": "jszx-jxpt.cuit.edu.cn",
            "Upgrade-Insecure-Requests": "1",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",

            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "Cookie": str(cookieN)
        }
        res13 = requests.get(url="http://jszx-jxpt.cuit.edu.cn/Jxgl/Xs/netks/sj.asp", headers=header13,
                             allow_redirects=False)
        res13.encoding = "GBK"
        # print("res13 header")
        # print(res13.headers)
        clock = res13.headers['Set-Cookie']
        clock = str(clock).split(";")[0]
        clockCookie = str(clock) + ";" + str(cookieN)
        sel = Selector(text=res13.text)
        bodys = sel.css('.tabThinM tbody').extract()[0]
        sel2 = Selector(text=str(bodys))
        newCommission = sel2.css('a::attr(href)').extract_first()
        newCommission = "http://jszx-jxpt.cuit.edu.cn/Jxgl/Xs/netKs/" + newCommission
        # print(newCommission)
        clockMsg = ClockMsg()
        clockMsg.cookie = clockCookie
        clockMsg.url = newCommission
        return clockMsg

    # 获取今天的工作状态
    def getWorkStatus(self, cookie):
        try:
            # cookie = "refreshCT=UserName=Xs%5F2017081180; ASPSESSIONIDSQQACRQB=GEODKDEDNLFGILAPAGEEEPJL"
            header1 = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:75.0) Gecko/20100101 Firefox/75.0",
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
                "Connection": "keep-alive",
                "Host": "jszx-jxpt.cuit.edu.cn",
                "Upgrade-Insecure-Requests": "1",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Referer": "http://jszx-jxpt.cuit.edu.cn/Jxgl/Xs/netKs/sj.asp?UTp=Xs&jkdk=Y",
                "Cache-Control": "no-cache",
                "Pragma": "no-cache",
                "Cookie": str(cookie)
            }
            session = requests.Session()
            res = session.get(url="http://jszx-jxpt.cuit.edu.cn/jxgl/xs/netks/sj.asp?jkdk=Y", headers=header1)
            res.encoding = "GBK"
            soup = BeautifulSoup(str(res.text), 'lxml')
            trs = soup.select(" tr[valign=top]")
            trs = trs[3:]
            sF21650_6 = ""
            for tr in trs:
                if "√" in str(tr) and "疫情防控——师生健康状态采集" in str(tr):
                    soup2 = BeautifulSoup(str(tr), 'lxml')
                    # print()

                    lostUrl = soup2.select_one("a")['href']
                    clockMsg_url = f"http://jszx-jxpt.cuit.edu.cn/Jxgl/Xs/netKs/{lostUrl}"
                    url4 = "http://jszx-jxpt.cuit.edu.cn/Jxgl/Xs/netKs/sjDb.asp?UTp=Xs&jkdk=Y&" + lostUrl
                    res4 = session.get(url=url4, allow_redirects=False)
                    res4.encoding = "GBK"
                    lostUrl = str(clockMsg_url).split("Y&")[1]
                    urledit = "http://jszx-jxpt.cuit.edu.cn/Jxgl/Xs/netKs/editSj.asp?UTp=Xs&Tx=33_1&" + \
                              str(clockMsg_url).split("Y&")[1]
                    # print(urledit)
                    header5 = {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:75.0) Gecko/20100101 Firefox/75.0",
                        "Accept-Encoding": "gzip, deflate",
                        "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
                        "Connection": "keep-alive",
                        "Host": "jszx-jxpt.cuit.edu.cn",
                        "Upgrade-Insecure-Requests": "1",
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                        "Referer": "http://jszx-jxpt.cuit.edu.cn/Jxgl/Xs/netKs/sj.asp?UTp=Xs&jkdk=Y",
                        "Cache-Control": "no-cache",
                        "Pragma": "no-cache",
                        "Cookie": str(cookie)
                    }
                    res5 = requests.get(url=urledit, headers=header5)
                    res5.encoding = "GBK"
                    # print(res5.text)
                    soup3 = BeautifulSoup(str(res5.text), 'lxml')
                    sF21650_6 = soup3.select_one("select[name=sF21650_6] option[selected]")['value']
                    break
                else:
                    continue
            return sF21650_6
        except Exception as e:
            return None

    def clock(self, clockMsg, location, reason):
        try:
            header1 = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:75.0) Gecko/20100101 Firefox/75.0",
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
                "Connection": "keep-alive",
                "Host": "jszx-jxpt.cuit.edu.cn",
                "Upgrade-Insecure-Requests": "1",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Referer": "http://jszx-jxpt.cuit.edu.cn/Jxgl/Xs/netKs/sj.asp?UTp=Xs&jkdk=Y",
                "Cache-Control": "no-cache",
                "Pragma": "no-cache",
                "Cookie": str(clockMsg.cookie)
            }
            res1 = requests.get(url=clockMsg.url, headers=header1, allow_redirects=False)
            res1.encoding = "GBK"
            # print(res1.headers)
            # print(clockMsg.url)

            lostUrl = str(clockMsg.url).split("Y&")[1]
            url2 = "http://jszx-jxpt.cuit.edu.cn/Jxgl/Xs/netKs/sjDb.asp?UTp=Xs&jkdk=Y&" + lostUrl
            res2 = requests.get(url=url2, headers=header1, allow_redirects=False)
            res2.encoding = "GBK"
            # print(res2.headers)
            # print(res2.text)
            header3 = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:75.0) Gecko/20100101 Firefox/75.0",
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
                "Connection": "keep-alive",
                "Host": "jszx-jxpt.cuit.edu.cn",
                "Upgrade-Insecure-Requests": "1",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Referer": "http://jszx-jxpt.cuit.edu.cn/Jxgl/Xs/MainMenu.asp",
                "Cache-Control": "no-cache",
                "Pragma": "no-cache",
                "Cookie": str(clockMsg.cookie)
            }
            res3 = requests.get(url="http://jszx-jxpt.cuit.edu.cn/Jxgl/Xs/netKs/sj.asp?UTp=Xs&jkdk=Y", headers=header3,
                                allow_redirects=False)
            res3.encoding = "GBK"
            # print(res3.headers)
            # print(res3.text)
            # print(res3.text)
            # un_clock =
            soup = BeautifulSoup(str(res3.text), 'lxml')
            # total_clocks = soup.select("td[align=center]")
            ttc = soup.select(" tr[valign=top]")
            total_clocks1 = ttc[2:]
            total_clocks = ttc[3:]
            # print(total_clocks)
            # print(total_clocks)
            nowTime = str(time.strftime('%m%d', time.localtime(time.time())))
            nowData = f"{nowTime}疫情防控——师生健康状态采集"
            if "√" in str(total_clocks1[0]) and str(nowData) in str(total_clocks1[0]):
                response = {
                    "username": "",
                    "result": "您今天已经打过卡了,不用再重复打了~"
                }
                return response
            user_clocked = 0
            user_unclocked = 0
            un_clock_title = "无"
            clock_probability = 100
            try:
                for a_clock in total_clocks:
                    if str(a_clock).__contains__("√"):
                        user_clocked += 1
                    else:
                        user_unclocked += 1
                        if user_unclocked == 1:
                            soup2 = BeautifulSoup(str(a_clock), 'lxml')
                            un_clock_title = soup2.select_one("td > a").text
                clock_probability = int((user_clocked / (user_unclocked + user_clocked)) * 100)
            except Exception as e:
                print(e)
            clock_detail = soup.select_one(".tabThinM  a").text
            url4 = "http://jszx-jxpt.cuit.edu.cn/Jxgl/Xs/netKs/sjDb.asp?UTp=Xs&jkdk=Y&" + lostUrl
            res4 = requests.get(url=url4, headers=header1, allow_redirects=False)
            res4.encoding = "GBK"
            urledit = "http://jszx-jxpt.cuit.edu.cn/Jxgl/Xs/netKs/editSj.asp?UTp=Xs&Tx=33_1&" + \
                      str(clockMsg.url).split("Y&")[1]
            # print(urledit)
            header5 = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:75.0) Gecko/20100101 Firefox/75.0",
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
                "Connection": "keep-alive",
                "Host": "jszx-jxpt.cuit.edu.cn",
                "Upgrade-Insecure-Requests": "1",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Referer": "http://jszx-jxpt.cuit.edu.cn/Jxgl/Xs/netKs/sj.asp?UTp=Xs&jkdk=Y",
                "Cache-Control": "no-cache",
                "Pragma": "no-cache",
                "Cookie": str(clockMsg.cookie)
            }
            res5 = requests.get(url=urledit, headers=header5)
            res5.encoding = "GBK"
            sel = Selector(text=res5.text)
            ObjId = sel.css('b ::text').extract_first()
            provence = sel.css('input[name="sF21650_2"]::attr(value)').extract_first()
            city = sel.css('input[name="sF21650_3"]::attr(value)').extract_first()
            xian = sel.css('input[name="sF21650_4"]::attr(value)').extract_first()

            if provence is None or provence == "":
                provence = "  "
            if city is None or city == "":
                city = "  "
            if xian is None or xian == "":
                xian = "  "
            # 到res5 之后就已经进入了打卡页面
            soup = BeautifulSoup(str(res5.text), 'lxml')
            try:
                now_located = soup.select("select[name=sF21650_1] option[selected]")[0]['value']
            except:
                now_located = "无"
            try:
                Transportation = soup.select("select[name=sF21649_1] option[selected]")[0]['value']
                TransportationSelect = soup.select("select[name=sF21649_1] option[selected]")[0].text
                if str(TransportationSelect).__contains__("请选择"):
                    Transportation = str("")
            except:
                Transportation = str("")
            if Transportation == "":
                Transportation = None
            # 是否去过北京,黑龙江地区
            try:
                SF48_1 = soup.select("select[name=sF21648_1] option[selected]")[0]['value']
            except:
                SF48_1 = "N"
            try:
                SF48_2 = soup.select("textarea[name=sF21648_2]")[0].text
            except:
                SF48_2 = " "
            try:
                SF48_3 = soup.select("select[name=sF21648_3] option[selected]")[0]['value']
            except:
                SF48_3 = "N"
            try:
                SF48_4 = soup.select("textarea[name=sF21648_4]")[0].text
            except:
                SF48_4 = " "
            try:
                SF48_5 = soup.select("select[name=sF21648_5] option[selected]")[0]['value']
            except:
                SF48_5 = "N"
            try:
                SF48_6 = soup.select("textarea[name=sF21648_6]")[0].text
            except:
                SF48_6 = " "
            ID = sel.css('input[name=Id]::attr(value)').extract_first()
            RsNum = sel.css('input[name=RsNum]::attr(value)').extract_first()
            Tx = sel.css('input[name=Tx]::attr(value)').extract_first()
            canTj = sel.css('input[name=canTj]::attr(value)').extract_first()
            isNeedAns = sel.css('input[name=isNeedAns]::attr(value)').extract_first()
            th_3 = sel.css('input[name=th_3]::attr(value)').extract_first()
            th_2 = sel.css('input[name=th_2]::attr(value)').extract_first()
            th_1 = sel.css('input[name=th_1]::attr(value)').extract_first()
            cxStYt = sel.css('input[name=cxStYt]::attr(value)').extract_first()
            SF48_N = soup.select("input[name=sF21648_N]")[0]['value']
            sF21650_6 = self.getWorkStatus(str(clockMsg.cookie))
            if sF21650_6 is None:
                sF21650_6 = 1
            postData = {
                "zw1": "",
                "zw2": "",
                "B2": "",
                "RsNum": str(RsNum),
                "Id": str(ID),
                "Tx": str(Tx),
                "canTj": str(canTj),
                "isNeedAns": str(isNeedAns),
                "UTp": "Xs",
                "ObjId": str(ObjId),
                "th_3": str(th_3),
                "wtOR_1": "N\|/\|/N\|/\|/N\|/",
                "wtOR_3": "6\|/\|/\|/\|/1\|/5\|/1\|/1\|/1\|/",
                "sF21648_1": str(SF48_1),
                "sF21648_2": str(SF48_2).encode("GBK"),
                "sF21648_3": str(SF48_3),
                "sF21648_4": str(SF48_4).encode("GBK"),
                "sF21648_5": str(SF48_5),
                "sF21648_6": str(SF48_6).encode("GBK"),
                "sF21648_N": str(SF48_N),
                "th_2": str(th_2),
                # "sF21649_1": str(Transportation),
                # "sF21649_2": "",
                # "sF21649_3": "",
                # "sF21649_4": "",
                # "sF21649_N": "4",
                "wtOR_2": "6\|/\|/\|/",
                "th_1": str(th_1),
                "cxStYt": str(cxStYt),
                "sF21650_1": str(now_located),
                "sF21650_2": str(provence).encode("GBK"),
                "sF21650_3": str(city).encode("GBK"),
                "sF21650_4": str(xian).encode("GBK"),
                "sF21650_5": "1",
                "sF21650_6": str(sF21650_6),
                "sF21650_7": "1",
                "sF21650_8": "1",
                "sF21650_9": "1",
                "sF21650_10": "",
                "sF21650_N": "10",
                "sF21912_1": str(location).encode("GBK"),
                "sF21912_2": str(reason).encode("GBK"),
                "sF21912_3": "",
                "sF21912_4": "",
                "sF21912_5": "",
                "sF21912_6": "",
                "sF21912_N": '6'
            }
            headerp = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:75.0) Gecko/20100101 Firefox/75.0",
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
                "Connection": "keep-alive",
                "Host": "jszx-jxpt.cuit.edu.cn",
                "Upgrade-Insecure-Requests": "1",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Referer": str(urledit),
                "Cache-Control": "max-age=0",
                "Pragma": "no-cache",
                "Cookie": str(clockMsg.cookie),
                "Content-Type": "application/x-www-form-urlencoded",
                "Origin": "http://jszx-jxpt.cuit.edu.cn"
            }
            # print(headerp)
            resP = requests.post("http://jszx-jxpt.cuit.edu.cn/Jxgl/Xs/netKs/editSjRs.asp", headers=headerp,
                                 data=postData,
                                 allow_redirects=True)
            status = resP.status_code
            resP.encoding = "GBK"
            sel = Selector(text=resP.text)
            name = sel.css('table').extract_first()
            sel = Selector(text=str(name))
            name = sel.css('p::text').extract()[0]
            name = str(name).replace("(", "")
            name = str(name).replace(")", "")
            soup = BeautifulSoup(str(resP.text), 'lxml')

            # print(clock_detail)
            locate = soup.select("select[name=sF21650_5] option[selected]")[0]
            is_success = str(locate).__contains__("一般地区")
            print(is_success)
            nowTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            if is_success:
                result = "--------------------------\n" + str(clock_detail) + "\n【" + str(
                    name) + "】:\n打卡成功!\n打卡时间：" + nowTime + "\n" \
                                                           "您最近" + str(len(total_clocks)) + "个打卡任务的打卡率为：" + str(
                    clock_probability
                ) + "%\n" \
                    "您最近未打卡：" + str(un_clock_title) + "\n"
            else:
                result = "--------------------------\n【" + str(
                    name) + "】:\n打卡失败,网络错误,请重试!\n打卡时间：" + nowTime + "\n"
            print(name)
            response = {
                "username": name,
                "result": result
            }
        except Exception as e:
            print(e)
            name = "打卡失败",
            result = "打卡失败,网络错误,请重试!"
            response = {
                "username": name,
                "result": result
            }

        return response
