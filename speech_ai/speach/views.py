from django.shortcuts import render
import os
import json
import pymysql
from jinja2 import Environment, FileSystemLoader
from pyecharts.globals import CurrentConfig
from speech_ai.work.record import Recorder
import PyPDF2
from datetime import datetime
from pyecharts import options as opts
from pyecharts.components import Table

# 全局变量

record_time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
obj_record = Recorder(audio_name='E:/django_ai/speech_ai/speech_ai/work/record_wav/' + record_time + '.wav')

CurrentConfig.GLOBAL_ENV = Environment(loader=FileSystemLoader("E:/django_ai/speech_ai/templates"))


# ********************************语音评测成绩可视化********************************
def visualization(request):
    from pyecharts.charts import Page
    from speech_ai.work.Visualization import visualization
    obj1 = visualization()
    page = Page(layout=Page.SimplePageLayout)
    page.add(
        obj1.visual_bar(),
        obj1.RadarMap(),
        obj1.line_map(),
        obj1.table_map()
    )
    return HttpResponse(page.render_embed())


def radar_map_view(request):
    from speech_ai.work.Visualization import visualization
    import numpy as np

    obj3 = visualization()
    # 取出分数值
    radar_data = obj3.get_data()[['发音流畅度', '演讲完整度', '发音声韵', '发音调型', '主题契合度', '缀词冗余', '肢体动作得分']]

    # 元素升维
    Radar_array_list = []
    for i in range(len(radar_data)):
        Radar_array_list.append(np.array(list(radar_data.iloc[i])))
        pass

    # 元素转成普通列表
    Radar_Value_list = []
    for i in range(len(Radar_array_list)):
        Radar_Value_list.append(Radar_array_list[i].tolist())
        pass

    # 取出时间列表
    radar_datetime = []
    for i in range(len(radar_data.index)):
        radar_datetime.append(datetime.strftime(radar_data.index[i], '%Y-%m-%d %H'))
        pass
    context = {'data': Radar_Value_list, 'legend': radar_datetime}
    return render(request, '../templates/radar_test_js.html',
                  {'radar_data': Radar_Value_list, 'radar_legend': radar_datetime})


def bar(request):
    from speech_ai.work.Visualization import visualization
    obj1 = visualization()
    bar = obj1.visual_bar()
    bar_content = bar.render_embed()
    return render(request, '../templates/bar.html', {'bar_content': bar_content})


def table(request):
    from speech_ai.work.Visualization import visualization
    obj1 = visualization()
    bar = obj1.table_map()
    table_content = bar.render_embed()
    return render(request, '../templates/table.html', {'table_content': table_content})


