# -*- coding: utf-8 -*-

import datetime

from load_data import *
from outbound_model import *


# Press the green button in the gutter to run the script.
def run(data_path, org_path, result_path, outbound_path=None, outResult_path=None):
    time1 = datetime.now()
    print('-' * 20 + '导入数据' + '-' * 20)
    org = load_data(data_path)
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
    writer = pd.ExcelWriter('{}stockClass1_{}.xlsx'.format(org_path, str_writime))
    df.to_excel(excel_writer=writer, sheet_name='OriginalData', float_format='%.4f')
    outBound_ref.to_excel(excel_writer=writer, sheet_name='outBound_ref')

    # I_class_data.to_excel(excel_writer=writer, sheet_name='I_class_data')
    # II_class_data.to_excel(excel_writer=writer, sheet_name='II_class_data')
    # III_class_data.to_excel(excel_writer=writer, sheet_name='III_class_data')
    # IV_class_data.to_excel(excel_writer=writer, sheet_name='IV_class_data')
    IV_class_data.to_excel(excel_writer=writer, sheet_name='IV_class_data')
    sku_pc_class.to_excel(excel_writer=writer, sheet_name='sku_pc_class')

    ### 平均托盘件数

    tmp1 = pd.pivot_table(df, index=['IV_class'],
                          values=['SKU_ID'], aggfunc='count',
                          fill_value=0,
                          margins=True).reset_index()

    tmp2 = pd.pivot_table(df, index=['IV_class'],
                          values=['pltQty', 'fullCaseUnit'], aggfunc='mean',
                          fill_value=0,
                          margins=True).reset_index()
    avg_pltQty = pd.merge(tmp1, tmp2, how='left', sort=False)
    avg_pltQty.to_excel(excel_writer=writer, sheet_name='avg_pltQty')

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

    factor_path = 'D:/Work/Project/09蜜思肤/Output/msf_stock_factor.xlsx'

    ### -------------------------------------------------------------------------------
    ## 计算不同托盘尺寸下存储区/拣选区的存储系数
    # get_stock_factor(df, outFileName=factor_path)

    # generate_pivot_table(df, outFileName=result_path)
    pt2 = datetime.now()
    print('-' * 50)
    print('库存分析字段计算及文件写入时间：', (pt2 - pt1).seconds, ' S')

    ### -------------------------------------------------------------------------------
    # 调用出库模型
    outTime1 = datetime.now()
    if outbound_path is not None and outResult_path is not None:
        outbound_org = load_outbound(outbound_path)
        outTime2 = datetime.now()
        print('出库数据导入时间：', (outTime2 - outTime1).seconds, ' S')
        outbound(outBound_ref, outbound_org, outResult_path)

        outTime3 = datetime.now()
        print('出库分析字段计算时间&文件写入时间：', (outTime3 - outTime2).seconds, ' S')

def gene_factor():
    plt_config = [1200, 1000]
    print('git test')

if __name__ == '__main__':
    startTime = datetime.now()
    print('-' * 20 + '程序开始' + '-' * 20 + '')

    # stock_file1 = 'D:/Project/亿格/YG/jy_original.xlsx'
    # stock_file2 = 'D:/Project/亿格/YG/ly_original.xlsx'
    # org_path1 = 'D:/Project/亿格/YG/output/jy_org.xlsx'
    # org_path2 = 'D:/Project/亿格/YG/output/ly_org.xlsx'
    # result_fileName1 = 'D:/Project/亿格/YG/output/jy_result.xlsx'
    # result_fileName2 = 'D:/Project/亿格/YG/output/ly_result.xlsx'

    # run(stock_file1, org_path1, result_fileName1)
    # run(stock_file2, org_path2, result_fileName2)

    # stock_file3 = 'D:/Project/亿格/YG/source_data.xlsx'
    # org_path3 = 'D:/Project/亿格/YG/output/all_org.xlsx'
    # result_fileName3 = 'D:/Project/亿格/YG/output/all_result.xlsx'
    # run(stock_file3, org_path3, result_fileName3)

    stock_file = 'D:/Work/Project/09蜜思肤/msf_data/msf_original.xlsx'
    outbound_file = 'D:/Work/Project/09蜜思肤/msf_data/msf_outbound_original.xlsx'

    org_path = 'D:/Work/Project/09蜜思肤/Output/msf_'
    result_path = 'D:/Work/Project/09蜜思肤/Output/msf_'
    out_result_path = 'D:/Work/Project/09蜜思肤/Output/msf_'

    # run(stock_file, org_path, result_path)

    run(stock_file, org_path, result_path, outbound_path=outbound_file, outResult_path=out_result_path)

    print('-' * 20 + '程序运行完成！' + '-' * 20 + '')
    endTime = datetime.now()
    print('-' * 50)
    print('程序运行总时间：', (endTime - startTime).seconds, ' S')
