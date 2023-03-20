from pyecharts.charts import Bar, Grid, Line, Liquid, Page, Pie
from pyecharts.commons.utils import JsCode
from pyecharts.components import Table
from pyecharts.faker import Faker
from pyecharts.globals import ThemeType
import pyecharts.options as opts
from pyecharts.charts import Line, Timeline, Bar
from datetime import *
from pyecharts.options import ComponentTitleOpts
import numpy as np
from datetime import *
from pyecharts import options as opts #用以设置
from pyecharts.charts import Radar #导入雷达类
from matplotlib import pyplot as plt
import random
import pyecharts.options as opts
from pyecharts.charts import Line
import pymysql
import pandas as pd


class visualization:
 # ********************************数据库取值****************************************
    def get_data(self):
        conn = pymysql.connect(host='127.0.0.1',
                            user='root',
                            passwd='Kosm133164',
                            port=3306,
                            db='speech_score',
                            charset='utf8')

        cursor = conn.cursor()  # 生成游标对象
        sql = 'select * from speach_table'
        res1 = cursor.execute(sql)
        res2 = cursor.fetchall()
        # ********************************分割线********************************
        # 取出表中所有值
        table_list = []
        for i in range(len(res2)):
            table_list.append(list(res2[i]))
            pass
        # ********************************分割线*******************************
        # 将所有值转换成dataframe
        col = ['序号','演讲时间','演讲内容','发音流畅度','演讲完整度','发音声韵','发音调型','主题契合度','缀词冗余','总分','肢体动作得分']
        score = pd.DataFrame(table_list,columns=col)
        score = score.set_index(score.演讲时间)
        return score
    # ********************************表格****************************************
    def table_map(self) -> Table:
        obj1 = visualization()
    # 取出所用数据
        table_data = obj1.get_data()[['演讲时间','总分','发音流畅度','演讲完整度','发音声韵','发音调型','主题契合度','缀词冗余','肢体动作得分']]
        table_data = table_data.sort_index(ascending=False)
        # 绘制表格
        table = Table()

        # 表头
        headers = ['演讲时间','总分', '发音流畅度', '演讲完整度', '发音声韵', '发音调型', '主题契合度', '缀词冗余', '肢体动作得分']

        # 数据
        rows = []
        for i in range(len(table_data)):
            rows.append(list(table_data.iloc[i]))

        table.add(headers, rows)
        table.set_global_opts(
            title_opts=ComponentTitleOpts(title="演讲数据表")
        )
        return table
# ********************************条形图****************************************
    def visual_bar(self) -> Bar:
        obj2 = visualization()
        bar_data = obj2.get_data()[['发音流畅度','演讲完整度','发音声韵','发音调型','主题契合度','缀词冗余','肢体动作得分','总分']]
        bar_data = bar_data.sort_index(ascending=False)
        x = Faker.choose()
        tl = Timeline()
        for i in bar_data.index:
            sort_info = bar_data.loc[i]
            b1 = (
                Bar(init_opts=opts.InitOpts(
                    width='800px', height='600px',))
                .add_xaxis(list(sort_info.index)[-20:])
                .add_yaxis('', (sort_info.values).tolist()[-20:],
                        category_gap='30%',
                        itemstyle_opts={
                        'normal': {
                            'shadowColor': '#e37a89',  # 阴影颜色
                            'shadowBlur': 5,  # 阴影大小
                            'shadowOffsetY': 2,  # Y轴方向阴影偏移
                            'shadowOffsetX': 2,  # x轴方向阴影偏移
                            'borderColor': '#fff'
                            }
                        }
                        )
                .reversal_axis()
                .set_global_opts(
                    xaxis_opts=opts.AxisOpts(is_show=False),    
                    yaxis_opts=opts.AxisOpts(is_show=False,
                        axisline_opts=opts.AxisLineOpts(is_show=False),
                        axistick_opts=opts.AxisTickOpts(is_show=False)
                    ),
                    title_opts=opts.TitleOpts(
                        title=datetime.strftime(i,'%Y-%m-%d %H:%M')+'演讲得分',
                        pos_left='4%',
                        pos_top='9%',
                        title_textstyle_opts=opts.TextStyleOpts(
                            color='#e37a89', font_size=16)
                    ),
                    visualmap_opts=opts.VisualMapOpts(
                        is_show=False,
                        max_=20,
                        series_index=0,
                    ),
                )
                .set_series_opts(
                    itemstyle_opts={
                        "normal": {
                            "color": JsCode(
                                """new echarts.graphic.LinearGradient(0, 0, 0, 1, [{
                            offset: 0,
                            color: '#e37a89'
                        }, {
                            offset: 1,
                            color: '#e37a89'
                        }], false)"""
                            ),
                            "barBorderRadius": [25, 25, 25, 25],
                            "shadowColor": "rgb(0, 160, 221)",
                        }
                    },
                    label_opts=opts.LabelOpts(position="insideLeft",
                                                        font_size=10,
                                                        vertical_align='middle',
                                                        horizontal_align='left',
                                                        font_weight='bold',
                                                        formatter='{b}: {c}'))
            )

            tl.add(b1, "{}".format(i))    
        tl.add_schema(is_auto_play=True, play_interval=1500)  
        return tl