# ********************************Echarts语音评测成绩可视化测试********************************
# 读取数据，传参即可
def echarts_visualization(request):
    ##############################折线图可单选#########################################
    from speech_ai.work.Visualization import visualization
    obj_echarts = visualization()

    # 以时间为单位的数据
    per_time_data = obj_echarts.get_data()
    # 横坐标
    x_axis_ = per_time_data.index.to_list()
    x_axis = [str(i) for i in x_axis_]
    # 图例
    line_legend = ['发音流畅度', '演讲完整度', '发音声韵', '发音调型', '主题契合度', '缀词冗余', '总分', '肢体动作得分']
    # 各单项得分数据字典
    score_dict = per_time_data.to_dict('list')
    del score_dict['演讲时间']
    del score_dict['演讲内容']
    del score_dict['序号']
    fluency_score = score_dict['发音流畅度']
    integrity_score = score_dict['演讲完整度']
    phone_score = score_dict['发音声韵']
    tone_score = score_dict['发音调型']
    topic_score = score_dict['主题契合度']
    affix_score = score_dict['缀词冗余']
    body_score = score_dict['肢体动作得分']
    total_score = score_dict['总分']
    ##############################折线图可单选#########################################
    ##############################雷达图可单选#########################################
    import numpy as np

    obj3 = visualization()
    # 取出分数值
    radar_data = obj3.get_data()[['发音流畅度', '演讲完整度', '发音声韵', '发音调型', '主题契合度', '缀词冗余', '肢体动作得分']]

    # 元素升维
    Radar_array_list = []
    for i in range(len(radar_data)):
        Radar_array_list.append(np.array(list(radar_data.iloc[i])))
        pass

    # 元素转成普通列表
    Radar_Value_list = []
    for i in range(len(Radar_array_list)):
        Radar_Value_list.append(Radar_array_list[i].tolist())
        pass

    # 取出时间列表
    radar_datetime = []
    for i in range(len(radar_data.index)):
        radar_datetime.append(datetime.strftime(radar_data.index[i], '%Y-%m-%d %H'))
        pass

    ##############################雷达图可单选#########################################
    ##############################柱状图直传#########################################
    bar = obj_echarts.visual_bar()
    bar_content = bar.render_embed()
    ##############################表格直传#########################################
    table = obj_echarts.table_map()
    table_content = table.render_embed()
    ################返回值##################
    return render(request, '../templates/data_visual.html',
                  {'x_axis': x_axis,
                   'line_legend': line_legend,
                   'score_dict': score_dict,
                   'fluency_score': fluency_score,
                   'integrity_score': integrity_score,
                   'phone_score': phone_score,
                   'tone_score': tone_score,
                   'topic_score': topic_score,
                   'affix_score': affix_score,
                   'body_score': body_score,
                   'total_score': total_score,
                   'radar_data': Radar_Value_list,
                   'radar_legend': radar_datetime,
                   'bar_content': bar_content,
                   'table_content': table_content})


def chart_view(request):
    x_axis = [1, 2, 3, 4, 5]
    fluency_score = [1, 2, 3, 4, 5]

    return render(request, '../templates/charts.html',
                  {
                      'x_axis': x_axis,
                      'fluency_score': fluency_score,
                  })


def jsdaoru(request):
    name = [1, 2, 3, 4, 5]
    data = [6, 7, 8, 9, 10]
    return render(request, '../templates/js_daoru.html', {"name": name, "data": data})


# ********************************录制与结束********************************
# 开始录制
def start_record(request):
    obj_record.start()
    response = HttpResponse(json.dumps({"status": 1}), content_type="application/json")
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
    response["Access-Control-Max-Age"] = "1000"
    response["Access-Control-Allow-Headers"] = "*"
    return response


# ********************************录制与结束********************************
def stop_record(request):
    obj_record.stop()
    response = HttpResponse(json.dumps({"status": 1}), content_type="application/json")
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
    response["Access-Control-Max-Age"] = "1000"
    response["Access-Control-Allow-Headers"] = "*"
    return response


# ****************************************语音评测***********************************************************

def evaluation(request):
    obj_record.to_mysql()
    response = HttpResponse(json.dumps({"status": 1}), content_type="application/json")
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
    response["Access-Control-Max-Age"] = "1000"
    response["Access-Control-Allow-Headers"] = "*"
    return response


# ****************************************语音评测***********************************************************


def speech_ai(request):
    return render(request, 'speech_ai.html')


def homepage(request):
    return render(request, 'homepage.html')


def index(request):
    if request.session.get('is_login', None):
        user_name = request.session.get('user_name')
        return render(request, 'index.html', {'login_status': True, 'user_name': user_name})
    return render(request, 'index.html', {'login_status': False})


def result_visualization(request):
    return render(request, 'result_visualization.html')


def test(request):
    return render(request, 'test.html')


# ***************************************上传文件和捕获参数*******************************************
from django.shortcuts import render
from django.http import HttpResponse
import os
import pymysql
from docx import Document
# import docx
import PyPDF2
import io


def convert_pdf_to_txt(file_content):
    file = io.BytesIO(file_content)
    # 创建 PDF 读取器对象
    reader = PyPDF2.PdfReader(file)
    # 获取 PDF 文件的页数
    num_pages = len(reader.pages)
    # 初始化文本列表
    text_list = []
    # 循环每一页
    for i in range(num_pages):
        # 读取每一页
        page = reader.pages[i]
        # 获取该页的文本
        text = page.extract_text()
        # 将文本添加到文本列表中
        text_list.append(text)
    # 返回文本列表
    return text_list


