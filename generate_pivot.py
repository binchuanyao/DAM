# -*- coding: utf-8 -*-

from calculate import *


def generate_pivot_table(df, outFileName):
    """
    according to the calculated dataframe, generate several pivot tables and write to excel file
    :param df: calculated dataframe, 176 valid columns totally
    :param outFileName: the file name written in
    """
    # 加载config参数
    config = Config()
    config.run()

    writer = pd.ExcelWriter(outFileName)
    workbook = writer.book
    workbook.add_format(
        {'bold': False, 'font_size': 8, 'font_name': u'Microsoft YaHei Light'})
    # fmt = workbook.add_format({'font_name': u'Microsoft YaHei Light'})
    # percent_fmt = workbook.add_format({'num_format': '0.00%'})
    # amt_fmt = workbook.add_format({'num_format': '#,##0'})
    # border_format = workbook.add_format({'border': 1})
    # note_fmt = workbook.add_format(
    #     {'bold': True, 'font_name': u'Microsoft YaHei Light', 'font_color': 'red', 'align': 'left', 'valign': 'vcenter'})
    # date_fmt = workbook.add_format({'bold': False, 'font_name': u'Microsoft YaHei Light', 'num_format': 'yyyy-mm-dd'})
    # date_fmt1 = workbook.add_format(
    #     {'bold': True, 'font_size': 10, 'font_name': u'Microsoft YaHei Light', 'num_format': 'yyyy-mm-dd',
    #      'bg_color': '#9FC3D1',
    #      'valign': 'vcenter', 'align': 'center'})

    ### ---------------------------------------------
    '''
    101 透视托盘拣选位托盘数，拣选位商品总体积，计算托盘拣选位存储系数
    '''
    pt1 = df.loc[(df['current_stock_equipment'] == '托盘'),
                 ['warehouse', 'current_pltPickN', 'current_pickVol_m']]
    # print(pt1)
    palletPick_factor = pd.pivot_table(df, index='warehouse', values=['current_pltPickN', 'current_pickVol_m'],
                                       aggfunc=np.sum, fill_value=0).reset_index()

    palletPick_factor['factor'] = palletPick_factor['current_pickVol_m'] * pow(10, 9) / (
            palletPick_factor['current_pltPickN'] *
            config.PALLET_STOCK['valid_vol'] / config.PALLET_STOCK['rate'])

    # write to file
    palletPick_factor.to_excel(excel_writer=writer, sheet_name='01-palletPick_factor')
    # worksheet = writer.sheets['01-palletPick_factor']
    # worksheet.format()

    '''
    # 102 透视托盘存储位托盘数，存储位商品总体积，存储位箱规体积(m3)，计算托盘存储位存储系数
    '''
    # pt2 = df.loc[(df['sku_state'] == '良品') & (df['corrSW_isAbnormal_tag'] == 'N') & (df['CW_isAbnormal_tag'] == 'N'),
    #              ['warehouse', 'current_pltStockN', 'current_stockVol_m', 'current_stockCtnVol']]

    palletStock_factor = pd.pivot_table(df, index='warehouse',
                                        values=['current_pltStockN', 'current_stockVol_m', 'current_stockCtnVol'],
                                        aggfunc=np.sum, fill_value=0).reset_index()

    palletStock_factor['vol_factor'] = palletStock_factor['current_stockVol_m'] * pow(10, 9) / (
            palletStock_factor['current_pltStockN'] *
            config.PALLET_STOCK['valid_vol'] / config.PALLET_STOCK['rate'])
    palletStock_factor['ctn_factor'] = palletStock_factor['current_stockCtnVol'] * pow(10, 9) / (
            palletStock_factor['current_pltStockN'] *
            config.PALLET_STOCK['valid_vol'] / config.PALLET_STOCK['rate'])

    # write to file
    palletStock_factor.to_excel(excel_writer=writer, sheet_name='02-palletStock_factor', inf_rep='')

    '''
    # 103 透视 箱规每托(含托盘)实际码放高度(mm)(按额定体积&重量折算)，计算 均高/设计高度
    # PalletStoc-CartonS1H_O1
    '''
    pt3 = df.loc[(df['sku_state'] == '良品') & (df['corrSW_isAbnormal_tag'] == 'N') & (df['CW_isAbnormal_tag'] == 'N'),
                 ['ctn_pltHeight', 'current_pltStockN']]

    palletStock_height_factor = pt3.groupby('ctn_pltHeight').agg(
        current_pltStockN=pd.NamedAgg(column='current_pltStockN', aggfunc='sum')).reset_index()

    palletStock_height_factor['sum_pallet_height'] = palletStock_height_factor['ctn_pltHeight'] * \
                                                     palletStock_height_factor['current_pltStockN']

    if (palletStock_height_factor['current_pltStockN']).sum() > 0:
        palletStock_height_factor['avg_pallet_height'] = (palletStock_height_factor['sum_pallet_height']).sum() / \
                                                         (palletStock_height_factor['current_pltStockN']).sum()
    else:
        palletStock_height_factor['avg_pallet_height'] = 0

    palletStock_height_factor['design_pallet_height'] = config.PALLET_STOCK['valid_height'] + config.PALLET_STOCK[
        'plt_height']

    palletStock_height_factor['pallet_height_factor'] = palletStock_height_factor['avg_pallet_height'] / \
                                                        palletStock_height_factor['design_pallet_height']

    # write to file
    palletStock_height_factor.to_excel(excel_writer=writer, sheet_name='03-palletStock_factor', inf_rep='')

    ### ---------------------------------------------------------
    # 公共参数
    sku = ['SKU_ID']

    ### -------------------------------------------------
    '''
    SKU 相关属性透视表
    '''
    # 111 良品/残品统计

    idx11 = ['sku_state']
    pt_col11 = ['daily_stock_sku', 'daily_stock_qty', 'daily_stock_vol_m']
    stockGood_and_Damaged = general_class(df, sku=sku, index=idx11, pt_col=pt_col11)
    stockGood_and_Damaged.to_excel(excel_writer=writer, sheet_name='11-stockGood_and_Damaged', inf_rep='')

    # 112透视_SIZE_O1
    size_df = df.loc[(df['sku_state'] == '良品') & (df['stock_qty_isNonZero'] == 'Y'),
                     ['SKU_ID', 'size', 'daily_stock_sku', 'daily_stock_qty', 'daily_stock_vol_m',
                      'daily_stock_weight', 'daily_stock_pltN', 'daily_deli_sku', 'daily_deli_qty',
                      'daily_deli_vol_m', 'current_pltStockN', 'current_pltPickN',
                      'current_stockQty', 'current_pickQty']]
    idx12 = ['size']
    pt_col_com = ['daily_stock_sku', 'daily_stock_qty', 'daily_stock_vol_m', 'daily_stock_weight',
                  'daily_stock_pltN', 'daily_deli_sku', 'daily_deli_qty', 'daily_deli_vol_m',
                  'current_pltStockN', 'current_pltPickN',
                  'current_stockQty', 'current_pickQty']
    size = general_class(size_df, sku=sku, index=idx12, pt_col=pt_col_com, isAvg=True)
    size.to_excel(excel_writer=writer, sheet_name='12-size', inf_rep='')

    '''
    # 113透视_CLASS1_O1
    '''
    class_df = df.loc[(df['stock_qty_isNonZero'] == 'Y'),
                      ['SKU_ID', 'size', 'I_class', 'II_class', 'III_class', 'IV_class',
                       'daily_stock_sku', 'daily_stock_qty', 'daily_stock_vol_m',
                       'daily_stock_weight', 'daily_stock_pltN', 'daily_deli_sku', 'daily_deli_qty',
                       'daily_deli_vol_m', 'current_pltStockN', 'current_pltPickN',
                       'current_stockQty', 'current_pickQty']]
    idx13 = ['IV_class']
    class_pt = general_class(class_df, sku=sku, index=idx13, pt_col=pt_col_com, isAvg=True)
    class_pt.to_excel(excel_writer=writer, sheet_name='13-class_pt', inf_rep='')

    plt_col = ['daily_stock_sku', 'daily_stock_qty', 'daily_deli_qty',
               'current_pltStockN', 'current_pltPickN',
               'current_stockQty', 'current_pickQty']

    idx14 = ['IV_class']
    ### 类别均值
    class_avg = pd.pivot_table(df, index=idx14,
                               values=['pltQty', 'fullCaseUnit'], aggfunc='mean',
                               fill_value=0,
                               margins=True).reset_index()
    class_avg.to_excel(excel_writer=writer, sheet_name='class_avg', inf_rep='')

    # class_pt = avg_pltQty_class(df, index=idx14, pt_col=plt_col)
    # class_pt.to_excel(excel_writer=writer, sheet_name='class_pt', inf_rep='')

    '''
    114透视_Size&Class1_O1
    '''
    idx14 = ['size', 'IV_class']
    size_class_pt = general_class(class_df, sku=sku, index=idx14, pt_col=pt_col_com)
    size_class_pt.to_excel(excel_writer=writer, sheet_name='14-size_class_pt', inf_rep='')

    '''
    115透视_WarehouseType_O1  warehouse_pt
    '''
    idx15 = ['warehouse']
    warehouse_pt = general_class(df, sku=sku, index=idx15, pt_col=pt_col_com)
    warehouse_pt.to_excel(excel_writer=writer, sheet_name='15-warehouse_pt', inf_rep='')

    # ---------------------------------------------------------------------------------
    '''
    分级相关字段透视表
    '''
    '''
    121透视_PalletW-V-Pallet_O1 托盘重量分级透视表-成托
    '''
    palletWt_class_df = df.loc[(df['sku_state'] == '良品'),
                               ['SKU_ID', 'pltWt_class_palletized', 'pltWt_class_all',
                                'daily_stock_sku', 'daily_stock_qty', 'daily_stock_vol_m', 'daily_stock_weight',
                                'daily_stock_pltN', 'daily_deli_sku', 'daily_deli_qty', 'daily_deli_vol_m', ]]

    idx21 = ['pltWt_class_palletized']
    pltWt_class_palletized = general_class(palletWt_class_df, sku=sku, index=idx21, isCumu=True)
    pltWt_class_palletized.to_excel(excel_writer=writer, sheet_name='21-pltWt_class_palletized', inf_rep='')

    # 122透视_PalletW-V-Pallet_O1 托盘重量分级透视表-成托&不成托
    idx22 = ['pltWt_class_all']
    pltWt_class_all = general_class(palletWt_class_df, sku=sku, index=idx22, isCumu=True)
    pltWt_class_all.to_excel(excel_writer=writer, sheet_name='22-pltWt_class_all', inf_rep='')

    '''
    123 料箱重量分级 
    '''
    toteWt_class_df = df.loc[(df['sku_state'] == '良品'),
                             ['SKU_ID', 'toteWt_class',
                              'daily_stock_sku', 'daily_stock_qty', 'daily_stock_vol_m', 'daily_stock_weight',
                              'daily_stock_pltN', 'daily_deli_sku', 'daily_deli_qty', 'daily_deli_vol_m']]
    idx23 = ['toteWt_class']
    toteWt_class = general_class(toteWt_class_df, sku=sku, index=idx23, isCumu=True)
    toteWt_class.to_excel(excel_writer=writer, sheet_name='23-toteWt_class', inf_rep='')

    ### --------------------------------------------
    '''
    提取ABC数据
    '''

    # 131 透视_ABC-MADQ_O1
    idx31 = ['ABC_MADQ']
    ABC_MADQ = abc_class(df, index=idx31)
    ABC_MADQ.to_excel(excel_writer=writer, sheet_name='31-ABC_MADQ', inf_rep='')

    # 132 透视_ABC-MADQ_O1
    idx32 = ['ABC_MADV']
    ABC_MADV = abc_class(df, index=idx32)
    ABC_MADV.to_excel(excel_writer=writer, sheet_name='32-ABC_MADV', inf_rep='')

    # 133 透视_ABC-MADQ_O1
    idx33 = ['ABC_MPDQ']
    ABC_MPDQ = abc_class(df, index=idx33)
    ABC_MPDQ.to_excel(excel_writer=writer, sheet_name='33-ABC_MPDQ', inf_rep='')

    # 134 透视_ABC-MADQ_O1
    idx34 = ['ABC_MPDV']
    ABC_MPDV = abc_class(df, index=idx34)
    ABC_MPDV.to_excel(excel_writer=writer, sheet_name='34-ABC_MPDV', inf_rep='')

    # 135 透视_ABC-MPDQ&MPDQ_O1
    idx35 = ['ABC_MADQ', 'ABC_MADV']
    ABC_MADQ_ABC_MADV = abc_class(df, index=idx35)
    ABC_MADQ_ABC_MADV.to_excel(excel_writer=writer, sheet_name='35-ABC_MADQ_ABC_MADV', inf_rep='')

    # 136透视_ABC-MADQ&库存-出库天数分级_O1
    idx36 = ['ABC_MADQ', 'stock_days_class', 'deli_days_class']
    ABC_MADQ_days_class = abc_class(df, index=idx36)
    ABC_MADQ_days_class.to_excel(excel_writer=writer, sheet_name='36-ABC_MADQ_days_class', inf_rep='')

    # 137透视_ABC-MPDQ&库存-出库天数分级_O1
    idx37 = ['ABC_MPDQ', 'stock_days_class', 'deli_days_class']
    ABC_MPDQ_days_class = abc_class(df, index=idx37)
    ABC_MPDQ_days_class.to_excel(excel_writer=writer, sheet_name='37-ABC_MPDQ_days_class', inf_rep='')

    # ------------------------------------------------------------------------------------
    '''
    库存储量分级
    '''
    # 140 透视_CTN_QTY-CLASS
    idx40 = ['daily_stock_ctnQty_class']
    col = ['daily_stock_pltN', 'daily_stock_toteN', 'daily_stock_qty', 'daily_deli_sku',
           'daily_deli_pltN', 'daily_deli_toteN', 'daily_deli_qty']
    stock_PC_class = pc_class(df, index=idx40, pt_col=col)
    stock_PC_class.to_excel(excel_writer=writer, sheet_name='40-daily_stock_ctnQty_class', inf_rep='')

    # 141透视_P&C-CLASS-V&W_O1
    idx41 = ['daily_stock_PC_class']
    # col = ['daily_stock_pltN', 'daily_stock_toteN', 'daily_stock_qty', 'daily_deli_sku',
    #        'daily_deli_pltN', 'daily_deli_toteN', 'daily_deli_qty']
    stock_PC_class = pc_class(df, index=idx41, pt_col=col)
    stock_PC_class.to_excel(excel_writer=writer, sheet_name='41-stock_PC_class', inf_rep='')

    # 142透视_SIZE-P&C-CLASS-V&W_O1
    idx42 = ['size', 'daily_stock_PC_class']
    stock_size_PC_class = pc_class(df, index=idx42, pt_col=col, isCumu=True)
    stock_size_PC_class.to_excel(excel_writer=writer, sheet_name='42-stock_size_PC_class', inf_rep='')

    # 143透视_P&C-CLASS-V&W_O1  出库
    idx43 = ['daily_deli_PC_class']
    deli_PC_class = pc_class(df, index=idx43, pt_col=col, isCumu=True)
    deli_PC_class.to_excel(excel_writer=writer, sheet_name='43-deli_PC_class', inf_rep='')

    # 144透视_SIZE-P&C-CLASS-V&W_O1 出库
    idx44 = ['size', 'daily_deli_PC_class']
    deli_size_PC_class = pc_class(df, index=idx44, pt_col=col, isCumu=True)
    deli_size_PC_class.to_excel(excel_writer=writer, sheet_name='44-deli_size_PC_class', inf_rep='')

    ## 145 库存分级 & 出库分级透视
    idx45 = ['daily_stock_PC_class', 'daily_deli_PC_class']
    stock_deli_class = pc_class(df, index=idx45, pt_col=col, isCumu=True)
    stock_deli_class.to_excel(excel_writer=writer, sheet_name='45-stock_deli_class', inf_rep='')

    # --------------------------------------------------------------------------------------
    '''
    透视 现状设备相关字段
    '''
    #  51  162透视_StorageEquType2-NOW
    # 3级透视: 存拣模式_现状, 存储设备_现状, 存储设备-货架规格_现状
    equ_df = df.loc[(df['sku_state'] == '良品'),
                    ['SKU_ID', 'size', 'current_stock_mode', 'current_stock_equipment', 'current_stock_equiSize',
                     'current_shelfD300_num', 'current_shelfD500_num', 'current_shelfD600_num',
                     'current_shuttle_num', 'current_pltStockN', 'current_pltPickN',
                     'daily_stock_sku', 'daily_stock_qty', 'daily_stock_vol_m',
                     'daily_stock_weight', 'daily_stock_pltN', 'daily_deli_sku',
                     'daily_deli_qty', 'daily_deli_vol_m',
                     'current_stockQty', 'current_pickQty',
                     'current_stockVol_m', 'current_pickVol_m'
                     ]]
    idx51 = ['current_stock_mode', 'current_stock_equipment', 'current_stock_equiSize']
    current_equType = general_class(equ_df, index=idx51)
    current_equType.to_excel(excel_writer=writer, sheet_name='51-current_equType', inf_rep='')

    # 52 现状存储设备透视
    idx52 = ['current_stock_mode', 'current_stock_equipment', 'current_stock_equiSize']
    current_equNum = current_equ_class(equ_df, index=idx52)
    current_equNum.to_excel(excel_writer=writer, sheet_name='52-current_equNum', inf_rep='')

    # 53 现状存储设备 & 件型 透视
    idx53 = ['current_stock_mode', 'current_stock_equiSize', 'size']
    current_equType_size = current_equ_class(equ_df, index=idx53)
    current_equType_size.to_excel(excel_writer=writer, sheet_name='53-current_equType_size', inf_rep='')

    ### --------------------------------------------
    '''
    提取design数据
    '''
    # 171透视_StorageEqu-DESI_O101
    # 61 规划设备 库存&出库 相关字段透视
    idx61 = ['design_stock_mode', 'design_stock_equipment', 'design_stock_equiSize']
    pt_col61 = ['design_daily_stock_sku', 'design_daily_stock_qty',
                'design_daily_stock_vol_m', 'design_daily_stock_pltN',
                'design_daily_deli_sku', 'design_daily_deli_qty', 'design_daily_deli_vol_m']

    design_equType = design_equ_class(df, index=idx61, pt_col=pt_col61)
    design_equType.to_excel(excel_writer=writer, sheet_name='61-design_equType', inf_rep='')
    # pprint.pprint(design_equClass)

    # 62 规划设备 设备数量 相关字段透视
    idx62 = ['design_stock_mode', 'design_stock_equipment', 'design_stock_equiSize']
    # pt_col2 = ['design_daily_stock_sku', 'design_daily_stock_qty',
    #            'design_shelfD300_num', 'design_shelfD500_num', 'design_shelfD600_num', 'design_shuttle_num',
    #            'design_stockQty', 'design_pickQty', 'design_stockVol_m', 'design_pickVol_m',
    #            'design_pltStockN', 'design_pltPickN']

    design_equTypeNum = design_equ_class(df, index=idx62)
    design_equTypeNum.to_excel(excel_writer=writer, sheet_name='62-design_equTypeNum', inf_rep='')

    # 63 规划设备&件型 设备数量 相关字段透视
    idx63 = ['design_stock_mode', 'design_stock_equiSize', 'size']
    design_equType_size = design_equ_class(df, index=idx63)
    design_equType_size.to_excel(excel_writer=writer, sheet_name='63-design_equType_size', inf_rep='')

    # 保存文件
    writer.save()
    writer.close()


