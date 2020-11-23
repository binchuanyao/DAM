# -*- coding: utf-8 -*-

import calendar
from datetime import datetime
from warnings import simplefilter

# import numpy as np
import pandas as pd

from config import *

simplefilter(action='ignore', category=FutureWarning)  # ignore FutureWarning


class Calculate:
    def __init__(self):
        self.cols = ['static_date', 'SKU_ID', 'sku_name', 'sku_state', 'warehouse',
                     'I_class', 'II_class', 'III_class', 'IV_class',
                     'weight', 'long', 'width', 'height',
                     'fullCaseUnit', 'ctn_long', 'ctn_width', 'ctn_height',
                     'monthly_stock_cumu_qty', 'monthly_stock_cumu_days',
                     'monthly_deli_cumu_qty', 'monthly_deli_cumu_times', 'monthly_deli_cumu_days',
                     'monthly_rec_cumu_qty', 'monthly_rec_cumu_times', 'monthly_rec_cumu_days',
                     'static_stock_qty', 'warehouse_cate', 'country', 'expiry', 'good_property'
                     ]
        self.df = pd.DataFrame(columns=self.cols)

    def correct_missing_data(self):
        """
        修正缺失数据，透视类目补全
        :return:
        """
        pass

    def classify(self):
        """
        件型分级、P&C分级，托件数&料箱件数等
        :return:
        """
        pass

    def calculate_stock(self):
        """
        计算 库存相关字段
        :return:
        """
        pass

    def calculate_outbound(self):
        """
        计算 出库相关字段
        :return:
        """
        pass

    def calculate_inbound(self):
        """
        计算 入库相关字段
        :return:
        """
        pass

    def get_category_correction_data(self):
        """
        透视类别数据，用于按类别补全缺失数据
        :return:
        """
        pass

    def calculate_stock_tactic(self):
        """
        现状存拣模式&设备
        :return:
        """
        pass

    def calculate_design_tactic(self):
        """
        规划存拣模式&设备
        :return:
        """
        pass


