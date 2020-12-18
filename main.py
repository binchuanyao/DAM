# -*- coding: utf-8 -*-

import datetime

from load_data import *
from outbound_model import *
from fp_growth import *


# Press the green button in the gutter to run the script.
def run(stock_orgData, output_path, outbound_orgData=None, isValidFile=False):
    '''
    Stock class and outbound analysis model
    :param stock_orgData: the stock original data
    :param output_path: the result file path
    :param outbound_orgData: the outbound original data
    :param isValidFile: if FALSE output all the pivot of stock and outbound,
                        if TRUE only output the simple pivot of stock and outbound
    :return: none
    '''
    time1 = datetime.now()
    print('-' * 20 + '导入数据' + '-' * 20)
    org = load_data(stock_orgData)
    time2 = datetime.now()
    print('数据导入时间：', (time2 - time1).seconds, ' S')

    ### -------------------------------------------------------------------------------
    df, outBound_ref, IV_class_data, sku_pc_class = calu_stock_data(org)
    # df, I_class_data, II_class_data, III_class_data, IV_class_data = calu_stock_data(org)
    time3 = datetime.now()
    print('-' * 50)
    print('字段计算时间：', (time3 - time2).seconds, ' S')

    # 计算结果写入execle文件
    ### -------------------------------------------------------------------------------
    wriTime1 = datetime.now()
    str_writime = wriTime1.strftime('%Y_%m_%d_%H_%M')
    writer = pd.ExcelWriter('{}stockClass1_{}.xlsx'.format(output_path, str_writime))

    # df.to_excel(excel_writer=writer, sheet_name='OriginalData', float_format='%.4f')
    # outBound_ref.to_excel(excel_writer=writer, sheet_name='outBound_ref')
    # IV_class_data.to_excel(excel_writer=writer, sheet_name='IV_class_data')
    # sku_pc_class.to_excel(excel_writer=writer, sheet_name='sku_pc_class')

    format_data(writer, df=df, sheet_name='00-outBound')
    format_data(writer, df=outBound_ref, sheet_name='01-outBound_ref')
    format_data(writer, df=IV_class_data, sheet_name='02-IV_class_data')
    format_data(writer, df=sku_pc_class, sheet_name='03-sku_pc_class')

    ### 平均托盘件数

    # tmp1 = pd.pivot_table(df, index=['IV_class'],
    #                       values=['SKU_ID'], aggfunc='count',
    #                       fill_value=0,
    #                       margins=True).reset_index()
    #
    # tmp2 = pd.pivot_table(df, index=['IV_class'],
    #                       values=['pltQty', 'fullCaseUnit'], aggfunc='mean',
    #                       fill_value=0,
    #                       margins=True).reset_index()
    # avg_pltQty = pd.merge(tmp1, tmp2, how='left', sort=False)
    # # avg_pltQty.to_excel(excel_writer=writer, sheet_name='avg_pltQty')
    # format_data(writer, df=avg_pltQty, sheet_name='04-avg_pltQty')

    writer.save()
    writer.close()

    wriTime2 = datetime.now()
    print('-' * 50)
    print('原始数据行数：', df.shape[0])
    print('原始数据列数：', df.shape[1])
    print('Original文件写入时间：', (wriTime2 - wriTime1).seconds, ' S')

    # 库存分析生成透视表并写入文件
    ### -------------------------------------------------------------------------------
    pt1 = datetime.now()

    if isValidFile:
        gene_stock_valid_pivot(df, output_path=output_path)
    else:
        gene_stock_pivot(df, output_path=output_path)

    pt2 = datetime.now()
    print('-' * 50)
    print('库存分析字段计算及文件写入时间：', (pt2 - pt1).seconds, ' S')

    ### -------------------------------------------------------------------------------
    # 调用出库模型
    outTime1 = datetime.now()
    if outbound_orgData is not None:
        outbound_org = load_outbound(outbound_orgData)
        outTime2 = datetime.now()
        print('出库数据导入时间：', (outTime2 - outTime1).seconds, ' S')
        outbound(outBound_ref, outbound_org, output_path, isValidFile=isValidFile)

        outTime3 = datetime.now()
        print('出库分析字段计算时间&文件写入时间：', (outTime3 - outTime2).seconds, ' S')


def gene_factor(output_path, data_path):
    '''
    Calculate the storage and pick coefficient under different pallet sizes
    :param data_path: the stock original data
    :return: none
    '''
    ### -------------------------------------------------------------------------------
    org = load_data(data_path)

    wriTime1 = datetime.now()
    str_time = wriTime1.strftime('%m_%d_%H_%M')

    factor_path = '{}stock_factor{}.xlsx'.format(output_path, str_time)

    ### -------------------------------------------------------------------------------
    # 计算不同托盘尺寸下存储区/拣选区的存储系数
    plt_list = [[1200, 1100],
                [1200, 1000],
                [1200, 1100],
                [1200, 800],
                [1100, 1100],
                [1100, 1000],
                [1000, 800]]

    writer = pd.ExcelWriter(factor_path)
    for i in range(len(plt_list)):
        config = Config()
        config.run()
        config.PALLET_STOCK['long'] = plt_list[i][0]
        config.PALLET_STOCK['width'] = plt_list[i][1]

        config.PALLET_PICK['long'] = plt_list[i][0]
        config.PALLET_PICK['width'] = plt_list[i][1]

        df, outBound_ref, IV_class_data, sku_pc_class = calu_stock_data(org, config=config)
        get_stock_factor(df, config, writer=writer)

    # 保存文件
    writer.save()
    writer.close()


if __name__ == '__main__':
    startTime = datetime.now()
    print('-' * 20 + '程序开始' + '-' * 20 + '')

    project_name = 'msf'
    #原始数据路径
    data_path = 'D:/Work/Project/09蜜思肤/msf_data/'
    # 输出结果路径
    output_path = 'D:/Work/Project/09蜜思肤/Output/msf_'

    stock_orgData_file = '{}msf_original.xlsx'.format(data_path)
    outbound_orgData_file = '{}msf_outbound_original.xlsx'.format(data_path)

    # org_path = 'D:/Work/Project/09蜜思肤/Output/msf_'
    # result_path = 'D:/Work/Project/09蜜思肤/Output/msf_'
    # out_result_path = 'D:/Work/Project/09蜜思肤/Output/msf_'


    # run(stock_file, stockOrg_path, stockResult_path)

    # # 运行库存模型，出库模型，生成不同维度的透视表
    run(stock_orgData_file, output_path, outbound_orgData=outbound_orgData_file, isValidFile=False)
    #
    # # 计算不同托盘尺寸下存储区/拣选区的存储系数
    # gene_factor(output_path, stock_orgData_file)

    # 计算出库关联规则
    # run_fpGrowth()


    print('-' * 20 + '程序运行完成！' + '-' * 20 + '')
    endTime = datetime.now()
    print('-' * 50)
    print('程序运行总时间：', (endTime - startTime).seconds, ' S')