def general_class(df, index, sku=None, pt_col=None, isCumu=False, isSimple=True, isAvg=False):
    """
    :param df: 透视表原始数据
    :param index: 透视的行
    :param sku: 是否添加 SKU_ID 字段
    :param pt_col: 透视的 values，即透视字段
    :param isCumu: 默认为False, 是否计算累计比例
    :param isSimple: 默认为True, 透视表是否只提前简化字段，SKU/件数/体积
    :return:
    """
    if sku is None:
        sku = ['SKU_ID']

    if pt_col is None:
        if isSimple:
            col = ['daily_stock_qty', 'daily_stock_vol_m',
                   'daily_deli_qty', 'daily_deli_vol_m']
        else:
            col = ['daily_stock_sku', 'daily_stock_qty', 'daily_stock_vol_m', 'daily_stock_weight',
                   'daily_stock_pltN', 'daily_deli_sku', 'daily_deli_qty', 'daily_deli_vol_m']
        pt_col = col

    tmp1 = pd.pivot_table(df, index=index,
                          values=sku, aggfunc='count',
                          fill_value=0,
                          margins=True).reset_index()

    tmp2 = pd.pivot_table(df, index=index,
                          values=pt_col,
                          aggfunc='sum', fill_value=0,
                          margins=True).reset_index()

    result_pt = pd.merge(tmp1, tmp2, how='outer', sort=False)

    # 重排列
    result_pt = result_pt[index + sku + pt_col]

    index_num = len(index)
    cols = list(result_pt.columns[index_num:])

    # 更新合计值
    for i in range(len(pt_col)):
        result_pt.loc[result_pt[index[0]] == 'All', [pt_col[i]]] = df[pt_col[i]].sum()

    # 计算比例
    for i in range(len(cols)):
        result_pt[cols[i] + '%'] = round(result_pt[cols[i]] / (result_pt[cols[i]].sum() / 2), 4)

    # 判断是否计算累计比例，若计算，一般为件数及体积的累计比例
    if isCumu:
        for i in range(len(cols)):
            result_pt[cols[i] + '%_cumu'] = result_pt[cols[i] + '%'].cumsum().apply(lambda x: '%.2f%%' % (x * 100))
            result_pt.loc[(result_pt[index[0]] == 'All'), [cols[i] + '%_cumu']] = ''

    # 更新比例为百分数
    for i in range(len(cols)):
        result_pt[cols[i] + '%'] = result_pt[cols[i] + '%'].apply(lambda x: '%.2f%%' % (x * 100))

    # 计算件数周转天数
    if 'daily_deli_qty' in result_pt.columns:
        result_pt['qty_turnover_days'] = round(result_pt['daily_stock_qty'] / result_pt['daily_deli_qty'], 2)

    # 计算体积周转天数
    if 'daily_deli_vol_m' in result_pt.columns:
        result_pt['vol_turnover_days'] = round(result_pt['daily_stock_vol_m'] / result_pt['daily_deli_vol_m'], 2)

    if isAvg:
        # 计算字段
        if 'daily_stock_qty' in result_pt.columns and 'daily_stock_vol_m' in result_pt.columns:
            result_pt['avg_vol'] = result_pt['daily_stock_vol_m'] / result_pt['daily_stock_qty']
        if 'daily_stock_qty' in result_pt.columns and 'daily_stock_weight' in result_pt.columns:
            result_pt['avg_weight'] = result_pt['daily_stock_weight'] / result_pt['daily_stock_qty']
        if 'current_stockQty' in result_pt.columns and 'current_pickQty' in result_pt.columns and \
                'current_pltStockN' in result_pt.columns and 'current_pltPickN' in result_pt.columns:
            result_pt['avg_pltQty'] = (result_pt['current_stockQty'] + result_pt['current_pickQty']) / \
                                      (result_pt['current_pltStockN'] + result_pt['current_pltPickN'])
    # 更新透视列数据为千分位形式
    if 'VOL' in cols:
        result_pt['VOL'] = round(result_pt['VOL'], 2)
    result_pt[cols] = result_pt[cols].applymap(lambda x: '{:,}'.format(x))

    result_pt.columns = trans(result_pt.columns)
    return result_pt