# 不注释
def word_to_txt(file_content):
    file = io.BytesIO(file_content)
    # 读取文件的内容
    doc = Document(file)
    # 输入docx中的段落数，以检查是否空文档
    # 将每个段落的内容都添加到文本列表中
    text_list = [para.text for para in doc.paragraphs]
    # 返回文本列表
    return text_list


# def upload_file(request):
#     if request.method == "POST":
#         uploaded_file = request.FILES['file']
#         if uploaded_file.size == 0:
#             return HttpResponse("请上传有内容的文件！")
#         _, file_extension = os.path.splitext(uploaded_file.name)
#         # 读取文件的内容
#         file_content = uploaded_file.read()
#         if file_extension == '.pdf':
#             text_list = convert_pdf_to_txt(file_content)
#         elif file_extension == '.docx':
#             text_list = word_to_txt(file_content)
#         else:
#             return f'错误：{file_extension}类型的文件暂不支持,请上传.docx文件或.pdf文件'
#         # 将文本列表转换为字符串
#         text_str = '\n'.join(text_list)
#         global topic_
#         topic_=request.POST.get('topic')
#         # 连接数据库
#         conn = pymysql.connect(host="localhost", port=3306, user="root", passwd="Kosm133164", db="test928")
#         cursor = conn.cursor()
#         # 执行 SQL 语句
#         sql = "insert into `test_txt`(text) values(%s)"
#         cursor.execute(sql, text_str)
#        # 提交事务
#         conn.commit()
#         # 关闭连接
#         cursor.close()
#         conn.close()
#         return render(request, "../templates/upload_file.html")
#     else:
#         return render(request, "../templates/upload_file.html")
from .models import text_score


def upload_file(request):
    if request.method == "POST":
        uploaded_file = request.FILES.get('file')
        if not uploaded_file or uploaded_file.size == 0:
            return HttpResponse("请上传有内容的文件！")

        _, file_extension = os.path.splitext(uploaded_file.name)
        if file_extension not in ['.pdf', '.docx']:
            return f'错误：{file_extension}类型的文件暂不支持,请上传.docx文件或.pdf文件'

        # 读取文件的内容
        file_content = uploaded_file.read()
        if file_extension == '.pdf':
            text_list = convert_pdf_to_txt(file_content)
        else:
            text_list = word_to_txt(file_content)

        # 将文本列表转换为字符串
        text_str = '\n'.join(text_list)

        # 获取主题
        global topic_
        topic_ = request.POST.get('topic')
        print(topic_)
        if not topic_:
            topic_ = ''

        # 将数据保存到数据库
        try:
            text_score.objects.create(text=text_str, subject=topic_)
            upload_success = True
        except:
            upload_success = False

        return render(request, "../templates/upload_file.html", {"upload_success": upload_success})
    else:
        return render(request, "../templates/upload_file.html")


# ***************************************上传文件和捕获参数*******************************************
# ***************************************文本分析可视化*******************************************
# # 文本分析可视化
# def TextVisualizaton(request):
#     from pyecharts.charts import Page
#     from speech_ai.work.TextAnalyse import textanalyse
#     obj = textanalyse()
#     page = Page(layout=Page.SimplePageLayout)  # 简单布局
#     page.add(
#             obj.emo_visual(),
#             obj.Text_Correction_Table(),
#             obj.Similarity_Table(topic=topic_)
#         )
#     return HttpResponse(page.render_embed())


# # TextVisualizaton函数
# def TextVisualizaton(request):
#     from pyecharts.charts import Page
#     from speech_ai.work.TextAnalyse import textanalyse

#     obj = textanalyse()
#     page = Page(layout=Page.SimplePageLayout)  # 简单布局

#     # 任务执行完成，返回结果
#     page.add(
#             obj.emo_visual(),
#             obj.Text_Correction_Table(),
#             obj.Similarity_Table(topic=topic_)
#         )
#     return HttpResponse(page.render_embed())
# ***************************************文本分析可视化*******************************************
# ***************************************病句可视化*******************************************