# ********************************雷达图****************************************    

    def RadarMap(self) -> Radar:
        obj3 = visualization()
        # 取出分数值
        radar_data = obj3.get_data()[['发音流畅度','演讲完整度','发音声韵','发音调型','主题契合度','缀词冗余','肢体动作得分']]

        # 元素升维
        Radar_array_list = []
        for i in range(len(radar_data)):
            Radar_array_list.append(np.array(list(radar_data.iloc[i])).reshape(1, len(radar_data.iloc[i])))
            pass

        # 元素转成普通列表
        Radar_Value_list = []
        for i in range(len(Radar_array_list)):
            Radar_Value_list.append(Radar_array_list[i].tolist())
            pass

        # 取出时间列表
        radar_datetime = []
        for i in range(len(radar_data.index)):
            radar_datetime.append(datetime.strftime(radar_data.index[i],  '%Y-%m-%d %H'))
            pass

        # 绘图
        radar1=(
            Radar()
            .add_schema(# 添加schema架构
                schema=[
                    opts.RadarIndicatorItem(name='发音流畅度',max_=100),# 设置指示器名称和最大值
                    opts.RadarIndicatorItem(name='演讲完整度',max_=100),
                    opts.RadarIndicatorItem(name='发音声韵',max_=100),
                    opts.RadarIndicatorItem(name='发音调型',max_=100),
                    opts.RadarIndicatorItem(name='主题契合度',max_=100),
                    opts.RadarIndicatorItem(name='缀词冗余',max_=100),
                    opts.RadarIndicatorItem(name='肢体动作得分',max_=100),
                ]
            )
            # .add(i,j,color='#e37a89') # 添加一条数据，参数1为数据名，参数2为数据，参数3为颜色
            # .add(table_datetime[7],Radar_Value_list[7],color=colors[7])
            .set_global_opts(title_opts=opts.TitleOpts(title='雷达图', pos_bottom=20))
        )
        for i,j in zip(radar_datetime, Radar_Value_list):
            radar1 = radar1.add(i, j, color=["#"+''.join([random.choice('0123456789ABCDEF') for j in range(6)])])
        return radar1
# ********************************折线图***************************************    

    def line_map(self) -> Line:
        obj4 = visualization()
        line_data = obj4.get_data()[['总分','发音流畅度','演讲完整度','发音声韵','发音调型','主题契合度','缀词冗余','肢体动作得分']]
        line_data = line_data.sort_index(ascending=False)
        # 取出时间列表作为坐标轴
        line_datetime = []
        for i in range(len(line_data.index)):
            line_datetime.append(datetime.strftime(line_data.index[i],  '%Y-%m-%d %H'))
            pass
        x_axis = line_datetime

        # 标签
        label = ['总分', '发音流畅度', '演讲完整度', '发音声韵', '发音调型', '主题契合度', '缀词冗余', '肢体动作得分']

        # 取出分数值
        total_score= line_data[label[0]]
        fluency_score = line_data[label[1]]
        integrity_score = line_data[label[2]]
        phone_score = line_data[label[3]]
        tone_score = line_data[label[4]]
        toipc_score = line_data[label[5]]
        affix_score = line_data[label[6]]
        body_score = line_data[label[7]]
        line=(
            Line()
            .add_xaxis(xaxis_data=x_axis)
            .add_yaxis(series_name=label[0],y_axis=total_score)
            .add_yaxis(series_name=label[1],y_axis=fluency_score)
            .add_yaxis(series_name=label[2],y_axis=integrity_score)
            .add_yaxis(series_name=label[3],y_axis=phone_score)
            .add_yaxis(series_name=label[4],y_axis=tone_score)
            .add_yaxis(series_name=label[5],y_axis=toipc_score)
            .add_yaxis(series_name=label[6],y_axis=affix_score)
            .add_yaxis(series_name=label[7],y_axis=body_score)
            
            .set_global_opts(title_opts=opts.TitleOpts(title="单项成绩", pos_bottom=20)
                            ,toolbox_opts=opts.ToolboxOpts(is_show=True, pos_right='40%')
                            ,legend_opts=opts.LegendOpts(
                                is_show=True,pos_right='60%'
                            )) 
        ) 
        return line