def avg_pltQty_class(df, index, sku=None, pt_col=None, isCumu=True, isSimple=True):
    if sku is None:
        sku = ['SKU_ID']
    if pt_col is None:
        if isSimple:
            col = ['daily_stock_qty', 'daily_stock_vol_m',
                   'daily_deli_qty', 'daily_deli_vol_m']
        else:
            col = ['daily_stock_sku', 'daily_stock_qty', 'daily_stock_vol_m', 'daily_stock_weight',
                   'daily_stock_pltN', 'daily_deli_sku', 'daily_deli_qty', 'daily_deli_vol_m']
        pt_col = col

    tmp1 = pd.pivot_table(df, index=index,
                          values=sku, aggfunc='count',
                          fill_value=0,
                          margins=True).reset_index()

    tmp2 = pd.pivot_table(df, index=index,
                          values=['pltQty', 'fullCaseUnit'], aggfunc='mean',
                          fill_value=0,
                          margins=True, ).reset_index()

    tmp2.columns = [index, 'avg_pltQty', 'avg_ctnQty']
    print(tmp2)
    print('*' * 10)

    tmp3 = pd.pivot_table(df, index=index,
                          values='fullCaseUnit', aggfunc='mean',
                          fill_value=0,
                          margins=True).reset_index()
    tmp3.columns = [index, 'avg_ctnQty']
    print(tmp3)

    tmp4 = pd.pivot_table(df, index=index,
                          values=pt_col,
                          aggfunc='sum', fill_value=0,
                          margins=True).reset_index()

    result_pt1 = pd.merge(tmp1, tmp2, how='left', sort=False)
    result_pt2 = pd.merge(tmp3, tmp4, how='left', sort=False)
    result_pt = pd.merge(result_pt1, result_pt2, how='left', sort=False)

    # 重排列
    result_pt = result_pt[index + sku + ['avg_pltQty', 'avg_ctnQty'] + pt_col]

    # result_pt['SKU_ID%'] = round(result_pt['SKU_ID'] / (result_pt['SKU_ID'].sum() / 2), 4)

    index_num = len(index)
    cols = list(result_pt.columns[index_num:])
    # 计算比例
    for i in range(len(cols)):
        result_pt[cols[i] + '%'] = round(result_pt[cols[i]] / (result_pt[cols[i]].sum() / 2), 4)

    # 判断是否计算累计比例，若计算，一般为件数及体积的累计比例
    if isCumu:
        for i in range(len(cols)):
            result_pt[cols[i] + '%_cumu'] = result_pt[cols[i] + '%'].cumsum()
            result_pt.loc[(result_pt[index[0]] == 'All'), [cols[i] + '%_cumu']] = ''

    # 更新比例为百分数
    for i in range(len(cols)):
        result_pt[cols[i] + '%'] = result_pt[cols[i] + '%'].apply(lambda x: '%.2f%%' % (x * 100))

        # 计算件数周转天数
    if 'daily_deli_qty' in result_pt.columns:
        result_pt['qty_turnover_days'] = round(result_pt['daily_stock_qty'] / result_pt['daily_deli_qty'], 2)

        # 计算体积周转天数
    if 'daily_deli_vol_m' in result_pt.columns:
        result_pt['vol_turnover_days'] = round(result_pt['daily_stock_vol_m'] / result_pt['daily_deli_vol_m'], 2)

    # 更新透视列数据为千分位形式
    if 'VOL' in cols:
        result_pt['VOL'] = round(result_pt['VOL'], 2)
    result_pt[cols] = result_pt[cols].applymap(lambda x: '{:,}'.format(x))

    result_pt.columns = trans(result_pt.columns)
    return result_pt


