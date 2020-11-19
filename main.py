# -*- coding: utf-8 -*-

import datetime

from load_data import *
from outbound_model import *


# Press the green button in the gutter to run the script.
def run(data_path, org_path, result_path, outbound_path=None, outResult_path=None):
    time1 = datetime.datetime.now()
    print('-' * 20 + '导入数据' + '-' * 20)
    org = load_data(data_path)
    time2 = datetime.datetime.now()
    print('数据导入时间：', (time2 - time1).seconds, ' S')

    ### -------------------------------------------------------------------------------
    df, outBound_ref, IV_class_data, sku_pc_class = correction_data(org)
    # df, I_class_data, II_class_data, III_class_data, IV_class_data = correction_data(org)
    time3 = datetime.datetime.now()
    print('-' * 50)
    print('字段计算时间：', (time3 - time2).seconds, ' S')

    # 计算结果写入execle文件
    ### -------------------------------------------------------------------------------
    wriTime1 = datetime.datetime.now()
    writer = pd.ExcelWriter(org_path)
    df.to_excel(excel_writer=writer, sheet_name='OriginalData', float_format='%.4f')
    outBound_ref.to_excel(excel_writer=writer, sheet_name='outBound_ref')
    # I_class_data.to_excel(excel_writer=writer, sheet_name='I_class_data')
    # II_class_data.to_excel(excel_writer=writer, sheet_name='II_class_data')
    # III_class_data.to_excel(excel_writer=writer, sheet_name='III_class_data')
    # IV_class_data.to_excel(excel_writer=writer, sheet_name='IV_class_data')
    IV_class_data.to_excel(excel_writer=writer, sheet_name='IV_class_data')
    sku_pc_class.to_excel(excel_writer=writer, sheet_name='sku_pc_class')
    writer.save()
    writer.close()

    wriTime2 = datetime.datetime.now()
    print('-' * 50)
    print('原始数据行数：', df.shape[0])
    print('原始数据列数：', df.shape[1])
    print('Original文件写入时间：', (wriTime2 - wriTime1).seconds, ' S')

    # 库存分析生成透视表并写入文件
    ### -------------------------------------------------------------------------------
    pt1 = datetime.datetime.now()
    generate_pivot_table(df, outFileName=result_path)
    pt2 = datetime.datetime.now()
    print('-' * 50)
    print('库存分析字段计算及文件写入时间：', (pt2 - pt1).seconds, ' S')

    ### -------------------------------------------------------------------------------
    # 调用出库模型
    outTime1 = datetime.datetime.now()
    if outbound_path is not None and outResult_path is not None:
        outbound_org = load_outbound(outbound_path)
        outTime2 = datetime.datetime.now()
        print('出库数据导入时间：', (outTime2 - outTime1).seconds, ' S')
        outbound(outBound_ref, outbound_org, outResult_path)

        outTime3 = datetime.datetime.now()
        print('出库分析字段计算时间&文件写入时间：', (outTime3 - outTime2).seconds, ' S')


if __name__ == '__main__':
    startTime = datetime.datetime.now()
    print('-' * 20 + '程序开始' + '-' * 20 + '')

    # file_path1 = 'D:/Project/亿格/YG/jy_original.xlsx'
    # file_path2 = 'D:/Project/亿格/YG/ly_original.xlsx'
    # org_path1 = 'D:/Project/亿格/YG/output/jy_org.xlsx'
    # org_path2 = 'D:/Project/亿格/YG/output/ly_org.xlsx'
    # result_fileName1 = 'D:/Project/亿格/YG/output/jy_result.xlsx'
    # result_fileName2 = 'D:/Project/亿格/YG/output/ly_result.xlsx'

    # run(file_path1, org_path1, result_fileName1)
    # run(file_path2, org_path2, result_fileName2)

    # file_path3 = 'D:/Project/亿格/YG/source_data.xlsx'
    # org_path3 = 'D:/Project/亿格/YG/output/all_org.xlsx'
    # result_fileName3 = 'D:/Project/亿格/YG/output/all_result.xlsx'
    # run(file_path3, org_path3, result_fileName3)

    file_path = 'D:/Work/Project/09蜜思肤/data/msf_original.xlsx'
    out_path = 'D:/Work/Project/09蜜思肤/data/msf_outbound_original.xlsx'

    org_path = 'D:/Work/Project/09蜜思肤/Output/msf_stockClass1.xlsx'
    result_path = 'D:/Work/Project/09蜜思肤/Output/msf_stockClass2.xlsx'
    out_result_path = 'D:/Work/Project/09蜜思肤/Output/msf_outBound.xlsx'

    run(file_path, org_path, result_path, outbound_path=out_path, outResult_path=out_result_path)

    print('-' * 20 + '程序运行完成！' + '-' * 20 + '')
    endTime = datetime.datetime.now()
    print('-' * 50)
    print('程序运行总时间：', (endTime - startTime).seconds, ' S')