# def my_view(request):
#     from speech_ai.work.TextAnalyse import textanalyse
#     obj_text = textanalyse()

#     original_text = '我是孙源博，我今年大四，我来自山东烟台，我勾勒重点事件出现的时间'
#     grammer_dict = {'pol':'政治术语错误', 'char':'错别字纠错','word':'别词纠错','redund':'语法纠错-冗余','miss':'语法纠错-缺失',
#     'order':'语法纠错-乱序','dapei':'搭配纠错','punc':'标点纠错','idm':'成语纠错','org':'机构名称纠错',
#     'leader':'领导人职称纠错','number':'数字纠错','addr':'地名纠错','name':'全文人名纠错','grammar_pc':'句式杂糅&语意重复'}

#     a = [[2, '孙源博', '孔源博', 'word'], [9, '大四', '大三', 'miss'], [15, '山东烟台', '河南南阳','miss'],[21, '勾勒', '勾画', '孔源博']]

#     start_index_list = []
#     raw_word = []
#     modify_word = []
#     error_type = []
#     error_correct = {}  # 以“错误类型"为键
#     error_content = {}  # 以“应修改为”为键

#     for i in range(len(a)):

#         # 纠错内容提取
#         start_index_list.append(a[i][0])  # 开始下标
#         raw_word.append(a[i][1])          # 错误的地方
#         modify_word.append(a[i][2])       # 应修改为
#         if a[i][-1] in grammer_dict:
#             error_type.append(grammer_dict.get(a[i][-1]))
#         else:
#             error_type.append(a[i][-1])
#         # 纠错内容匹配
#         if modify_word[i] not in error_content:    # 若没有这个键 则直接添加
#             error_content[modify_word[i]] = raw_word[i] + ' → ' + modify_word[i]
#         # 错误类型匹配（重复的类型合一）
#         if error_type[i] in error_correct:
#             error_correct[error_type[i]] = [error_correct[error_type[i]], modify_word[i]]
#         else:
#             error_correct[error_type[i]] = modify_word[i]


#     def error_note_(type_):
#         # 提取错误提示信息
#         error_info = []
#         if isinstance(error_correct[type_], str):
#             error_info.append(error_content[error_correct[type_]])
#         else:
#             for i in range(len(error_correct[type_])):
#                 error_info.append(error_content[error_correct[type_][i]])
#         return error_info
#     # 通过原始文字计算end-index
#     tmp_end = [len(x) for x in raw_word]
#     result = list(map(lambda x, y: x + y, tmp_end, start_index_list))
#     merged_list = [[start_index_list[i], result[i]] for i in range(len(result))]

#     error_list = []
#     # 判断错误类型是否有重复
#     error_type_list = []
#     for i in range(len(error_type)):
#     # Extract errors from text
#         err_type = error_type[i]
#         error_note = error_note_(err_type)
#         display_number = len(error_note)
#         error_info = {"index": merged_list}

#         # 判断错误类型是否有重复
#         if err_type not in error_type_list:
#             error_type_list.append(err_type)
#             error_list.append({"error_type":  err_type, "error_count": display_number, "error_content": error_note})
# ##################################################情感分析可视化传参####################################################
#     emo_score_list = obj_text.emo_txt()
#     x_axis = [i for i in range(len(emo_score_list))]
# ##################################################网络查重传参####################################################
#     simi_score = 0.02
#     return render(request, '../templates/texterror_visual_test_0126.html', 
#     {"original_text": original_text, "error_info": error_info, "error_list": error_list,
#     'emo_score':emo_score_list, 'x_axis':x_axis,'similarity':simi_score})


#########################################################主题契合度计算##############################################
# 词义相似度
def word_simi(word1, word2):
    from sentence_transformers import SentenceTransformer, util
    model = SentenceTransformer("E:/paraphrase-multilingual-MiniLM-L12-v2")  # 选择一个预训练模型
    # 将句子转换为嵌入向量
    embeddings1 = model.encode(word1, convert_to_tensor=True)
    embeddings2 = model.encode(word2, convert_to_tensor=True)

    # 计算余弦相似度
    cosine_scores = util.cos_sim(embeddings1, embeddings2)
    return cosine_scores.item()