def abc_class(df, index, sku=None, pt_col=None, isCumu=True, isSimple=True):
    if sku is None:
        sku = ['SKU_ID']
    if pt_col is None:
        if isSimple:
            col = ['daily_stock_qty', 'daily_stock_vol_m',
                   'daily_deli_qty', 'daily_deli_vol_m']
        else:
            col = ['daily_stock_sku', 'daily_stock_qty', 'daily_stock_vol_m', 'daily_stock_weight',
                   'daily_stock_pltN', 'daily_deli_sku', 'daily_deli_qty', 'daily_deli_vol_m']
        pt_col = col

    tmp1 = pd.pivot_table(df, index=index,
                          values=sku, aggfunc='count',
                          fill_value=0,
                          margins=True).reset_index()

    tmp2 = pd.pivot_table(df, index=index,
                          values=pt_col,
                          aggfunc='sum', fill_value=0,
                          margins=True).reset_index()

    result_pt = pd.merge(tmp1, tmp2, how='outer', sort=False)

    # 重排列
    result_pt = result_pt[index + sku + pt_col]

    # result_pt['SKU_ID%'] = round(result_pt['SKU_ID'] / (result_pt['SKU_ID'].sum() / 2), 4)

    index_num = len(index)
    cols = list(result_pt.columns[index_num:])
    # 计算比例
    for i in range(len(cols)):
        result_pt[cols[i] + '%'] = round(result_pt[cols[i]] / (result_pt[cols[i]].sum() / 2), 4)

    # 判断是否计算累计比例，若计算，一般为件数及体积的累计比例
    if isCumu:
        for i in range(len(cols)):
            result_pt[cols[i] + '%_cumu'] = result_pt[cols[i] + '%'].cumsum()
            result_pt.loc[(result_pt[index[0]] == 'All'), [cols[i] + '%_cumu']] = ''
    # 更新比例为百分数
    for i in range(len(cols)):
        result_pt[cols[i] + '%'] = result_pt[cols[i] + '%'].apply(lambda x: '%.2f%%' % (x * 100))

    # 计算件数周转天数
    if 'daily_deli_qty' in result_pt.columns:
        result_pt['qty_turnover_days'] = round(result_pt['daily_stock_qty'] / result_pt['daily_deli_qty'], 2)

    # 计算体积周转天数
    if 'daily_deli_vol_m' in result_pt.columns:
        result_pt['vol_turnover_days'] = round(result_pt['daily_stock_vol_m'] / result_pt['daily_deli_vol_m'], 2)

    # 更新透视列数据为千分位形式
    if 'VOL' in cols:
        result_pt['VOL'] = round(result_pt['VOL'], 2)
    result_pt[cols] = result_pt[cols].applymap(lambda x: '{:,}'.format(x))

    result_pt.columns = trans(result_pt.columns)
    return result_pt