def calu_stock_data(original):
    # 加载配置参数
    config = Config()
    config.run()

    # 显示所有列
    pd.set_option('display.max_columns', None)
    # 显示所有行
    pd.set_option('display.max_rows', None)

    rows = original.shape[0]
    cols = original.shape[1]

    print('-' * 50)
    print('原始数据行数：', rows)
    print('原始数据列数：', cols)

    columns = ['static_date', 'SKU_ID', 'sku_name', 'sku_state', 'warehouse',
               'I_class', 'II_class', 'III_class', 'IV_class',
               'weight', 'long', 'width', 'height',
               'fullCaseUnit', 'ctn_long', 'ctn_width', 'ctn_height',
               'monthly_stock_cumu_qty', 'monthly_stock_cumu_days',
               'monthly_deli_cumu_qty', 'monthly_deli_cumu_times', 'monthly_deli_cumu_days',
               'monthly_rec_cumu_qty', 'monthly_rec_cumu_times', 'monthly_rec_cumu_days',
               'static_stock_qty', 'warehouse_cate', 'country', 'expiry', 'good_property'
               ]

    df = pd.DataFrame(original, columns=columns)

    # df['SKU_ID'] = df['SKU_ID'].astype(str)

    # 将字符串形式的日期转换为 datetime
    # df['static_date'] = pd.to_datetime(df['static_date'])

    # 填充空值
    df['long'].fillna(value=0, inplace=True)
    df['width'].fillna(value=0, inplace=True)
    df['height'].fillna(value=0, inplace=True)
    df['weight'].fillna(value=0, inplace=True)
    df['ctn_long'].fillna(value=0, inplace=True)
    df['ctn_width'].fillna(value=0, inplace=True)
    df['ctn_height'].fillna(value=0, inplace=True)

    # 37 AL 最长边(mm)_原始
    df['longest'] = df[['long', 'width', 'height']].max(axis=1)  # 求一行的最大值

    # 38 AM 最小包装体积(mm3)_原始
    df['vol'] = df['long'] * df['width'] * df['height']

    '''
    月度日均 库存参数
    '''
    # 获取静态在库日期当月天数
    static_date = df['static_date'][0]
    if type(static_date) == datetime:
        month = static_date.month
    else:
        month = datetime.strptime(str(static_date), '%Y-%m-%d').strftime('%m')

    # 计算日均库存的总天数
    if len(df['monthly_stock_cumu_days'].unique()) == 1:
        mdays = 1
    else:
        mdays = calendar.mdays[int(month)]

    # 79 CB 月度日均库存数量_现状
    df['daily_stock_qty'] = df['monthly_stock_cumu_qty'] / mdays
    # print('test daily_stock_qty')
    # print(df[['I_class','monthly_stock_cumu_qty', 'daily_stock_qty']])
    # 80 CC 月度日均库存体积(mm3)_现状
    df['daily_stock_vol_mm'] = df['daily_stock_qty'] * df['vol']
    # 81 CD 月度日均库存体积(m3)_现状
    df['daily_stock_vol_m'] = df['daily_stock_qty'] * df['vol'] / pow(10, 9)
    # 82. CE 月度日均库存重量(kg)_现状
    df['daily_stock_weight'] = df['daily_stock_qty'] * df['weight']  # weight or weight_corr

    # 83. CF 月度日均库存折合料箱数量(按额定体积折算&重量折算)_现状
    # df['daily_stock_toTote'] = df

    '''
    月度日均出库参数  总量/当月天数
    '''
    # 91. CN 月度日均出库数量_现状
    # 92. CO 月度日均订购次数_现状
    df['daily_deli_qty'] = 0
    df['daily_order_times'] = 0
    for index, row in df.iterrows():
        if row['monthly_deli_cumu_days'] > 0:
            df.loc[index, ['daily_deli_qty']] = round(row['monthly_deli_cumu_qty'] / row['monthly_deli_cumu_days'], 2)
            df.loc[index, ['daily_order_times']] = round(row['monthly_deli_cumu_times'] / row['monthly_deli_cumu_days'],
                                                         2)
        else:
            df.loc[index, ['daily_deli_qty']] = round(row['monthly_deli_cumu_qty'] / mdays, 2)
            df.loc[index, ['daily_order_times']] = round(row['monthly_deli_cumu_times'] / mdays, 2)

    # 93. CP 月度日均出库体积(mm3)_现状
    df['daily_deli_vol_mm'] = round(df['daily_deli_qty'] * df['vol'], 2)
    # 94. CQ 月度日均出库体积(m3)_现状
    df['daily_deli_vol_m'] = round(df['daily_deli_qty'] * df['vol'] / pow(10, 9), 2)
    # 月度日均出库重量(kg)_现状
    df['daily_deli_weight'] = round(df['daily_deli_qty'] * df['weight'], 2)  # weight or weight_corr

    '''
    月度日均 入库参数
    '''
    # 101. CX 月度日均入库数量_现状
    df['daily_rec_qty'] = df['monthly_rec_cumu_qty'] / mdays  # 月度日均出库件数
    df.loc[(df['daily_rec_qty'].isna()), ['daily_rec_qty']] = 0
    # 102. CY 月度日均入库体积(mm3)_现状
    df['daily_rec_vol_mm'] = df['daily_rec_qty'] * df['vol']
    # 103. CZ 月度日均入库体积(m3)_现状
    df['daily_rec_vol_m'] = df['daily_rec_qty'] * df['vol'] / pow(10, 9)
    # 月度日均入库重量(kg)_现状
    df['daily_rec_weight'] = df['daily_rec_qty'] * df['weight']  # weight or weight_corr

    '''
    实际日均出库相关字段 总量/实际出库天数
    '''
    # 109 DF 月度实际日均库存数量_现状
    df['prac_daily_stock_qty'] = df['monthly_stock_cumu_qty'] / df['monthly_stock_cumu_days']
    df.loc[(df['prac_daily_stock_qty'].isna()), ['prac_daily_stock_qty']] = 0
    # 110 DG 月度实际日均出库数量_现状
    df['prac_daily_deli_qty'] = df['monthly_deli_cumu_qty'] / df['monthly_deli_cumu_days']
    df.loc[(df['prac_daily_deli_qty'].isna()), ['prac_daily_deli_qty']] = 0
    # 111 DH 月度实际日均订购次数_现状
    df['prac_daily_deli_times'] = df['monthly_deli_cumu_times'] / df['monthly_deli_cumu_days']
    df.loc[(df['prac_daily_deli_times'].isna()), ['prac_daily_deli_times']] = 0

    #  46~49 AU~AX 月度日均库存重量MDQG(KG)/库存长度合计MDQL(mm)/库存宽度合计MDQW(mm)/库存高度合计MDQH(mm)
    #  用于类别补全
    df['MDTG'] = df['weight'] * df['daily_stock_qty']
    df['MDTL'] = df['long'] * df['daily_stock_qty']
    df['MDTW'] = df['width'] * df['daily_stock_qty']
    df['MDTH'] = df['height'] * df['daily_stock_qty']

    tmp_cols = ['I_class', 'II_class', 'III_class', 'IV_class',
                'MDTG', 'MDTL', 'MDTW', 'MDTH', 'weight', 'longest', 'daily_stock_qty']

    cate_tmp = df[tmp_cols]

    '''
    四个类别透视数据，聚合列为MDTG,MDTL,MDTW,MDTH,daily_stock_qty
    聚合后分别计算各类别的 I_avgWeight,I_avgLong,I_avgWidth,I_avgHeight
    '''
    # 一级类目透视数据
    # I_class_data = cate_tmp.groupby('I_class').agg({'MDTG': sum, 'MDTL': sum, 'MDTG': sum,
    # 'MDTL': sum, 'daily_stock_qty': sum})
    I_class_data = cate_tmp.groupby('I_class').agg(sumMDTG=pd.NamedAgg(column='MDTG', aggfunc='sum'),
                                                   sumMDTL=pd.NamedAgg(column='MDTL', aggfunc='sum'),
                                                   sumMDTW=pd.NamedAgg(column='MDTW', aggfunc='sum'),
                                                   sumMDTH=pd.NamedAgg(column='MDTH', aggfunc='sum'),
                                                   sumDailyStockQty=pd.NamedAgg(column='daily_stock_qty',
                                                                                aggfunc='sum')).reset_index()

    I_class_data['I_avgWeight'] = I_class_data['sumMDTG'] / I_class_data['sumDailyStockQty']
    I_class_data['I_avgLong'] = I_class_data['sumMDTL'] / I_class_data['sumDailyStockQty']
    I_class_data['I_avgWidth'] = I_class_data['sumMDTW'] / I_class_data['sumDailyStockQty']
    I_class_data['I_avgHeight'] = I_class_data['sumMDTH'] / I_class_data['sumDailyStockQty']

    I_class_avg = {
        'weight': I_class_data['I_avgWeight'].mean(),
        'long': I_class_data['I_avgLong'].mean(),
        'width': I_class_data['I_avgWidth'].mean(),
        'height': I_class_data['I_avgHeight'].mean()
    }

    # I_class_avgWeight = np.average(I_class_data['avgWeight'])
    # I_class_avgLong = np.average(I_class_data['avgLong'])
    # I_class_avgWidth = np.average(I_class_data['avgWidth'])
    # I_class_avgHeight = np.average(I_class_data['avgHeight'])

    # 二级类目透视数据
    # II_class_data = cate_tmp.groupby('II_class').agg(
    #     {'MDTG': sum, 'MDTL': sum, 'MDTG': sum, 'MDTL': sum, 'daily_stock_qty': sum})
    II_class_data = cate_tmp.groupby('II_class').agg(sumMDTG=pd.NamedAgg(column='MDTG', aggfunc='sum'),
                                                     sumMDTL=pd.NamedAgg(column='MDTL', aggfunc='sum'),
                                                     sumMDTW=pd.NamedAgg(column='MDTW', aggfunc='sum'),
                                                     sumMDTH=pd.NamedAgg(column='MDTH', aggfunc='sum'),
                                                     sumDailyStockQty=pd.NamedAgg(column='daily_stock_qty',
                                                                                  aggfunc='sum')).reset_index()

    II_class_data['II_avgWeight'] = II_class_data['sumMDTG'] / II_class_data['sumDailyStockQty']
    II_class_data['II_avgLong'] = II_class_data['sumMDTL'] / II_class_data['sumDailyStockQty']
    II_class_data['II_avgWidth'] = II_class_data['sumMDTW'] / II_class_data['sumDailyStockQty']
    II_class_data['II_avgHeight'] = II_class_data['sumMDTH'] / II_class_data['sumDailyStockQty']

    II_class_avg = {
        'weight': II_class_data['II_avgWeight'].mean(),
        'long': II_class_data['II_avgLong'].mean(),
        'width': II_class_data['II_avgWidth'].mean(),
        'height': II_class_data['II_avgHeight'].mean()
    }

    # II_class_avgWeight = np.average(II_class_data['avgWeight'])
    # II_class_avgLong = np.average(II_class_data['avgLong'])
    # II_class_avgWidth = np.average(II_class_data['avgWidth'])
    # II_class_avgHeight = np.average(II_class_data['avgHeight'])

    # 三级类目透视数据
    # III_class_data = cate_tmp.groupby('I_class').agg(
    #     {'MDTG': sum, 'MDTL': sum, 'MDTG': sum, 'MDTL': sum, 'daily_stock_qty': sum})
    III_class_data = cate_tmp.groupby('III_class').agg(sumMDTG=pd.NamedAgg(column='MDTG', aggfunc='sum'),
                                                       sumMDTL=pd.NamedAgg(column='MDTL', aggfunc='sum'),
                                                       sumMDTW=pd.NamedAgg(column='MDTW', aggfunc='sum'),
                                                       sumMDTH=pd.NamedAgg(column='MDTH', aggfunc='sum'),
                                                       sumDailyStockQty=pd.NamedAgg(column='daily_stock_qty',
                                                                                    aggfunc='sum')).reset_index()

    III_class_data['III_avgWeight'] = III_class_data['sumMDTG'] / III_class_data['sumDailyStockQty']
    III_class_data['III_avgLong'] = III_class_data['sumMDTL'] / III_class_data['sumDailyStockQty']
    III_class_data['III_avgWidth'] = III_class_data['sumMDTW'] / III_class_data['sumDailyStockQty']
    III_class_data['III_avgHeight'] = III_class_data['sumMDTH'] / III_class_data['sumDailyStockQty']

    III_class_avg = {
        'weight': III_class_data['III_avgWeight'].mean(),
        'long': III_class_data['III_avgLong'].mean(),
        'width': III_class_data['III_avgWidth'].mean(),
        'height': III_class_data['III_avgHeight'].mean()
    }

    # III_class_avgWeight = np.average(III_class_data['avgWeight'])
    # III_class_avgLong = np.average(III_class_data['avgLong'])
    # III_class_avgWidth = np.average(III_class_data['avgWidth'])
    # III_class_avgHeight = np.average(III_class_data['avgHeight'])

    # 四级类目透视数据
    # IV_class_data = cate_tmp.groupby('IV_class').agg(
    #     {'MDTG': sum, 'MDTL': sum, 'MDTG': sum, 'MDTL': sum, 'daily_stock_qty': sum})
    IV_class_data = cate_tmp.groupby('IV_class').agg(sumMDTG=pd.NamedAgg(column='MDTG', aggfunc='sum'),
                                                     sumMDTL=pd.NamedAgg(column='MDTL', aggfunc='sum'),
                                                     sumMDTW=pd.NamedAgg(column='MDTW', aggfunc='sum'),
                                                     sumMDTH=pd.NamedAgg(column='MDTH', aggfunc='sum'),
                                                     maxWeight=pd.NamedAgg(column='weight', aggfunc='max'),
                                                     maxLongest=pd.NamedAgg(column='longest', aggfunc='max'),
                                                     sumDailyStockQty=pd.NamedAgg(column='daily_stock_qty',
                                                                                  aggfunc='sum')).reset_index()

    IV_class_data['IV_avgWeight'] = IV_class_data['sumMDTG'] / IV_class_data['sumDailyStockQty']
    IV_class_data['IV_avgLong'] = IV_class_data['sumMDTL'] / IV_class_data['sumDailyStockQty']
    IV_class_data['IV_avgWidth'] = IV_class_data['sumMDTW'] / IV_class_data['sumDailyStockQty']
    IV_class_data['IV_avgHeight'] = IV_class_data['sumMDTH'] / IV_class_data['sumDailyStockQty']

    IV_class_avg = {
        'weight': IV_class_data['IV_avgWeight'].mean(),
        'long': IV_class_data['IV_avgLong'].mean(),
        'width': IV_class_data['IV_avgWidth'].mean(),
        'height': IV_class_data['IV_avgHeight'].mean()
    }

    # IV_class_avgWeight = np.average(IV_class_data['avgWeight'])
    # IV_class_avgLong = np.average(IV_class_data['avgLong'])
    # IV_class_avgWidth = np.average(IV_class_data['avgWidth'])
    # IV_class_avgHeight = np.average(IV_class_data['avgHeight'])

    '''
    异常状态 & 异常标识
    '''
    '''
    类目透视数据，用于按四级类目自动补全
    '''
    class_col = ['SKU_ID', 'I_class', 'II_class', 'III_class', 'IV_class']

    classData = pd.merge(df[class_col],
                         I_class_data[['I_class', 'I_avgWeight', 'I_avgLong', 'I_avgWidth', 'I_avgHeight']],
                         on='I_class', how='left', sort=False)
    classData = pd.merge(classData,
                         II_class_data[['II_class', 'II_avgWeight', 'II_avgLong', 'II_avgWidth', 'II_avgHeight']],
                         on='II_class', how='left', sort=False)

    classData = pd.merge(classData,
                         III_class_data[['III_class', 'III_avgWeight', 'III_avgLong', 'III_avgWidth', 'III_avgHeight']],
                         on='III_class', how='left', sort=False)
    classData = pd.merge(classData,
                         IV_class_data[['IV_class', 'IV_avgWeight', 'IV_avgLong', 'IV_avgWidth', 'IV_avgHeight']],
                         on='IV_class', how='left', sort=False)

    # 四级类别的异常值点
    isNorm_cols = ['SKU_ID', 'IV_class']
    isNormData = pd.merge(df[isNorm_cols], IV_class_data[['IV_class', 'maxWeight', 'maxLongest']],
                          how='left', on='IV_class', sort=False)

    '''
    托盘重量折算 按托盘额定体积折算 & 按箱规码放折算
    '''

    # 39 AN 每托重量(kg)(按额定体积折算)_原始
    df['vol_pltWt'] = config.PALLET_STOCK['specified_vol'] / df['vol'] * df['weight'] + config.PALLET_STOCK[
        'unit_weight']

    # 42 AQ 箱规托盘每层码放箱数
    plt_l = config.PALLET_STOCK['long']
    plt_w = config.PALLET_STOCK['width']
    max_s = df[['ctn_long', 'ctn_width']].max(axis=1)
    min_s = df[['ctn_long', 'ctn_width']].min(axis=1)

    # type(left) = series
    left = np.floor(plt_l / max_s) * np.floor(plt_w / min_s) \
           + np.floor((plt_l - np.floor(plt_l / max_s) * max_s) / min_s) * np.floor(plt_w / max_s)
    right = np.floor(plt_l / min_s) * np.floor(plt_w / max_s) \
            + np.floor((plt_w - np.floor(plt_w / max_s) * max_s) / min_s) * np.floor(plt_l / min_s)

    tmp = left.to_frame(name='left')
    tmp['right'] = right.to_frame(name='right')
    df['layer_cartons'] = tmp[['left', 'right']].max(axis=1)

    # 43 AR 箱规每托重量折算(kg)(按额定体积)
    df['ctn_pltWt'] = 0
    df.loc[(df['ctn_long'] > 0) & (df['ctn_width'] > 0) & (df['ctn_height'] > 0), ['ctn_pltWt']] \
        = np.floor(config.PALLET_STOCK['valid_height'] / df[['ctn_long', 'ctn_width', 'ctn_height']].min(axis=1)) \
          * df['layer_cartons'] * df['fullCaseUnit'] * df['weight']

    # 40 AO 商品尺寸&重量&托盘重量折算异常标识-原始数据  SW_isAbnormal_tag
    # 先全部赋值为'N',再根据异常情况赋值为'Y'
    df['SW_isAbnormal_tag'] = 'N'
    df['SW_isAbnormal_state'] = '01原始数据可用'
    df.loc[(df['weight'].isna()) | (df['weight'] == 0) |
           (df['long'].isna()) | (df['long'] == 0) |
           (df['width'].isna()) | (df['width'] == 0) |
           (df['height'].isna()) | (df['height'] == 0),
           ['SW_isAbnormal_tag']] = 'Y'
    df.loc[(df['weight'].isna()) | (df['weight'] == 0) |
           (df['long'].isna()) | (df['long'] == 0) |
           (df['width'].isna()) | (df['width'] == 0) |
           (df['height'].isna()) | (df['height'] == 0),
           ['SW_isAbnormal_state']] = '02体积/重量缺失'

    # index = IV_class_data[IV_class_data.loc[:, 'IV_class'].isin(df['class'])].index
    # df.loc[(df['weight']> IV_class_data.loc[index,'maxWeight'].reset_index()['maxWeight']), ['state']] = 'Y'

    df.loc[(df['weight'] > isNormData['maxWeight']) |
           (df['longest'] > isNormData['maxLongest']),
           ['SW_isAbnormal_tag']] = 'Y'
    df.loc[(df['vol_pltWt'] < config.THRESHOLD['pltWeight_lower']) |
           (df['vol_pltWt'] > config.THRESHOLD['pltWeight_upper']) |
           (df['longest'] > config.THRESHOLD['longest_upper']) |
           (df['weight'] > config.THRESHOLD['weight_upper']),
           ['SW_isAbnormal_tag']] = 'Y'

    df.loc[(df['weight'] > isNormData['maxWeight']) |
           (df['longest'] > isNormData['maxLongest']),
           ['SW_isAbnormal_state']] = '03体积/重量超过四级类目最大值'
    df.loc[(df['vol_pltWt'] < config.THRESHOLD['pltWeight_lower']) |
           (df['vol_pltWt'] > config.THRESHOLD['pltWeight_upper']) |
           (df['longest'] > config.THRESHOLD['longest_upper']) |
           (df['weight'] > config.THRESHOLD['weight_upper']),
           ['SW_isAbnormal_state']] = '04体积/重量超过阀值范围'

    # if pd.isna(df[['weight', 'long', 'width', 'height']]):
    #     df['abnormal_tag'] = 'Y'
    # elif df['weight'] > IV_class_data['maxWeight'] or df['longest'] > IV_class_data['maxLongest']:
    #     df['abnormal_tag'] = 'Y'
    # elif df['vol_pltWt'] < config.THRESHOLD['pltWeight_lower'] or df['vol_pltWt'] > config.THRESHOLD[
    #     'pltWeight_upper']:
    #     df['abnormal_tag'] = 'Y'
    # elif df['longest'] > config.THRESHOLD['longest_upper'] or df['weight'] > config.THRESHOLD['weight_upper']:
    #     df['abnormal_tag'] = 'Y'
    # else:
    #     df['abnormal_tag'] = 'N'

    # 41 AP 商品尺寸 & 重量 & 托盘重量折算状态标识-原始  SW_isAbnormal_state
    # df['SW_isAbnormal_state'] = '01原始数据可用'
    # df.loc[(df['SW_isAbnormal_tag'] == 'Y') , ['SW_isAbnormal_state']] = '03体积/重量维护可能有误'
    # df.loc[(df['weight'].isna()) | (df['vol'].isna()), ['SW_isAbnormal_state']] = '02体积/重量缺失'

    # if pd.isna(df[['weight', 'vol']]):
    #     df['SW_isAbnormal_state'] = '03体积/重量缺少'
    # else:
    #     if df['SW_isAbnormal_state'] == 'Y':
    #         df['SW_isAbnormal_state'] = '02体积/重量维护可能有误'
    #     else:
    #         df['SW_isAbnormal_state'] = '01原始数据可用'

    # 44 AS箱规重量折算_异常标识/异常状态  CW_isAbnormal_tag, CW_isAbnormal_state
    df['CW_isAbnormal_tag'] = 'N'
    df['CW_isAbnormal_state'] = '01箱规数据可用'

    df.loc[(df['fullCaseUnit'].isna()) | (df['fullCaseUnit'] == 0) |
           (df['ctn_long'].isna()) | (df['ctn_long'] == 0) |
           (df['ctn_width'].isna()) | (df['ctn_width'] == 0) |
           df['ctn_height'].isna() | (df['ctn_height'] == 0),
           ['CW_isAbnormal_tag']] = 'Y'
    df.loc[(df['ctn_pltWt'] < config.THRESHOLD['pltWeight_lower']) |
           (df['ctn_pltWt'] > config.THRESHOLD['pltWeight_upper']) |
           (df['vol'] * df['fullCaseUnit'] > df['ctn_long'] * df['ctn_width'] * df['ctn_height']),
           ['CW_isAbnormal_tag']] = 'Y'

    df.loc[(df['ctn_pltWt'] < config.THRESHOLD['pltWeight_lower']) |
           (df['ctn_pltWt'] > config.THRESHOLD['pltWeight_upper']) |
           (df['vol'] * df['fullCaseUnit'] > df['ctn_long'] * df['ctn_width'] * df['ctn_height']),
           ['CW_isAbnormal_state']] = '03箱规维护可能有误'
    df.loc[(df['fullCaseUnit'].isna()) | (df['fullCaseUnit'] == 0) |
           (df['ctn_long'].isna()) | (df['ctn_long'] == 0) |
           (df['ctn_width'].isna()) | (df['ctn_width'] == 0) |
           df['ctn_height'].isna() | (df['ctn_height'] == 0),
           ['CW_isAbnormal_state']] = '02无箱规数据/数据缺失'

    # if pd.isna(df[['fullCaseUnit', 'ctn_long', 'ctn_width', 'ctn_height']]):
    #     df['CW_isAbnormal_state'] = 'Y'
    # elif df['ctn_pltWt'] < config.THRESHOLD['pltWeight_lower'] \
    #         or df['ctn_pltWt'] > config.THRESHOLD['pltWeight_upper']:
    #     df['CW_isAbnormal_state'] = 'Y'
    # elif df['vol'] * df['fullCaseUnit'] > df['ctn_long'] * df['ctn_width'] * df['ctn_height']:
    #     df['CW_isAbnormal_state'] = 'Y'
    # else:
    #     df['CW_isAbnormal_state'] = 'N'

    # 44 AT箱规重量折算_异常状态  CW_isAbnormal_state
    # df['CW_isAbnormal_state'] = '01箱规数据可用'
    # df.loc[(df['CW_isAbnormal_tag'] == 'Y') & (df['CW_isAbnormal_state'].isna()), ['CW_isAbnormal_state']] = '03箱规维护可能有误'
    # df.loc[(df['fullCaseUnit'].isna()) | (df['ctn_long'].isna()) |
    #        (df['ctn_width'].isna()) | (df['ctn_height'].isna()), ['CW_isAbnormal_state']] = '02无箱规数据/数据缺失'

    '''
    重量，长宽高缺少数据，用类目数据修正
    '''
    # 50 AY 最小包装重量(kg)_自动类目修正补全
    # 先给'corrWeight' 赋值 NAN,
    # 无异常用原始数据赋值
    # 有异常，依次用四级类目，三级类目，二级类目，一级类目，全部一级修正
    df['corrWeight'] = 0
    # for index, row in df.iterrows():
    #     if row['SW_isAbnormal_tag'] == 'N':
    #         if row['weight'] > 0:
    #             df.loc[index, ['corrWeight']] = row['weight']
    #             continue
    #     else:
    #         if classData.loc[index,['IV_avgWeight']]> 0:
    #             df.loc[index, ['corrWeight']] = classData.loc[index,['IV_avgWeight']]
    #             continue
    #         elif classData.loc[index,['III_avgWeight']]> 0:
    #             df.loc[index, ['corrWeight']] = classData.loc[index, ['III_avgWeight']]
    #             continue
    #         elif classData.loc[index,['II_avgWeight']]> 0:
    #             df.loc[index, ['corrWeight']] = classData.loc[index, ['II_avgWeight']]
    #             continue
    #         elif classData.loc[index,['I_avgWeight']]> 0:
    #             df.loc[index, ['corrWeight']] = classData.loc[index, ['I_avgWeight']]
    #             continue
    #         else:
    #             df.loc[index, ['corrWeight']] = I_class_avg['weight']

    df.loc[(df['SW_isAbnormal_tag'] == 'N') & (df['weight'] > 0), ['corrWeight']] = df['weight']
    df.loc[(df['SW_isAbnormal_tag'] == 'Y') & (classData['IV_avgWeight'] > 0), ['corrWeight']] = classData[
        'IV_avgWeight']
    df.loc[(df['SW_isAbnormal_tag'] == 'Y') & (df['corrWeight'] == 0) &
           (classData['III_avgWeight'] > 0), ['corrWeight']] = classData['III_avgWeight']
    df.loc[(df['SW_isAbnormal_tag'] == 'Y') & (df['corrWeight'] == 0) &
           (classData['II_avgWeight'] > 0), ['corrWeight']] = classData['II_avgWeight']
    df.loc[(df['SW_isAbnormal_tag'] == 'Y') & (df['corrWeight'] == 0) &
           (classData['I_avgWeight'] > 0), ['corrWeight']] = classData['I_avgWeight']
    df.loc[(df['SW_isAbnormal_tag'] == 'Y') & (df['corrWeight'] == 0), ['corrWeight']] = I_class_avg['weight']
    df.loc[(df['corrWeight'].isna()), ['corrWeight']] = 0

    # 52 BA 最小包装L(mm)_自动类目修正补全
    df['corrLong'] = 0
    df.loc[(df['SW_isAbnormal_tag'] == 'N') & (df['long'] > 0), ['corrLong']] = df['long']
    df.loc[(df['SW_isAbnormal_tag'] == 'Y') & (classData['IV_avgLong'] > 0), ['corrLong']] = classData[
        'IV_avgLong']
    df.loc[(df['SW_isAbnormal_tag'] == 'Y') & (df['corrLong'] == 0) &
           (classData['III_avgLong'] > 0), ['corrLong']] = classData['III_avgLong']
    df.loc[(df['SW_isAbnormal_tag'] == 'Y') & (df['corrLong'] == 0) &
           (classData['II_avgLong'] > 0), ['corrLong']] = classData['II_avgLong']
    df.loc[(df['SW_isAbnormal_tag'] == 'Y') & (df['corrLong'] == 0) &
           (classData['I_avgLong'] > 0), ['corrLong']] = classData['I_avgLong']
    df.loc[(df['SW_isAbnormal_tag'] == 'Y') & (df['corrLong'] == 0), ['corrLong']] = I_class_avg['long']
    df.loc[(df['corrLong'].isna()), ['corrLong']] = 0

    # 52 BB 最小包装W(mm)_自动类目修正补全
    df['corrWidth'] = 0
    df.loc[(df['SW_isAbnormal_tag'] == 'N') & (df['width'] > 0), ['corrWidth']] = df['width']
    df.loc[(df['SW_isAbnormal_tag'] == 'Y') & (classData['IV_avgWidth'] > 0), ['corrWidth']] = classData[
        'IV_avgWidth']
    df.loc[(df['SW_isAbnormal_tag'] == 'Y') & (df['corrWidth'] == 0) &
           (classData['III_avgWidth'] > 0), ['corrWidth']] = classData['III_avgWidth']
    df.loc[(df['SW_isAbnormal_tag'] == 'Y') & (df['corrWidth'] == 0) &
           (classData['II_avgWidth'] > 0), ['corrWidth']] = classData['II_avgWidth']
    df.loc[(df['SW_isAbnormal_tag'] == 'Y') & (df['corrWidth'] == 0) &
           (classData['I_avgWidth'] > 0), ['corrWidth']] = classData['I_avgWidth']
    df.loc[(df['SW_isAbnormal_tag'] == 'Y') & (df['corrWidth'] == 0), ['corrWidth']] = I_class_avg['width']
    df.loc[(df['corrWidth'].isna()), ['corrWidth']] = 0

    # 52 BC 最小包装H(mm)_自动类目修正补全
    df['corrHeight'] = 0
    df.loc[(df['SW_isAbnormal_tag'] == 'N') & (df['height'] > 0), ['corrHeight']] = df['height']
    df.loc[(df['SW_isAbnormal_tag'] == 'Y') & (classData['IV_avgHeight'] > 0), ['corrHeight']] = classData[
        'IV_avgHeight']
    df.loc[(df['SW_isAbnormal_tag'] == 'Y') & (df['corrHeight'] == 0) &
           (classData['III_avgHeight'] > 0), ['corrHeight']] = classData['III_avgHeight']
    df.loc[(df['SW_isAbnormal_tag'] == 'Y') & (df['corrHeight'] == 0) &
           (classData['II_avgHeight'] > 0), ['corrHeight']] = classData['II_avgHeight']
    df.loc[(df['SW_isAbnormal_tag'] == 'Y') & (df['corrHeight'] == 0) &
           (classData['I_avgHeight'] > 0), ['corrHeight']] = classData['I_avgHeight']
    df.loc[(df['SW_isAbnormal_tag'] == 'Y') & (df['corrHeight'] == 0), ['corrHeight']] = I_class_avg['height']
    df.loc[(df['corrHeight'].isna()), ['corrHeight']] = 0

    # 51 AZ 商品最长边(mm)_含全部修正 corrLongest
    df['corrLongest'] = df[['corrLong', 'corrWidth', 'corrHeight']].max(axis=1)

    # 55 BD	商品最小包装V(mm3)_含全部修正 corrVol
    df['corrVol'] = df['corrLong'] * df['corrWidth'] * df['corrHeight']

    # 56 BE	"每托重量(kg)(按额定体积折算)_含全部修正 corr_vol_pltWt
    df['corr_vol_pltWt'] = config.PALLET_STOCK['specified_vol'] / df['corrVol'] * df['corrWeight'] + \
                           config.PALLET_STOCK[
                               'unit_weight']

    '''
    数据修正后的 异常标识和异常状态
    '''
    # 57 BF	商品尺寸&重量&托盘重量折算异常标识(含全部修正) corrSW_isAbnormal_tag
    df['corrSW_isAbnormal_tag'] = 'N'

    df.loc[(df['corrWeight'].isna()) | (df['corrWeight'] == 0) |
           (df['corrLong'].isna()) | (df['corrLong'] == 0) |
           (df['corrWidth'].isna()) | (df['corrWidth'] == 0) |
           (df['corrHeight'].isna()) | (df['corrHeight'] == 0),
           ['corrSW_isAbnormal_tag']] = 'Y'
    df.loc[(df['corrWeight'] > isNormData['maxWeight']) |
           (df['corrLongest'] > isNormData['maxLongest']),
           ['corrSW_isAbnormal_tag']] = 'Y'
    df.loc[(df['corr_vol_pltWt'] < config.THRESHOLD['pltWeight_lower']) |
           (df['corr_vol_pltWt'] > config.THRESHOLD['pltWeight_upper']) |
           (df['corrLongest'] > config.THRESHOLD['longest_upper']) |
           (df['corrWeight'] > config.THRESHOLD['weight_upper']),
           ['corrSW_isAbnormal_tag']] = 'Y'

    #  58 BG 商品尺寸&重量&托盘重量折算状态标识(含全部修正) corrSW_isAbnormal_state
    df['corrSW_isAbnormal_state'] = '01原始数据可用'

    df.loc[(df['corrWeight'].isna()) | (df['corrWeight'] == 0) |
           (df['corrVol'].isna()) | (df['corrVol'] == 0),
           ['corrSW_isAbnormal_state']] = '02体积/重量缺失'

    df.loc[(df['SW_isAbnormal_tag'] == 'Y') & (df['corrSW_isAbnormal_tag'] == 'Y'),
           ['corrSW_isAbnormal_state']] = '03体积/重量修正后可能有误'

    df.loc[(df['SW_isAbnormal_tag'] == 'Y') & (df['corrSW_isAbnormal_tag'] == 'N') & (df['corrVol'] > 0),
           ['corrSW_isAbnormal_state']] = '04体积/重量类目自动补齐后可用'

    '''
    基础字段计算
    '''

    # 59 BH	静态库存数量_非0判定 stock_qty_isNonZero
    df['stock_qty_isNonZero'] = 'Y'
    df.loc[(df['static_stock_qty'].isna()) | (df['static_stock_qty'] == 0), ['stock_qty_isNonZero']] = 'N'

    '''
    用PARM3 的原箱出库阀值判断
    '''
    # 60 BI	单件商品出库最长边阀值状态标识
    df['unit_deli_longest_state'] = df['corrSW_isAbnormal_state']
    df.loc[(df['corrSW_isAbnormal_tag'] == 'N') &
           (df['corrLongest'] >= config.ORG_CARTON['longest_lower'][1]) &
           (df['corrLongest'] < config.ORG_CARTON['longest_upper'][1]),
           ['unit_deli_longest_state']] = config.ORG_CARTON['type'][1]

    df.loc[(df['corrSW_isAbnormal_tag'] == 'N') &
           (df['corrLongest'] > config.ORG_CARTON['longest_lower'][2]),
           ['unit_deli_longest_state']] = config.ORG_CARTON['type'][2]

    df.loc[(df['corrSW_isAbnormal_tag'] == 'N'),
           ['unit_deli_longest_state']] = config.ORG_CARTON['type'][0]

    # 61 BJ	一级箱规原箱出库最长边阀值状态标识
    df['ctn_deli_longest_state'] = df['corrSW_isAbnormal_state']
    df.loc[(df['corrSW_isAbnormal_tag'] == 'N') &
           (df['corrLongest'] >= config.ORG_CARTON['longest_lower'][1]) &
           (df['corrLongest'] < config.ORG_CARTON['longest_upper'][1]),
           ['ctn_deli_longest_state']] = config.ORG_CARTON['type'][1]

    df.loc[(df['corrSW_isAbnormal_tag'] == 'N') &
           (df['corrLongest'] > config.ORG_CARTON['longest_lower'][2]),
           ['ctn_deli_longest_state']] = config.ORG_CARTON['type'][2]

    df.loc[(df['corrSW_isAbnormal_tag'] == 'N'),
           ['ctn_deli_longest_state']] = config.ORG_CARTON['type'][0]

    # 62 BK 件型
    # 添加辅助列，第二长边
    df['min_side'] = df[['corrLong', 'corrWidth', 'corrHeight']].min(axis=1)
    df['mid_side'] = df[['corrLong', 'corrWidth', 'corrHeight']].sum(axis=1) - df['corrLongest'] - \
                     df[['corrLong', 'corrWidth', 'corrHeight']].min(axis=1)

    ## 原箱件型辅助列
    df['ctn_max_side'] = df[['ctn_long', 'ctn_width', 'ctn_height']].max(axis=1)
    df['ctn_min_side'] = df[['ctn_long', 'ctn_width', 'ctn_height']].min(axis=1)
    df['ctn_mid_side'] = df['ctn_max_side'] - df['ctn_min_side']

    df['size'] = ''  # '4H'
    df.loc[(df['corrLongest'] <= config.SIZE['longest'][0]) &
           (df['mid_side'] <= config.SIZE['middle'][0]) &
           (df['corrWeight'] <= config.SIZE['weight'][0]), ['size']] = config.SIZE['type'][0]
    df.loc[(df['corrLongest'] <= config.SIZE['longest'][1]) &
           (df['corrWeight'] <= config.SIZE['weight'][1]) &
           (df['size'].isna()), ['size']] = config.SIZE['type'][1]
    df.loc[(df['corrLongest'] <= config.SIZE['longest'][2]) &
           (df['size'].isna()), ['size']] = config.SIZE['type'][2]
    df.loc[(df['corrLongest'] > config.SIZE['longest'][2]) &
           (df['size'].isna()), ['size']] = config.SIZE['type'][3]  # '4H'
    # df.drop('mid_side')  # 删除赋值列

    #### 原箱件型
    df['ctn_size'] = np.NAN  # '4H'
    df.loc[(df['ctn_max_side'] <= config.SIZE['longest'][0]) &
           (df['ctn_mid_side'] <= config.SIZE['middle'][0]), ['ctn_size']] = config.SIZE['ctn_type'][0]
    df.loc[(df['ctn_max_side'] <= config.SIZE['longest'][1]) &
           (df['ctn_size'].isna()), ['ctn_size']] = config.SIZE['ctn_type'][1]
    df.loc[(df['ctn_max_side'] <= config.SIZE['longest'][2]) &
           (df['ctn_size'].isna()), ['ctn_size']] = config.SIZE['ctn_type'][2]
    df.loc[(df['ctn_max_side'] > config.SIZE['longest'][2]) &
           (df['ctn_size'].isna()), ['ctn_size']] = config.SIZE['ctn_type'][3]  # '4H'

    '''
    实际日均出库体积
    '''
    # 112 DI 月度实际日均出库体积(mm3)_现状
    df['prac_daily_deli_vol_mm'] = df['prac_daily_deli_qty'] * df['corrVol']
    df.loc[(df['corrSW_isAbnormal_tag'] == 'Y'), 'prac_daily_deli_vol_mm'] = 0
    # 113 DJ 月度实际日均出库体积(m3)_现状
    df['prac_daily_deli_vol_m'] = df['prac_daily_deli_vol_mm'] / pow(10, 9)

    '''
    ABC分类，按日均出库件数&实际日均出库件数 计算累计出库比例
    '''
    # 添加辅助列 出库件数占比，出库体积占比
    df['daily_qty_rate'] = df['daily_deli_qty'] / df['daily_deli_qty'].sum()
    df['daily_vol_rate'] = df['daily_deli_vol_m'] / df['daily_deli_vol_m'].sum()

    df['prac_daily_qty_rate'] = df['prac_daily_deli_qty'] / df['prac_daily_deli_qty'].sum()
    df['prac_daily_vol_rate'] = df['prac_daily_deli_vol_m'] / df['prac_daily_deli_vol_m'].sum()

    df['qty_rank'] = df['daily_qty_rate'].rank(ascending=False, method='first')
    df['vol_rank'] = df['daily_vol_rate'].rank(ascending=False, method='first')

    df['prac_qty_rank'] = df['prac_daily_qty_rate'].rank(ascending=False, method='first')
    df['prac_vol_rank'] = df['prac_daily_vol_rate'].rank(ascending=False, method='first')

    # 动销SKU数量
    salesNum = (df['daily_deli_qty'] > 0).sum()
    # print('salesNum: ')
    # print(salesNum)
    prac_salesNum = (df['prac_daily_deli_qty'] > 0).sum()
    # print('prac_salesNum: ')
    # print(prac_salesNum)

    # 64 BM	ABC_MADQ 日均出库件数 ABC分级
    df['ABC_MADQ'] = 'ZZZZ' + '_' + config.ABC_CLASS[4]
    for index, row in df.iterrows():
        cumu_rate = df[(df['qty_rank'] <= row['qty_rank'])]['daily_qty_rate'].sum()
        if row['daily_deli_qty'] == 0:
            continue
        elif row['qty_rank'] == 1:
            df.loc[index, ['ABC_MADQ']] = 'MADQ' + '_' + config.ABC_CLASS[0]
        elif cumu_rate <= config.ABC_INTERVAL[0]:
            df.loc[index, ['ABC_MADQ']] = 'MADQ' + '_' + config.ABC_CLASS[0]
        elif cumu_rate <= config.ABC_INTERVAL[1]:
            df.loc[index, ['ABC_MADQ']] = 'MADQ' + '_' + config.ABC_CLASS[1]
        elif cumu_rate <= config.ABC_INTERVAL[2]:
            df.loc[index, ['ABC_MADQ']] = 'MADQ' + '_' + config.ABC_CLASS[2]
        elif cumu_rate <= config.ABC_INTERVAL[3]:
            df.loc[index, ['ABC_MADQ']] = 'MADQ' + '_' + config.ABC_CLASS[3]

    # df['ABC_MADQ'] = np.NAN
    # df['comp'] = config.ABC_INTERVAL[0] * salesNum
    # print('salesNum: ',salesNum)
    # print(df['comp'])
    # df.loc[(df['qty_rank'] <= df['comp']),
    #        ['ABC_MADQ']] = 'MADQ' + '_' + config.ABC_CLASS[0]
    #
    # df['comp'] = config.ABC_INTERVAL[1] * salesNum
    # df.loc[(df['qty_rank'] <= df['comp']) & (df['ABC_MADQ'].isna()),
    #        ['ABC_MADQ']] = 'MADQ' + '_' + config.ABC_CLASS[1]
    #
    # df['comp'] = config.ABC_INTERVAL[2] * salesNum
    # df.loc[(df['qty_rank'] <= df['comp']) & (df['ABC_MADQ'].isna()),
    #        ['ABC_MADQ']] = 'MADQ' + '_' + config.ABC_CLASS[2]
    #
    # df['comp'] = config.ABC_INTERVAL[3] * salesNum
    # df.loc[(df['qty_rank'] <= df['comp']) & (df['ABC_MADQ'].isna()),
    #        ['ABC_MADQ']] = 'MADQ' + '_' + config.ABC_CLASS[3]
    #
    # df.loc[(df['daily_deli_qty'] == 0) | (df['ABC_MADQ'].isna()),
    #        ['ABC_MADQ']] = 'ZZZZ' + '_' + config.ABC_CLASS[4]

    # 65 BN	ABC_MADV 日均出库体积 ABC分级

    df['ABC_MADV'] = 'ZZZZ' + '_' + config.ABC_CLASS[4]
    for index, row in df.iterrows():
        cumu_rate = df[(df['vol_rank'] <= row['vol_rank'])]['daily_vol_rate'].sum()
        if row['daily_deli_qty'] == 0:
            continue
        elif row['vol_rank'] == 1:
            df.loc[index, ['ABC_MADV']] = 'MADV' + '_' + config.ABC_CLASS[0]
        elif cumu_rate <= config.ABC_INTERVAL[0]:
            df.loc[index, ['ABC_MADV']] = 'MADV' + '_' + config.ABC_CLASS[0]
        elif cumu_rate <= config.ABC_INTERVAL[1]:
            df.loc[index, ['ABC_MADV']] = 'MADV' + '_' + config.ABC_CLASS[1]
        elif cumu_rate <= config.ABC_INTERVAL[2]:
            df.loc[index, ['ABC_MADV']] = 'MADV' + '_' + config.ABC_CLASS[2]
        elif cumu_rate <= config.ABC_INTERVAL[3]:
            df.loc[index, ['ABC_MADV']] = 'MADV' + '_' + config.ABC_CLASS[3]

    # df['ABC_MADV'] = np.NAN
    # df['comp'] = config.ABC_INTERVAL[0] * salesNum
    # df.loc[(df['vol_rank'] <= df['comp']),
    #        ['ABC_MADV']] = 'MADV' + '_' + config.ABC_CLASS[0]
    #
    # df['comp'] = config.ABC_INTERVAL[1] * salesNum
    # df.loc[(df['vol_rank'] <= df['comp']) & (df['ABC_MADV'].isna()),
    #        ['ABC_MADV']] = 'MADV' + '_' + config.ABC_CLASS[1]
    #
    # df['comp'] = config.ABC_INTERVAL[2] * salesNum
    # df.loc[(df['vol_rank'] <= df['comp']) & (df['ABC_MADV'].isna()),
    #        ['ABC_MADV']] = 'MADV' + '_' + config.ABC_CLASS[2]
    #
    # df['comp'] = config.ABC_INTERVAL[3] * salesNum
    # df.loc[(df['vol_rank'] <= df['comp']) & (df['ABC_MADV'].isna()),
    #        ['ABC_MADV']] = 'MADV' + '_' + config.ABC_CLASS[3]
    #
    # df.loc[(df['daily_deli_qty'] == 0) | (df['ABC_MADV'].isna()),
    #        ['ABC_MADV']] = 'ZZZZ' + '_' + config.ABC_CLASS[4]

    # 66 BO	ABC_MPDQ 实际日均出库件数 ABC分级

    df['ABC_MPDQ'] = 'ZZZZ' + '_' + config.ABC_CLASS[4]
    for index, row in df.iterrows():
        cumu_rate = df[(df['prac_qty_rank'] <= row['prac_qty_rank'])]['prac_daily_qty_rate'].sum()
        if row['prac_daily_deli_qty'] == 0:
            continue
        elif row['prac_qty_rank'] == 1:
            df.loc[index, ['ABC_MPDQ']] = 'MPDQ' + '_' + config.ABC_CLASS[0]
        elif cumu_rate <= config.ABC_INTERVAL[0]:
            df.loc[index, ['ABC_MPDQ']] = 'MPDQ' + '_' + config.ABC_CLASS[0]
        elif cumu_rate <= config.ABC_INTERVAL[1]:
            df.loc[index, ['ABC_MPDQ']] = 'MPDQ' + '_' + config.ABC_CLASS[1]
        elif cumu_rate <= config.ABC_INTERVAL[2]:
            df.loc[index, ['ABC_MPDQ']] = 'MPDQ' + '_' + config.ABC_CLASS[2]
        elif cumu_rate <= config.ABC_INTERVAL[3]:
            df.loc[index, ['ABC_MPDQ']] = 'MPDQ' + '_' + config.ABC_CLASS[3]

    # df['ABC_MPDQ'] = np.NAN
    # df['comp'] = config.ABC_INTERVAL[0] * prac_salesNum
    # df.loc[(df['qty_rank'] <= df['comp']),
    #        ['ABC_MPDQ']] = 'MPDQ' + '_' + config.ABC_CLASS[0]
    #
    # df['comp'] = config.ABC_INTERVAL[1] * prac_salesNum
    # df.loc[(df['qty_rank'] <= df['comp']) & (df['ABC_MPDQ'].isna()),
    #        ['ABC_MPDQ']] = 'MPDQ' + '_' + config.ABC_CLASS[1]
    #
    # df['comp'] = config.ABC_INTERVAL[2] * prac_salesNum
    # df.loc[(df['qty_rank'] <= df['comp']) & (df['ABC_MPDQ'].isna()),
    #        ['ABC_MPDQ']] = 'MPDQ' + '_' + config.ABC_CLASS[2]
    #
    # df['comp'] = config.ABC_INTERVAL[3] * prac_salesNum
    # df.loc[(df['qty_rank'] <= df['comp']) & (df['ABC_MPDQ'].isna()),
    #        ['ABC_MPDQ']] = 'MPDQ' + '_' + config.ABC_CLASS[3]
    #
    # df.loc[(df['prac_daily_deli_qty'] == 0) | (df['ABC_MPDQ'].isna()),
    #        ['ABC_MPDQ']] = 'ZZZZ' + '_' + config.ABC_CLASS[4]

    # 67 BP	ABC_MPDV ABC分级 实际日均出库体积 ABC分级

    df['ABC_MPDV'] = 'ZZZZ' + '_' + config.ABC_CLASS[4]
    for index, row in df.iterrows():
        cumu_rate = df[(df['prac_vol_rank'] <= row['prac_vol_rank'])]['prac_daily_vol_rate'].sum()
        if row['prac_daily_deli_qty'] == 0:
            continue
        elif row['prac_vol_rank'] == 1:
            df.loc[index, ['ABC_MPDV']] = 'MPDV' + '_' + config.ABC_CLASS[0]
        elif cumu_rate <= config.ABC_INTERVAL[0]:
            df.loc[index, ['ABC_MPDV']] = 'MPDV' + '_' + config.ABC_CLASS[0]
        elif cumu_rate <= config.ABC_INTERVAL[1]:
            df.loc[index, ['ABC_MPDV']] = 'MPDV' + '_' + config.ABC_CLASS[1]
        elif cumu_rate <= config.ABC_INTERVAL[2]:
            df.loc[index, ['ABC_MPDV']] = 'MPDV' + '_' + config.ABC_CLASS[2]
        elif cumu_rate <= config.ABC_INTERVAL[3]:
            df.loc[index, ['ABC_MPDV']] = 'MPDV' + '_' + config.ABC_CLASS[3]

    # df['ABC_MPDV'] = np.NAN
    # df['comp'] = config.ABC_INTERVAL[0] * prac_salesNum
    # df.loc[(df['vol_rank'] <= df['comp']),
    #        ['ABC_MPDV']] = 'MPDV' + '_' + config.ABC_CLASS[0]
    #
    # df['comp'] = config.ABC_INTERVAL[1] * prac_salesNum
    # df.loc[(df['vol_rank'] <= df['comp']) & (df['ABC_MPDV'].isna()),
    #        ['ABC_MPDV']] = 'MPDV' + '_' + config.ABC_CLASS[1]
    #
    # df['comp'] = config.ABC_INTERVAL[2] * prac_salesNum
    # df.loc[(df['vol_rank'] <= df['comp']) & (df['ABC_MPDV'].isna()),
    #        ['ABC_MPDV']] = 'MPDV' + '_' + config.ABC_CLASS[2]
    #
    # df['comp'] = config.ABC_INTERVAL[3] * prac_salesNum
    # df.loc[(df['vol_rank'] <= df['comp']) & (df['ABC_MPDV'].isna()),
    #        ['ABC_MPDV']] = 'MPDV' + '_' + config.ABC_CLASS[3]
    #
    # df.loc[(df['prac_daily_deli_qty'] == 0) | (df['ABC_MPDV'].isna()),
    #        ['ABC_MPDV']] = 'ZZZZ' + '_' + config.ABC_CLASS[4]

    # 63 BL	ABC_MADQ&MADV
    df['ABC_MADQ&MADV'] = df['ABC_MADQ'] + '&' + df['ABC_MADV']

    # 68 BQ	ABC_MPDQ&MPDV
    df['ABC_MPDQ&MPDV'] = df['ABC_MPDQ'] + '&' + df['ABC_MPDV']

    # 添加辅助列 出库件数占比，出库体积占比
    #  df.drop(['daily_qty_rate','daily_vol_rate','prac_daily_qty_rate','prac_daily_vol_rate',
    #          'qty_rank','vol_rank','prac_qty_rank','prac_vol_rank''comp'])

    '''
    托盘码托件数&重量
    '''
    # 69 BR	箱规每托(含托盘)实际码放高度(mm)(按额定体积&重量折算)
    df['ctn_pltHeight'] = np.NAN
    df.loc[(df['CW_isAbnormal_tag'] == 'N') & (df['corrLongest'] <= config.SIZE['longest'][2]) &
           (df['ctn_pltWt'] <= config.PALLET_STOCK['weight_upper']) &
           (df['min_side'] < config.PALLET_STOCK['valid_height']), ['ctn_pltHeight']] = \
        np.floor(config.PALLET_STOCK['valid_height'] / df['ctn_height']) * df['ctn_height'] + config.PALLET_STOCK[
            'plt_height']

    # 70 BS	箱规每托实际码放件数(按额定体积&重量折算)  码放层数 * 每层箱数 * 箱件数
    df['ctn_pltQty'] = 0
    # 箱高计算的码垛层数 * 每层箱数 * 箱件数
    df.loc[(df['CW_isAbnormal_tag'] == 'N') & (df['ctn_pltWt'] <= config.PALLET_STOCK['weight_upper']),
           ['ctn_pltQty']] = np.floor(config.PALLET_STOCK['valid_height'] / df['ctn_height']) \
                             * df['layer_cartons'] * df['fullCaseUnit']

    ### 托均箱数
    df['ctn_per_plt'] = 0
    df.loc[(df['CW_isAbnormal_tag'] == 'N') & (df['ctn_pltWt'] <= config.PALLET_STOCK['weight_upper']),
           ['ctn_per_plt']] = np.floor(config.PALLET_STOCK['valid_height'] / df['ctn_height']) \
                              * df['layer_cartons']

    # 托盘最大载重计算的码垛层数 * 每层箱数 * 箱件数
    df.loc[(df['CW_isAbnormal_tag'] == 'N') & (df['ctn_pltWt'] > config.PALLET_STOCK['weight_upper']),
           ['ctn_pltQty']] = np.floor(config.PALLET_STOCK['weight_upper']
                                      / (df['corrWeight'] * df['layer_cartons'] * df['fullCaseUnit'])) * \
                             df['layer_cartons'] * df['fullCaseUnit']

    # 71 BT	料箱装载均件数(按额定体积&重量折算)_含全部修正
    df['toteQty'] = 0
    df.loc[(df['corrSW_isAbnormal_tag'] == 'N') & (df['size'] == config.SIZE['type'][0]) &
           (config.TOTE['valid_vol'] / df['corrVol'] * df['corrWeight'] <= config.TOTE['weight_upper']),
           ['toteQty']] = config.TOTE['valid_vol'] / df['corrVol']
    df.loc[(df['corrSW_isAbnormal_tag'] == 'N') & (df['size'] == config.SIZE['type'][0]) &
           (config.TOTE['valid_vol'] / df['corrVol'] * df['corrWeight'] > config.TOTE['weight_upper']),
           ['toteQty']] = config.TOTE['weight_upper'] / df['corrWeight'] * config.TOTE['rate']

    # 72 BU	托盘码放均件数(按额定体积&重量折算)_含全部修正
    df['pltQty'] = np.NAN
    df.loc[(df['ctn_pltQty'] > 0), ['pltQty']] = df['ctn_pltQty']
    df.loc[(df['pltQty'].isna()) & (df['corrSW_isAbnormal_tag'] == 'N') &
           (config.PALLET_STOCK['valid_vol'] / df['corrVol'] * df['corrWeight'] <= config.PALLET_STOCK['weight_upper']),
           ['pltQty']] = config.PALLET_STOCK['valid_vol'] / df['corrVol']
    df.loc[(df['pltQty'].isna()) & (df['corrSW_isAbnormal_tag'] == 'N') &
           (config.PALLET_STOCK['valid_vol'] / df['corrVol'] * df['corrWeight'] > config.PALLET_STOCK['weight_upper']),
           ['pltQty']] = config.PALLET_STOCK['weight_upper'] / df['corrWeight'] * config.PALLET_STOCK['rate']

    # 75 BX	每托重量(kg)(按额定体积&重量折算)_含全部修正
    df['pltWt'] = 0
    df.loc[(df['ctn_pltWt'] > 0), ['pltWt']] = df['ctn_pltWt']
    df.loc[(df['corrSW_isAbnormal_tag'] == 'N') &
           (config.PALLET_STOCK['valid_vol'] / df['corrVol'] * df['corrWeight'] <= config.PALLET_STOCK['weight_upper']),
           ['pltWt']] = config.PALLET_STOCK['valid_vol'] / df['corrVol'] * df['corrWeight'] \
                        + config.PALLET_STOCK['unit_weight']
    df.loc[(df['corrSW_isAbnormal_tag'] == 'N') &
           (config.PALLET_STOCK['valid_vol'] / df['corrVol'] * df['corrWeight'] > config.PALLET_STOCK['weight_upper']),
           ['pltWt']] = config.PALLET_STOCK['weight_upper'] / df['corrWeight'] * config.PALLET_STOCK['rate'] * \
                        df['corrWeight'] + config.PALLET_STOCK['unit_weight']

    # 73 BV	每料箱重量(kg)(按额定体积折算)_含全部修正
    df['vol_toteWt'] = 0
    df.loc[(df['corrSW_isAbnormal_tag'] == 'N') & (df['size'] == config.SIZE['type'][0]) &
           (config.TOTE['valid_vol'] / df['corrVol'] * df['corrWeight'] <= config.TOTE['weight_upper']),
           ['vol_toteWt']] = config.TOTE['valid_vol'] / df['corrVol'] * df['corrWeight'] + config.TOTE['unit_weight']

    # 74 BW	每料箱重量(kg)(按额定体积折算&重量折算)_含全部修正
    df['toteWt'] = 0
    df.loc[(df['corrSW_isAbnormal_tag'] == 'N') & (df['size'] == config.SIZE['type'][0]) &
           (config.TOTE['valid_vol'] / df['corrVol'] * df['corrWeight'] <= config.TOTE['weight_upper']),
           ['toteWt']] = config.TOTE['valid_vol'] / df['corrVol'] * df['corrWeight'] + config.TOTE['unit_weight']
    df.loc[(df['corrSW_isAbnormal_tag'] == 'N') & (df['size'] == config.SIZE['type'][0]) &
           (config.TOTE['valid_vol'] / df['corrVol'] * df['corrWeight'] > config.TOTE['weight_upper']),
           ['toteWt']] = config.TOTE['weight_upper'] / df['corrWeight'] * config.TOTE['rate'] * df['corrWeight'] + \
                         config.TOTE['unit_weight']

    # 根据料箱和托盘装载件数，计算库存折合料箱数&托盘数
    # 83 CF 月度日均库存折合料箱数量(按额定体积折算 & 重量折算)_现状
    df['daily_stock_toteN'] = 0
    df.loc[(df['corrSW_isAbnormal_tag'] == 'N') & (df['size'] == config.SIZE['type'][0]),
           ['daily_stock_toteN']] = df['daily_stock_qty'] / df['toteQty']

    # 84 CG 月度日均库存折合托盘数量(按额定体积 & 重量折算)_现状
    df['daily_stock_pltN'] = 0
    df.loc[(df['corrSW_isAbnormal_tag'] == 'N') & (df['CW_isAbnormal_tag'] == 'N'),
           ['daily_stock_pltN']] = df['daily_stock_qty'] / df['ctn_pltQty']
    df.loc[(df['corrSW_isAbnormal_tag'] == 'N') & (df['CW_isAbnormal_tag'] == 'Y'),
           ['daily_stock_pltN']] = df['daily_stock_qty'] / df['pltQty']

    '''
    托盘料箱重量分级
    '''
    # 76 BY	托盘重量分级(按额定体积&重量折算)_成托
    df['pltWt_class_palletized'] = np.NAN
    df.loc[(df['corrSW_isAbnormal_tag'] == 'Y'), ['pltWt_class_palletized']] = df['corrSW_isAbnormal_state']
    df.loc[(df['size'] == config.SIZE['type'][3]), ['pltWt_class_palletized']] = config.SIZE['type'][3]
    df.loc[(df['daily_stock_pltN'] < 0.5), ['pltWt_class_palletized']] = "00当前库存不成托"

    pltWtClassNum = len(config.PLT_WEIGHT_CLASS)
    # print('pltWtClassNum:')
    # print(pltWtClassNum)
    # print(range(pltWtClassNum))
    # print(len(config.PLT_WEIGHT_INTERVAL))
    # print('*'*10 + 'config.PLT_WEIGHT_CLASS' + '*'*10)
    # print("\n".join(str(i) for i in config.PLT_WEIGHT_CLASS))
    for i in range(pltWtClassNum):
        df.loc[(df['pltWt'] > config.PLT_WEIGHT_INTERVAL[i]) &
               (df['pltWt'] <= config.PLT_WEIGHT_INTERVAL[i + 1]),
               ['pltWt_class_palletized']] = config.PLT_WEIGHT_CLASS[i][0]

    # 77 BZ	托盘重量分级(按额定体积&重量折算)_成托&不成托
    df['pltWt_class_all'] = np.NAN
    df.loc[(df['corrSW_isAbnormal_tag'] == 'Y'), ['pltWt_class_all']] = df['corrSW_isAbnormal_state']
    df.loc[(df['size'] == config.SIZE['type'][3]), ['pltWt_class_all']] = config.SIZE['type'][3]

    # pltWtClassNum = len(config.PLT_WEIGHT_CLASS)
    for i in range(pltWtClassNum):
        df.loc[(df['pltWt'] > config.PLT_WEIGHT_CLASS[i][1]) &
               (df['pltWt'] <= config.PLT_WEIGHT_CLASS[i][2]),
               ['pltWt_class_all']] = config.PLT_WEIGHT_CLASS[i][0]

    # 78 CA	料箱重量分级(按额定体积&重量折算)
    df['toteWt_class'] = np.NAN
    df.loc[(df['corrSW_isAbnormal_tag'] == 'Y'), ['toteWt_class']] = df['corrSW_isAbnormal_state']
    df.loc[(df['toteWt_class'].isna()), ['toteWt_class']] = df['size']

    toteWtClassNum = len(config.TOTE_WEIGHT_CLASS)
    # print('*'*10 + 'config.TOTE_WEIGHT_CLASS' + '*'*10)
    # print("\n".join(str(i) for i in config.TOTE_WEIGHT_CLASS))
    for i in range(toteWtClassNum):
        df.loc[(df['toteWt'] > config.TOTE_WEIGHT_CLASS[i][1]) &
               (df['toteWt'] <= config.TOTE_WEIGHT_CLASS[i][2]),
               ['toteWt_class']] = config.TOTE_WEIGHT_CLASS[i][0]

    '''
    库存相关字段
    '''
    # 85 CH	月度日均库存SKU数量折算_现状
    df['daily_stock_sku'] = df['monthly_stock_cumu_days'] / mdays

    '''
    增加字段，库存折合箱数 分级
    '''
    df['daily_stock_ctnQty_class'] = np.NAN
    df.loc[(df['corrSW_isAbnormal_tag'] == 'Y'), ['daily_stock_ctnQty_class']] = df['corrSW_isAbnormal_state']
    df.loc[(df['size'] == config.SIZE['type'][3]), ['daily_stock_ctnQty_class']] = df['size']
    ctnQty_classNum = len(config.CTN_QTY_CLASS)
    for i in range(ctnQty_classNum):
        if i == ctnQty_classNum - 1:
            df.loc[(df['daily_stock_toteN'] > config.CTN_QTY_CLASS[i][1]),
                   ['daily_stock_ctnQty_class']] = config.CTN_QTY_CLASS[i][0]
        else:
            df.loc[(df['daily_stock_toteN'] > config.CTN_QTY_CLASS[i][1]) &
                   (df['daily_stock_toteN'] <= config.CTN_QTY_CLASS[i][2]),
                   ['daily_stock_ctnQty_class']] = config.CTN_QTY_CLASS[i][0]

    # 86 CI	月度日均库存储量分级(按额定体积&重量折算)_现状 daily_stock_PC_class
    df['daily_stock_PC_class'] = np.NAN

    toteClassNum = len(config.TOTE_CLASS_INTERVAL) - 1
    PCClassNum = len(config.PC_CLASS)
    # pprint.pprint(config.PC_CLASS)
    # print('*' * 10 + 'config.PC_CLASS' + '*' * 10)
    # print("\n".join(str(i) for i in config.PC_CLASS))
    # print(config.PC_CLASS)

    for index, row in df.iterrows():
        if row['corrSW_isAbnormal_tag'] == 'Y':
            df.loc[index, ['daily_stock_PC_class']] = row['corrSW_isAbnormal_state']
        elif row['size'] == config.SIZE['type'][3]:
            df.loc[index, ['daily_stock_PC_class']] = row['size']
        else:
            for i in range(PCClassNum):
                if i < toteClassNum:
                    if row['daily_stock_toteN'] > config.PC_CLASS[i][1] and row['daily_stock_toteN'] <= \
                            config.PC_CLASS[i][2]:
                        df.loc[index, ['daily_stock_PC_class']] = config.PC_CLASS[i][0]
                        break
                else:
                    if row['daily_stock_pltN'] > config.PC_CLASS[i][1] and row['daily_stock_pltN'] <= \
                            config.PC_CLASS[i][2]:
                        df.loc[index, ['daily_stock_PC_class']] = config.PC_CLASS[i][0]
                        break

    # for i in range(PCClassNum):
    #     if i < toteClassNum:
    #         df.loc[(df['daily_stock_toteN'] > config.PC_CLASS[i][1]) &
    #                (df['daily_stock_toteN'] <= config.PC_CLASS[i][2]),
    #                ['daily_stock_PC_class']] = config.PC_CLASS[i][0]
    #     else:
    #         df.loc[(df['daily_stock_PC_class'] == np.NAN) &
    #                (df['daily_stock_pltN'] > config.PC_CLASS[i][1]) &
    #                (df['daily_stock_pltN'] <= config.PC_CLASS[i][2]),
    #                ['daily_stock_PC_class']] = config.PC_CLASS[i][0]

    # 87 CJ	月度库存天数分级
    df['stock_days_class'] = 0
    daysClassNum = len(config.DAYS_CLASS)
    for i in range(daysClassNum):
        df.loc[(df['monthly_stock_cumu_days'] > config.DAYS_CLASS[i][1]) &
               (df['monthly_stock_cumu_days'] <= config.DAYS_CLASS[i][2]),
               ['stock_days_class']] = config.DAYS_CLASS[i][0]

    # 88 CK	静态库存折合料箱数量(按额定体积折算&重量折算)_现状
    df['static_stock_toteN'] = 0
    df.loc[(df['corrSW_isAbnormal_tag'] == 'N') & (df['size'] == config.SIZE['type'][0]),
           ['static_stock_toteN']] = df['static_stock_qty'] / df['toteQty']

    # 89 CL	静态库存折合托盘数量(按额定体积&重量折算)_现状
    df['static_stock_pltN'] = 0
    df.loc[(df['corrSW_isAbnormal_tag'] == 'N') & (df['CW_isAbnormal_tag'] == 'N'),
           ['static_stock_pltN']] = df['static_stock_qty'] / df['ctn_pltQty']
    df.loc[(df['corrSW_isAbnormal_tag'] == 'N') & (df['CW_isAbnormal_tag'] == 'Y'),
           ['static_stock_pltN']] = df['static_stock_qty'] / df['pltQty']

    # 90 CM	静态库存储量分级(按额定体积&重量折算)_现状
    df['static_stock_PC_class'] = np.NAN

    for index, row in df.iterrows():
        if row['corrSW_isAbnormal_tag'] == 'Y':
            df.loc[index, ['static_stock_PC_class']] = row['corrSW_isAbnormal_state']
        elif row['size'] == config.SIZE['type'][3]:
            df.loc[index, ['static_stock_PC_class']] = row['size']
        else:
            for i in range(PCClassNum):
                if i < toteClassNum:
                    if row['static_stock_toteN'] > config.PC_CLASS[i][1] and row['static_stock_toteN'] <= \
                            config.PC_CLASS[i][2]:
                        df.loc[index, ['static_stock_PC_class']] = config.PC_CLASS[i][0]
                        break
                else:
                    if row['static_stock_pltN'] > config.PC_CLASS[i][1] and row['static_stock_pltN'] <= \
                            config.PC_CLASS[i][2]:
                        df.loc[index, ['static_stock_PC_class']] = config.PC_CLASS[i][0]
                        break

    '''
    出库相关字段
    '''
    # 95 CR	月度日均出库折合料箱数量(按额定体积&重量折算)_现状
    df['daily_deli_toteN'] = 0
    df.loc[(df['corrSW_isAbnormal_tag'] == 'N') & (df['size'] == config.SIZE['type'][0]),
           ['daily_deli_toteN']] = df['daily_deli_qty'] / df['toteQty']

    # 96 CS	月度日均出库折合托盘数量(按额定体积&重量折算)_现状
    df['daily_deli_pltN'] = 0
    df.loc[(df['corrSW_isAbnormal_tag'] == 'N') & (df['CW_isAbnormal_tag'] == 'N'),
           ['daily_deli_pltN']] = df['daily_deli_qty'] / df['ctn_pltQty']
    df.loc[(df['corrSW_isAbnormal_tag'] == 'N') & (df['CW_isAbnormal_tag'] == 'Y'),
           ['daily_deli_pltN']] = df['daily_deli_qty'] / df['pltQty']

    # 97 CT	月度日均出库SKU数量折算_现状
    df['daily_deli_sku'] = df['monthly_deli_cumu_days'] / mdays

    # 98 CU	月度SKU动碰计数_现状
    df['daily_deli_saled_sku'] = 0
    df.loc[(df['daily_deli_qty'] > 1), ['daily_deli_saled_sku']] = 1

    # 99 CV	月度日均出库体量分级_现状
    df['daily_deli_PC_class'] = np.NAN

    for index, row in df.iterrows():
        if row['corrSW_isAbnormal_tag'] == 'Y':
            df.loc[index, ['daily_deli_PC_class']] = row['corrSW_isAbnormal_state']
        elif row['size'] == config.SIZE['type'][3]:
            df.loc[index, ['daily_deli_PC_class']] = row['size']
        else:
            for i in range(PCClassNum):
                if i < toteClassNum:
                    if row['daily_deli_toteN'] > config.PC_CLASS[i][1] and row['daily_deli_toteN'] <= \
                            config.PC_CLASS[i][2]:
                        df.loc[index, ['daily_deli_PC_class']] = config.PC_CLASS[i][0]
                        break
                else:
                    if row['daily_deli_pltN'] > config.PC_CLASS[i][1] and row['daily_deli_pltN'] <= \
                            config.PC_CLASS[i][2]:
                        df.loc[index, ['daily_deli_PC_class']] = config.PC_CLASS[i][0]
                        break

    # 100 CW 月度出库天数分级
    df['deli_days_class'] = 0
    for i in range(daysClassNum):
        df.loc[(df['monthly_deli_cumu_days'] > config.DAYS_CLASS[i][1]) &
               (df['monthly_deli_cumu_days'] <= config.DAYS_CLASS[i][2]),
               ['deli_days_class']] = config.DAYS_CLASS[i][0]

    '''
    入库相关字段
    '''
    # 104 DA 月度日均入库折合料箱数量(按额定体积&重量折算)_现状
    df['daily_rec_toteN'] = 0
    df.loc[(df['corrSW_isAbnormal_tag'] == 'N') & (df['size'] == config.SIZE['type'][0]),
           ['daily_rec_toteN']] = df['daily_rec_qty'] / df['toteQty']

    # 105 DB 月度日均入库折合托盘数量(按额定体积 & 重量折算)_现状
    df['daily_rec_pltN'] = 0
    df.loc[(df['corrSW_isAbnormal_tag'] == 'N') & (df['CW_isAbnormal_tag'] == 'N'),
           ['daily_rec_pltN']] = df['daily_rec_qty'] / df['ctn_pltQty']
    df.loc[(df['corrSW_isAbnormal_tag'] == 'N') & (df['CW_isAbnormal_tag'] == 'Y'),
           ['daily_rec_pltN']] = df['daily_rec_qty'] / df['pltQty']

    # 106 DC 月度日均入库SKU数量折算_现状
    df['daily_rec_sku'] = df['monthly_rec_cumu_days'] / mdays

    # 107 DD 月度日均入库体量分级_现状
    df['daily_rec_PC_class'] = np.NAN
    df.loc[(df['corrSW_isAbnormal_tag'] == 'Y'), ['daily_rec_PC_class']] = df['corrSW_isAbnormal_state']
    df.loc[(df['size'] == config.SIZE['type'][3]), ['daily_rec_PC_class']] = df['size']

    for i in range(PCClassNum):
        if i < toteClassNum:
            df.loc[(df['daily_rec_toteN'] > config.PC_CLASS[i][1]) &
                   (df['daily_rec_toteN'] <= config.PC_CLASS[i][2]),
                   ['daily_rec_PC_class']] = config.PC_CLASS[i][0]
        else:
            df.loc[(df['daily_rec_pltN'] > config.PC_CLASS[i][1]) &
                   (df['daily_rec_pltN'] <= config.PC_CLASS[i][2]),
                   ['daily_rec_PC_class']] = config.PC_CLASS[i][0]

    # 108 DE 月度入库天数分级
    df['rec_days_class'] = 0
    for i in range(daysClassNum):
        df.loc[(df['monthly_rec_cumu_days'] > config.DAYS_CLASS[i][1]) &
               (df['monthly_rec_cumu_days'] <= config.DAYS_CLASS[i][2]),
               ['rec_days_class']] = config.DAYS_CLASS[i][0]

    '''
    实际日均出库相关字段 总量/实际出库天数
    '''
    # 114 DK 月度实际日均出库折合料箱数(按额定体积&重量折算)_现状
    df['prac_daily_deli_toteN'] = 0
    df.loc[(df['corrSW_isAbnormal_tag'] == 'N') & (df['size'] == config.SIZE['type'][0]),
           ['prac_daily_deli_toteN']] = df['prac_daily_deli_qty'] / df['toteQty']

    # 115 DL 月度实际日均出库折合托盘数(按额定体积&重量折算)_现状
    df['prac_daily_deli_pltN'] = 0
    df.loc[(df['corrSW_isAbnormal_tag'] == 'N') & (df['CW_isAbnormal_tag'] == 'N'),
           ['prac_daily_deli_pltN']] = df['prac_daily_deli_qty'] / df['ctn_pltQty']
    df.loc[(df['corrSW_isAbnormal_tag'] == 'N') & (df['CW_isAbnormal_tag'] == 'Y'),
           ['prac_daily_deli_pltN']] = df['prac_daily_deli_qty'] / df['pltQty']

    # 116 DM 月度实际日均出库体积分级(按额定体积&重量折算)_现状
    df['prac_daily_deli_PC_class'] = np.NAN
    df.loc[(df['corrSW_isAbnormal_tag'] == 'Y'), ['daily_rec_PC_class']] = df['corrSW_isAbnormal_state']
    df.loc[(df['size'] == config.SIZE['type'][3]), ['daily_rec_PC_class']] = df['size']

    for i in range(PCClassNum):
        if i < toteClassNum:
            df.loc[(df['prac_daily_deli_toteN'] > config.PC_CLASS[i][1]) &
                   (df['prac_daily_deli_toteN'] <= config.PC_CLASS[i][2]),
                   ['prac_daily_deli_PC_class']] = config.PC_CLASS[i][0]
        else:
            df.loc[(df['prac_daily_deli_pltN'] > config.PC_CLASS[i][1]) &
                   (df['prac_daily_deli_pltN'] <= config.PC_CLASS[i][2]),
                   ['prac_daily_deli_PC_class']] = config.PC_CLASS[i][0]

    '''
    存拣模式&设备数量
    '''

    # 117 DN 存拣模式_现状 current_stock_mode
    df['current_stock_mode'] = np.NAN
    df.loc[(df['daily_stock_qty'].isna()) | (df['daily_stock_qty'] == 0), ['current_stock_mode']] = '零库存'
    df.loc[(df['corrSW_isAbnormal_tag'] == 'Y') & (df['current_stock_mode'].isna()),
           ['current_stock_mode']] = df['corrSW_isAbnormal_state']
    # 4H 超大件 存拣合一
    df.loc[(df['size'] == config.SIZE['type'][3]) & (df['current_stock_mode'].isna()),
           ['current_stock_mode']] = config.STOCK_TACTIC['mode'][0]
    df.loc[(df['current_stock_mode'].isna()) & (df['daily_stock_pltN'] <= config.STOCK_TACTIC['mode_interval'][0]),
           ['current_stock_mode']] = config.STOCK_TACTIC['mode'][0]
    df.loc[(df['current_stock_mode'].isna()) & (df['daily_stock_pltN'] <= config.STOCK_TACTIC['mode_interval'][1]),
           ['current_stock_mode']] = config.STOCK_TACTIC['mode'][0]
    df.loc[(df['current_stock_mode'].isna()), ['current_stock_mode']] = config.STOCK_TACTIC['mode'][1]

    # 118 DO 存储设备_现状
    df['current_stock_equipment'] = np.NAN
    df.loc[(df['daily_stock_qty'].isna()) | (df['daily_stock_qty'] == 0), ['current_stock_equipment']] = '零库存'
    df.loc[(df['current_stock_equipment'].isna()) & (df['corrSW_isAbnormal_tag'] == 'Y'),
           ['current_stock_equipment']] = df['corrSW_isAbnormal_state']
    df.loc[(df['current_stock_equipment'].isna()) & (df['size'] == config.SIZE['type'][3]),
           ['current_stock_equipment']] = config.STOCK_TACTIC['mode'][0]
    # 多穿匹配条件，使用多穿&小件&(高值 | MADQ_30B)
    df.loc[(df['current_stock_equipment'].isna()) &
           (config.STOCK_TACTIC['isShuttle'] == 'Y') &
           (df['size'] == config.STOCK_TACTIC['equipment'][0][1][0]) &
           ((df['ABC_MADQ'] == config.STOCK_TACTIC['equipment'][0][2][0]) |
            (df['good_property'] == config.STOCK_TACTIC['equipment'][0][2][1])),
           ['current_stock_equipment']] = config.STOCK_TACTIC['equipment'][0][0]
    # 轻架匹配条件，小件& 托盘数<=0.5
    df.loc[(df['current_stock_equipment'].isna()) & (df['size'] == config.STOCK_TACTIC['equipment'][1][1][0]) &
           (df['daily_stock_pltN'] <= config.STOCK_TACTIC['plt_interval']),
           ['current_stock_equipment']] = config.STOCK_TACTIC['equipment'][1][0]
    # 其他的都为托盘存储
    df.loc[(df['current_stock_equipment'].isna()), ['current_stock_equipment']] = config.STOCK_TACTIC['equipment'][2][0]

    # df['current_stock_equipment'] = np.NAN
    # for index,row in df.iterrows():
    #     # print('daily_stock_qty/corrSW_isAbnormal_tag/size/daily_stock_pltN/ABC_MADQ/good_property')
    #     # print(row[['daily_stock_qty','corrSW_isAbnormal_tag','size','daily_stock_pltN',
    #     #            'ABC_MADQ','good_property']])
    #     if row['daily_stock_qty'] > 0:
    #         if row['corrSW_isAbnormal_tag'] == 'N':
    #             if row['size'] == config.SIZE['type'][0]:
    #                 if row['daily_stock_pltN'] <= config.STOCK_TACTIC['plt_interval']:
    #                     if config.STOCK_TACTIC['isShuttle'] == 'Y':
    #                         if (row['ABC_MADQ'] in config.STOCK_TACTIC['equipment'][0][2] or
    #                               row['good_property'] in config.STOCK_TACTIC['equipment'][0][2]):
    #                             df.loc[index,['current_stock_equipment']] = config.STOCK_TACTIC['equipment'][0][0]
    #                         else:
    #                             df.loc[index,['current_stock_equipment']] = config.STOCK_TACTIC['equipment'][1][0]
    #                     else:
    #                         df.loc[index, ['current_stock_equipment']] = config.STOCK_TACTIC['equipment'][1][0]
    #                 else:
    #                     df.loc[index,['current_stock_equipment']] = config.STOCK_TACTIC['equipment'][2][0]
    #             else:
    #                 df.loc[index, ['current_stock_equipment']] = config.STOCK_TACTIC['equipment'][2][0]
    #         else:
    #             df.loc[index,['current_stock_equipment']] = row['corrSW_isAbnormal_state']
    #     else:
    #         df.loc[index,['current_stock_equipment']] = '库存为0'

    '''
    120 DQ 轻型货架(D300)组数_现状 current_shelfD300N
    '''
    # 120 DQ 轻型货架(D300)组数_现状 current_shelfD300N
    # 增加辅助列 按箱规 和 料箱 计算的拣选为体积
    df['ctn_pickVol'] = np.ceil(df['daily_deli_qty'] * config.STOCK_TACTIC['support_days'] /
                                df['fullCaseUnit']) * df['fullCaseUnit'] / df['corrVol']
    df['tote_pickVol'] = np.ceil(df['daily_deli_qty'] * config.STOCK_TACTIC['support_days'] /
                                 df['toteQty']) * df['toteQty'] / df['corrVol']

    df['current_shelfD300_num'] = 0

    # 计算D300最小货格/最大货格体积
    #  【D300宽】*【D300货位理论最小宽度(100)】*（【D300高】/【D300拟定层数】）*【D300码放系数】/
    #  【D300每货位SKU数量上限】/【D300存拣合一一货多位均值】
    # 最小货格体积
    D300_minUnitVol = config.SHELF_D300['width'] * config.SHELF_D300['min_wid'] * (
            config.SHELF_D300['height'] / config.SHELF_D300['layer']) * config.SHELF_D300['rate']

    # 最大货格体积
    D300_maxUnitVol = config.SHELF_D300['width'] * config.SHELF_D300['max_wid'] * (
            config.SHELF_D300['height'] / config.SHELF_D300['layer']) * config.SHELF_D300['rate']

    # 最长边<300 & 轻架 & 存拣合一 & < 最大货格
    df.loc[(df['corrSW_isAbnormal_tag'] == 'N') &
           (df['daily_stock_qty'] > 0) &
           (df['corrLongest'] <= config.SHELF_D300['width']) &
           (df['current_stock_equipment'] == config.STOCK_TACTIC['equipment'][1][0]) &
           (df['current_stock_mode'] == config.STOCK_TACTIC['mode'][0]) &
           (df['daily_stock_vol_mm'] / config.SHELF_D300['combine_locs'] <= D300_maxUnitVol),
           ['current_shelfD300_num']] \
        = df['daily_stock_vol_mm'] / config.SHELF_D300['valid_vol']
    # 最长边<300 & 轻架 & 存拣合一 & < 最小货格的N（每货位SKU上限）等分 → 最小货格N等分 * 1货多位 位置数
    df.loc[(df['corrSW_isAbnormal_tag'] == 'N') &
           (df['daily_stock_qty'] > 0) &
           (df['corrLongest'] <= config.SHELF_D300['width']) &
           (df['current_stock_equipment'] == config.STOCK_TACTIC['equipment'][1][0]) &
           (df['current_stock_mode'] == config.STOCK_TACTIC['mode'][0]) &
           (df['daily_stock_vol_mm'] / config.SHELF_D300['combine_locs']
            <= D300_minUnitVol / config.SHELF_D300['sku_upper']),
           ['current_shelfD300_num']] \
        = D300_minUnitVol / config.SHELF_D300['sku_upper'] / config.SHELF_D300['valid_vol'] * config.SHELF_D300[
        'combine_locs']

    # 最长边<300 & 轻架 & 存拣分离 & 整箱补货 & 箱规正常 & < 最大货格
    df.loc[(df['corrSW_isAbnormal_tag'] == 'N') &
           (df['daily_stock_qty'] > 0) &
           (df['corrLongest'] <= config.SHELF_D300['width']) &
           (df['current_stock_equipment'] == config.STOCK_TACTIC['equipment'][1][0]) &
           (df['current_stock_mode'] == config.STOCK_TACTIC['mode'][1]) &
           (config.SHELF_D300['replenish'] == '整箱') &
           (df['CW_isAbnormal_tag'] == 'N') &
           (df['ctn_pickVol'] / config.SHELF_D300['separate_locs']
            <= D300_maxUnitVol / config.SHELF_D300['sku_upper']),
           ['current_shelfD300_num']] \
        = df['ctn_pickVol'] / config.SHELF_D300['valid_vol']

    # 最长边<300 & 轻架 & 存拣分离 & 整箱补货 & 箱规异常 & < 最大货格
    df.loc[(df['corrSW_isAbnormal_tag'] == 'N') &
           (df['daily_stock_qty'] > 0) &
           (df['corrLongest'] <= config.SHELF_D300['width']) &
           (df['current_stock_equipment'] == config.STOCK_TACTIC['equipment'][1][0]) &
           (df['current_stock_mode'] == config.STOCK_TACTIC['mode'][1]) &
           (config.SHELF_D300['replenish'] == '整箱') &
           (df['CW_isAbnormal_tag'] == 'Y') &
           (df['tote_pickVol'] / config.SHELF_D300['separate_locs']
            <= D300_maxUnitVol / config.SHELF_D300['sku_upper']),
           ['current_shelfD300_num']] \
        = df['tote_pickVol'] / config.SHELF_D300['valid_vol']

    '''
     遍历行 更新D300组数  (runtime +6s)
     '''
    # for index, row in df.iterrows():
    #     if row['corrSW_isAbnormal_tag'] == 'N':
    #         if row['daily_stock_qty'] > 0:
    #             if row['corrLongest'] <= config.SHELF_D300['width']:
    #                 if row['current_stock_equipment'] == config.STOCK_TACTIC['equipment'][1][0]:
    #                     if row['current_stock_mode'] == config.STOCK_TACTIC['mode'][0]:
    #                         if row['daily_stock_vol_mm'] / config.SHELF_D300['combine_locs'] <= D300_minUnitVol / \
    #                                 config.SHELF_D300['sku_upper']:
    #                             df.loc[index, ['current_shelfD300_num']] = D300_minUnitVol / config.SHELF_D300[
    #                                 'sku_upper'] / \
    #                                                                        config.SHELF_D300['valid_vol'] * \
    #                                                                        config.SHELF_D300[
    #                                                                            'combine_locs']
    #                         elif row['daily_stock_vol_mm'] / config.SHELF_D300['combine_locs'] <= D300_maxUnitVol / \
    #                                 config.SHELF_D300['sku_upper']:
    #                             df.loc[index, ['current_shelfD300_num']] = row['daily_stock_vol_mm'] / config.SHELF_D300[
    #                                 'valid_vol']
    #                         else:
    #                             df['current_shelfD300_num'] = 0
    #                     else:
    #                         if config.SHELF_D300['replenish'] == '整箱':
    #                             if row['CW_isAbnormal_tag'] == 'N':
    #                                 if row['ctn_pickVol'] / config.SHELF_D300['separate_locs'] <= D300_maxUnitVol / \
    #                                         config.SHELF_D300['sku_upper']:
    #                                     df.loc[index, ['current_shelfD300_num']] = row['ctn_pickVol'] / \
    #                                                                                config.SHELF_D300['valid_vol']
    #                                 else:
    #                                     df.loc[index, ['current_shelfD300_num']] = 0
    #                             else:
    #                                 if row['tote_pickVol'] / config.SHELF_D300['separate_locs'] <= D300_maxUnitVol / \
    #                                         config.SHELF_D300['sku_upper']:
    #                                     df.loc[index, ['current_shelfD300_num']] = row['tote_pickVol'] / \
    #                                                                                config.SHELF_D300['valid_vol']
    #                                 else:
    #                                     df.loc[index, ['current_shelfD300_num']] = 0

    '''
    121 DR 轻型货架(D500)组数_现状 current_shelfD500N
    '''
    # 121 DR 轻型货架(D500)组数_现状 current_shelfD500N
    # 增加辅助列 按箱规 和 料箱 计算的拣选为体积

    df['current_shelfD500_num'] = 0

    # 计算D500最小货格/最大货格体积
    #  【D500宽】*【D500货位理论最小宽度(240)】*（【D500高】/【D500拟定层数】）*【D500码放系数】/
    #  【D500每货位SKU数量上限】/【D500存拣合一一货多位均值】
    # 最小货格体积
    D500_minUnitVol = config.SHELF_D500['width'] * config.SHELF_D500['min_wid'] * (
            config.SHELF_D500['height'] / config.SHELF_D500['layer']) * config.SHELF_D500['rate']

    # 最长边<500 & 轻架 & 存拣合一
    df.loc[(df['corrSW_isAbnormal_tag'] == 'N') &
           (df['daily_stock_qty'] > 0) &
           (df['corrLongest'] <= config.SHELF_D500['width']) &
           (df['current_stock_equipment'] == config.STOCK_TACTIC['equipment'][1][0]) &
           (df['current_stock_mode'] == config.STOCK_TACTIC['mode'][0]),
           ['current_shelfD500_num']] \
        = df['daily_stock_vol_mm'] / config.SHELF_D500['valid_vol']
    # 最长边<500 & 轻架 & 存拣合一 & < 最小货格的N（每货位SKU上限）等分 → 最小货格N等分 * 1货多位 位置数
    df.loc[(df['corrSW_isAbnormal_tag'] == 'N') &
           (df['daily_stock_qty'] > 0) &
           (df['corrLongest'] <= config.SHELF_D500['width']) &
           (df['current_stock_equipment'] == config.STOCK_TACTIC['equipment'][1][0]) &
           (df['current_stock_mode'] == config.STOCK_TACTIC['mode'][0]) &
           (df['daily_stock_vol_mm'] / config.SHELF_D500['combine_locs']
            <= D500_minUnitVol / config.SHELF_D500['sku_upper']),
           ['current_shelfD500_num']] \
        = D500_minUnitVol / config.SHELF_D500['sku_upper'] / config.SHELF_D500['valid_vol'] * config.SHELF_D500[
        'combine_locs']

    # 最长边<500 & 轻架 & 存拣分离 & 整箱补货 & 箱规正常
    df.loc[(df['corrSW_isAbnormal_tag'] == 'N') &
           (df['daily_stock_qty'] > 0) &
           (df['corrLongest'] <= config.SHELF_D500['width']) &
           (df['current_stock_equipment'] == config.STOCK_TACTIC['equipment'][1][0]) &
           (df['current_stock_mode'] == config.STOCK_TACTIC['mode'][1]) &
           (config.SHELF_D500['replenish'] == '整箱') &
           (df['CW_isAbnormal_tag'] == 'N'),
           ['current_shelfD500_num']] \
        = df['ctn_pickVol'] / config.SHELF_D500['valid_vol']
    # 最长边<500 & 轻架 & 存拣分离 & 整箱补货  & 箱规正常 & < 最小货格的N（每货位SKU上限）等分
    df.loc[(df['corrSW_isAbnormal_tag'] == 'N') &
           (df['daily_stock_qty'] > 0) &
           (df['corrLongest'] <= config.SHELF_D500['width']) &
           (df['current_stock_equipment'] == config.STOCK_TACTIC['equipment'][1][0]) &
           (df['current_stock_mode'] == config.STOCK_TACTIC['mode'][1]) &
           (config.SHELF_D500['replenish'] == '整箱') &
           (df['CW_isAbnormal_tag'] == 'N') &
           (df['ctn_pickVol'] / config.SHELF_D500['separate_locs']
            <= D500_minUnitVol / config.SHELF_D500['sku_upper']),
           ['current_shelfD500_num']] \
        = D500_minUnitVol / config.SHELF_D500['sku_upper'] / config.SHELF_D500['valid_vol'] * config.SHELF_D500[
        'separate_locs']

    # 最长边<500 & 轻架 & 存拣分离 & 整箱补货 & 箱规异常 & < 最大货格
    df.loc[(df['corrSW_isAbnormal_tag'] == 'N') &
           (df['daily_stock_qty'] > 0) &
           (df['corrLongest'] <= config.SHELF_D500['width']) &
           (df['current_stock_equipment'] == config.STOCK_TACTIC['equipment'][1][0]) &
           (df['current_stock_mode'] == config.STOCK_TACTIC['mode'][1]) &
           (config.SHELF_D500['replenish'] == '整箱') &
           (df['CW_isAbnormal_tag'] == 'Y'),
           ['current_shelfD500_num']] \
        = df['tote_pickVol'] / config.SHELF_D500['valid_vol']
    # 最长边<500 & 轻架 & 存拣分离 & 箱规异常 & < 最小货格的N（每货位SKU上限）等分 → 最小货格N等分 * 1货多位 位置数
    df.loc[(df['corrSW_isAbnormal_tag'] == 'N') &
           (df['daily_stock_qty'] > 0) &
           (df['corrLongest'] <= config.SHELF_D500['width']) &
           (df['current_stock_equipment'] == config.STOCK_TACTIC['equipment'][1][0]) &
           (df['current_stock_mode'] == config.STOCK_TACTIC['mode'][1]) &
           (config.SHELF_D500['replenish'] == '整箱') &
           (df['CW_isAbnormal_tag'] == 'Y') &
           (df['tote_pickVol'] / config.SHELF_D500['separate_locs']
            <= D500_minUnitVol / config.SHELF_D500['sku_upper']),
           ['current_shelfD500_num']] \
        = D500_minUnitVol / config.SHELF_D500['sku_upper'] / config.SHELF_D500['valid_vol'] * config.SHELF_D500[
        'separate_locs']

    # 最长边<500 & 轻架 & 存拣分离 & 整托补货
    df.loc[(df['corrSW_isAbnormal_tag'] == 'N') &
           (df['daily_stock_qty'] > 0) &
           (df['corrLongest'] <= config.SHELF_D500['width']) &
           (df['current_stock_equipment'] == config.STOCK_TACTIC['equipment'][1][0]) &
           (df['current_stock_mode'] == config.STOCK_TACTIC['mode'][1]) &
           (config.SHELF_D500['replenish'] == '整托'),
           ['current_shelfD500_num']] \
        = np.ceil(df['daily_deli_qty'] * config.STOCK_TACTIC['support_days'] / df['pltQty']) \
          * df['pltQty'] * df['corrVol'] / config.SHELF_D500['valid_vol']

    # D300组数>0的更新为0
    df.loc[(df['current_shelfD300_num'] > 0), ['current_shelfD500_num']] = 0

    '''
    122 DS 轻型货架(D600)组数_现状 current_shelfD600N
    '''
    # 122 DS 轻型货架(D600)组数_现状 current_shelfD600N
    df['current_shelfD600_num'] = np.NAN

    # 计算D600最小货格/最大货格体积
    #  【D600宽】*【D600货位理论最小宽度(240)】*（【D600高】/【D600拟定层数】）*【D600码放系数】/
    #  【D600每货位SKU数量上限】/【D600存拣合一一货多位均值】
    # 最小货格体积
    D600_minUnitVol = config.SHELF_D600['width'] * config.SHELF_D600['min_wid'] * (
            config.SHELF_D600['height'] / config.SHELF_D600['layer']) * config.SHELF_D600['rate']

    # 最长边<600 & 轻架 & 存拣合一
    df.loc[(df['corrSW_isAbnormal_tag'] == 'N') &
           (df['daily_stock_qty'] > 0) &
           (df['current_shelfD300_num'] == 0) &
           (df['current_shelfD500_num'] == 0) &
           (df['corrLongest'] <= config.SHELF_D600['width']) &
           (df['current_stock_equipment'] == config.STOCK_TACTIC['equipment'][1][0]) &
           (df['current_stock_mode'] == config.STOCK_TACTIC['mode'][0]),
           ['current_shelfD600_num']] \
        = df['daily_stock_vol_mm'] / config.SHELF_D600['valid_vol']
    # 最长边<600 & 轻架 & 存拣合一 & < 最小货格的N（每货位SKU上限）等分 → 最小货格N等分 * 1货多位 位置数
    df.loc[(df['corrSW_isAbnormal_tag'] == 'N') &
           (df['daily_stock_qty'] > 0) &
           (df['current_shelfD300_num'] == 0) &
           (df['current_shelfD500_num'] == 0) &
           (df['corrLongest'] <= config.SHELF_D600['width']) &
           (df['current_stock_equipment'] == config.STOCK_TACTIC['equipment'][1][0]) &
           (df['current_stock_mode'] == config.STOCK_TACTIC['mode'][0]) &
           (df['daily_stock_vol_mm'] / config.SHELF_D600['combine_locs']
            <= D600_minUnitVol / config.SHELF_D600['sku_upper']),
           ['current_shelfD600_num']] \
        = D600_minUnitVol / config.SHELF_D600['sku_upper'] / config.SHELF_D600['valid_vol'] * config.SHELF_D600[
        'combine_locs']

    # 最长边<600 & 轻架 & 存拣分离 & 整箱补货 & 箱规正常
    df.loc[(df['corrSW_isAbnormal_tag'] == 'N') &
           (df['daily_stock_qty'] > 0) &
           (df['current_shelfD300_num'] == 0) &
           (df['current_shelfD500_num'] == 0) &
           (df['corrLongest'] <= config.SHELF_D600['width']) &
           (df['current_stock_equipment'] == config.STOCK_TACTIC['equipment'][1][0]) &
           (df['current_stock_mode'] == config.STOCK_TACTIC['mode'][1]) &
           (config.SHELF_D600['replenish'] == '整箱') &
           (df['CW_isAbnormal_tag'] == 'N'),
           ['current_shelfD600_num']] \
        = df['ctn_pickVol'] / config.SHELF_D600['valid_vol']
    # 最长边<600 & 轻架 & 存拣分离 & 整箱补货  & 箱规正常 & < 最小货格的N（每货位SKU上限）等分
    df.loc[(df['corrSW_isAbnormal_tag'] == 'N') &
           (df['daily_stock_qty'] > 0) &
           (df['current_shelfD300_num'] == 0) &
           (df['current_shelfD500_num'] == 0) &
           (df['corrLongest'] <= config.SHELF_D600['width']) &
           (df['current_stock_equipment'] == config.STOCK_TACTIC['equipment'][1][0]) &
           (df['current_stock_mode'] == config.STOCK_TACTIC['mode'][1]) &
           (config.SHELF_D600['replenish'] == '整箱') &
           (df['CW_isAbnormal_tag'] == 'N') &
           (df['ctn_pickVol'] / config.SHELF_D600['separate_locs']
            <= D600_minUnitVol / config.SHELF_D600['sku_upper']),
           ['current_shelfD600_num']] \
        = D600_minUnitVol / config.SHELF_D600['sku_upper'] / config.SHELF_D600['valid_vol'] * config.SHELF_D600[
        'separate_locs']

    # 最长边<600 & 轻架 & 存拣分离 & 整箱补货 & 箱规异常 & < 最大货格
    df.loc[(df['corrSW_isAbnormal_tag'] == 'N') &
           (df['daily_stock_qty'] > 0) &
           (df['current_shelfD300_num'] == 0) &
           (df['current_shelfD500_num'] == 0) &
           (df['corrLongest'] <= config.SHELF_D600['width']) &
           (df['current_stock_equipment'] == config.STOCK_TACTIC['equipment'][1][0]) &
           (df['current_stock_mode'] == config.STOCK_TACTIC['mode'][1]) &
           (config.SHELF_D600['replenish'] == '整箱') &
           (df['CW_isAbnormal_tag'] == 'Y'),
           ['current_shelfD600_num']] \
        = df['tote_pickVol'] / config.SHELF_D600['valid_vol']
    # 最长边<600 & 轻架 & 存拣分离 & 箱规异常 & < 最小货格的N（每货位SKU上限）等分 → 最小货格N等分 * 1货多位 位置数
    df.loc[(df['corrSW_isAbnormal_tag'] == 'N') &
           (df['daily_stock_qty'] > 0) &
           (df['current_shelfD300_num'] == 0) &
           (df['current_shelfD500_num'] == 0) &
           (df['corrLongest'] <= config.SHELF_D600['width']) &
           (df['current_stock_equipment'] == config.STOCK_TACTIC['equipment'][1][0]) &
           (df['current_stock_mode'] == config.STOCK_TACTIC['mode'][1]) &
           (config.SHELF_D600['replenish'] == '整箱') &
           (df['CW_isAbnormal_tag'] == 'Y') &
           (df['tote_pickVol'] / config.SHELF_D600['separate_locs']
            <= D600_minUnitVol / config.SHELF_D600['sku_upper']),
           ['current_shelfD600_num']] \
        = D600_minUnitVol / config.SHELF_D600['sku_upper'] / config.SHELF_D600['valid_vol'] * config.SHELF_D600[
        'separate_locs']

    # 最长边<600 & 轻架 & 存拣分离 & 整托补货
    df.loc[(df['corrSW_isAbnormal_tag'] == 'N') &
           (df['daily_stock_qty'] > 0) &
           (df['current_shelfD300_num'] == 0) &
           (df['current_shelfD500_num'] == 0) &
           (df['corrLongest'] <= config.SHELF_D600['width']) &
           (df['current_stock_equipment'] == config.STOCK_TACTIC['equipment'][1][0]) &
           (df['current_stock_mode'] == config.STOCK_TACTIC['mode'][1]) &
           (config.SHELF_D600['replenish'] == '整托'),
           ['current_shelfD600_num']] \
        = np.ceil(df['daily_deli_qty'] * config.STOCK_TACTIC['support_days'] / df['pltQty']) \
          * df['pltQty'] * df['corrVol'] / config.SHELF_D600['valid_vol']

    # 更新空值为0
    df.loc[(df['current_shelfD600_num'].isna()), ['current_shelfD600_num']] = 0

    # 119 DP 存储设备-货架规格_现状 current_stock_equiSize
    df['current_stock_equiSize'] = df['current_stock_equipment']
    df.loc[(df['current_stock_equipment'] == config.STOCK_TACTIC['equipment'][1][0]) &
           (df['current_shelfD300_num'] > 0),
           ['current_stock_equiSize']] = config.SHELF_D300['name']
    df.loc[(df['current_stock_equipment'] == config.STOCK_TACTIC['equipment'][1][0]) &
           (df['current_shelfD500_num'] > 0),
           ['current_stock_equiSize']] = config.SHELF_D500['name']
    df.loc[(df['current_stock_equipment'] == config.STOCK_TACTIC['equipment'][1][0]) &
           (df['current_shelfD600_num'] > 0),
           ['current_stock_equiSize']] = config.SHELF_D600['name']

    '''
    123	DT 多穿货位数量_现状 current_shuttle_num
    '''
    df['current_shuttle_num'] = 0
    for index, row in df.iterrows():
        if row['corrSW_isAbnormal_tag'] == 'N':
            if row['daily_stock_qty'] > 0:
                if row['current_stock_equipment'] == '多穿':
                    if row['current_stock_mode'] == '存拣合一':
                        df.loc[index, ['current_shuttle_num']] = np.ceil(
                            row['daily_stock_vol_mm'] / config.TOTE['valid_vol'])
                    else:
                        if config.SHUTTLE['replenish'] == '整托':
                            df.loc[index, ['current_shuttle_num']] = np.ceil(np.ceil(
                                row['prac_daily_deli_pltN'] * config.STOCK_TACTIC['support_days']) * (
                                                                                     config.PALLET_STOCK[
                                                                                         'valid_vol'] / config.TOTE[
                                                                                         'valid_vol']))
                        else:
                            if row['CW_isAbnormal_tag'] == 'N':
                                df.loc[index, ['current_shuttle_num']] = np.ceil(np.ceil(
                                    row['prac_daily_deli_qty'] * config.STOCK_TACTIC['support_days']) * (
                                                                                         row['fullCaseUnit'] / row[
                                                                                     'toteQty']))
                            else:
                                df.loc[index, ['current_shuttle_num']] = np.ceil(
                                    row['prac_daily_deli_toteN'] * config.STOCK_TACTIC['support_days'])

    '''
    124 DU 托盘拣选位托盘数(P)_现状
    '''
    df['current_pltPickN'] = 0
    for index, row in df.iterrows():
        if row['corrSW_isAbnormal_tag'] == 'N':
            if row['daily_stock_qty'] > 0:
                if row['current_stock_equipment'] == '托盘':
                    if row['current_stock_mode'] == '存拣合一':
                        df.loc[index, ['current_pltPickN']] = np.ceil(row['daily_stock_pltN'])
                    else:
                        if row['prac_daily_deli_pltN'] * config.STOCK_TACTIC['support_days'] <= row[
                            'daily_stock_qty'] - np.floor(row['daily_stock_qty'] / row['pltQty']) * row['pltQty']:
                            df.loc[index, ['current_pltPickN']] = 1
                        elif row['prac_daily_deli_pltN'] * config.STOCK_TACTIC['support_days'] - np.floor(
                                row['prac_daily_deli_pltN'] * config.STOCK_TACTIC['support_days'] / row['pltQty']) * \
                                row['pltQty'] <= row['daily_stock_qty'] - np.floor(
                            row['daily_stock_qty'] / row['pltQty']) * row['pltQty']:
                            df.loc[index, ['current_pltPickN']] = np.ceil(
                                row['prac_daily_deli_pltN'] * config.STOCK_TACTIC['support_days'])
                        else:
                            df.loc[index, ['current_pltPickN']] = np.ceil(
                                row['prac_daily_deli_pltN'] * config.STOCK_TACTIC['support_days']) + 1

    '''
    127 DX 拣货位商品件数_现状 current_pickQty
    '''
    df['current_pickQty'] = 0
    for index, row in df.iterrows():
        if row['current_stock_mode'] == '存拣合一':
            df.loc[index, ['current_pickQty']] = row['daily_stock_qty']
        else:
            if row['corrVol'] > 0 and row['current_shelfD300_num'] * config.SHELF_D300['valid_vol'] / row['corrVol'] + \
                    row['current_shelfD500_num'] * config.SHELF_D500['valid_vol'] / row['corrVol'] + \
                    row['current_shelfD600_num'] * config.SHELF_D600['valid_vol'] / row['corrVol'] + \
                    row['current_shuttle_num'] * config.TOTE['valid_vol'] / row['corrVol'] + \
                    row['current_pltPickN'] * config.PALLET_STOCK['valid_vol'] / row['corrVol'] > row[
                'daily_stock_qty']:
                df.loc[index, ['current_pickQty']] = row['daily_stock_qty']
            else:
                if row['corrVol'] > 0 and row['pltQty'] > 0 and row['current_pltPickN'] > 0:
                    df.loc[index, ['current_pickQty']] = row['current_shelfD300_num'] * config.SHELF_D300['valid_vol'] / \
                                                         row['corrVol'] + \
                                                         row['current_shelfD500_num'] * config.SHELF_D500['valid_vol'] / \
                                                         row['corrVol'] + \
                                                         row['current_shelfD600_num'] * config.SHELF_D600['valid_vol'] / \
                                                         row['corrVol'] + \
                                                         row['current_shuttle_num'] * config.TOTE['valid_vol'] / row[
                                                             'corrVol'] + ((row['daily_stock_qty'] - np.floor(
                        row['daily_stock_qty'] / row['pltQty']) * row['pltQty']) + (row['current_pltPickN'] - 1) * row[
                                                                               'pltQty'])

    '''
    128 DY 存储位商品件数_现状 current_stockQty
    '''
    df['current_stockQty'] = 0
    df.loc[(df['daily_stock_qty'] - df['current_pickQty'] > 0), ['current_stockQty']] = df['daily_stock_qty'] - \
                                                                                        df['current_pickQty']

    '''
    125 DV 托盘存储位托盘数(P)_现状 current_pltStockN
    '''
    df['current_pltStockN'] = 0
    df.loc[(df['corrSW_isAbnormal_tag'] == 'N') & (df['daily_stock_qty'] > 0)
           & (df['current_stock_equipment'] != '轻架'), ['current_pltStockN']] = df['current_stockQty'] / df['pltQty']

    '''
    126	DW 拣选位存储单元折算托盘数量_现状
    '''
    df['current_pickUnit2plt'] = 0
    df.loc[(df['current_stock_equipment'] == '多穿'), ['current_pickUnit2plt']] = df['current_shuttle_num'] * \
                                                                                config.TOTE['2plt']
    df.loc[(df['current_stock_equipment'] == '轻型货架(D300)'), ['current_pickUnit2plt']] = df['current_shuttle_num'] * \
                                                                                        config.SHELF_D300['2plt']
    df.loc[(df['current_stock_equipment'] == '轻型货架(D500)'), ['current_pickUnit2plt']] = df['current_shuttle_num'] * \
                                                                                        config.SHELF_D500['2plt']
    df.loc[(df['current_stock_equipment'] == '轻型货架(D600)'), ['current_pickUnit2plt']] = df['current_shuttle_num'] * \
                                                                                        config.SHELF_D600['2plt']

    # 129 DZ 拣货位商品体积(m3)_现状
    df['current_pickVol_m'] = df['current_pickQty'] * df['corrVol'] / pow(10, 9)

    # 130 EA 存储位商品体积(m3)_现状
    df['current_stockVol_m'] = df['current_stockQty'] * df['corrVol'] / pow(10, 9)

    df['vol_factor'] = df['current_stockVol_m'] * pow(10, 9) / (
            df['current_pltStockN'] * config.PALLET_STOCK['valid_vol'] / config.PALLET_STOCK['rate'])

    # 131 EB 存储位箱规体积(m3)_现状
    df['current_stockCtnVol'] = 0
    df.loc[(df['CW_isAbnormal_tag'] == 'N'), ['current_stockCtnVol']] = (df['pltQty'] / df['fullCaseUnit']) * (
            df['ctn_long'] * df['ctn_width'] * df['ctn_height']) * \
                                                                        (df['current_stockQty'] / df['pltQty']) / pow(
        10, 9)

    df['ctnVol_factor'] = df['current_stockCtnVol'] * pow(10, 9) / (
            df['current_pltStockN'] * config.PALLET_STOCK['valid_vol'] / config.PALLET_STOCK['rate'])

    # 132 EC 调拨出库(ABC标识) allot_tag_ABC
    df['allot_tag_ABC'] = 'N'
    df.loc[(df['ABC_MADQ'] == 'MADQ_1SA') | (df['ABC_MADQ'] == 'MADQ_20A') |
           (df['ABC_MADQ'] == 'MADQ_30B'), ['allot_tag_ABC']] = 'Y'

    '''
    规划相关字段
    '''
    '''
    规划库存/出库/入库 相关字段, 乘规划相关系数
    '''
    # 153 EX 月度日均库存数量(随库存周期改变-含SKU增加库存)_规划 design_daily_stock_qty
    df['design_daily_stock_qty'] = df['daily_stock_qty'] * config.DESIGN_COEFFICIENT['total_qty_coe']

    # 154 EY 月度日均库存体积(m3)(随库存周期改变-含SKU增加库存)_规划 design_daily_stock_vol_m
    df['design_daily_stock_vol_m'] = df['daily_stock_vol_m'] * config.DESIGN_COEFFICIENT['total_qty_coe']

    # 155 EZ 月度日均库存折合托盘数量(随SKU数量及库存周期改变-含SKU增加库存-按额定体积&重量折算)_规划
    df['design_daily_stock_pltN'] = df['daily_stock_pltN'] * config.DESIGN_COEFFICIENT['total_qty_coe']

    # 156 FA 月度日均库存SKU数量折算_规划
    df['design_daily_stock_sku'] = df['daily_stock_sku'] * config.DESIGN_COEFFICIENT['sku_num_coe']

    # 157 FB 月度日均出库数量(随SKU数量及库存周期改变-含SKU增加库存-含调拨)_规划
    df['design_daily_deli_qty'] = round(df['daily_deli_qty'] * config.DESIGN_COEFFICIENT['total_qty_coe'], 2)

    # 158 FC 月度日均出库体积(m3)(随SKU数量及库存周期改变-含SKU增加库存-含调拨)_规划
    df['design_daily_deli_vol_m'] = df['daily_deli_vol_m'] * config.DESIGN_COEFFICIENT['total_qty_coe']

    # 159 FD 月度日均出库折合托盘数量(随SKU数量及库存周期改变-含SKU增加库存-含调拨)_规划
    df['design_daily_deli_pltN'] = df['daily_deli_pltN'] * config.DESIGN_COEFFICIENT['total_qty_coe']

    # 160 FE 月度日均出库SKU数量折算_规划
    df['design_daily_deli_sku'] = df['daily_deli_sku'] * config.DESIGN_COEFFICIENT['sku_num_coe']

    # 161 FF 月度SKU动碰计数_规划
    df['design_daily_deli_saled_sku'] = df['daily_deli_saled_sku'] * config.DESIGN_COEFFICIENT['sku_num_coe']

    '''
    规划的实际出库相关字段
    '''
    # 162 FG 月度实际日均库存数量(随SKU数量及库存周期改变而变化-含SKU增加部分库存件数)_规划
    df['design_prac_daily_stock_qty'] = df['prac_daily_stock_qty'] * config.DESIGN_COEFFICIENT['total_qty_coe']

    # 163 FH 月度实际日均出库数量(随SKU数量及库存周期改变而变化,不含SKU增加部分库存件数-含调拨)_规划
    df['design_prac_daily_deli_qty'] = df['prac_daily_deli_qty'] * config.DESIGN_COEFFICIENT['total_qty_coe']

    # 164 FI 月度实际日均出库折合托盘数量(随SKU数量及库存周期改变而变化,不含SKU增加部分库存件数-含调拨)_规划
    df['design_prac_daily_deli_pltN'] = df['prac_daily_deli_pltN'] * config.DESIGN_COEFFICIENT['total_qty_coe']

    # 165 FJ 月度日均入库数量(随SKU数量及库存周期改变而变化,含SKU增加部分库存件数)_规划
    df['design_daily_rec_qty'] = df['daily_rec_qty'] * config.DESIGN_COEFFICIENT['total_qty_coe']

    # 166 FK 月度日均入库折合托盘数量(随SKU数量及库存周期改变而变化,含SKU增加部分库存件数)_规划
    df['design_daily_rec_pltN'] = df['daily_rec_pltN'] * config.DESIGN_COEFFICIENT['total_qty_coe']

    '''
    存拣模式相关字段
    '''
    # 133 ED 存拣模式_规划 design_stock_mode
    df['design_stock_mode'] = df['current_stock_mode']
    # 小于等于1托，存拣合一
    df.loc[(df['daily_stock_pltN'] * config.DESIGN_COEFFICIENT['single_sku_qty_coe'] <=
            config.STOCK_TACTIC['mode_interval'][1]), ['design_stock_mode']] = config.STOCK_TACTIC['mode'][0]
    # 大于1托，存拣分离
    df.loc[(df['daily_stock_pltN'] * config.DESIGN_COEFFICIENT['single_sku_qty_coe'] >
            config.STOCK_TACTIC['mode_interval'][1]), ['design_stock_mode']] = config.STOCK_TACTIC['mode'][1]

    # 134 EE 存储设备_规划 design_stock_equipment
    df['design_stock_equipment'] = df['current_stock_equipment']
    # 轻架匹配条件，小件& 托盘数 * 规划系数<=0.5
    df.loc[(df['size'] == config.STOCK_TACTIC['equipment'][1][1][0]) &
           (df['daily_stock_pltN'] * config.DESIGN_COEFFICIENT['single_sku_qty_coe'] <=
            config.STOCK_TACTIC['mode_interval'][0]),
           ['design_stock_equipment']] = config.STOCK_TACTIC['equipment'][1][0]
    df.loc[(df['size'] == config.STOCK_TACTIC['equipment'][1][1][0]) &
           (df['daily_stock_pltN'] * config.DESIGN_COEFFICIENT['single_sku_qty_coe'] <=
            config.STOCK_TACTIC['mode_interval'][1]),
           ['design_stock_equipment']] = config.STOCK_TACTIC['equipment'][1][0]
    # 其他的都为托盘存储
    df.loc[(df['design_stock_equipment'].isna()), ['design_stock_equipment']] = config.STOCK_TACTIC['equipment'][2][0]

    '''
    136 EG 轻型货架(D300)组数_规划 
    '''
    df['design_ctn_pickVol'] = np.ceil(df['daily_deli_qty'] * config.DESIGN_COEFFICIENT['single_sku_qty_coe']
                                       * config.STOCK_TACTIC['support_days'] / df['fullCaseUnit']) * \
                               df['fullCaseUnit'] / df['corrVol']
    df['design_tote_pickVol'] = np.ceil(df['daily_deli_qty'] * config.DESIGN_COEFFICIENT['single_sku_qty_coe']
                                        * config.STOCK_TACTIC['support_days'] / df['toteQty']) * \
                                df['toteQty'] / df['corrVol']

    df['design_shelfD300_num'] = 0
    for index, row in df.iterrows():
        if row['corrSW_isAbnormal_tag'] == 'N':
            if row['daily_stock_qty'] > 0:
                if row['corrLongest'] <= config.SHELF_D300['width']:
                    if row['design_stock_equipment'] == config.STOCK_TACTIC['equipment'][1][0]:  # 轻架
                        if row['design_stock_mode'] == config.STOCK_TACTIC['mode'][0]:  # 存拣合一
                            if row['daily_stock_vol_mm'] * config.DESIGN_COEFFICIENT['single_sku_qty_coe'] / \
                                    config.SHELF_D300['combine_locs'] <= D300_minUnitVol / config.SHELF_D300[
                                'sku_upper']:
                                df.loc[index, ['design_shelfD300_num']] = D300_minUnitVol / config.SHELF_D300[
                                    'sku_upper'] / config.SHELF_D300['valid_vol'] * config.SHELF_D300['combine_locs']
                            elif row['daily_stock_vol_mm'] * config.DESIGN_COEFFICIENT['single_sku_qty_coe'] / \
                                    config.SHELF_D300['combine_locs'] <= D300_maxUnitVol / config.SHELF_D300[
                                'sku_upper']:
                                df.loc[index, ['design_shelfD300_num']] = row['daily_stock_vol_mm'] * \
                                                                          config.DESIGN_COEFFICIENT[
                                                                              'single_sku_qty_coe'] / config.SHELF_D300[
                                                                              'valid_vol']
                        else:  # 存拣分离
                            if config.SHELF_D300['replenish'] == '整箱':
                                if row['CW_isAbnormal_tag'] == 'N':
                                    if row['design_ctn_pickVol'] / config.SHELF_D300[
                                        'separate_locs'] <= D300_maxUnitVol / \
                                            config.SHELF_D300['sku_upper']:
                                        df.loc[index, ['design_shelfD300_num']] = row['design_ctn_pickVol'] / \
                                                                                  config.SHELF_D300['valid_vol']
                                else:
                                    if row['design_tote_pickVol'] / config.SHELF_D300[
                                        'separate_locs'] <= D300_maxUnitVol / \
                                            config.SHELF_D300['sku_upper']:
                                        df.loc[index, ['design_shelfD300_num']] = row['design_tote_pickVol'] / \
                                                                                  config.SHELF_D300['valid_vol']

    '''
    137 EG 轻型货架(D500)组数_规划
    '''
    df['design_shelfD500_num'] = 0
    for index, row in df.iterrows():
        if row['corrSW_isAbnormal_tag'] == 'N':
            if row['daily_stock_qty'] > 0:
                if row['design_shelfD300_num'] == 0:
                    if row['corrLongest'] <= config.SHELF_D500['width']:
                        if row['design_stock_equipment'] == config.STOCK_TACTIC['equipment'][1][0]:  # 轻架
                            if row['design_stock_mode'] == config.STOCK_TACTIC['mode'][0]:  # 存拣合一
                                if row['daily_stock_vol_mm'] * config.DESIGN_COEFFICIENT['single_sku_qty_coe'] / \
                                        config.SHELF_D500['combine_locs'] <= D500_minUnitVol / config.SHELF_D500[
                                    'sku_upper']:
                                    df.loc[index, ['design_shelfD500_num']] = D500_minUnitVol / config.SHELF_D500[
                                        'sku_upper'] / config.SHELF_D500['valid_vol'] * config.SHELF_D500[
                                                                                  'combine_locs']
                                else:
                                    df.loc[index, ['design_shelfD500_num']] = row['daily_stock_vol_mm'] * \
                                                                              config.DESIGN_COEFFICIENT[
                                                                                  'single_sku_qty_coe'] / \
                                                                              config.SHELF_D500[
                                                                                  'valid_vol']
                            else:  # 存拣分离
                                if config.SHELF_D500['replenish'] == '整箱':  # 整箱补货
                                    if row['CW_isAbnormal_tag'] == 'N':  # 箱规正常
                                        if row['design_ctn_pickVol'] / config.SHELF_D500[
                                            'separate_locs'] <= D500_minUnitVol / \
                                                config.SHELF_D500['sku_upper']:
                                            df.loc[index, ['design_shelfD500_num']] = D500_minUnitVol / \
                                                                                      config.SHELF_D500[
                                                                                          'sku_upper'] / \
                                                                                      config.SHELF_D500['valid_vol'] * \
                                                                                      config.SHELF_D500[
                                                                                          'combine_locs']
                                        else:
                                            df.loc[index, ['design_shelfD500_num']] = row['design_ctn_pickVol'] / \
                                                                                      config.SHELF_D500['valid_vol']
                                    else:  # 箱规异常常
                                        if row['design_tote_pickVol'] / config.SHELF_D500[
                                            'separate_locs'] <= D500_minUnitVol / \
                                                config.SHELF_D500['sku_upper']:
                                            df.loc[index, ['design_shelfD500_num']] = D500_minUnitVol / \
                                                                                      config.SHELF_D500[
                                                                                          'sku_upper'] / \
                                                                                      config.SHELF_D500['valid_vol'] * \
                                                                                      config.SHELF_D500[
                                                                                          'combine_locs']
                                        else:
                                            df.loc[index, ['design_shelfD500_num']] = row['design_tote_pickVol'] / \
                                                                                      config.SHELF_D500['valid_vol']
                                else:
                                    df.loc[index, ['design_shelfD500_num']] = np.ceil(
                                        row['daily_deli_qty'] * config.DESIGN_COEFFICIENT['single_sku_qty_coe'] *
                                        config.STOCK_TACTIC['support_days'] / row['pltQty']) * row['pltQty'] * row[
                                                                                  'corrVol'] / config.SHELF_D500[
                                                                                  'valid_vol'] * (
                                                                                      config.DESIGN_COEFFICIENT[
                                                                                          'total_qty_coe'] /
                                                                                      config.DESIGN_COEFFICIENT[
                                                                                          'single_sku_qty_coe'])

    '''
    137 EG 轻型货架(D600)组数_规划
    '''
    df['design_shelfD600_num'] = 0
    for index, row in df.iterrows():
        if row['corrSW_isAbnormal_tag'] == 'N':
            if row['daily_stock_qty'] > 0:
                if row['design_shelfD300_num'] == 0 and row['design_shelfD500_num'] == 0:
                    if row['corrLongest'] <= config.SHELF_D600['width']:
                        if row['design_stock_equipment'] == config.STOCK_TACTIC['equipment'][1][0]:  # 轻架
                            if row['design_stock_mode'] == config.STOCK_TACTIC['mode'][0]:  # 存拣合一
                                if row['daily_stock_vol_mm'] * config.DESIGN_COEFFICIENT['single_sku_qty_coe'] / \
                                        config.SHELF_D600['combine_locs'] <= D600_minUnitVol / config.SHELF_D600[
                                    'sku_upper']:
                                    df.loc[index, ['design_shelfD600_num']] = D600_minUnitVol / config.SHELF_D600[
                                        'sku_upper'] / config.SHELF_D600['valid_vol'] * config.SHELF_D600[
                                                                                  'combine_locs']
                                else:
                                    df.loc[index, ['design_shelfD600_num']] = row['daily_stock_vol_mm'] * \
                                                                              config.DESIGN_COEFFICIENT[
                                                                                  'single_sku_qty_coe'] / \
                                                                              config.SHELF_D600[
                                                                                  'valid_vol']
                            else:  # 存拣分离
                                if config.SHELF_D600['replenish'] == '整箱':  # 整箱补货
                                    if row['CW_isAbnormal_tag'] == 'N':  # 箱规正常
                                        if row['design_ctn_pickVol'] / config.SHELF_D600[
                                            'separate_locs'] <= D600_minUnitVol / \
                                                config.SHELF_D600['sku_upper']:
                                            df.loc[index, ['design_shelfD600_num']] = D600_minUnitVol / \
                                                                                      config.SHELF_D600[
                                                                                          'sku_upper'] / \
                                                                                      config.SHELF_D600['valid_vol'] * \
                                                                                      config.SHELF_D600[
                                                                                          'combine_locs']
                                        else:
                                            df.loc[index, ['design_shelfD600_num']] = row['design_ctn_pickVol'] / \
                                                                                      config.SHELF_D600['valid_vol']
                                    else:  # 箱规异常常
                                        if row['design_tote_pickVol'] / config.SHELF_D600[
                                            'separate_locs'] <= D600_minUnitVol / \
                                                config.SHELF_D600['sku_upper']:
                                            df.loc[index, ['design_shelfD600_num']] = D600_minUnitVol / \
                                                                                      config.SHELF_D600[
                                                                                          'sku_upper'] / \
                                                                                      config.SHELF_D600['valid_vol'] * \
                                                                                      config.SHELF_D600[
                                                                                          'combine_locs']
                                        else:
                                            df.loc[index, ['design_shelfD600_num']] = row['design_tote_pickVol'] / \
                                                                                      config.SHELF_D600['valid_vol']
                                else:
                                    df.loc[index, ['design_shelfD600_num']] = np.ceil(
                                        row['daily_deli_qty'] * config.DESIGN_COEFFICIENT['single_sku_qty_coe'] *
                                        config.STOCK_TACTIC['support_days'] / row['pltQty']) * row['pltQty'] * row[
                                                                                  'corrVol'] / config.SHELF_D600[
                                                                                  'valid_vol'] * (
                                                                                      config.DESIGN_COEFFICIENT[
                                                                                          'total_qty_coe'] /
                                                                                      config.DESIGN_COEFFICIENT[
                                                                                          'single_sku_qty_coe'])

    '''
    135	EF	存储设备-货架规格_规划 design_stock_equiSize
    '''
    df['design_stock_equiSize'] = df['design_stock_equipment']
    df.loc[(df['design_stock_equipment'] == config.STOCK_TACTIC['equipment'][1][0]) &
           (df['design_shelfD300_num'] > 0),
           ['design_stock_equiSize']] = config.SHELF_D300['name']
    df.loc[(df['design_stock_equipment'] == config.STOCK_TACTIC['equipment'][1][0]) &
           (df['design_shelfD500_num'] > 0),
           ['design_stock_equiSize']] = config.SHELF_D500['name']
    df.loc[(df['design_stock_equipment'] == config.STOCK_TACTIC['equipment'][1][0]) &
           (df['design_shelfD600_num'] > 0),
           ['design_stock_equiSize']] = config.SHELF_D600['name']

    '''
    139	EJ 多穿货位数量_规划 design_shuttle_num
    '''
    df['design_shuttle_num'] = 0
    for index, row in df.iterrows():
        if row['corrSW_isAbnormal_tag'] == 'N':
            if row['daily_stock_qty'] > 0:
                if row['design_stock_equipment'] == '多穿':
                    if row['design_stock_mode'] == '存拣合一':
                        df.loc[index, ['design_shuttle_num']] = np.ceil(
                            row['daily_stock_vol_mm'] * config.DESIGN_COEFFICIENT['single_sku_qty_coe'] /
                            config.TOTE['valid_vol']) * (config.DESIGN_COEFFICIENT['total_qty_coe'] /
                                                         config.DESIGN_COEFFICIENT['single_sku_qty_coe'])
                    else:
                        if config.SHUTTLE['replenish'] == '整托':
                            df.loc[index, ['design_shuttle_num']] = np.ceil(np.ceil(
                                row['prac_daily_deli_pltN'] * config.STOCK_TACTIC['support_days'] *
                                config.DESIGN_COEFFICIENT['single_sku_qty_coe']) * (
                                                                                    config.PALLET_STOCK['valid_vol'] /
                                                                                    config.TOTE['valid_vol'])) * (
                                                                            config.DESIGN_COEFFICIENT['total_qty_coe'] /
                                                                            config.DESIGN_COEFFICIENT[
                                                                                'single_sku_qty_coe'])
                        else:
                            if row['CW_isAbnormal_tag'] == 'N':
                                df.loc[index, ['design_shuttle_num']] = np.ceil(np.ceil(
                                    row['prac_daily_deli_qty'] * config.STOCK_TACTIC['support_days'] *
                                    config.DESIGN_COEFFICIENT['single_sku_qty_coe']) * row['fullCaseUnit'] /
                                                                                row['toteQty']) * (
                                                                                config.DESIGN_COEFFICIENT[
                                                                                    'total_qty_coe'] /
                                                                                config.DESIGN_COEFFICIENT[
                                                                                    'single_sku_qty_coe'])
                            else:
                                df.loc[index, ['design_shuttle_num']] = np.ceil(
                                    row['prac_daily_deli_toteN'] * config.STOCK_TACTIC['support_days']) * \
                                                                        config.DESIGN_COEFFICIENT[
                                                                            'single_sku_qty_coe'] * (
                                                                                config.DESIGN_COEFFICIENT[
                                                                                    'total_qty_coe'] /
                                                                                config.DESIGN_COEFFICIENT[
                                                                                    'single_sku_qty_coe'])

    '''
    140 EK 托盘拣选位托盘数(P)_规划
    '''
    df['design_pltPickN'] = 0
    for index, row in df.iterrows():
        if row['corrSW_isAbnormal_tag'] == 'N':
            if row['daily_stock_qty'] > 0:
                if row['design_stock_equipment'] == '托盘':
                    if row['design_stock_mode'] == '存拣合一':
                        df.loc[index, ['design_pltPickN']] = np.ceil(
                            row['daily_stock_pltN'] * config.DESIGN_COEFFICIENT[
                                'single_sku_qty_coe']) * (
                                                                     config.DESIGN_COEFFICIENT[
                                                                         'total_qty_coe'] /
                                                                     config.DESIGN_COEFFICIENT[
                                                                         'single_sku_qty_coe'])
                    else:
                        if row['prac_daily_deli_pltN'] * config.STOCK_TACTIC['support_days'] * \
                                config.DESIGN_COEFFICIENT[
                                    'single_sku_qty_coe'] <= config.STOCK_TACTIC['mode_interval'][1]:
                            df.loc[index, ['design_pltPickN']] = 1
                        else:
                            df.loc[index, ['design_pltPickN']] = np.ceil(
                                row['prac_daily_deli_pltN'] * config.STOCK_TACTIC['support_days'] *
                                config.DESIGN_COEFFICIENT[
                                    'single_sku_qty_coe'] * (config.DESIGN_COEFFICIENT[
                                                                 'total_qty_coe'] /
                                                             config.DESIGN_COEFFICIENT[
                                                                 'single_sku_qty_coe']))

    # 143 EN 拣货位商品件数_规划 design_pickQty
    df['design_pickQty'] = 0
    for index, row in df.iterrows():
        if row['design_stock_mode'] == '存拣合一':
            df.loc[index, ['design_pickQty']] = row['daily_stock_qty'] * config.DESIGN_COEFFICIENT[
                'single_sku_qty_coe']
        else:
            if row['design_shelfD300_num'] * config.SHELF_D300['valid_vol'] / row['corrVol'] + \
                    row['design_shelfD500_num'] * config.SHELF_D500['valid_vol'] / row['corrVol'] + \
                    row['design_shelfD600_num'] * config.SHELF_D600['valid_vol'] / row['corrVol'] + \
                    row['design_shuttle_num'] * config.TOTE['valid_vol'] / row['corrVol'] + \
                    row['design_pltPickN'] * config.PALLET_STOCK['valid_vol'] / row['corrVol'] > \
                    row['daily_stock_qty'] * config.DESIGN_COEFFICIENT['single_sku_qty_coe']:
                df.loc[index, ['design_pickQty']] = row['daily_stock_qty'] * config.DESIGN_COEFFICIENT[
                    'single_sku_qty_coe']
            else:
                df.loc[index, ['design_pickQty']] = row['design_shelfD300_num'] * config.SHELF_D300['valid_vol'] / \
                                                    row['corrVol'] + \
                                                    row['design_shelfD500_num'] * config.SHELF_D500['valid_vol'] / \
                                                    row['corrVol'] + \
                                                    row['design_shelfD600_num'] * config.SHELF_D600['valid_vol'] / \
                                                    row['corrVol'] + \
                                                    row['design_shuttle_num'] * config.TOTE['valid_vol'] / row[
                                                        'corrVol'] + ((row['daily_stock_qty'] - np.floor(
                    row['daily_stock_qty'] / row['pltQty']) * row['pltQty']) + (row['design_pltPickN'] - 1) * row[
                                                                          'pltQty'])

    # 144 EO 存储位商品件数_规划 design_stockQty
    df['design_stockQty'] = 0
    df.loc[(df['design_daily_stock_qty'] - df['design_pickQty'] > 0), ['design_stockQty']] = df[
                                                                                                 'design_daily_stock_qty'] - \
                                                                                             df['current_pickQty']
    # 141 EL 托盘存储位托盘数(P)_规划 design_pltStockN
    df['design_pltStockN'] = 0
    df.loc[(df['SW_isAbnormal_tag'] == 'N') & (df['daily_stock_qty'] > 0) & (df['design_stock_equipment'] != '轻架'),
           ['design_pltStockN']] = np.ceil(df['design_stockQty'] / df['pltQty'])

    # 142 EM 拣选位存储单元折算托盘数量_规划 design_pickUnit2plt
    df['design_pickUnit2plt'] = 0
    df.loc[(df['design_stock_equipment'] == '多穿'), ['design_pickUnit2plt']] = df['design_shuttle_num'] * \
                                                                              config.TOTE['2plt']
    df.loc[(df['design_stock_equipment'] == '轻型货架(D300)'), ['design_pickUnit2plt']] = df['design_shuttle_num'] * \
                                                                                      config.SHELF_D300['2plt']
    df.loc[(df['design_stock_equipment'] == '轻型货架(D500)'), ['design_pickUnit2plt']] = df['design_shuttle_num'] * \
                                                                                      config.SHELF_D500['2plt']
    df.loc[(df['design_stock_equipment'] == '轻型货架(D600)'), ['design_pickUnit2plt']] = df['design_shuttle_num'] * \
                                                                                      config.SHELF_D600['2plt']

    # 145 EP 拣货位商品体积_规划(m3) design_pickVol_m
    df['design_pickVol_m'] = df['design_pickQty'] * df['corrVol'] / pow(10, 9)

    # 146 EQ 存储位商品体积_规划(m3) design_stockVol_m
    df['design_stockVol_m'] = df['design_stockQty'] * df['corrVol'] / pow(10, 9)

    # 147 ER 托盘拣货位总重量_规划(kg) design_pltPickWt
    df['design_pltPickWt'] = df['corrWeight'] * df['design_pickQty'] + np.ceil(
        df['design_pltPickN'] * config.PALLET_STOCK['unit_weight'])

    # 148 ES 托盘存储位总重量_规划(kg) design_pltStockWt
    df['design_pltStockWt'] = df['corrWeight'] * df['design_stockQty'] + np.ceil(
        df['design_pltStockN'] * config.PALLET_STOCK['unit_weight'])

    '''
    规划面积相关字段
    '''
    # 149 ET 拣选位面积(m2)_规划 design_pick_square
    df['design_pick_square'] = 0
    df.loc[(df['design_shelfD300_num'] > 0), ['design_pick_square']] = df['design_shelfD300_num'] * \
                                                                       config.SHELF_D300['unit_square']
    df.loc[(df['design_shelfD500_num'] > 0), ['design_pick_square']] = df['design_shelfD500_num'] * \
                                                                       config.SHELF_D500['unit_square']
    df.loc[(df['design_shelfD600_num'] > 0), ['design_pick_square']] = df['design_shelfD600_num'] * \
                                                                       config.SHELF_D600['unit_square']
    df.loc[(df['design_shuttle_num'] > 0), ['design_pick_square']] = df['design_shuttle_num'] * \
                                                                     config.SHUTTLE['unit_square']
    df.loc[(df['design_pltPickN'] > 0), ['design_pick_square']] = df['design_pltPickN'] * \
                                                                  config.PALLET_PICK['unit_square']

    # 150 EU 存储位面积(m2)(24米单深)_规划 design_stock_ASRS_24_SINGLE_square
    df['design_stock_ASRS_24_SINGLE_square'] = 0
    df.loc[(df['design_pltStockN'] > 0), ['design_stock_ASRS_24_SINGLE_square']] = df['design_pltStockN'] * \
                                                                                   config.ASRS_24_SINGLE['unit_square']
    # 151 EV 存储位面积(m2)(36米单深)_规划 design_stock_ASRS_36_SINGLE_square
    df['design_stock_ASRS_36_SINGLE_square'] = 0
    df.loc[(df['design_pltStockN'] > 0), ['design_stock_ASRS_36_SINGLE_square']] = df['design_pltStockN'] * \
                                                                                   config.ASRS_36_SINGLE['unit_square']

    # 152 EW 存储位面积(m2)(36米双深)_规划 design_stock_ASRS_36_DOUBLE_square
    df['design_stock_ASRS_36_DOUBLE_square'] = 0
    df.loc[(df['design_pltStockN'] > 0), ['design_stock_ASRS_36_DOUBLE_square']] = df['design_pltStockN'] * \
                                                                                   config.ASRS_36_DOUBLE['unit_square']

    """
    StockClass2 透视表
    """

    # 101 透视托盘拣选位托盘数，拣选位商品总体积，计算托盘拣选位存储系数

    # pt1 = df.loc[(df['sku_state'] == '良品') & (df['corrSW_isAbnormal_tag'] == 'N') &
    #              (df['current_stock_equipment'] == '托盘'),
    #              ['warehouse', 'current_pltPickN', 'current_pickVol_m']]

    # palletPick_factor = pd.pivot_table(pt1, index='warehouse', values=['current_pltPickN', 'current_pickVol_m'],
    #                                    aggfunc=np.sum, fill_value=0).reset_index()
    #
    # palletPick_factor['factor'] = palletPick_factor['current_pickVol_m'] * pow(10, 9) / (
    #         palletPick_factor['current_pltPickN'] *
    #         config.PALLET_STOCK['valid_vol'] / config.PALLET_STOCK['rate'])
    #
    # print(palletPick_factor)
    #
    # # 102 透视托盘存储位托盘数，存储位商品总体积，存储位箱规体积(m3)，计算托盘存储位存储系数
    # pt2 = df.loc[(df['sku_state'] == '良品') & (df['corrSW_isAbnormal_tag'] == 'N') & (df['CW_isAbnormal_tag'] == 'N'),
    #              ['warehouse', 'current_pltStockN', 'current_stockVol_m', 'current_stockCtnVol']]
    #
    # palletStock_factor = pd.pivot_table(pt2, index='warehouse',
    #                                     values=['current_pltStockN', 'current_stockVol_m', 'current_stockCtnVol'],
    #                                     aggfunc=np.sum, fill_value=0).reset_index()
    #
    # palletStock_factor['vol_factor'] = palletStock_factor['current_stockVol_m'] * pow(10, 9) / (
    #         palletStock_factor['current_pltStockN'] *
    #         config.PALLET_STOCK['valid_vol'] / config.PALLET_STOCK['rate'])
    # palletStock_factor['ctn_factor'] = palletStock_factor['current_stockCtnVol'] * pow(10, 9) / (
    #         palletStock_factor['current_pltStockN'] *
    #         config.PALLET_STOCK['valid_vol'] / config.PALLET_STOCK['rate'])
    #
    # # 103 透视 箱规每托(含托盘)实际码放高度(mm)(按额定体积&重量折算)，计算 均高/设计高度
    # # PalletStoc-CartonS1H_O1
    # pt3 = df.loc[(df['sku_state'] == '良品') & (df['corrSW_isAbnormal_tag'] == 'N') & (df['CW_isAbnormal_tag'] == 'N'),
    #              ['ctn_pltHeight', 'current_pltStockN']]
    #
    # palletStock_height_factor = pt3.groupby('ctn_pltHeight').agg(
    #     current_pltStockN=pd.NamedAgg(column='current_pltStockN', aggfunc='sum')).reset_index()
    #
    # palletStock_height_factor['sum_pallet_height'] = palletStock_height_factor['ctn_pltHeight'] * \
    #                                                  palletStock_height_factor['current_pltStockN']
    #
    # palletStock_height_factor['avg_pallet_height'] = (palletStock_height_factor['sum_pallet_height']).sum() / \
    #                                                  (palletStock_height_factor['current_pltStockN']).sum()
    #
    # palletStock_height_factor['design_pallet_height'] = config.PALLET_STOCK['valid_height'] + config.PALLET_STOCK[
    #     'plt_height']
    #
    # palletStock_height_factor['pallet_height_factor'] = palletStock_height_factor['avg_pallet_height'] / \
    #                                                     palletStock_height_factor['design_pallet_height']
    #
    # # print(df.dtypes)
    # # 111 良品/残品统计
    # good_tmp1 = pd.pivot_table(df, index='sku_state', values='SKU_ID', aggfunc='count', fill_value=0,
    #                            margins=True).reset_index()
    #
    # good_tmp2 = pd.pivot_table(df, index='sku_state',
    #                            values=['daily_stock_sku', 'daily_stock_qty', 'daily_stock_vol_m'], aggfunc='sum',
    #                            margins=True).reset_index()
    # good_tmp2.loc[(good_tmp2['sku_state'] == 'All'), ['daily_stock_qty']] = df['daily_stock_qty'].sum()
    # good_tmp2.loc[(good_tmp2['sku_state'] == 'All'), ['daily_stock_sku']] = df['daily_stock_sku'].sum()
    #
    # stockGood_and_Damaged = pd.merge(good_tmp1, good_tmp2, how='outer', sort=False)
    #
    # # print(col1['daily_stock_sku'])
    # stockGood_and_Damaged['daily_stock_sku%'] = round(stockGood_and_Damaged['daily_stock_sku'] / (
    #         stockGood_and_Damaged['daily_stock_sku'].sum() / 2), 6)
    # stockGood_and_Damaged['daily_stock_sku%'] = stockGood_and_Damaged['daily_stock_sku%'].apply(
    #     lambda x: '%.4f%%' % (x * 100))
    #
    # stockGood_and_Damaged['daily_stock_qty%'] = round(stockGood_and_Damaged['daily_stock_qty'] / (
    #         stockGood_and_Damaged['daily_stock_qty'].sum() / 2), 6)
    # stockGood_and_Damaged['daily_stock_qty%'] = stockGood_and_Damaged['daily_stock_qty%'].apply(
    #     lambda x: '%.4f%%' % (x * 100))
    #
    # stockGood_and_Damaged['daily_stock_vol_m%'] = round(stockGood_and_Damaged['daily_stock_vol_m'] / (
    #         stockGood_and_Damaged['daily_stock_vol_m'].sum() / 2), 6)
    # stockGood_and_Damaged['daily_stock_vol_m%'] = stockGood_and_Damaged['daily_stock_vol_m%'].apply(
    #     lambda x: '%.4f%%' % (x * 100))

    # pprint.pprint(stockGood_and_Damaged)

    # '''
    # 112透视_SIZE_O1  size_pt
    # '''
    #
    # # 筛选透视数据
    # size_df = df.loc[(df['sku_state'] == '良品') & (df['stock_qty_isNonZero'] == 'Y'),
    #                  ['SKU_ID', 'size', 'daily_stock_sku', 'daily_stock_qty', 'daily_stock_vol_m',
    #                   'daily_stock_weight', 'daily_stock_pltN', 'daily_deli_sku', 'daily_deli_qty',
    #                   'daily_deli_vol_m', 'current_pltStockN', 'current_pltPickN', 'current_pickUnit2plt',
    #                   'current_stockQty', 'current_pickQty']]
    #
    # size_tmp1 = pd.pivot_table(size_df, index='size', values='SKU_ID', aggfunc='count', fill_value=0,
    #                            margins=True).reset_index()
    #
    # size_tmp2 = pd.pivot_table(size_df, index='size',
    #                            values=['daily_stock_sku', 'daily_stock_qty', 'daily_stock_vol_m', 'daily_stock_weight',
    #                                    'daily_stock_pltN', 'daily_deli_sku', 'daily_deli_qty', 'daily_deli_vol_m',
    #                                    'current_pltStockN', 'current_pltPickN',
    #                                    'current_pickUnit2plt', 'current_stockQty', 'current_pickQty'],
    #                            aggfunc='sum', fill_value=0,
    #                            margins=True).reset_index()
    #
    # size_pt = pd.merge(size_tmp1, size_tmp2, how='outer', sort=False)
    #
    # # 更新汇总数据
    # size_pt.loc[(size_pt['size'] == 'All'), ['daily_stock_sku']] = size_df['daily_stock_sku'].sum()
    # size_pt.loc[(size_pt['size'] == 'All'), ['daily_stock_qty']] = size_df['daily_stock_qty'].sum()
    # size_pt.loc[(size_pt['size'] == 'All'), ['daily_stock_vol_m']] = size_df['daily_stock_vol_m'].sum()
    # size_pt.loc[(size_pt['size'] == 'All'), ['daily_stock_weight']] = size_df['daily_stock_weight'].sum()
    # size_pt.loc[(size_pt['size'] == 'All'), ['daily_stock_pltN']] = size_df['daily_stock_pltN'].sum()
    # size_pt.loc[(size_pt['size'] == 'All'), ['daily_deli_sku']] = size_df['daily_deli_sku'].sum()
    # size_pt.loc[(size_pt['size'] == 'All'), ['daily_deli_qty']] = size_df['daily_deli_qty'].sum()
    # size_pt.loc[(size_pt['size'] == 'All'), ['daily_deli_vol_m']] = size_df['daily_deli_vol_m'].sum()
    # size_pt.loc[(size_pt['size'] == 'All'), ['current_pltStockN']] = size_df['current_pltStockN'].sum()
    # size_pt.loc[(size_pt['size'] == 'All'), ['current_pltPickN']] = size_df['current_pltPickN'].sum()
    # size_pt.loc[(size_pt['size'] == 'All'), ['current_pickUnit2plt']] = size_df['current_pickUnit2plt'].sum()
    # size_pt.loc[(size_pt['size'] == 'All'), ['current_stockQty']] = size_df['current_stockQty'].sum()
    # size_pt.loc[(size_pt['size'] == 'All'), ['current_pickQty']] = size_df['current_pickQty'].sum()
    #
    # # 重排列
    # size_pt = size_pt[
    #     ['size', 'SKU_ID', 'daily_stock_sku', 'daily_stock_qty', 'daily_stock_vol_m',
    #      'daily_stock_weight', 'daily_stock_pltN', 'daily_deli_sku', 'daily_deli_qty',
    #      'daily_deli_vol_m', 'current_pltStockN', 'current_pltPickN', 'current_pickUnit2plt',
    #      'current_stockQty', 'current_pickQty']]
    #
    # # 计算比例
    # size_pt['SKU_ID%'] = round(size_pt['SKU_ID'] / (size_pt['SKU_ID'].sum() / 2), 6).apply(
    #     lambda x: '%.4f%%' % (x * 100))
    # size_pt['daily_stock_qty%'] = round(size_pt['daily_stock_qty'] / (size_pt['daily_stock_qty'].sum() / 2), 6).apply(
    #     lambda x: '%.4f%%' % (x * 100))
    # size_pt['daily_stock_vol_m%'] = round(size_pt['daily_stock_vol_m'] / (size_pt['daily_stock_vol_m'].sum() / 2),
    #                                       6).apply(
    #     lambda x: '%.4f%%' % (x * 100))
    # size_pt['daily_stock_weight%'] = round(size_pt['daily_stock_weight'] / (size_pt['daily_stock_weight'].sum() / 2),
    #                                        6).apply(
    #     lambda x: '%.4f%%' % (x * 100))
    # size_pt['daily_deli_qty%'] = round(size_pt['daily_deli_qty'] / (size_pt['daily_deli_qty'].sum() / 2), 6).apply(
    #     lambda x: '%.4f%%' % (x * 100))
    # size_pt['daily_deli_vol_m%'] = round(size_pt['daily_deli_vol_m'] / (size_pt['daily_deli_vol_m'].sum() / 2),
    #                                      6).apply(lambda x: '%.4f%%' % (x * 100))
    # size_pt['current_pltStockN%'] = round(size_pt['current_pltStockN'] / (size_pt['current_pltStockN'].sum() / 2),
    #                                       6).apply(lambda x: '%.4f%%' % (x * 100))
    # size_pt['current_pltPickN%'] = round(size_pt['current_pltPickN'] / (size_pt['current_pltPickN'].sum() / 2),
    #                                      6).apply(lambda x: '%.4f%%' % (x * 100))
    # size_pt['current_stockQty%'] = round(size_pt['current_stockQty'] / (size_pt['current_stockQty'].sum() / 2),
    #                                      6).apply(lambda x: '%.4f%%' % (x * 100))
    # size_pt['current_pickQty%'] = round(size_pt['current_pickQty'] / (size_pt['current_pickQty'].sum() / 2), 6).apply(
    #     lambda x: '%.4f%%' % (x * 100))
    #
    # # 计算字段
    # size_pt['qty_turnover_days'] = size_pt['daily_stock_qty'] / size_pt['daily_deli_qty']
    # size_pt['vol_turnover_days'] = size_pt['daily_stock_vol_m'] / size_pt['daily_deli_vol_m']
    # size_pt['avg_vol'] = size_pt['daily_stock_vol_m'] / size_pt['daily_stock_qty']
    # size_pt['avg_weight'] = size_pt['daily_stock_weight'] / size_pt['daily_stock_qty']
    # size_pt['avg_pltQty'] = (size_pt['current_stockQty'] + size_pt['current_pickQty']) / \
    #                         (size_pt['current_pltStockN'] + size_pt['current_pltPickN'])
    #
    # # pprint.pprint(size_pt)
    #
    # '''
    # 113透视_CLASS1_O1
    # '''
    # # 筛选透视数据 库存非零sku
    # class_df = df.loc[(df['stock_qty_isNonZero'] == 'Y'),
    #                   ['SKU_ID', 'size', 'I_class', 'II_class', 'III_class', 'IV_class',
    #                    'daily_stock_sku', 'daily_stock_qty', 'daily_stock_vol_m',
    #                    'daily_stock_weight', 'daily_stock_pltN', 'daily_deli_sku', 'daily_deli_qty',
    #                    'daily_deli_vol_m', 'current_pltStockN', 'current_pltPickN', 'current_pickUnit2plt',
    #                    'current_stockQty', 'current_pickQty']]
    #
    # class_tmp1 = pd.pivot_table(class_df, index='I_class', values='SKU_ID', aggfunc='count', fill_value=0,
    #                             margins=True).reset_index()
    #
    # class_tmp2 = pd.pivot_table(class_df, index='I_class',
    #                             values=['daily_stock_sku', 'daily_stock_qty', 'daily_stock_vol_m', 'daily_stock_weight',
    #                                     'daily_stock_pltN', 'daily_deli_sku', 'daily_deli_qty', 'daily_deli_vol_m',
    #                                     'current_pltStockN', 'current_pltPickN',
    #                                     'current_pickUnit2plt', 'current_stockQty', 'current_pickQty'],
    #                             aggfunc='sum', fill_value=0,
    #                             margins=True).reset_index()
    #
    # class_pt = pd.merge(class_tmp1, class_tmp2, how='outer', sort=False)
    #
    # # 重排列
    # class_pt = class_pt[
    #     ['I_class', 'SKU_ID', 'daily_stock_sku', 'daily_stock_qty', 'daily_stock_vol_m',
    #      'daily_stock_weight', 'daily_stock_pltN', 'daily_deli_sku', 'daily_deli_qty',
    #      'daily_deli_vol_m', 'current_pltStockN', 'current_pltPickN', 'current_pickUnit2plt',
    #      'current_stockQty', 'current_pickQty']]
    #
    # # 更新汇总数据
    # class_pt.loc[(class_pt['I_class'] == 'All'), ['daily_stock_sku']] = class_df['daily_stock_sku'].sum()
    # class_pt.loc[(class_pt['I_class'] == 'All'), ['daily_stock_qty']] = class_df['daily_stock_qty'].sum()
    # class_pt.loc[(class_pt['I_class'] == 'All'), ['daily_stock_vol_m']] = class_df['daily_stock_vol_m'].sum()
    # class_pt.loc[(class_pt['I_class'] == 'All'), ['daily_stock_weight']] = class_df['daily_stock_weight'].sum()
    # class_pt.loc[(class_pt['I_class'] == 'All'), ['daily_stock_pltN']] = class_df['daily_stock_pltN'].sum()
    # class_pt.loc[(class_pt['I_class'] == 'All'), ['daily_deli_sku']] = class_df['daily_deli_sku'].sum()
    # class_pt.loc[(class_pt['I_class'] == 'All'), ['daily_deli_qty']] = class_df['daily_deli_qty'].sum()
    # class_pt.loc[(class_pt['I_class'] == 'All'), ['daily_deli_vol_m']] = class_df['daily_deli_vol_m'].sum()
    # class_pt.loc[(class_pt['I_class'] == 'All'), ['current_pltStockN']] = class_df['current_pltStockN'].sum()
    # class_pt.loc[(class_pt['I_class'] == 'All'), ['current_pltPickN']] = class_df['current_pltPickN'].sum()
    # class_pt.loc[(class_pt['I_class'] == 'All'), ['current_pickUnit2plt']] = class_df['current_pickUnit2plt'].sum()
    # class_pt.loc[(class_pt['I_class'] == 'All'), ['current_stockQty']] = class_df['current_stockQty'].sum()
    # class_pt.loc[(class_pt['I_class'] == 'All'), ['current_pickQty']] = class_df['current_pickQty'].sum()
    #
    # # 计算百分比
    # class_pt['daily_stock_sku%'] = round(class_pt['daily_stock_sku'] / (class_pt['daily_stock_sku'].sum() / 2),
    #                                      6).apply(
    #     lambda x: '%.4f%%' % (x * 100))
    # class_pt['daily_stock_qty%'] = round(class_pt['daily_stock_qty'] / (class_pt['daily_stock_qty'].sum() / 2),
    #                                      6).apply(
    #     lambda x: '%.4f%%' % (x * 100))
    # class_pt['daily_stock_vol_m%'] = round(class_pt['daily_stock_vol_m'] / (class_pt['daily_stock_vol_m'].sum() / 2),
    #                                        6).apply(
    #     lambda x: '%.4f%%' % (x * 100))
    # class_pt['daily_deli_sku%'] = round(class_pt['daily_deli_sku'] / (class_pt['daily_deli_sku'].sum() / 2), 6).apply(
    #     lambda x: '%.4f%%' % (x * 100))
    # class_pt['daily_deli_qty%'] = round(class_pt['daily_deli_qty'] / (class_pt['daily_deli_qty'].sum() / 2), 6).apply(
    #     lambda x: '%.4f%%' % (x * 100))
    # class_pt['daily_deli_vol_m%'] = round(class_pt['daily_deli_vol_m'] / (class_pt['daily_deli_vol_m'].sum() / 2),
    #                                       6).apply(lambda x: '%.4f%%' % (x * 100))
    #
    # # 计算字段
    # class_pt['qty_turnover_days'] = class_pt['daily_stock_qty'] / class_pt['daily_deli_qty']
    # class_pt['vol_turnover_days'] = class_pt['daily_stock_vol_m'] / class_pt['daily_deli_vol_m']
    # class_pt['avg_vol'] = class_pt['daily_stock_vol_m'] / class_pt['daily_stock_qty']
    # class_pt['avg_weight'] = class_pt['daily_stock_weight'] / class_pt['daily_stock_qty']
    # class_pt['avg_pltQty'] = (class_pt['current_stockQty'] + class_pt['current_pickQty']) / \
    #                          (class_pt['current_pltStockN'] + class_pt['current_pltPickN'])
    #
    # # pprint.pprint(class_pt)
    #
    # '''
    # 114透视_Size&Class1_O1
    # '''
    # size_class_tmp1 = pd.pivot_table(class_df, index=['size', 'I_class'], values='SKU_ID', aggfunc='count',
    #                                  fill_value=0,
    #                                  margins=True).reset_index()
    #
    # size_class_tmp2 = pd.pivot_table(class_df, index=['size', 'I_class'],
    #                                  values=['daily_stock_sku', 'daily_stock_qty', 'daily_stock_vol_m',
    #                                          'daily_stock_weight',
    #                                          'daily_stock_pltN', 'daily_deli_sku', 'daily_deli_qty', 'daily_deli_vol_m',
    #                                          'current_pltStockN', 'current_pltPickN',
    #                                          'current_pickUnit2plt', 'current_stockQty', 'current_pickQty'],
    #                                  aggfunc='sum', fill_value=0,
    #                                  margins=True).reset_index()
    #
    # size_class_pt = pd.merge(size_class_tmp1, size_class_tmp2, on=['size', 'I_class'], how='outer', sort=False)
    #
    # # 重排列
    # size_class_pt = size_class_pt[
    #     ['size', 'I_class', 'SKU_ID', 'daily_stock_sku', 'daily_stock_qty', 'daily_stock_vol_m',
    #      'daily_stock_weight', 'daily_stock_pltN', 'daily_deli_sku', 'daily_deli_qty',
    #      'daily_deli_vol_m', 'current_pltStockN', 'current_pltPickN', 'current_pickUnit2plt',
    #      'current_stockQty', 'current_pickQty']]
    #
    # # 更新汇总数据
    # size_class_pt.loc[(size_class_pt['size'] == 'All'), ['daily_stock_sku']] = class_df['daily_stock_sku'].sum()
    # size_class_pt.loc[(size_class_pt['size'] == 'All'), ['daily_stock_qty']] = class_df['daily_stock_qty'].sum()
    # size_class_pt.loc[(size_class_pt['size'] == 'All'), ['daily_stock_vol_m']] = class_df['daily_stock_vol_m'].sum()
    # size_class_pt.loc[(size_class_pt['size'] == 'All'), ['daily_stock_weight']] = class_df['daily_stock_weight'].sum()
    # size_class_pt.loc[(size_class_pt['size'] == 'All'), ['daily_stock_pltN']] = class_df['daily_stock_pltN'].sum()
    # size_class_pt.loc[(size_class_pt['size'] == 'All'), ['daily_deli_sku']] = class_df['daily_deli_sku'].sum()
    # size_class_pt.loc[(size_class_pt['size'] == 'All'), ['daily_deli_qty']] = class_df['daily_deli_qty'].sum()
    # size_class_pt.loc[(size_class_pt['size'] == 'All'), ['daily_deli_vol_m']] = class_df['daily_deli_vol_m'].sum()
    # size_class_pt.loc[(size_class_pt['size'] == 'All'), ['current_pltStockN']] = class_df['current_pltStockN'].sum()
    # size_class_pt.loc[(size_class_pt['size'] == 'All'), ['current_pltPickN']] = class_df['current_pltPickN'].sum()
    # size_class_pt.loc[(size_class_pt['size'] == 'All'), ['current_pickUnit2plt']] = class_df[
    #     'current_pickUnit2plt'].sum()
    # size_class_pt.loc[(size_class_pt['size'] == 'All'), ['current_stockQty']] = class_df['current_stockQty'].sum()
    # size_class_pt.loc[(size_class_pt['size'] == 'All'), ['current_pickQty']] = class_df['current_pickQty'].sum()
    #
    # # 计算百分比
    # size_class_pt['daily_stock_sku%'] = round(
    #     size_class_pt['daily_stock_sku'] / (size_class_pt['daily_stock_sku'].sum() / 2),
    #     6).apply(
    #     lambda x: '%.4f%%' % (x * 100))
    # size_class_pt['daily_stock_qty%'] = round(
    #     size_class_pt['daily_stock_qty'] / (size_class_pt['daily_stock_qty'].sum() / 2),
    #     6).apply(
    #     lambda x: '%.4f%%' % (x * 100))
    # size_class_pt['daily_stock_vol_m%'] = round(
    #     size_class_pt['daily_stock_vol_m'] / (size_class_pt['daily_stock_vol_m'].sum() / 2),
    #     6).apply(
    #     lambda x: '%.4f%%' % (x * 100))
    # size_class_pt['daily_deli_sku%'] = round(
    #     size_class_pt['daily_deli_sku'] / (size_class_pt['daily_deli_sku'].sum() / 2), 6).apply(
    #     lambda x: '%.4f%%' % (x * 100))
    # size_class_pt['daily_deli_qty%'] = round(
    #     size_class_pt['daily_deli_qty'] / (size_class_pt['daily_deli_qty'].sum() / 2), 6).apply(
    #     lambda x: '%.4f%%' % (x * 100))
    # size_class_pt['daily_deli_vol_m%'] = round(
    #     size_class_pt['daily_deli_vol_m'] / (size_class_pt['daily_deli_vol_m'].sum() / 2),
    #     6).apply(lambda x: '%.4f%%' % (x * 100))
    #
    # # 计算字段
    # size_class_pt['qty_turnover_days'] = size_class_pt['daily_stock_qty'] / size_class_pt['daily_deli_qty']
    # size_class_pt['vol_turnover_days'] = size_class_pt['daily_stock_vol_m'] / size_class_pt['daily_deli_vol_m']
    # size_class_pt['avg_vol'] = size_class_pt['daily_stock_vol_m'] / size_class_pt['daily_stock_qty']
    # size_class_pt['avg_weight'] = size_class_pt['daily_stock_weight'] / size_class_pt['daily_stock_qty']
    # size_class_pt['avg_pltQty'] = (size_class_pt['current_stockQty'] + size_class_pt['current_pickQty']) / \
    #                               (size_class_pt['current_pltStockN'] + size_class_pt['current_pltPickN'])
    #
    # # pprint.pprint(size_class_pt)
    #
    # '''
    # 115透视_WarehouseType_O1  warehouse_pt
    # '''
    # warehouse_df = df[['SKU_ID', 'warehouse',
    #                    'daily_stock_sku', 'daily_stock_qty', 'daily_stock_vol_m',
    #                    'daily_stock_weight', 'daily_stock_pltN', 'daily_deli_sku', 'daily_deli_qty',
    #                    'daily_deli_vol_m', 'current_pltStockN', 'current_pltPickN', 'current_pickUnit2plt',
    #                    'current_stockQty', 'current_pickQty']]
    #
    # warehouse_tmp1 = pd.pivot_table(warehouse_df, index='warehouse', values='SKU_ID', aggfunc='count', fill_value=0,
    #                                 margins=True).reset_index()
    #
    # warehouse_tmp2 = pd.pivot_table(warehouse_df, index='warehouse',
    #                                 values=['daily_stock_sku', 'daily_stock_qty', 'daily_stock_vol_m',
    #                                         'daily_stock_weight',
    #                                         'daily_stock_pltN', 'daily_deli_sku', 'daily_deli_qty', 'daily_deli_vol_m',
    #                                         'current_pltStockN', 'current_pltPickN',
    #                                         'current_pickUnit2plt', 'current_stockQty', 'current_pickQty'],
    #                                 aggfunc='sum', fill_value=0,
    #                                 margins=True).reset_index()
    #
    # warehouse_pt = pd.merge(warehouse_tmp1, warehouse_tmp2, how='outer', sort=False)
    #
    # # 更新汇总数据
    # warehouse_pt.loc[(warehouse_pt['warehouse'] == 'All'), ['daily_stock_sku']] = warehouse_df['daily_stock_sku'].sum()
    # warehouse_pt.loc[(warehouse_pt['warehouse'] == 'All'), ['daily_stock_qty']] = warehouse_df['daily_stock_qty'].sum()
    # warehouse_pt.loc[(warehouse_pt['warehouse'] == 'All'), ['daily_stock_vol_m']] = warehouse_df[
    #     'daily_stock_vol_m'].sum()
    # warehouse_pt.loc[(warehouse_pt['warehouse'] == 'All'), ['daily_stock_weight']] = warehouse_df[
    #     'daily_stock_weight'].sum()
    # warehouse_pt.loc[(warehouse_pt['warehouse'] == 'All'), ['daily_stock_pltN']] = warehouse_df[
    #     'daily_stock_pltN'].sum()
    # warehouse_pt.loc[(warehouse_pt['warehouse'] == 'All'), ['daily_deli_sku']] = warehouse_df['daily_deli_sku'].sum()
    # warehouse_pt.loc[(warehouse_pt['warehouse'] == 'All'), ['daily_deli_qty']] = warehouse_df['daily_deli_qty'].sum()
    # warehouse_pt.loc[(warehouse_pt['warehouse'] == 'All'), ['daily_deli_vol_m']] = warehouse_df[
    #     'daily_deli_vol_m'].sum()
    # warehouse_pt.loc[(warehouse_pt['warehouse'] == 'All'), ['current_pltStockN']] = warehouse_df[
    #     'current_pltStockN'].sum()
    # warehouse_pt.loc[(warehouse_pt['warehouse'] == 'All'), ['current_pltPickN']] = warehouse_df[
    #     'current_pltPickN'].sum()
    # warehouse_pt.loc[(warehouse_pt['warehouse'] == 'All'), ['current_pickUnit2plt']] = warehouse_df[
    #     'current_pickUnit2plt'].sum()
    # warehouse_pt.loc[(warehouse_pt['warehouse'] == 'All'), ['current_stockQty']] = warehouse_df[
    #     'current_stockQty'].sum()
    # warehouse_pt.loc[(warehouse_pt['warehouse'] == 'All'), ['current_pickQty']] = warehouse_df['current_pickQty'].sum()
    #
    # # 重排列
    # warehouse_pt = warehouse_pt[
    #     ['warehouse', 'SKU_ID', 'daily_stock_sku', 'daily_stock_qty', 'daily_stock_vol_m',
    #      'daily_stock_weight', 'daily_stock_pltN', 'daily_deli_sku', 'daily_deli_qty',
    #      'daily_deli_vol_m', 'current_pltStockN', 'current_pltPickN', 'current_pickUnit2plt',
    #      'current_stockQty', 'current_pickQty']]
    #
    # # 计算比例
    # warehouse_pt['SKU_ID%'] = round(warehouse_pt['SKU_ID'] / (warehouse_pt['SKU_ID'].sum() / 2), 6).apply(
    #     lambda x: '%.4f%%' % (x * 100))
    # warehouse_pt['daily_stock_qty%'] = round(
    #     warehouse_pt['daily_stock_qty'] / (warehouse_pt['daily_stock_qty'].sum() / 2), 6).apply(
    #     lambda x: '%.4f%%' % (x * 100))
    # warehouse_pt['daily_stock_vol_m%'] = round(
    #     warehouse_pt['daily_stock_vol_m'] / (warehouse_pt['daily_stock_vol_m'].sum() / 2),
    #     6).apply(
    #     lambda x: '%.4f%%' % (x * 100))
    # warehouse_pt['daily_stock_weight%'] = round(
    #     warehouse_pt['daily_stock_weight'] / (warehouse_pt['daily_stock_weight'].sum() / 2),
    #     6).apply(
    #     lambda x: '%.4f%%' % (x * 100))
    # warehouse_pt['daily_deli_qty%'] = round(warehouse_pt['daily_deli_qty'] / (warehouse_pt['daily_deli_qty'].sum() / 2),
    #                                         6).apply(
    #     lambda x: '%.4f%%' % (x * 100))
    # warehouse_pt['daily_deli_vol_m%'] = round(
    #     warehouse_pt['daily_deli_vol_m'] / (warehouse_pt['daily_deli_vol_m'].sum() / 2),
    #     6).apply(lambda x: '%.4f%%' % (x * 100))
    # warehouse_pt['current_pltStockN%'] = round(
    #     warehouse_pt['current_pltStockN'] / (warehouse_pt['current_pltStockN'].sum() / 2),
    #     6).apply(lambda x: '%.4f%%' % (x * 100))
    # warehouse_pt['current_pltPickN%'] = round(
    #     warehouse_pt['current_pltPickN'] / (warehouse_pt['current_pltPickN'].sum() / 2),
    #     6).apply(lambda x: '%.4f%%' % (x * 100))
    # warehouse_pt['current_stockQty%'] = round(
    #     warehouse_pt['current_stockQty'] / (warehouse_pt['current_stockQty'].sum() / 2),
    #     6).apply(lambda x: '%.4f%%' % (x * 100))
    # warehouse_pt['current_pickQty%'] = round(
    #     warehouse_pt['current_pickQty'] / (warehouse_pt['current_pickQty'].sum() / 2), 6).apply(
    #     lambda x: '%.4f%%' % (x * 100))
    #
    # # 计算字段
    # warehouse_pt['qty_turnover_days'] = warehouse_pt['daily_stock_qty'] / warehouse_pt['daily_deli_qty']
    # warehouse_pt['vol_turnover_days'] = warehouse_pt['daily_stock_vol_m'] / warehouse_pt['daily_deli_vol_m']
    # warehouse_pt['avg_vol'] = warehouse_pt['daily_stock_vol_m'] / warehouse_pt['daily_stock_qty']
    # warehouse_pt['avg_weight'] = warehouse_pt['daily_stock_weight'] / warehouse_pt['daily_stock_qty']
    # warehouse_pt['avg_pltQty'] = (warehouse_pt['current_stockQty'] + warehouse_pt['current_pickQty']) / \
    #                              (warehouse_pt['current_pltStockN'] + warehouse_pt['current_pltPickN'])
    #
    # # pprint.pprint(warehouse_pt)
    #
    # '''
    # 121透视_PalletW-V-Pallet_O1 托盘重量分级透视表-成托
    # '''
    # palletWt_class_df = df.loc[(df['sku_state'] == '良品'),
    #                            ['SKU_ID', 'pltWt_class_palletized', 'pltWt_class_all',
    #                             'daily_stock_sku', 'daily_stock_qty', 'daily_stock_vol_m', 'daily_stock_weight',
    #                             'daily_stock_pltN', 'daily_deli_sku', 'daily_deli_qty', 'daily_deli_vol_m', ]]
    #
    # palletWt_tmp1 = pd.pivot_table(palletWt_class_df, index='pltWt_class_all', values='SKU_ID', aggfunc='count',
    #                                fill_value=0,
    #                                margins=True).reset_index()
    #
    # palletWt_tmp2 = pd.pivot_table(palletWt_class_df, index='pltWt_class_all',
    #                                values=['daily_stock_sku', 'daily_stock_qty', 'daily_stock_vol_m',
    #                                        'daily_stock_weight',
    #                                        'daily_stock_pltN', 'daily_deli_sku', 'daily_deli_qty', 'daily_deli_vol_m'],
    #                                aggfunc='sum', fill_value=0,
    #                                margins=True).reset_index()
    #
    # pltWt_class_pt = pd.merge(palletWt_tmp1, palletWt_tmp2, how='outer', sort=False)
    #
    # # 重排列
    # pltWt_class_pt = pltWt_class_pt[
    #     ['pltWt_class_all', 'SKU_ID', 'daily_stock_sku', 'daily_stock_qty', 'daily_stock_vol_m',
    #      'daily_stock_weight', 'daily_stock_pltN', 'daily_deli_sku', 'daily_deli_qty', 'daily_deli_vol_m']]
    #
    # # 更新汇总数据
    # pltWt_class_pt.loc[(pltWt_class_pt['pltWt_class_all'] == 'All'), ['daily_stock_sku']] = \
    #     palletWt_class_df['daily_stock_sku'].sum()
    # pltWt_class_pt.loc[(pltWt_class_pt['pltWt_class_all'] == 'All'), ['daily_stock_qty']] = \
    #     palletWt_class_df['daily_stock_qty'].sum()
    # pltWt_class_pt.loc[
    #     (pltWt_class_pt['pltWt_class_all'] == 'All'), ['daily_stock_vol_m']] = palletWt_class_df[
    #     'daily_stock_vol_m'].sum()
    # pltWt_class_pt.loc[
    #     (pltWt_class_pt['pltWt_class_all'] == 'All'), ['daily_stock_weight']] = palletWt_class_df[
    #     'daily_stock_weight'].sum()
    # pltWt_class_pt.loc[
    #     (pltWt_class_pt['pltWt_class_all'] == 'All'), ['daily_stock_pltN']] = palletWt_class_df[
    #     'daily_stock_pltN'].sum()
    # pltWt_class_pt.loc[(pltWt_class_pt['pltWt_class_all'] == 'All'), ['daily_deli_sku']] = \
    #     palletWt_class_df['daily_deli_sku'].sum()
    # pltWt_class_pt.loc[(pltWt_class_pt['pltWt_class_all'] == 'All'), ['daily_deli_qty']] = \
    #     palletWt_class_df['daily_deli_qty'].sum()
    # pltWt_class_pt.loc[
    #     (pltWt_class_pt['pltWt_class_all'] == 'All'), ['daily_deli_vol_m']] = palletWt_class_df[
    #     'daily_deli_vol_m'].sum()
    #
    # # 计算比例
    # pltWt_class_pt['SKU_ID%'] = round(
    #     pltWt_class_pt['SKU_ID'] / (pltWt_class_pt['SKU_ID'].sum() / 2), 6)
    # pltWt_class_pt['daily_stock_qty%'] = round(
    #     pltWt_class_pt['daily_stock_qty'] / (pltWt_class_pt['daily_stock_qty'].sum() / 2), 6)
    # pltWt_class_pt['daily_stock_vol_m%'] = round(
    #     pltWt_class_pt['daily_stock_vol_m'] / (pltWt_class_pt['daily_stock_vol_m'].sum() / 2), 6)
    # pltWt_class_pt['daily_stock_weight%'] = round(
    #     pltWt_class_pt['daily_stock_weight'] / (pltWt_class_pt['daily_stock_weight'].sum() / 2),
    #     6)
    # pltWt_class_pt['daily_deli_qty%'] = round(
    #     pltWt_class_pt['daily_deli_qty'] / (pltWt_class_pt['daily_deli_qty'].sum() / 2), 6)
    # pltWt_class_pt['daily_deli_vol_m%'] = round(
    #     pltWt_class_pt['daily_deli_vol_m'] / (pltWt_class_pt['daily_deli_vol_m'].sum() / 2), 6)
    #
    # # 计算累计比例
    # pltWt_class_pt['daily_stock_qty_cumu%'] = pltWt_class_pt['daily_stock_qty%'].cumsum()
    # pltWt_class_pt['daily_stock_vol_cumu%'] = pltWt_class_pt['daily_stock_vol_m%'].cumsum()
    # pltWt_class_pt['daily_deli_qty_cumu%'] = pltWt_class_pt['daily_deli_qty%'].cumsum()
    # pltWt_class_pt['daily_deli_vol_cumu%'] = pltWt_class_pt['daily_deli_vol_m%'].cumsum()
    #
    # # 格式化百分比
    # pltWt_class_pt['SKU_ID%'] = pltWt_class_pt['SKU_ID%'].apply(lambda x: '%.4f%%' % (x * 100))
    # pltWt_class_pt['daily_stock_qty%'] = pltWt_class_pt['daily_stock_qty%'].apply(
    #     lambda x: '%.4f%%' % (x * 100))
    # pltWt_class_pt['daily_stock_vol_m%'] = pltWt_class_pt['daily_stock_vol_m%'].apply(
    #     lambda x: '%.4f%%' % (x * 100))
    # pltWt_class_pt['daily_stock_weight%'] = pltWt_class_pt['daily_stock_weight%'].apply(
    #     lambda x: '%.4f%%' % (x * 100))
    # pltWt_class_pt['daily_deli_qty%'] = pltWt_class_pt['daily_deli_qty%'].apply(
    #     lambda x: '%.4f%%' % (x * 100))
    # pltWt_class_pt['daily_deli_vol_m%'] = pltWt_class_pt['daily_deli_vol_m%'].apply(
    #     lambda x: '%.4f%%' % (x * 100))
    # pltWt_class_pt['daily_stock_qty_cumu%'] = pltWt_class_pt['daily_stock_qty_cumu%'].apply(
    #     lambda x: '%.4f%%' % (x * 100))
    # pltWt_class_pt['daily_stock_vol_cumu%'] = pltWt_class_pt['daily_stock_vol_cumu%'].apply(
    #     lambda x: '%.4f%%' % (x * 100))
    # pltWt_class_pt['daily_deli_qty_cumu%'] = pltWt_class_pt['daily_deli_qty_cumu%'].apply(
    #     lambda x: '%.4f%%' % (x * 100))
    # pltWt_class_pt['daily_deli_vol_cumu%'] = pltWt_class_pt['daily_deli_vol_cumu%'].apply(
    #     lambda x: '%.4f%%' % (x * 100))
    #
    # # 计算字段
    # pltWt_class_pt['qty_turnover_days'] = pltWt_class_pt['daily_stock_qty'] / pltWt_class_pt['daily_deli_qty']
    # pltWt_class_pt['vol_turnover_days'] = pltWt_class_pt['daily_stock_vol_m'] / pltWt_class_pt['daily_deli_vol_m']
    #
    # # pprint.pprint(pltWt_class_pt)
    #
    # '''
    # 料箱重量分级
    # '''
    # toteWt_class_df = df.loc[(df['sku_state'] == '良品'),
    #                          ['SKU_ID', 'toteWt_class',
    #                           'daily_stock_sku', 'daily_stock_qty', 'daily_stock_vol_m', 'daily_stock_weight',
    #                           'daily_stock_pltN', 'daily_deli_sku', 'daily_deli_qty', 'daily_deli_vol_m']]
    #
    # toteWt_tmp1 = pd.pivot_table(toteWt_class_df, index='toteWt_class', values='SKU_ID', aggfunc='count',
    #                              fill_value=0,
    #                              margins=True).reset_index()
    #
    # toteWt_tmp2 = pd.pivot_table(toteWt_class_df, index='toteWt_class',
    #                              values=['daily_stock_sku', 'daily_stock_qty', 'daily_stock_vol_m',
    #                                      'daily_stock_weight',
    #                                      'daily_stock_pltN', 'daily_deli_sku', 'daily_deli_qty', 'daily_deli_vol_m'],
    #                              aggfunc='sum', fill_value=0,
    #                              margins=True).reset_index()
    #
    # toteWt_class_pt = pd.merge(toteWt_tmp1, toteWt_tmp2, how='outer', sort=False)
    #
    # # 重排列
    # toteWt_class_pt = toteWt_class_pt[
    #     ['toteWt_class', 'SKU_ID', 'daily_stock_sku', 'daily_stock_qty', 'daily_stock_vol_m',
    #      'daily_stock_weight', 'daily_stock_pltN', 'daily_deli_sku', 'daily_deli_qty', 'daily_deli_vol_m']]
    #
    # # 更新汇总数据
    # toteWt_class_pt.loc[(toteWt_class_pt['toteWt_class'] == 'All'), ['daily_stock_sku']] = \
    #     palletWt_class_df['daily_stock_sku'].sum()
    # toteWt_class_pt.loc[(toteWt_class_pt['toteWt_class'] == 'All'), ['daily_stock_qty']] = \
    #     palletWt_class_df['daily_stock_qty'].sum()
    # toteWt_class_pt.loc[
    #     (toteWt_class_pt['toteWt_class'] == 'All'), ['daily_stock_vol_m']] = palletWt_class_df[
    #     'daily_stock_vol_m'].sum()
    # toteWt_class_pt.loc[
    #     (toteWt_class_pt['toteWt_class'] == 'All'), ['daily_stock_weight']] = palletWt_class_df[
    #     'daily_stock_weight'].sum()
    # toteWt_class_pt.loc[
    #     (toteWt_class_pt['toteWt_class'] == 'All'), ['daily_stock_pltN']] = palletWt_class_df[
    #     'daily_stock_pltN'].sum()
    # toteWt_class_pt.loc[(toteWt_class_pt['toteWt_class'] == 'All'), ['daily_deli_sku']] = \
    #     palletWt_class_df['daily_deli_sku'].sum()
    # toteWt_class_pt.loc[(toteWt_class_pt['toteWt_class'] == 'All'), ['daily_deli_qty']] = \
    #     palletWt_class_df['daily_deli_qty'].sum()
    # toteWt_class_pt.loc[
    #     (toteWt_class_pt['toteWt_class'] == 'All'), ['daily_deli_vol_m']] = palletWt_class_df[
    #     'daily_deli_vol_m'].sum()
    #
    # # 计算比例
    # toteWt_class_pt['SKU_ID%'] = round(
    #     toteWt_class_pt['SKU_ID'] / (toteWt_class_pt['SKU_ID'].sum() / 2), 6)
    # toteWt_class_pt['daily_stock_qty%'] = round(
    #     toteWt_class_pt['daily_stock_qty'] / (toteWt_class_pt['daily_stock_qty'].sum() / 2), 6)
    # toteWt_class_pt['daily_stock_vol_m%'] = round(
    #     toteWt_class_pt['daily_stock_vol_m'] / (toteWt_class_pt['daily_stock_vol_m'].sum() / 2), 6)
    # toteWt_class_pt['daily_stock_weight%'] = round(
    #     toteWt_class_pt['daily_stock_weight'] / (toteWt_class_pt['daily_stock_weight'].sum() / 2),
    #     6)
    # toteWt_class_pt['daily_deli_qty%'] = round(
    #     toteWt_class_pt['daily_deli_qty'] / (toteWt_class_pt['daily_deli_qty'].sum() / 2), 6)
    # toteWt_class_pt['daily_deli_vol_m%'] = round(
    #     toteWt_class_pt['daily_deli_vol_m'] / (toteWt_class_pt['daily_deli_vol_m'].sum() / 2), 6)
    #
    # # 计算累计比例
    # toteWt_class_pt['daily_stock_qty_cumu%'] = toteWt_class_pt['daily_stock_qty%'].cumsum()
    # toteWt_class_pt['daily_stock_vol_cumu%'] = toteWt_class_pt['daily_stock_vol_m%'].cumsum()
    # toteWt_class_pt['daily_deli_qty_cumu%'] = toteWt_class_pt['daily_deli_qty%'].cumsum()
    # toteWt_class_pt['daily_deli_vol_cumu%'] = toteWt_class_pt['daily_deli_vol_m%'].cumsum()
    #
    # # 格式化百分比
    # # toteWt_class_pt['SKU_ID%'] = toteWt_class_pt['SKU_ID%'].apply(lambda x: '%.4f%%' % (x * 100))
    # # toteWt_class_pt['daily_stock_qty%'] = toteWt_class_pt['daily_stock_qty%'].apply(
    # #     lambda x: '%.4f%%' % (x * 100))
    # # toteWt_class_pt['daily_stock_vol_m%'] = toteWt_class_pt['daily_stock_vol_m%'].apply(
    # #     lambda x: '%.4f%%' % (x * 100))
    # # toteWt_class_pt['daily_stock_weight%'] = toteWt_class_pt['daily_stock_weight%'].apply(
    # #     lambda x: '%.4f%%' % (x * 100))
    # # toteWt_class_pt['daily_deli_qty%'] = toteWt_class_pt['daily_deli_qty%'].apply(
    # #     lambda x: '%.4f%%' % (x * 100))
    # # toteWt_class_pt['daily_deli_vol_m%'] = toteWt_class_pt['daily_deli_vol_m%'].apply(
    # #     lambda x: '%.4f%%' % (x * 100))
    # # toteWt_class_pt['daily_stock_qty_cumu%'] = toteWt_class_pt['daily_stock_qty_cumu%'].apply(
    # #     lambda x: '%.4f%%' % (x * 100))
    # # toteWt_class_pt['daily_stock_vol_cumu%'] = toteWt_class_pt['daily_stock_vol_cumu%'].apply(
    # #     lambda x: '%.4f%%' % (x * 100))
    # # toteWt_class_pt['daily_deli_qty_cumu%'] = toteWt_class_pt['daily_deli_qty_cumu%'].apply(
    # #     lambda x: '%.4f%%' % (x * 100))
    # # toteWt_class_pt['daily_deli_vol_cumu%'] = toteWt_class_pt['daily_deli_vol_cumu%'].apply(
    # #     lambda x: '%.4f%%' % (x * 100))
    #
    # # 计算字段
    # toteWt_class_pt['qty_turnover_days'] = toteWt_class_pt['daily_stock_qty'] / toteWt_class_pt['daily_deli_qty']
    # toteWt_class_pt['vol_turnover_days'] = toteWt_class_pt['daily_stock_vol_m'] / toteWt_class_pt['daily_deli_vol_m']

    # d = toteWt_class_pt[['toteWt_class','daily_stock_qty%','daily_stock_vol_m%' ]].hist().get_figure()
    #
    # d.savefig('1.jpg')

    ### 绘制直方图
    # pprint.pprint(toteWt_class_pt)
    # toteWt_class_pt.plot(x='toteWt_class',
    #                      y=['daily_stock_qty%', 'daily_stock_vol_m%', 'daily_deli_qty%', 'daily_deli_vol_m%'],
    #                      kind='bar', rot = -60)
    # plt.show()

    # '''
    # 162透视_StorageEquType2-NOW
    # 3级透视: 存拣模式_现状, 存储设备_现状, 存储设备-货架规格_现状
    # '''
    # # equ_df = df.loc[(df['sku_state'] == '良品'),
    # #                 ['SKU_ID', 'current_stock_mode', 'current_stock_equipment', 'current_stock_equiSize',
    # #                  'current_shelfD300_num', 'current_shelfD500_num', 'current_shelfD600_num',
    # #                  'current_shuttle_num', 'current_pltStockN', 'current_pltPickN',
    # #                  'daily_stock_sku', 'daily_stock_qty', 'daily_stock_vol_m',
    # #                  'daily_stock_weight', 'daily_stock_pltN', 'daily_deli_sku',
    # #                  'daily_deli_qty', 'daily_deli_vol_m'
    # #                  ]]
    # #
    # # equ_tmp1 = pd.pivot_table(equ_df, index=['current_stock_mode', 'current_stock_equipment', 'current_stock_equiSize'],
    # #                           values='SKU_ID', aggfunc='count',
    # #                           fill_value=0,
    # #                           margins=True).reset_index()
    # #
    # # equ_tmp2 = pd.pivot_table(equ_df, index=['current_stock_mode', 'current_stock_equipment', 'current_stock_equiSize'],
    # #                           values=['daily_stock_sku', 'daily_stock_qty', 'daily_stock_vol_m',
    # #                                   'daily_stock_weight', 'daily_stock_pltN', 'daily_deli_sku',
    # #                                   'daily_deli_qty', 'daily_deli_vol_m'],
    # #                           aggfunc='sum', fill_value=0,
    # #                           margins=True).reset_index()
    # #
    # # current_stockEquClass = pd.merge(equ_tmp1, equ_tmp2, how='outer', sort=False)
    # #
    # # # 重排列
    # # current_stockEquClass = current_stockEquClass[
    # #     ['current_stock_mode', 'current_stock_equipment', 'current_stock_equiSize',
    # #      'SKU_ID', 'daily_stock_sku', 'daily_stock_qty', 'daily_stock_vol_m',
    # #      'daily_stock_weight', 'daily_stock_pltN', 'daily_deli_sku', 'daily_deli_qty', 'daily_deli_vol_m']]
    # #
    # # # 计算比例
    # # current_stockEquClass['SKU_ID%'] = round(
    # #     current_stockEquClass['SKU_ID'] / (current_stockEquClass['SKU_ID'].sum() / 2), 6)
    # # current_stockEquClass['daily_stock_qty%'] = round(
    # #     current_stockEquClass['daily_stock_qty'] / (current_stockEquClass['daily_stock_qty'].sum() / 2), 6)
    # # current_stockEquClass['daily_stock_vol_m%'] = round(
    # #     current_stockEquClass['daily_stock_vol_m'] / (current_stockEquClass['daily_stock_vol_m'].sum() / 2), 6)
    # # current_stockEquClass['daily_stock_weight%'] = round(
    # #     current_stockEquClass['daily_stock_weight'] / (current_stockEquClass['daily_stock_weight'].sum() / 2),
    # #     6)
    # # current_stockEquClass['daily_deli_qty%'] = round(
    # #     current_stockEquClass['daily_deli_qty'] / (current_stockEquClass['daily_deli_qty'].sum() / 2), 6)
    # # current_stockEquClass['daily_deli_vol_m%'] = round(
    # #     current_stockEquClass['daily_deli_vol_m'] / (current_stockEquClass['daily_deli_vol_m'].sum() / 2), 6)
    # #
    # # # 计算周转天数
    # # current_stockEquClass['qty_turnover_days'] = current_stockEquClass['daily_stock_qty'] / current_stockEquClass[
    # #     'daily_deli_qty']
    # # current_stockEquClass['vol_turnover_days'] = current_stockEquClass['daily_stock_vol_m'] / current_stockEquClass[
    # #     'daily_deli_vol_m']
    # #
    # # print('-' * 50)
    # # pprint.pprint(current_stockEquClass)
    #
    # '''
    # 163透视_StorageEquType2-NOW
    # 2级透视： 存拣模式_现状, 存储设备-货架规格_现状
    # '''
    # # equ_tmp1 = pd.pivot_table(equ_df, index=['current_stock_mode', 'current_stock_equiSize'],
    # #                           values='SKU_ID', aggfunc='count',
    # #                           fill_value=0,
    # #                           margins=True).reset_index()
    # #
    # # equ_tmp2 = pd.pivot_table(equ_df, index=['current_stock_mode', 'current_stock_equiSize'],
    # #                           values=['daily_stock_sku', 'current_shelfD300_num', 'current_shelfD500_num',
    # #                                   'current_shelfD600_num', 'current_shuttle_num', 'current_pltPickN',
    # #                                   'current_pltStockN'],
    # #                           aggfunc='sum', fill_value=0,
    # #                           margins=True).reset_index()
    # #
    # # current_stockEquNum = pd.merge(equ_tmp1, equ_tmp2, how='outer', sort=False)
    # #
    # # # 重排列
    # # current_stockEquNum = current_stockEquNum[
    # #     ['current_stock_mode', 'current_stock_equiSize', 'SKU_ID', 'daily_stock_sku',
    # #      'current_shelfD300_num', 'current_shelfD500_num', 'current_shelfD600_num',
    # #      'current_shuttle_num', 'current_pltPickN', 'current_pltStockN']]
    # #
    # # # 计算比例
    # # current_stockEquNum['SKU_ID%'] = round(
    # #     current_stockEquNum['SKU_ID'] / (current_stockEquNum['SKU_ID'].sum() / 2), 6)
    # # current_stockEquNum['daily_stock_sku%'] = round(
    # #     current_stockEquNum['daily_stock_sku'] / (current_stockEquNum['daily_stock_sku'].sum() / 2), 6)
    # # current_stockEquNum['current_shelfD300_num%'] = round(
    # #     current_stockEquNum['current_shelfD300_num'] / (current_stockEquNum['current_shelfD300_num'].sum() / 2), 6)
    # # current_stockEquNum['current_shelfD500_num%'] = round(
    # #     current_stockEquNum['current_shelfD500_num'] / (current_stockEquNum['current_shelfD500_num'].sum() / 2),
    # #     6)
    # # current_stockEquNum['current_shelfD600_num%'] = round(
    # #     current_stockEquNum['current_shelfD600_num'] / (current_stockEquNum['current_shelfD600_num'].sum() / 2), 6)
    # # current_stockEquNum['current_shuttle_num%'] = round(
    # #     current_stockEquNum['current_shuttle_num'] / (current_stockEquNum['current_shuttle_num'].sum() / 2), 6)
    # # current_stockEquNum['current_pltPickN%'] = round(
    # #     current_stockEquNum['current_pltPickN'] / (current_stockEquNum['current_pltPickN'].sum() / 2), 6)
    # # current_stockEquNum['current_pltStockN%'] = round(
    # #     current_stockEquNum['current_pltStockN'] / (current_stockEquNum['current_pltStockN'].sum() / 2), 6)
    #
    # '''
    # 171透视_StorageEqu-DESI
    # '''
    #
    # desi_equ_df = df.loc[(df['sku_state'] == '良品'),
    #                      ['SKU_ID', 'design_stock_mode', 'design_stock_equipment', 'design_stock_equiSize',
    #                       'design_shelfD300_num', 'design_shelfD500_num', 'design_shelfD600_num',
    #                       'design_shuttle_num', 'design_pltStockN', 'design_pltPickN',
    #                       'design_daily_stock_sku', 'design_daily_stock_qty', 'design_daily_stock_vol_m',
    #                       'design_daily_stock_pltN',
    #                       'design_daily_deli_sku', 'design_daily_deli_qty', 'design_daily_deli_vol_m',
    #                       'design_stockQty', 'design_pickQty','design_stockVol_m','design_pickVol_m'
    #                       ]]
    # idx = ['design_stock_mode', 'design_stock_equipment', 'design_stock_equiSize']
    # pt_col = ['design_daily_stock_sku', 'design_daily_stock_qty',
    #            'design_shelfD300_num', 'design_shelfD500_num', 'design_shelfD600_num',
    #            'design_shuttle_num', 'design_pltStockN', 'design_pltPickN',
    #            'design_stockQty', 'design_pickQty','design_stockVol_m','design_pickVol_m']
    #
    #
    # # idx = ['design_stock_mode', 'design_stock_equipment', 'design_stock_equiSize']
    # # pt_col = ['design_daily_stock_sku', 'design_daily_stock_qty', 'design_daily_stock_vol_m',
    # #          'design_daily_deli_sku', 'design_daily_deli_qty', 'design_daily_deli_vol_m']
    # # all_col = ['design_stock_mode', 'design_stock_equipment', 'design_stock_equiSize',
    # #     'design_daily_stock_sku', 'design_daily_stock_qty', 'design_daily_stock_vol_m',
    # #     'design_daily_deli_sku', 'design_daily_deli_qty', 'design_daily_deli_vol_m']
    # desi_equNum = pd.pivot_table(desi_equ_df,
    #                              index=idx,
    #                              values=pt_col,
    #                              aggfunc='sum', fill_value=0,
    #                              margins=True).reset_index()
    #
    # # 重排列
    # desi_equNum = desi_equNum[idx + pt_col]
    #
    # # 计算比例
    # for i in range(len(pt_col)):
    #     desi_equNum[pt_col[i]+'%'] = round( desi_equNum[pt_col[i]]/(desi_equNum[pt_col[i]].sum()/2), 6)

    # pt_col2 = ['design_daily_stock_sku', 'design_daily_stock_qty',
    #            'design_shelfD300_num', 'design_shelfD500_num', 'design_shelfD600_num',
    #            'design_shuttle_num', 'design_pltStockN', 'design_pltPickN',
    #            'design_stockQty', 'design_pickQty', 'design_stockVol_m', 'design_pickVol_m',
    #            'design_pltStockN', 'design_pltPickN']
    #
    # df['design_stockVol_m']

    sku_pc_class = df[['SKU_ID', 'sku_name', 'daily_stock_PC_class', 'daily_deli_PC_class']]

    outBound_ref = df[['SKU_ID', 'fullCaseUnit', 'corrVol', 'CW_isAbnormal_tag', 'toteQty', 'pltQty',
                       'unit_deli_longest_state', 'ctn_deli_longest_state', 'size', 'ctn_size',
                       'current_stock_mode', 'current_stock_equiSize', 'prac_daily_deli_PC_class']]

    return df, outBound_ref, IV_class_data, sku_pc_class

    # return df, I_class_data, II_class_data, III_class_data, IV_class_data