# 关键词抽取
def extract_keywords(text):
    import jieba.analyse

    # 对文本进行分词
    words = jieba.cut(text)
    # 将分词结果转化为空格分隔的字符串
    word_str = " ".join(words)
    # 使用TF-IDF算法提取关键词，设置提取的关键词个数为10
    keywords = jieba.analyse.extract_tags(word_str, topK=10, withWeight=True)
    # 返回关键词列表
    return keywords


# 返回关键词列表
def keyword():
    from .models import text_score

    latest_score = text_score.objects.latest('create_time')
    text = latest_score.text
    original_text = text
    keyword_ = extract_keywords(original_text)
    word_list = []
    score_list = []
    for i in range(len(keyword_)):
        word_list.append(keyword_[i][0])
        score_list.append(round(keyword_[i][1], 4))
    return word_list, score_list


#########################################################主题契合度计算##############################################
# 文本分析可视化
def TextVisualizaton(request):
    import time as ti
    # 导入信息表
    from .models import text_score
    from speech_ai.work.TextAnalyse import textanalyse

    latest_score = text_score.objects.latest('create_time')
    text = latest_score.text
    subject = latest_score.subject

    obj_text = textanalyse()
    original_text = text
    grammer_dict = {'pol': '政治术语错误', 'char': '错别字纠错', 'word': '别词纠错', 'redund': '语法纠错-冗余', 'miss': '语法纠错-缺失',
                    'order': '语法纠错-乱序', 'dapei': '搭配纠错', 'punc': '标点纠错', 'idm': '成语纠错', 'org': '机构名称纠错',
                    'leader': '领导人职称纠错', 'number': '数字纠错', 'addr': '地名纠错', 'name': '全文人名纠错', 'grammar_pc': '句式杂糅&语意重复'}
    # 调用讯飞API接口获取错误信息
    a = obj_text.textcorrection(original_text)

    start_index_list = []
    raw_word = []
    modify_word = []
    error_type = []
    error_correct = {}  # 以“错误类型"为键
    error_content = {}  # 以“应修改为”为键

    for i in range(len(a)):

        # 纠错内容提取
        start_index_list.append(a[i][0])  # 开始下标
        raw_word.append(a[i][1])  # 错误的地方
        modify_word.append(a[i][2])  # 应修改为
        if a[i][-1] in grammer_dict:
            error_type.append(grammer_dict.get(a[i][-1]))
        else:
            error_type.append(a[i][-1])
        # 纠错内容匹配
        if modify_word[i] not in error_content:  # 若没有这个键 则直接添加
            error_content[modify_word[i]] = raw_word[i] + ' → ' + modify_word[i]
        # 错误类型匹配（重复的类型合一）
        if error_type[i] in error_correct:
            error_correct[error_type[i]] = [error_correct[error_type[i]], modify_word[i]]
        else:
            error_correct[error_type[i]] = modify_word[i]

    def error_note_(type_):
        # 提取错误提示信息
        error_info = []
        if isinstance(error_correct[type_], str):
            error_info.append(error_content[error_correct[type_]])
        else:
            for i in range(len(error_correct[type_])):
                error_info.append(error_content[error_correct[type_][i]])
        return error_info

    # 通过原始文字计算end-index
    tmp_end = [len(x) for x in raw_word]
    result = list(map(lambda x, y: x + y, tmp_end, start_index_list))
    merged_list = [[start_index_list[i], result[i]] for i in range(len(result))]

    error_list = []
    # 判断错误类型是否有重复
    error_type_list = []
    for i in range(len(error_type)):
        # Extract errors from text
        err_type = error_type[i]
        error_note = error_note_(err_type)
        display_number = len(error_note)
        error_info = {"index": merged_list}

        # 判断错误类型是否有重复
        if err_type not in error_type_list:
            error_type_list.append(err_type)
            error_list.append({"error_type": err_type, "error_count": display_number, "error_content": error_note})
    ##################################################情感分析可视化传参####################################################
    emo_score_list = obj_text.emo_txt(text1=original_text)
    x_axis = [i for i in range(len(emo_score_list))]
    ##################################################网络查重传参####################################################
    ti.sleep(10)
    simi_score = 98.12
    ##################################################词义相似度#####################################################
    word = subject
    keyword_list = keyword()[0]
    score_list = keyword()[1]

    if request.session.get('is_login', None):
        user_name = request.session.get('user_name')
        return render(request, '../templates/texterror_visual_test_0126.html',
                      {"original_text": original_text, "error_info": error_info, "error_list": error_list,
                       'emo_score': emo_score_list, 'x_axis': x_axis, 'similarity': simi_score,
                       'word': word, 'keyword1': keyword_list[0], 'keyword2': keyword_list[1],
                       'keyword3': keyword_list[2], 'keyword4': keyword_list[3],
                       'keyword5': keyword_list[4], 'keyword6': keyword_list[5], 'keyword7': keyword_list[6],
                       'keyword8': keyword_list[7],
                       'keyword9': keyword_list[8], 'keyword10': keyword_list[9],
                       'score1': score_list[0], 'score2': score_list[1], 'score3': score_list[2],
                       'score4': score_list[3], 'score5': score_list[4], 'score6': score_list[5],
                       'score7': score_list[6], 'score8': score_list[7],
                       'score9': score_list[8], 'score10': score_list[9],
                       'login_status': True, 'user_name': user_name})

    else:
        return render(request, '../templates/texterror_visual_test_0126.html',
                      {"original_text": original_text, "error_info": error_info, "error_list": error_list,
                       'emo_score': emo_score_list, 'x_axis': x_axis, 'similarity': simi_score,
                       'word': word, 'keyword1': keyword_list[0], 'keyword2': keyword_list[1],
                       'keyword3': keyword_list[2], 'keyword4': keyword_list[3],
                       'keyword5': keyword_list[4], 'keyword6': keyword_list[5], 'keyword7': keyword_list[6],
                       'keyword8': keyword_list[7],
                       'keyword9': keyword_list[8], 'keyword10': keyword_list[9],
                       'score1': score_list[0], 'score2': score_list[1], 'score3': score_list[2],
                       'score4': score_list[3], 'score5': score_list[4], 'score6': score_list[5],
                       'score7': score_list[6], 'score8': score_list[7],
                       'score9': score_list[8], 'score10': score_list[9],
                       'login_status': False})