def pc_class(df, index, sku=None, pt_col=None, isCumu=False, isSimple=True):
    if sku is None:
        sku = ['SKU_ID']

    if pt_col is None:
        if isSimple:
            col = ['daily_stock_qty', 'daily_stock_vol_m',
                   'daily_deli_qty', 'daily_deli_vol_m']
        else:
            col = ['daily_stock_sku', 'daily_stock_qty', 'daily_stock_vol_m', 'daily_stock_weight',
                   'daily_stock_pltN', 'daily_deli_sku', 'daily_deli_qty', 'daily_deli_vol_m']
        pt_col = col

    tmp1 = pd.pivot_table(df, index=index,
                          values=sku, aggfunc='count',
                          fill_value=0,
                          margins=True).reset_index()

    tmp2 = pd.pivot_table(df, index=index,
                          values=pt_col,
                          aggfunc='sum', fill_value=0,
                          margins=True).reset_index()

    result_pt = pd.merge(tmp1, tmp2, how='outer', sort=False)

    # 重排列
    result_pt = result_pt[index + sku + pt_col]

    ## PC class 不需更新合计值
    # # 更新合计值
    # for i in range(len(pt_col)):
    #     result_pt.loc[result_pt[index[0]] == 'All', [pt_col[i]]] = df[pt_col[i]].sum()

    index_num = len(index)
    cols = list(result_pt.columns[index_num:])
    # 计算比例
    for i in range(len(cols)):
        result_pt[cols[i] + '%'] = round(result_pt[cols[i]] / (result_pt[cols[i]].sum() / 2), 4)

    # 判断是否计算累计比例，若计算，一般为件数及体积的累计比例
    if isCumu:
        for i in range(len(cols)):
            result_pt[cols[i] + '%_cumu'] = result_pt[cols[i] + '%'].cumsum()
            result_pt.loc[(result_pt[index[0]] == 'All'), [cols[i] + '%_cumu']] = ''

    # 更新比例为百分数
    for i in range(len(cols)):
        result_pt[cols[i] + '%'] = result_pt[cols[i] + '%'].apply(lambda x: '%.2f%%' % (x * 100))

    # 计算件数周转天数
    if 'daily_deli_qty' in result_pt.columns:
        result_pt['qty_turnover_days'] = round(result_pt['daily_stock_qty'] / result_pt['daily_deli_qty'], 2)

    # 计算体积周转天数
    if 'daily_deli_vol_m' in result_pt.columns:
        result_pt['vol_turnover_days'] = round(result_pt['daily_stock_vol_m'] / result_pt['daily_deli_vol_m'], 2)

    # 更新透视列数据为千分位形式
    if 'VOL' in cols:
        result_pt['VOL'] = round(result_pt['VOL'], 2)
    result_pt[cols] = result_pt[cols].applymap(lambda x: '{:,}'.format(x))

    result_pt.columns = trans(result_pt.columns)
    return result_pt


def equ_class(df, class_index1, class_index2):
    equ_tmp1 = pd.pivot_table(df, index=[class_index1, class_index2],
                              values='SKU_ID', aggfunc='count',
                              fill_value=0,
                              margins=True).reset_index()

    equ_tmp2 = pd.pivot_table(df, index=[class_index1, class_index2],
                              values=['daily_stock_sku', 'current_shelfD300_num', 'current_shelfD500_num',
                                      'current_shelfD600_num', 'current_shuttle_num', 'current_pltPickN',
                                      'current_pltStockN'],
                              aggfunc='sum', fill_value=0,
                              margins=True).reset_index()

    result_pt = pd.merge(equ_tmp1, equ_tmp2, how='outer', sort=False)

    # 重排列
    result_pt = result_pt[
        [class_index1, class_index2, 'SKU_ID', 'daily_stock_sku',
         'current_shelfD300_num', 'current_shelfD500_num', 'current_shelfD600_num',
         'current_shuttle_num', 'current_pltPickN', 'current_pltStockN']]

    # 计算比例
    result_pt['SKU_ID%'] = round(
        result_pt['SKU_ID'] / (result_pt['SKU_ID'].sum() / 2), 2)
    result_pt['daily_stock_sku%'] = round(
        result_pt['daily_stock_sku'] / (result_pt['daily_stock_sku'].sum() / 2), 2)
    result_pt['current_shelfD300_num%'] = round(
        result_pt['current_shelfD300_num'] / (result_pt['current_shelfD300_num'].sum() / 2), 2)
    result_pt['current_shelfD500_num%'] = round(
        result_pt['current_shelfD500_num'] / (result_pt['current_shelfD500_num'].sum() / 2),
        6)
    result_pt['current_shelfD600_num%'] = round(
        result_pt['current_shelfD600_num'] / (result_pt['current_shelfD600_num'].sum() / 2), 2)
    result_pt['current_shuttle_num%'] = round(
        result_pt['current_shuttle_num'] / (result_pt['current_shuttle_num'].sum() / 2), 2)
    result_pt['current_pltPickN%'] = round(
        result_pt['current_pltPickN'] / (result_pt['current_pltPickN'].sum() / 2), 2)
    result_pt['current_pltStockN%'] = round(
        result_pt['current_pltStockN'] / (result_pt['current_pltStockN'].sum() / 2), 2)


def current_equ_class(df, index, sku=None, pt_col=None, isCumu=False):
    if sku is None:
        sku = ['SKU_ID']
    tmp1 = pd.pivot_table(df, index=index,
                          values='SKU_ID', aggfunc='count',
                          fill_value=0,
                          margins=True).reset_index()

    if pt_col is None:
        pt_col = ['daily_stock_sku', 'daily_stock_qty',
                  'current_shelfD300_num', 'current_shelfD500_num', 'current_shelfD600_num',
                  'current_shuttle_num',
                  'current_pltPickN', 'current_pltStockN', 'current_stockQty', 'current_pickQty',
                  'current_stockVol_m', 'current_pickVol_m']

    tmp2 = pd.pivot_table(df, index=index,
                          values=pt_col,
                          aggfunc='sum', fill_value=0,
                          margins=True).reset_index()

    result_pt = pd.merge(tmp1, tmp2, how='outer', sort=False)
    # 重排列
    result_pt = result_pt[index + sku + pt_col]

    index_num = len(index)
    cols = list(result_pt.columns[index_num:])
    # 计算比例
    for i in range(len(cols)):
        result_pt[cols[i] + '%'] = round(result_pt[cols[i]] / (result_pt[cols[i]].sum() / 2), 4)

    # 判断是否计算累计比例，若计算，一般为件数及体积的累计比例
    if isCumu:
        for i in range(len(cols)):
            result_pt[cols[i] + '%_cumu'] = result_pt[cols[i] + '%'].cumsum()
            result_pt.loc[(result_pt[index[0]] == 'All'), [cols[i] + '%_cumu']] = ''

    # 更新比例为百分数
    for i in range(len(cols)):
        result_pt[cols[i] + '%'] = result_pt[cols[i] + '%'].apply(lambda x: '%.2f%%' % (x * 100))

    # 更新透视列数据为千分位形式
    result_pt[cols] = result_pt[cols].applymap(lambda x: '{:,}'.format(x))

    result_pt.columns = trans(result_pt.columns)
    return result_pt


