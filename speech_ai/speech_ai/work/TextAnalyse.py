from pyecharts.charts import Line
from pyecharts.components import Table


class textanalyse():
    # 从MySQL取出最新的一条文本
    # def get_text(self):
    #     import pymysql

    #     # 创建数据库连接
    #     conn = pymysql.connect(
    #         host = '127.0.0.1', # 连接主机, 默认127.0.0.1 
    #         user = 'root',      # 用户名
    #         passwd = 'xxxxx',# 密码
    #         port = 3306,        # 端口，默认为3306
    #         db = 'test928',        # 数据库名称
    #         charset = 'utf8'    # 字符编码
    #     )

    #     # 生成游标对象 cursor
    #     cursor = conn.cursor()

    #     # 查询数据库版本
    #     cursor.execute('SELECT text from test_txt order by createdTime desc') # 返回值是查询到的数据数量
    #     # 通过 fetchall方法获得数据
    #     data = cursor.fetchone()
    #     cursor.close()  # 关闭游标
    #     conn.close()    # 关闭连接
    #     return data[0]

    # 获取url
    def get_url(self, theme):
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from bs4 import BeautifulSoup
        import time

        # 设置 Chrome 选项
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # 设置为无头模式

        # 创建 ChromeDriver 对象
        driver = webdriver.Chrome(chrome_options=chrome_options)
        url = 'https://www.baidu.com'
        driver.get(url)
        input = driver.find_element('id', 'kw')
        keys = '关于' + theme + '的演讲稿'
        input.send_keys(keys)
        search_btn = driver.find_element('id', 'su')
        search_btn.click()

        time.sleep(2)  # 在此等待 使浏览器解析并渲染到浏览器

        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        search_res_list = soup.select('.t')

        real_url_list = []
        # print(search_res_list)
        for el in search_res_list:
            js = 'window.open("' + el.a['href'] + '")'
            driver.execute_script(js)
            handle_this = driver.current_window_handle  # 获取当前句柄
            handle_all = driver.window_handles  # 获取所有句柄
            handle_exchange = None  # 要切换的句柄
            for handle in handle_all:  # 不匹配为新句柄
                if handle != handle_this:  # 不等于当前句柄就交换
                    handle_exchange = handle
            driver.switch_to.window(handle_exchange)  # 切换
            real_url = driver.current_url
            # print(real_url)
            real_url_list.append(real_url)  # 存储结果
            driver.close()
            driver.switch_to.window(handle_this)
        return real_url_list

    # 根据url获取内容
    def get_content(self, url_list):
        from urllib import response
        import requests
        from bs4 import BeautifulSoup
        import chardet  # 字符集检测
        from urllib.request import urlopen
        import re

        # 存储爬取的文本内容
        content_list = []
        for i in range(len(url_list)):
            try:
                header = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36'}
                url = url_list[i]
                response = requests.get(url, headers=header)
                # 判断网页编码格式
                content = urlopen(url).read()
                result = chardet.detect(content)
                response.encoding = result['encoding']
                print(response.status_code)
                html = response.text
                soup = BeautifulSoup(html, 'lxml')
                data = soup.find_all('p')

                # 临时存储单个结构
                temp_list = []
                for x in data:
                    if len(x.text) == 0:
                        continue
                    text = x.text
                    # print(text)
                    temp_list.append(text)
                    pass
                content_list.append(temp_list)
            except:
                # 跳过该url的操作
                continue
        # 将列表展开
        flat_list = [item for sublist in content_list for item in sublist]
        # 　转换为字符串
        str_content = ''.join(flat_list)
        # 剔除Unicode分隔符空格符等
        s = re.sub(r'[\u2002\u3000\n\xa0]+', '', str_content)
        return s

    def similarity(self, s1, s2):
        # s1为从database中读取的
        # s2为网络爬取的
        import jieba
        import math
        import re

        # 利用jieba分词与停用词表，将词分好并保存到向量中
        stopwords = []
        fstop = open('stopwords.txt', 'r', encoding='utf-8-sig')
        for eachWord in fstop:
            eachWord = re.sub("\n", "", eachWord)
            stopwords.append(eachWord)
        fstop.close()
        s1_cut = [i for i in jieba.cut(s1, cut_all=True) if (i not in stopwords) and i != '']
        s2_cut = [i for i in jieba.cut(s2, cut_all=True) if (i not in stopwords) and i != '']
        word_set = set(s1_cut).union(set(s2_cut))

        # 用字典保存两篇文章中出现的所有词并编上号
        word_dict = dict()
        i = 0
        for word in word_set:
            word_dict[word] = i
            i += 1

        # 根据词袋模型统计词在每篇文档中出现的次数，形成向量
        s1_cut_code = [0] * len(word_dict)

        for word in s1_cut:
            s1_cut_code[word_dict[word]] += 1

        s2_cut_code = [0] * len(word_dict)
        for word in s2_cut:
            s2_cut_code[word_dict[word]] += 1

        # 计算余弦相似度
        sum = 0
        sq1 = 0
        sq2 = 0
        for i in range(len(s1_cut_code)):
            sum += s1_cut_code[i] * s2_cut_code[i]
            sq1 += pow(s1_cut_code[i], 2)
            sq2 += pow(s2_cut_code[i], 2)

        try:
            result = round(float(sum) / (math.sqrt(sq1) * math.sqrt(sq2)), 3)
        except ZeroDivisionError:
            result = 0.0
        return result

    # 相似度均值函数
    def mean_similarity(self, topic, text_mysql):
        import numpy as np
        obj_mean_similarity = textanalyse()
        url_list = obj_mean_similarity.get_url(topic)
        text = obj_mean_similarity.get_content(url_list)

        length = len(text_mysql)
        split_list = []
        start = 0
        while start < len(text):
            split_list.append(text[start:start + length])
            start += length
        similarity = []
        for i in range(len(split_list)):
            similarity.append(obj_mean_similarity.similarity(text_mysql, str(split_list[i])))
        return np.mean(similarity)

    def emo_txt(self, text1):

        import re
        from jieba import lcut
        import pandas as pd

        text = re.sub('([。！？\?])([^”’])', r"\1\n\2", text1)  # 单字符断句符
        text = re.sub('(\.{6})([^”’])', r"\1\n\2", text)  # 英文省略号
        text = re.sub('(\…{2})([^”’])', r"\1\n\2", text)  # 中文省略号
        text = re.sub('([。！？\?][”’])([^，。！？\?])', r'\1\n\2', text)
        # 如果双引号前有终止符，那么双引号才是句子的终点，把分句符\n放到双引号后，注意前面的几句都小心保留了双引号
        text = text.rstrip()  # 段尾如果有多余的\n就去掉它
        # 很多规则中会考虑分号;，但是这里我把它忽略不计，破折号、英文双引号等同样忽略，需要的再做些简单调整即可。
        sentence_result = text.split("\n")
        # 存储单句分词结果的列表
        participles_list = []
        # 循环遍历每一个单句进行分词
        for i in range(len(sentence_result)):
            participles_list.append(lcut(sentence_result[i]))
            pass

        from pathlib import Path
        import os
        BaseDir = Path(__file__).resolve().parent.parent.parent

        temp = os.path.join(str(BaseDir), 'media', 'txt', 'stopwords.txt').replace("\\", "/")

        # 读取停用词列表
        with open(temp, 'r', encoding="utf8") as f:
            stop_words = f.read()
        # 对每一句话剔除停用词
        fliter_list = []
        for i in range(len(participles_list)):
            fliter_list.append([w for w in participles_list[i] if not w in stop_words])
        # 情感评分

        from pathlib import Path
        import os
        # 项目根目录
        BaseDir = Path(__file__).resolve().parent.parent.parent
        BaseDir = str(BaseDir).replace('\\', '/')

        df = pd.read_table(os.path.join(BaseDir, 'media', 'txt', 'BosonNLP_sentiment_score.txt').replace("\\", "/"),
                           sep=" ", names=['key', 'score'])
        # 提取出词
        key = df['key'].values.tolist()
        # 提取出分数
        score = df['score'].values.tolist()
        # 构造成一个字典
        score_dict = dict(zip(key, score))
        # 最终进行匹配的列表：fliter_list
        # 存单句分数的列表
        emo_list = []
        # 循环匹配计算单句得分
        for i in range(len(fliter_list)):
            score_list = [score[key.index(x)] for x in fliter_list[i] if (x in key)]
            emo_list.append(sum(score_list))
            pass
        return emo_list

    def emo_visual(self) -> Line:
        from pyecharts import options as opts
        from pyecharts.commons.utils import JsCode
        import pandas as pd

        obj_visual = textanalyse()
        emo_list = obj_visual.emo_txt()
        visualization_df = pd.DataFrame(emo_list, columns=['score'])
        x_axis = list(visualization_df.index)

        # 背景色
        background_color_js = """
        new echarts.graphic.RadialGradient(0.3, 0.3, 0.8, [{offset: 0,color: '#f7f8fa'}, 
        {offset: 1,color: '#cdd0d5'}])
        """
        # 线条样式
        linestyle_dic = {'normal': {
            'width': 4,
            'shadowColor': '#696969',
            'shadowBlur': 10,
            'shadowOffsetY': 10,
            'shadowOffsetX': 10,
        }
        }

        l1 = (
            Line(init_opts=opts.InitOpts(bg_color=JsCode(background_color_js)))
            .add_xaxis(xaxis_data=list(visualization_df.index))
            .add_yaxis(
                series_name="emo_score",
                y_axis=[round(float(i), 3) for i in emo_list],
                symbol_size=8,
                is_smooth=True,
                color="#009ad6",
            )
            # 系列配置项
            .set_series_opts(linestyle_opts=linestyle_dic,
                             areastyle_opts=opts.AreaStyleOpts(opacity=0.6),
                             label_opts=opts.LabelOpts(is_show=False),
                             markline_opts=opts.MarkLineOpts(data=[opts.MarkLineItem(type_="average")]),
                             markpoint_opts=opts.MarkPointOpts(
                                 data=[opts.MarkPointItem(type_="max"), opts.MarkPointItem(type_="min")],
                                 symbol_size=[65, 50],
                                 label_opts=opts.LabelOpts(position="inside", color="#fff", font_size=10)
                             ),
                             )
            # 通用配置项
            .set_global_opts(
                title_opts=opts.TitleOpts(
                    title='文章情感趋势',
                    pos_top='2%',
                    title_textstyle_opts=opts.TextStyleOpts(color='#4169E1', font_size=20)),
                tooltip_opts=opts.TooltipOpts(trigger="axis"),
                xaxis_opts=opts.AxisOpts(name="", type_="category",
                                         boundary_gap=True,
                                         axisline_opts=opts.AxisLineOpts(is_show=True,
                                                                         linestyle_opts=opts.LineStyleOpts(width=2,
                                                                                                           color='#DB7093')),
                                         axislabel_opts=opts.LabelOpts(rotate=45)),
                yaxis_opts=opts.AxisOpts(
                    axislabel_opts=opts.LabelOpts(formatter="{value} "),
                    is_scale=True,
                    name_textstyle_opts=opts.TextStyleOpts(font_size=12, font_weight='bold', color='#FF1493'),
                    splitline_opts=opts.SplitLineOpts(is_show=True,
                                                      linestyle_opts=opts.LineStyleOpts(type_='dashed')),
                    axisline_opts=opts.AxisLineOpts(is_show=False,
                                                    linestyle_opts=opts.LineStyleOpts(width=2, color='#DB7093'))
                ),
                # 图例样式
                legend_opts=opts.LegendOpts(is_show=True, pos_right='1%', pos_top='2%', legend_icon='roundRect'),
            )
        )
        return l1

    def TextCorection(self, Text):
        from datetime import datetime
        from wsgiref.handlers import format_date_time
        from time import mktime
        import hashlib
        import base64
        import hmac
        from urllib.parse import urlencode
        import json
        import requests
        class AssembleHeaderException(Exception):
            def __init__(self, msg):
                self.message = msg

        class Url:
            def __init__(this, host, path, schema):
                this.host = host
                this.path = path
                this.schema = schema
                pass

        class WebsocketDemo:
            def __init__(self, APPId, APISecret, APIKey, Text):
                self.appid = APPId
                self.apisecret = APISecret
                self.apikey = APIKey
                self.text = Text
                self.url = 'https://api.xf-yun.com/v1/private/s9a87e3ec'

            # calculate sha256 and encode to base64
            def sha256base64(self, data):
                sha256 = hashlib.sha256()
                sha256.update(data)
                digest = base64.b64encode(sha256.digest()).decode(encoding='utf-8')
                return digest

            def parse_url(self, requset_url):
                stidx = requset_url.index("://")
                host = requset_url[stidx + 3:]
                schema = requset_url[:stidx + 3]
                edidx = host.index("/")
                if edidx <= 0:
                    raise AssembleHeaderException("invalid request url:" + requset_url)
                path = host[edidx:]
                host = host[:edidx]
                u = Url(host, path, schema)
                return u

            # build websocket auth request url
            def assemble_ws_auth_url(self, requset_url, method="POST", api_key="", api_secret=""):
                u = self.parse_url(requset_url)
                host = u.host
                path = u.path
                now = datetime.now()
                date = format_date_time(mktime(now.timetuple()))
                # print(date)
                # date = "Thu, 12 Dec 2019 01:57:27 GMT"
                signature_origin = "host: {}\ndate: {}\n{} {} HTTP/1.1".format(host, date, method, path)
                # print(signature_origin)
                signature_sha = hmac.new(api_secret.encode('utf-8'), signature_origin.encode('utf-8'),
                                         digestmod=hashlib.sha256).digest()
                signature_sha = base64.b64encode(signature_sha).decode(encoding='utf-8')
                authorization_origin = "api_key=\"%s\", algorithm=\"%s\", headers=\"%s\", signature=\"%s\"" % (
                    api_key, "hmac-sha256", "host date request-line", signature_sha)
                authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')
                # print(authorization_origin)
                values = {
                    "host": host,
                    "date": date,
                    "authorization": authorization
                }

                return requset_url + "?" + urlencode(values)

            def get_body(self):
                body = {
                    "header": {
                        "app_id": self.appid,
                        "status": 3,
                        # "uid":"your_uid"
                    },
                    "parameter": {
                        "s9a87e3ec": {
                            # "res_id":"your_res_id",
                            "result": {
                                "encoding": "utf8",
                                "compress": "raw",
                                "format": "json"
                            }
                        }
                    },
                    "payload": {
                        "input": {
                            "encoding": "utf8",
                            "compress": "raw",
                            "format": "plain",
                            "status": 3,
                            "text": base64.b64encode(self.text.encode("utf-8")).decode('utf-8')
                        }
                    }
                }
                return body

            def get_result(self):
                request_url = self.assemble_ws_auth_url(self.url, "POST", self.apikey, self.apisecret)
                headers = {'content-type': "application/json", 'host': 'api.xf-yun.com', 'app_id': self.appid}
                body = self.get_body()
                response = requests.post(request_url, data=json.dumps(body), headers=headers)
                # print('onMessage：\n' + response.content.decode())
                tempResult = json.loads(response.content.decode())
                # print(base64.b64decode(tempResult['payload']['result']['text']).decode())
                return base64.b64decode(tempResult['payload']['result']['text']).decode()

        APPId = "xxxx"
        APISecret = "xxxx"
        APIKey = "xxxxxx"

        demo = WebsocketDemo(APPId, APISecret, APIKey, Text)
        result = demo.get_result()
        result_dict = json.loads(result)
        # 取出所有的键值对，判断哪些键有值并存储

        list_keys = list(result_dict.keys())
        list_values = list(result_dict.values())
        # 存储有值的键
        return_key_list = []

        for i in range(len(list_values)):
            if len(list_values[i]) != 0:
                temp = list_keys[list_values.index(list_values[i])]
                return_key_list.append(temp)
        # 取出键的值
        getvalue_list = []
        for i in range(len(return_key_list)):
            getvalue_list.append(result_dict.get(return_key_list[i])[0])
        # print(getvalue_list)
        return getvalue_list

    # 文本纠错
    def textcorrection(self, Text):
        obj_textcorrection = textanalyse()
        if len(Text) >= 1500:
            # 计算字符串中有多少段 1500 个字符的子串
            num_substrings = len(Text) // 1500
            # 将字符串分割为每 1500 个字符一段的列表
            substrings = [Text[i * 1500:(i + 1) * 1500] for i in range(num_substrings)]
            # 如果字符串最后剩余的长度大于 0，再添加一段长度不足 1500 个字符的子串
            if len(Text) % 1500 > 0:
                substrings.append(Text[num_substrings * 1500:])
            result_list = []
            for i in range(len(substrings)):
                tmp = obj_textcorrection.TextCorection(substrings[i])
                result_list.append(tmp)
            result = [x for sublist in result_list for x in sublist]
        else:
            result = obj_textcorrection.TextCorection(Text)
        return result

    # 病句绘图
    def Text_Correction_Table(self, Text) -> Table:
        from pyecharts.options import ComponentTitleOpts
        obj_Text_Correction_Table = textanalyse()
        error_list = obj_Text_Correction_Table.textcorrection(Text)
        table = Table()

        headers = ['下标', '原文', '修改', '病句类型']
        rows = error_list
        table.add(headers, rows)
        table.set_global_opts(
            title_opts=ComponentTitleOpts(title="文本纠错", subtitle='语病 错别字')
        )
        return table

    # 相似度绘图
    def Similarity_Table(self, topic) -> Table:
        from pyecharts.options import ComponentTitleOpts

        obj_Similarity_Table = textanalyse()
        similarity_value = obj_Similarity_Table.mean_similarity(topic)
        table = Table()
        headers = ['余弦相似度']
        rows = [[similarity_value]]
        table.add(headers, rows)
        table.set_global_opts(
            title_opts=ComponentTitleOpts(title="余弦相似度", subtitle='网络查重')
        )
        return table