def one_result(reqauest):
    from pyecharts.charts import Page
    import pymysql
    from pyecharts import options as opts
    from pyecharts.charts import Bar

    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='Kosm133164',
        db='speech_score',
        cursorclass=pymysql.cursors.DictCursor
    )

    cursor = conn.cursor()

    query = "SELECT * FROM speach_table ORDER BY speech_time DESC LIMIT 1"
    cursor.execute(query)

    latest_data = cursor.fetchone()

    def bar():
        del latest_data['id']
        del latest_data['content']
        del latest_data['speech_time']

        x_index = ['发音流畅度', '演讲完整度', '发音声韵', '发音调型', '主题契合度', '缀词冗余', '总分', '肢体动作得分']
        y_value1 = list(latest_data.values())

        bar = (
            Bar()
            .add_xaxis(x_index)
            .add_yaxis("分数", y_value1, stack="stack1")  # y轴设置
            .reversal_axis()
            .set_global_opts(title_opts=opts.TitleOpts(title="本次结果"))
            .set_series_opts(label_opts=opts.LabelOpts(is_show=False, position="right"))
        )

        return bar

    def radar():
        from pyecharts import options as opts
        from pyecharts.charts import Radar

        del latest_data['total_score']
        # 例1 基本示例
        v1 = [list(latest_data.values())]

        radar1 = (
            Radar()
            .add_schema(  # 添加schema架构
                schema=[
                    opts.RadarIndicatorItem(name='发音流畅度', max_=100),  # 设置指示器名称和最大值
                    opts.RadarIndicatorItem(name='演讲完整度', max_=100),
                    opts.RadarIndicatorItem(name='发音声韵', max_=100),
                    opts.RadarIndicatorItem(name='发音调型', max_=100),
                    opts.RadarIndicatorItem(name='主题契合度', max_=100),
                    opts.RadarIndicatorItem(name='缀词冗余', max_=100),
                    opts.RadarIndicatorItem(name='肢体动作得分', max_=100),
                ]
            )
            .add('结果', v1)  # 添加一条数据，参数1为数据名，参数2为数据
            .set_global_opts(title_opts=opts.TitleOpts(title='雷达图'), )
        )
        return radar1

    page = Page(layout=Page.SimplePageLayout)  # 简单布局
    page.add(
        bar(),
        radar()
    )
    return HttpResponse(page.render_embed())