def design_equ_class(df, index, sku=None, pt_col=None, isCumu=False):
    if sku is None:
        sku = ['SKU_ID']

    tmp1 = pd.pivot_table(df, index=index,
                          values='SKU_ID', aggfunc='count',
                          fill_value=0,
                          margins=True).reset_index()

    if pt_col is None:
        pt_col = ['design_daily_stock_sku', 'design_daily_stock_qty',
                  'design_shelfD300_num', 'design_shelfD500_num', 'design_shelfD600_num',
                  'design_shuttle_num', 'design_pltStockN', 'design_pltPickN',
                  'design_stockQty', 'design_pickQty', 'design_stockVol_m', 'design_pickVol_m']

    tmp2 = pd.pivot_table(df, index=index,
                          values=pt_col,
                          aggfunc='sum', fill_value=0,
                          margins=True).reset_index()

    result_pt = pd.merge(tmp1, tmp2, how='outer', sort=False)
    # 重排列
    result_pt = result_pt[index + sku + pt_col]

    index_num = len(index)
    cols = list(result_pt.columns[index_num:])
    # 计算比例
    for i in range(len(cols)):
        result_pt[cols[i] + '%'] = round(result_pt[cols[i]] / (result_pt[cols[i]].sum() / 2), 4)

    # 判断是否计算累计比例，若计算，一般为件数及体积的累计比例
    if isCumu:
        for i in range(len(cols)):
            result_pt[cols[i] + '%_cumu'] = result_pt[cols[i] + '%'].cumsum()
            result_pt.loc[(result_pt[index[0]] == 'All'), [cols[i] + '%_cumu']] = ''

    # 更新比例为百分数
    for i in range(len(cols)):
        result_pt[cols[i] + '%'] = result_pt[cols[i] + '%'].apply(lambda x: '%.2f%%' % (x * 100))

    # 更新透视列数据为千分位形式
    result_pt[cols] = result_pt[cols].applymap(lambda x: '{:,}'.format(x))

    result_pt.columns = trans(result_pt.columns)
    return result_pt


def out_sku_pivot(df, index, sku=None, pt_col=None, isCumu=True):
    if sku is None:
        sku = ['SKU_ID']

    # SKU的非重复计数
    distCount_sku = df[index + sku].groupby(index).SKU_ID.nunique()
    df_disCount = (pd.DataFrame(distCount_sku)).reset_index()
    df_disCount = pd.pivot_table(df_disCount, index=index,
                                 aggfunc='sum',
                                 fill_value=0,
                                 margins=True).reset_index()
    df_disCount.columns = index + ['sku_distCount']

    if pt_col is None:
        pt_col = ['total_qty', 'VOL']

    tmp1 = pd.pivot_table(df, index=index,
                          values=sku, aggfunc='count',
                          fill_value=0,
                          margins=True).reset_index()
    tmp1.columns = index + ['line_count']

    tmp2 = pd.pivot_table(df, index=index,
                          values=pt_col,
                          aggfunc='sum', fill_value=0,
                          margins=True).reset_index()

    result_temp = pd.merge(tmp1, tmp2, how='left', sort=False)
    result_pt = pd.merge(df_disCount, result_temp, how='left', sort=False)

    # 重排列
    result_pt = result_pt[index + ['sku_distCount', 'line_count'] + pt_col]

    index_num = len(index)
    cols = list(result_pt.columns[index_num:])

    # 更新合计值
    for i in range(len(pt_col)):
        result_pt.loc[result_pt[index[0]] == 'All', [pt_col[i]]] = df[pt_col[i]].sum()

    # 计算比例
    for i in range(len(cols)):
        result_pt[cols[i] + '%'] = round(result_pt[cols[i]] / (result_pt[cols[i]].sum() / 2), 4)
        # result_pt[cols[i] + '%'] = result_pt[cols[i]] / (result_pt[cols[i]].sum() / 2)

    # 判断是否计算累计比例，若计算，一般为件数及体积的累计比例
    if isCumu:
        for i in range(len(cols)):
            result_pt[cols[i] + '%_cumu'] = result_pt[cols[i] + '%'].cumsum().apply(lambda x: '%.2f%%' % (x * 100))
            # result_pt[cols[i] + '%_cumu'] = result_pt[cols[i] + '%'].cumsum()
            result_pt.loc[(result_pt[index[0]] == 'All'), [cols[i] + '%_cumu']] = ''

    # 更新比例为百分数
    for i in range(len(cols)):
        result_pt[cols[i] + '%'] = result_pt[cols[i] + '%'].apply(lambda x: '%.2f%%' % (x * 100))

    result_pt['daily_deli_qty_perSKU'] = round(result_pt['total_qty'] / result_pt['sku_distCount'], 2).apply(
        lambda x: '{:,}'.format(x))
    result_pt['daily_deli_line_perSKU'] = round(result_pt['line_count'] / result_pt['sku_distCount'], 2).apply(
        lambda x: '{:,}'.format(x))
    if 'VOL' in result_pt.columns:
        result_pt['daily_deli_vol_perSKU'] = round(result_pt['VOL'] / result_pt['sku_distCount'], 2).apply(
            lambda x: '{:,}'.format(x))

    # result_pt['daily_deli_qty_perSKU'] = result_pt['total_qty'] / result_pt['sku_distCount']
    # result_pt['daily_deli_line_perSKU'] = result_pt['line_count'] / result_pt['sku_distCount']
    # if 'VOL' in result_pt.columns:
    #     result_pt['daily_deli_vol_perSKU'] = result_pt['VOL'] / result_pt['sku_distCount']

    # 更新透视列数据为千分位形式
    if 'VOL' in cols:
        result_pt['VOL'] = round(result_pt['VOL'], 2)
    result_pt[cols] = result_pt[cols].applymap(lambda x: '{:,}'.format(x))

    # result_pt.style.set_precision(2)
    # pct_cols = [x for x in list(result_pt.columns) if '%' in x ]
    # result_pt.style.format("{:.2%}", subset= pct_cols, na_rep='')

    result_pt.columns = trans(result_pt.columns)
    # result_pt = result_pt.style.set_properties(**{
    #     'font-size': '10pt',
    #     'bold': 'Microsoft YaHei UI Light'
    # })
    return result_pt


