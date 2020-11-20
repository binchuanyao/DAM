# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd

'''Import Excel data into dataframe'''


def load_data(file_name, sheet_name=None):
    # 绝对路径 or 相对路径

    if type(file_name) == list:
        if len(file_name) == 4:
            stock_fileName = file_name[0]
            inBound_fileName = file_name[1]
            outBound_fileName = file_name[2]
            sku_fileName = file_name[3]
            original = load_source_data(stock_fileName, inBound_fileName, outBound_fileName, sku_fileName)
    else:
        original = load_original(file_name)

    return original


def load_outbound(outbound_file):
    if '.xlsx' in outbound_file:
        df = pd.read_excel(outbound_file)
    else:
        df = pd.read_csv(outbound_file)

    df.columns = ['warehouse', 'order_date', 'order_week', 'order_state', 'm_orderID',
                  'orderID', 'isSplit', 'order_type', 'operation_mode', 'SKU_ID', 'qty',
                  'deli_type', 'package_size', 'package_weight', 'package_long', 'package_width',
                  'package_height', 'package_num', 'province', 'city']
    return df


def load_original(original_fileName):
    # print(original_fileName)
    if '.xlsx' in original_fileName:
        original = pd.read_excel(original_fileName)
    else:
        original = pd.read_csv(original_fileName)

    # print(original.columns)

    original.columns = ['static_date', 'SKU_ID', 'sku_name', 'sku_state', 'warehouse',
                        'I_class', 'II_class', 'III_class', 'IV_class',
                        'weight', 'long', 'width', 'height',
                        'fullCaseUnit', 'ctn_long', 'ctn_width', 'ctn_height',
                        'monthly_stock_cumu_qty', 'monthly_stock_cumu_days',
                        'monthly_deli_cumu_qty', 'monthly_deli_cumu_times', 'monthly_deli_cumu_days',
                        'monthly_rec_cumu_qty', 'monthly_rec_cumu_times', 'monthly_rec_cumu_days',
                        'static_stock_qty', 'warehouse_cate', 'country', 'expiry', 'sku_cate'
                        ]

    # print('-'*50)
    # print(original.columns)
    return original


def load_source_data(stock_fileName, inBound_fileName, outBound_fileName, sku_fileName):
    # import inBound and outBound source data
    if ".xlsx" in stock_fileName:
        stock_data = pd.read_excel(stock_fileName)
    else:
        stock_data = pd.read_csv(stock_fileName)

    if ".xlsx" in outBound_fileName:
        out_data = pd.read_excel(outBound_fileName)
    else:
        out_data = pd.read_csv(outBound_fileName)

    if ".xlsx" in inBound_fileName:
        in_data = pd.read_excel(inBound_fileName)
    else:
        in_data = pd.read_csv(inBound_fileName)

    monthly_sku_detail = get_monthly_sku_detail(stock_data, out_data, in_data)
    sku_data = rename_sku_detail(sku_fileName)

    original_data = pd.merge(monthly_sku_detail, sku_data, how='outer', on='SKU_ID')

    return original_data


'''
Read data from receive, delivery and stock source data, calculate the monthly data group by skuID
receive_data: the source data of receive
delivery_data: the source data of delivery
stock_data: the source data of stock
'''


def get_monthly_sku_detail(stock_data, delivery_data=None, receive_data=None):
    stock = stock_data.groupby('SKU_ID').agg({"库存数量": np.sum, "在库日期": pd.Series.nunique}).reset_index()
    stock.columns = ['monthly_stock_cumu_qty', 'monthly_stock_cumu_days']

    deli = delivery_data.groupby('SKU_ID').agg(
        {"出库数量": np.sum, "SKU_ID": np.count, "下单日期": pd.Series.nunique}).reset_index()
    deli.columns = ['monthly_deli_cumu_qty', 'monthly_deli_cumu_times', 'monthly_deli_cumu_days']

    rec = receive_data.groupby('SKU_ID').agg(
        {"入库数量": np.sum, "SKU_ID": np.count, "收货日期": pd.Series.nunique}).reset_index()
    rec.columns = ['monthly_rec_cumu_qty', 'monthly_rec_cumu_times', 'monthly_rec_cumu_days']

    # 求取静态库存数量，取某一天的库存(最后一天)
    last_date = stock['在库日期'].max()
    last_date_stock = stock.where(['在库日期'] == last_date)['SKU_ID', '库存数量']
    last_date_stock.columns = ['SKU_ID', 'last_day_stock_qty']

    # 合并字段
    stock_rec = pd.merge(stock, rec, how='Outer', on='SKU_ID', sort=False)
    stock_deli = pd.merge(stock, deli, how='Outer', on='SKU_ID', sort=False)

    stock_detail = pd.merge(stock_rec, stock_deli, how='Outer', on='SKU_ID', sort=False)
    sku_detail = pd.merge(stock_detail, last_date_stock, how='outer', on='SKU_ID', sort=False)

    return sku_detail


def rename_sku_detail(sku_fileName):
    # load source data
    if ".xlsx" in sku_fileName:
        sku_data = pd.read_excel(sku_fileName)
    else:
        sku_data = pd.read_csv(sku_fileName)

    old_col_size = sku_data.shape[1]

    new_sku_detail_columns = ['warehouse', 'SKU_ID', 'skuName',
                              'I_class', 'II_class', 'III_class', 'IV_class',
                              'weight', 'long', 'width', 'height',
                              'fullCaseUnit', 'f_long', 'f_width', 'f_height']

    new_col_size = len(new_sku_detail_columns)

    # 重命名原始数据列名
    if old_col_size == new_col_size:
        sku_data.columns = new_sku_detail_columns
    elif old_col_size < new_col_size:
        sku_data.columns = new_sku_detail_columns[:old_col_size]
    else:
        sku_data.columns[:new_col_size] = new_sku_detail_columns

    return sku_data