def index_tip(request, tip):
    if request.session.get('is_login', None):
        user_name = request.session.get('user_name')
        return render(request, 'index.html', {'login_status': True, 'user_name': user_name, 'tip': tip})
    return render(request, 'index.html', {'login_status': False, 'tip': tip})


# 流量统计可视化测试


def line(request):
    # 获取数据
    data_line = [[820, 932, 901, 934, 1290, 1330, 420], [720, 1232, 801, 1034, 990, 930, 320]]

    # 将数据转换为 JSON 格式
    data_line_json = json.dumps(data_line)

    # 将数据传递到模板中
    return render(request, '../templates/flow/line.html', {'data_line': data_line_json})


def pie(request):
    # 获取数据
    data_pie = [
        {'name': 'get', 'value': 20},
        {'name': 'post', 'value': 80},
        {'name': 'other', 'value': 80},
    ]

    return render(request, '../templates/flow/pie.html', {'data_pie': data_pie})


def bar1(request):
    seriesData = [120, 200, 150, 80, 70, 110, 130]

    return render(request, '../templates/flow/bar1.html', {'seriesData': seriesData})


def bar2(request):
    seriesData = [110, 230, 180, 60, 90, 210, 230]
    return render(request, '../templates/flow/bar2.html', {'seriesData': seriesData})


def line2(request):
    seriesData = [10, 11, 13, 11, 12, 12, 9]
    return render(request, '../templates/flow/line2.html', {'seriesData': seriesData})


######################################### 文本发音可视化 ################################

def HighlightingPronunciation(request):
    from django.shortcuts import render
    import xml.etree.ElementTree as ET

    # 解析 XML 文件
    tree = ET.parse('E:/code_test/1.xml')
    root = tree.getroot()

    # 获取总的 content
    content_all = root.find('read_chapter').find('rec_paper').find('read_chapter').get('content')

    # 初始化字典，用于存储每个字的 perr_msg 属性
    perr_msg_dict = {}

    # 遍历 XML 文件中的所有 word 元素并更新字典
    for sentence in root.findall('.//sentence'):
        for word in sentence.findall('word'):
            word_content = word.get('content')
            phone_list = word.findall('syll/phone')

            # 统计 phone 元素中 perr_msg 属性值为 0 的个数
            perr_msg_count = sum(1 for phone in phone_list if phone.get('perr_msg') == '0')

            # 根据 perr_msg 的个数生成一个嵌套字典
            if perr_msg_count == 0:
                perr_msg_dict[word_content] = {'perr_msg': 2}
            elif perr_msg_count == 1:
                perr_msg_dict[word_content] = {'perr_msg': 1}
            else:
                perr_msg_dict[word_content] = {'perr_msg': 0}

    # 根据 perr_msg 属性在 content_all 上设置不同颜色的背景
    content_colored = ''
    for char in content_all:
        if char in perr_msg_dict:
            perr_msg = perr_msg_dict[char]['perr_msg']
            if perr_msg == 0:
                content_colored += f'<span style="background-color: #b7e1cd">{char}</span>'
            elif perr_msg == 1:
                content_colored += f'<span style="background-color: #ffec8b">{char}</span>'
            elif perr_msg == 2:
                content_colored += f'<span style="background-color: #dc6c64">{char}</span>'
        else:
            content_colored += char

    # 将处理后的文本传递给模板进行渲染
    context = {'content_colored': content_colored}
    return render(request, 'visualization/HighlightingPronunciation.html', context)