def out_order_pivot(df, index, order=None, pt_col=None, isCumu=True):
    if order is None:
        order = ['orderID']

    distCount_order = df[index + order].groupby(index).orderID.nunique()
    df_disCount = (pd.DataFrame(distCount_order)).reset_index()
    df_disCount = pd.pivot_table(df_disCount, index=index,
                                 aggfunc='sum',
                                 fill_value=0,
                                 margins=True).reset_index()
    df_disCount.columns = index + ['order_distCount']

    if pt_col is None:
        pt_col = ['total_qty', 'VOL']

    tmp1 = pd.pivot_table(df, index=index,
                          values=order, aggfunc='count',
                          fill_value=0,
                          margins=True).reset_index()
    tmp1.columns = index + ['line_count']

    tmp2 = pd.pivot_table(df, index=index,
                          values=pt_col,
                          aggfunc='sum', fill_value=0,
                          margins=True).reset_index()

    result_temp = pd.merge(tmp1, tmp2, how='left', sort=False)
    result_pt = pd.merge(df_disCount, result_temp, how='left', sort=False)

    # 重排列
    result_pt = result_pt[index + ['order_distCount', 'line_count'] + pt_col]

    index_num = len(index)
    cols = list(result_pt.columns[index_num:])

    # 更新合计值
    for i in range(len(pt_col)):
        result_pt.loc[result_pt[index[0]] == 'All', [pt_col[i]]] = df[pt_col[i]].sum()

    # 计算比例
    for i in range(len(cols)):
        result_pt[cols[i] + '%'] = round(result_pt[cols[i]] / (result_pt[cols[i]].sum() / 2), 4)

    # 判断是否计算累计比例，若计算，一般为件数及体积的累计比例
    if isCumu:
        for i in range(len(cols)):
            result_pt[cols[i] + '%_cumu'] = result_pt[cols[i] + '%'].cumsum().apply(lambda x: '%.2f%%' % (x * 100))
            result_pt.loc[(result_pt[index[0]] == 'All'), [cols[i] + '%_cumu']] = ''

    # 更新比例为百分数
    for i in range(len(cols)):
        result_pt[cols[i] + '%'] = result_pt[cols[i] + '%'].apply(lambda x: '%.2f%%' % (x * 100))

    result_pt['qty_per_order'] = round(result_pt['total_qty'] / result_pt['order_distCount'], 2)
    result_pt['line_per_order'] = round(result_pt['line_count'] / result_pt['order_distCount'], 2)
    result_pt['vol_per_order'] = round(result_pt['VOL'] / result_pt['order_distCount'], 2)

    # 更新透视列数据为千分位形式
    if 'VOL' in cols:
        result_pt['VOL'] = round(result_pt['VOL'], 2)
    result_pt[cols] = result_pt[cols].applymap(lambda x: '{:,}'.format(x))

    result_pt.columns = trans(result_pt.columns)
    return result_pt


def out_order_sku_pivot(df, index, order=None, sku=None, pt_col=None, isCumu=True):
    if order is None:
        order = ['orderID']
    distCount_order = df[index + order].groupby(index).orderID.nunique()
    df_disCount_order = (pd.DataFrame(distCount_order)).reset_index()
    df_disCount_order = pd.pivot_table(df_disCount_order, index=index,
                                       aggfunc='sum',
                                       fill_value=0,
                                       margins=True).reset_index()
    df_disCount_order.columns = index + ['order_distCount']

    if sku is None:
        sku = ['SKU_ID']
    # SKU的非重复计数
    distCount_sku = df[index + sku].groupby(index).SKU_ID.nunique()
    df_disCount_sku = (pd.DataFrame(distCount_sku)).reset_index()
    df_disCount_sku = pd.pivot_table(df_disCount_sku, index=index,
                                     aggfunc='sum',
                                     fill_value=0,
                                     margins=True).reset_index()
    df_disCount_sku.columns = index + ['sku_distCount']

    if pt_col is None:
        pt_col = ['total_qty', 'VOL']

    tmp1 = pd.pivot_table(df, index=index,
                          values=order, aggfunc='count',
                          fill_value=0,
                          margins=True).reset_index()
    tmp1.columns = index + ['line_count']

    tmp2 = pd.pivot_table(df, index=index,
                          values=pt_col,
                          aggfunc='sum', fill_value=0,
                          margins=True).reset_index()

    tmp3 = pd.merge(df_disCount_order, df_disCount_sku, how='outer', on=index, sort=False)

    result_temp = pd.merge(tmp1, tmp2, how='outer', sort=False)
    result_pt = pd.merge(tmp3, result_temp, how='outer', sort=False)

    # 重排列
    result_pt = result_pt[index + ['order_distCount', 'sku_distCount', 'line_count'] + pt_col]

    index_num = len(index)
    cols = list(result_pt.columns[index_num:])

    # 更新合计值
    for i in range(len(pt_col)):
        result_pt.loc[result_pt[index[0]] == 'All', [pt_col[i]]] = df[pt_col[i]].sum()

    # 计算比例
    for i in range(len(cols)):
        result_pt[cols[i] + '%'] = round(result_pt[cols[i]] / (result_pt[cols[i]].sum() / 2), 4)

    # 判断是否计算累计比例，若计算，一般为件数及体积的累计比例
    if isCumu:
        for i in range(len(cols)):
            result_pt[cols[i] + '%_cumu'] = result_pt[cols[i] + '%'].cumsum()
            result_pt.loc[(result_pt[index[0]] == 'All'), [cols[i] + '%_cumu']] = ''

    # 更新比例为百分数
    for i in range(len(cols)):
        result_pt[cols[i] + '%'] = result_pt[cols[i] + '%'].apply(lambda x: '%.2f%%' % (x * 100))

    result_pt['qty_per_order'] = round(result_pt['total_qty'] / result_pt['order_distCount'], 2)
    result_pt['line_per_order'] = round(result_pt['line_count'] / result_pt['order_distCount'], 2)
    if 'VOL' in result_pt.columns:
        result_pt['daily_deli_vol_perSKU'] = round(result_pt['VOL'] / result_pt['sku_distCount'], 2)

    # 更新透视列数据为千分位形式
    if 'VOL' in cols:
        result_pt['VOL'] = round(result_pt['VOL'], 2)
    result_pt[cols] = result_pt[cols].applymap(lambda x: '{:,}'.format(x))

    result_pt.columns = trans(result_pt.columns)
    return result_pt


def out_sku_qty_pivot(df, index, sku=None, pt_col=None, isCumu=False):
    if sku is None:
        sku = ['SKU_ID']
    # SKU的非重复计数
    distCount_sku = df[index + sku].groupby(index).SKU_ID.nunique()
    df_disCount_sku = (pd.DataFrame(distCount_sku)).reset_index()
    df_disCount_sku = pd.pivot_table(df_disCount_sku, index=index,
                                     aggfunc='sum',
                                     fill_value=0,
                                     margins=True).reset_index()
    df_disCount_sku.columns = index + ['sku_distCount']

    if pt_col is None:
        pt_col = ['pltN', 'ctnN', 'piece2ctn', 'pltQ', 'ctnQ', 'pieceQ', 'total_qty', 'VOL']

    tmp1 = pd.pivot_table(df, index=index,
                          values=sku, aggfunc='count',
                          fill_value=0,
                          margins=True).reset_index()
    tmp1.columns = index + ['line_count']

    tmp2 = pd.pivot_table(df, index=index,
                          values=pt_col,
                          aggfunc='sum', fill_value=0,
                          margins=True).reset_index()

    result_temp = pd.merge(tmp1, tmp2, how='outer', sort=False)
    result_pt = pd.merge(df_disCount_sku, result_temp, how='outer', sort=False)

    # 重排列
    result_pt = result_pt[index + ['sku_distCount', 'line_count'] + pt_col]

    index_num = len(index)
    cols = list(result_pt.columns[index_num:])

    # 更新合计值
    for i in range(len(pt_col)):
        result_pt.loc[result_pt[index[0]] == 'All', [pt_col[i]]] = df[pt_col[i]].sum()

    # 计算整托数、整箱数、散件数占总件数的比例
    h_pct_cols = pt_col[3:6]
    for item in h_pct_cols:
        result_pt[item + '/total_qty'] = result_pt[item] / result_pt['total_qty']

    # 计算比例
    for i in range(len(cols)):
        result_pt[cols[i] + '%'] = round(result_pt[cols[i]] / (result_pt[cols[i]].sum() / 2), 4)

    # 判断是否计算累计比例，若计算，一般为件数及体积的累计比例
    if isCumu:
        for i in range(len(cols)):
            result_pt[cols[i] + '%_cumu'] = result_pt[cols[i] + '%'].cumsum()
            result_pt.loc[(result_pt[index[0]] == 'All'), [cols[i] + '%_cumu']] = ''

    # 更新比例为百分数
    for i in range(len(cols)):
        result_pt[cols[i] + '%'] = result_pt[cols[i] + '%'].apply(lambda x: '%.2f%%' % (x * 100))

    result_pt['daily_deli_qty_perSKU'] = result_pt['total_qty'] / result_pt['sku_distCount']
    result_pt['daily_deli_line_perSKU'] = result_pt['line_count'] / result_pt['sku_distCount']
    if 'VOL' in result_pt.columns:
        result_pt['daily_deli_vol_perSKU'] = result_pt['VOL'] / result_pt['sku_distCount']

    # 更新透视列数据为千分位形式
    if 'VOL' in cols:
        result_pt['VOL'] = round(result_pt['VOL'], 2)
    result_pt[cols] = result_pt[cols].applymap(lambda x: '{:,}'.format(x))

    result_pt.columns = trans(result_pt.columns)
    return result_pt


def out_order_qty_pivot(df, index, order=None, sku=None, pt_col=None, isCumu=False):
    if order is None:
        order = ['orderID']
    distCount_order = df[index + order].groupby(index).orderID.nunique()
    df_disCount_order = (pd.DataFrame(distCount_order)).reset_index()
    df_disCount_order = pd.pivot_table(df_disCount_order, index=index,
                                       aggfunc='sum',
                                       fill_value=0,
                                       margins=True).reset_index()
    df_disCount_order.columns = index + ['order_distCount']

    if sku is None:
        sku = ['SKU_ID']
    # SKU的非重复计数
    distCount_sku = df[index + sku].groupby(index).SKU_ID.nunique()
    df_disCount_sku = (pd.DataFrame(distCount_sku)).reset_index()
    df_disCount_sku = pd.pivot_table(df_disCount_sku, index=index,
                                     aggfunc='sum',
                                     fill_value=0,
                                     margins=True).reset_index()
    df_disCount_sku.columns = index + ['sku_distCount']

    if pt_col is None:
        pt_col = ['pltN', 'ctnN', 'piece2ctn', 'pltQ', 'ctnQ', 'pieceQ', 'total_qty', 'VOL']

    tmp1 = pd.pivot_table(df, index=index,
                          values=order, aggfunc='count',
                          fill_value=0,
                          margins=True).reset_index()
    tmp1.columns = index + ['line_count']

    tmp2 = pd.pivot_table(df, index=index,
                          values=pt_col,
                          aggfunc='sum', fill_value=0,
                          margins=True).reset_index()

    tmp3 = pd.merge(df_disCount_order, df_disCount_sku, how='outer', on=index, sort=False)

    result_temp = pd.merge(tmp1, tmp2, how='outer', sort=False)
    result_pt = pd.merge(tmp3, result_temp, how='outer', sort=False)

    # 重排列
    result_pt = result_pt[index + ['order_distCount', 'sku_distCount', 'line_count'] + pt_col]

    index_num = len(index)
    cols = list(result_pt.columns[index_num:])

    # 更新合计值
    for i in range(len(pt_col)):
        result_pt.loc[result_pt[index[0]] == 'All', [pt_col[i]]] = df[pt_col[i]].sum()

    # 计算整托数、整箱数、散件数占总件数的比例
    h_pct_cols = pt_col[3:6]
    for item in h_pct_cols:
        result_pt[item + '/total_qty'] = result_pt[item] / result_pt['total_qty']

    # 计算比例
    for i in range(len(cols)):
        result_pt[cols[i] + '%'] = round(result_pt[cols[i]] / (result_pt[cols[i]].sum() / 2), 4)

    # 判断是否计算累计比例，若计算，一般为件数及体积的累计比例
    if isCumu:
        for i in range(len(cols)):
            result_pt[cols[i] + '%_cumu'] = result_pt[cols[i] + '%'].cumsum()
            result_pt.loc[(result_pt[index[0]] == 'All'), [cols[i] + '%_cumu']] = ''

    # 更新比例为百分数
    for i in range(len(cols)):
        result_pt[cols[i] + '%'] = result_pt[cols[i] + '%'].apply(lambda x: '%.2f%%' % (x * 100))

    result_pt['qty_per_order'] = round(result_pt['total_qty'] / result_pt['order_distCount'], 2)
    result_pt['line_per_order'] = round(result_pt['line_count'] / result_pt['order_distCount'], 2)
    if 'VOL' in result_pt.columns:
        result_pt['daily_deli_vol_perSKU'] = round(result_pt['VOL'] / result_pt['sku_distCount'], 2)

    # 更新透视列数据为千分位形式
    if 'VOL' in cols:
        result_pt['VOL'] = round(result_pt['VOL'], 2)
    result_pt[cols] = result_pt[cols].applymap(lambda x: '{:,}'.format(x))

    result_pt.columns = trans(result_pt.columns)
    return result_pt


def trans(columns):
    if len(columns) > 0:
        new_col = []
        for col in columns:
            # 库存分析字段翻译
            col = col.replace('daily', '日均')
            col = col.replace('stock', '库存')
            col = col.replace('deli', '出库')
            col = col.replace('rec', '入库')
            col = col.replace('class', '分级')
            col = col.replace('current', '现状')
            col = col.replace('design', '规划')
            col = col.replace('pick', '拣选')
            col = col.replace('equiSize', '设备规格')
            col = col.replace('shelf', '轻架')
            col = col.replace('shuttle', '多穿')
            col = col.replace('num', '数量')
            col = col.replace('equi', '设备')
            col = col.replace('mode', '模式')
            col = col.replace('pltStockN', '存储托盘数量')
            col = col.replace('pltPickN', '拣选托盘数量')
            col = col.replace('stockQty', '存储区件数')
            col = col.replace('pickQty', '拣选区件数')
            col = col.replace('palletized', '_成托')
            col = col.replace('weight', '重量')
            col = col.replace('turnover', '周转')
            col = col.replace('days', '天数')
            col = col.replace('avg', '平均')
            col = col.replace('plt', '托盘')
            col = col.replace('tote', '料箱')
            col = col.replace('Wt', '重量')
            col = col.replace('N', '数量')
            col = col.replace('Q', '件数')
            col = col.replace('ctn', '原箱')
            col = col.replace('piece', '散件')
            col = col.replace('total', '总')
            col = col.replace('skuClassInOrder', '订单内sku分级')

            # 出库透视表字段翻译
            col = col.replace('SKU_ID', 'SKU数')
            col = col.replace('orderID', '订单数')
            col = col.replace('order', '订单')
            col = col.replace('_', '')
            col = col.replace('qty', '件数')
            col = col.replace('Qty', '件数')
            col = col.replace('vol', '体积')
            col = col.replace('Vol', '体积')
            col = col.replace('VOL', '体积')
            col = col.replace('size', '件型')
            col = col.replace('line', '行')
            col = col.replace('rele', '关联')
            col = col.replace('structure', '结构')
            col = col.replace('distCount', '非重复计数')
            col = col.replace('count', '数')
            col = col.replace('cumu', '累计')
            col = col.replace('per', '/')

            new_col.append(col)

    return new_col
