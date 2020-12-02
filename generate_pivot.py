# -*- coding: utf-8 -*-

from stock_model import *


def generate_pivot_table(df, outFileName):
    """
    according to the calculated dataframe, generate several pivot tables and write to excel file
    :param df: calculated dataframe, 176 valid columns totally
    :param outFileName: the file name written in
    """
    # 加载config参数
    config = Config()
    config.run()

    time = datetime.now()
    str_time = time.strftime('%Y_%m_%d_%H_%M')
    writer = pd.ExcelWriter('{}stockClass2_{}.xlsx'.format(outFileName, str_time))
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
    palletPick_factor.to_excel(excel_writer=writer, sheet_name='01-palletPick_factor', inf_rep='')
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

    palletStock_factor['ctn_factor'] = palletStock_factor['current_stockCtnVol'] * pow(10, 9) / (
            palletStock_factor['current_pltStockN'] *
            config.PALLET_STOCK['valid_vol'] / config.PALLET_STOCK['rate'])

    palletStock_factor['vol_factor'] = palletStock_factor['current_stockVol_m'] * pow(10, 9) / (
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
    pt_col_com = ['daily_stock_sku', 'daily_stock_qty', 'daily_stock_pltN', 'daily_stock_ctnN',
                  'daily_stock_vol_m','daily_stock_weight',
                  'daily_deli_sku', 'daily_deli_qty', 'daily_deli_pltN', 'daily_deli_ctnN',
                  'daily_deli_vol_m',
                  'current_pltStockN', 'current_pltPickN',
                  'current_stockQty', 'current_pickQty']
    size = general_class(df, sku=sku, index=idx12, pt_col=pt_col_com, isAvg=True)
    size.to_excel(excel_writer=writer, sheet_name='12-size', inf_rep='')

    # 件型关联
    idx13 = ['ctn_size','size']
    size = general_class(df, sku=sku, index=idx13, pt_col=pt_col_com, isAvg=True)
    size.to_excel(excel_writer=writer, sheet_name='13-size_rele', inf_rep='')

    '''
    # 113透视_CLASS1_O1
    '''
    # class_df = df.loc[(df['stock_qty_isNonZero'] == 'Y'),
    #                   ['SKU_ID', 'size', 'I_class', 'II_class', 'III_class', 'IV_class',
    #                    'daily_stock_sku', 'daily_stock_qty', 'daily_stock_vol_m',
    #                    'daily_stock_weight', 'daily_stock_pltN', 'daily_deli_sku', 'daily_deli_qty',
    #                    'daily_deli_vol_m', 'current_pltStockN', 'current_pltPickN',
    #                    'current_stockQty', 'current_pickQty']]
    # idx13 = ['IV_class']
    # class_pt = general_class(class_df, sku=sku, index=idx13, pt_col=pt_col_com, isAvg=True)
    # class_pt.to_excel(excel_writer=writer, sheet_name='13-class_pt', inf_rep='')

    plt_col = ['daily_stock_sku', 'daily_stock_qty', 'daily_deli_qty',
               'current_pltStockN', 'current_pltPickN',
               'current_stockQty', 'current_pickQty']

    idx14 = ['IV_class']

    # class_pt = avg_pltQty_class(df, index=idx14, pt_col=plt_col)
    # class_pt.to_excel(excel_writer=writer, sheet_name='class_pt', inf_rep='')

    '''
    114透视_Size&Class1_O1
    '''
    idx14 = ['size', 'IV_class']
    size_class_pt = general_class(df, sku=sku, index=idx14, pt_col=pt_col_com)
    size_class_pt.to_excel(excel_writer=writer, sheet_name='14-size_class_pt', inf_rep='')

    '''
    115透视_WarehouseType_O1  warehouse_pt
    '''
    idx15 = ['warehouse']
    warehouse_pt = general_class(df, sku=sku, index=idx15, pt_col=pt_col_com)
    warehouse_pt.to_excel(excel_writer=writer, sheet_name='15-warehouse_pt', inf_rep='')

    ### 类别均值
    class_avg = pd.pivot_table(df, index=idx14,
                               values=['pltQty', 'fullCaseUnit'], aggfunc='mean',
                               fill_value=0,
                               margins=True).reset_index()
    class_avg.to_excel(excel_writer=writer, sheet_name='16-class_avg', inf_rep='')

    # idx16 = ['IV_class']
    # avg_pltQty = avg_pltQty_class(df, sku=sku, index=idx16)
    # avg_pltQty.to_excel(excel_writer=writer, sheet_name='16-avg_pltQty', inf_rep='')

    # ---------------------------------------------------------------------------------
    '''
    分级相关字段透视表
    '''
    '''
    121透视_PalletW-V-Pallet_O1 托盘重量分级透视表-成托
    '''
    # palletWt_class_df = df.loc[(df['sku_state'] == '良品'),
    #                            ['SKU_ID', 'pltWt_class_palletized', 'pltWt_class_all',
    #                             'daily_stock_sku', 'daily_stock_qty', 'daily_stock_vol_m', 'daily_stock_weight',
    #                             'daily_stock_pltN', 'daily_deli_sku', 'daily_deli_qty','daily_deli_pltN', 'daily_deli_vol_m', ]]

    idx21 = ['pltWt_class_palletized']
    pltWt_class_palletized = general_class(df, sku=sku, index=idx21, isCumu=True)
    pltWt_class_palletized.to_excel(excel_writer=writer, sheet_name='21-pltWt_class_palletized', inf_rep='')

    # 122透视_PalletW-V-Pallet_O1 托盘重量分级透视表-成托&不成托
    idx22 = ['pltWt_class_all']
    pltWt_class_all = general_class(df, sku=sku, index=idx22, isCumu=True)
    pltWt_class_all.to_excel(excel_writer=writer, sheet_name='22-pltWt_class_all', inf_rep='')

    idx23 = ['vol_pltWt_class']
    pltWt_class_all = general_class(df, sku=sku, index=idx23, isCumu=True)
    pltWt_class_all.to_excel(excel_writer=writer, sheet_name='23-vol_pltWt_class', inf_rep='')

    '''
    123 料箱重量分级 
    '''
    toteWt_class_df = df.loc[(df['sku_state'] == '良品'),
                             ['SKU_ID', 'toteWt_class', 'vol_toteWt_class',
                              'daily_stock_sku', 'daily_stock_qty', 'daily_stock_vol_m', 'daily_stock_weight',
                              'daily_stock_pltN', 'daily_deli_sku', 'daily_deli_qty', 'daily_deli_pltN',
                              'daily_deli_vol_m']]
    idx24 = ['toteWt_class']
    toteWt_class = general_class(toteWt_class_df, sku=sku, index=idx24, isCumu=True)
    toteWt_class.to_excel(excel_writer=writer, sheet_name='24-toteWt_class', inf_rep='')

    idx25 = ['vol_toteWt_class']
    toteWt_class = general_class(toteWt_class_df, sku=sku, index=idx25, isCumu=True)
    toteWt_class.to_excel(excel_writer=writer, sheet_name='25-vol_toteWt_class', inf_rep='')

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
    stock_PC_class = pc_class(df, index=idx40, pt_col=col, isCumu=True)
    stock_PC_class.to_excel(excel_writer=writer, sheet_name='40-daily_stock_ctnQty_class', inf_rep='')

    # 141透视_P&C-CLASS-V&W_O1
    idx41 = ['daily_stock_PC_class']
    # col = ['daily_stock_pltN', 'daily_stock_toteN', 'daily_stock_qty', 'daily_deli_sku',
    #        'daily_deli_pltN', 'daily_deli_toteN', 'daily_deli_qty']
    stock_PC_class = pc_class(df, index=idx41, pt_col=col, isCumu=True)
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
                     'daily_deli_qty', 'daily_deli_pltN', 'daily_deli_vol_m',
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

    layout_format(writer)

    # 保存文件
    writer.save()
    writer.close()


def get_stock_factor(df, config, writer):
    plt_long = config.PALLET_STOCK['long']
    plt_width = config.PALLET_STOCK['width']

    # d1 = pd.DataFrame.from_dict(config.PALLET_STOCK, orient='index', columns=['PALLET_STOCK']).reset_index()
    # d2 = pd.DataFrame.from_dict(config.PALLET_PICK, orient='index', columns=['PALLET_PICK']).reset_index()
    #
    # d = pd.merge(d1, d2, on='index', how='outer')
    # d.to_excel(excel_writer=writer, sheet_name='0-basic', inf_rep='')

    ### 存储位托盘系数
    palletStock_factor = pd.pivot_table(df, index='warehouse',
                                        values=['current_pltStockN', 'current_stockVol_m', 'current_stockCtnVol'],
                                        aggfunc=np.sum, fill_value=0).reset_index()

    palletStock_factor['ctn_factor'] = palletStock_factor['current_stockCtnVol'] * pow(10, 9) / (
            palletStock_factor['current_pltStockN'] *
            config.PALLET_STOCK['valid_vol'] / config.PALLET_STOCK['rate'])

    palletStock_factor['vol_factor'] = palletStock_factor['current_stockVol_m'] * pow(10, 9) / (
            palletStock_factor['current_pltStockN'] *
            config.PALLET_STOCK['valid_vol'] / config.PALLET_STOCK['rate'])
    # palletStock_factor.to_excel(excel_writer=writer,
    #                             sheet_name='stock_factor_{}_{}'.format(plt_long, plt_width),
    #                             inf_rep='')
    format_data(writer, df=palletStock_factor, sheet_name='stock_factor_{}_{}'.format(plt_long, plt_width),
                index=['warehouse'])

    ### 拣选位托盘系数
    palletPick_factor = pd.pivot_table(df, index='warehouse', values=['current_pltPickN', 'current_pickVol_m'],
                                       aggfunc=np.sum, fill_value=0).reset_index()

    palletPick_factor['factor'] = palletPick_factor['current_pickVol_m'] * pow(10, 9) / (
            palletPick_factor['current_pltPickN'] *
            config.PALLET_STOCK['valid_vol'] / config.PALLET_STOCK['rate'])

    # write to file
    # palletPick_factor.to_excel(excel_writer=writer,
    #                            sheet_name='pick_factor_{}_{}'.format(plt_long, plt_width),
    #                            inf_rep='')

    format_data(writer, df=palletPick_factor, sheet_name='pick_factor_{}_{}'.format(plt_long, plt_width),
                index=['warehouse'])


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
            col = ['daily_stock_qty', 'daily_stock_pltN', 'daily_stock_vol_m',
                   'daily_deli_qty', 'daily_deli_pltN', 'daily_deli_vol_m']
        else:
            col = ['daily_stock_sku', 'daily_stock_qty', 'daily_stock_pltN', 'daily_stock_ctnN',
                   'daily_stock_vol_m',
                   'daily_deli_sku', 'daily_deli_qty', 'daily_deli_pltN', 'daily_deli_vol_m']
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
        result_pt[cols[i] + '%'] = result_pt[cols[i]] / (result_pt[cols[i]].sum() / 2)

    # 判断是否计算累计比例，若计算，一般为件数及体积的累计比例
    if isCumu:
        for i in range(len(cols)):
            # result_pt[cols[i] + '%_cumu'] = result_pt[cols[i] + '%'].cumsum().apply(lambda x: '%.2f%%' % (x * 100))
            result_pt[cols[i] + '%_cumu'] = result_pt[cols[i] + '%'].cumsum()

    # # 更新比例为百分数
    # for i in range(len(cols)):
    #     result_pt[cols[i] + '%'] = result_pt[cols[i] + '%'].apply(lambda x: '%.2f%%' % (x * 100))

    # 计算件数周转天数
    if 'daily_deli_qty' in result_pt.columns:
        result_pt['qty_turnover_days'] = round(result_pt['daily_stock_qty'] / result_pt['daily_deli_qty'], 4)

    # 计算体积周转天数
    if 'daily_deli_vol_m' in result_pt.columns:
        result_pt['vol_turnover_days'] = result_pt['daily_stock_vol_m'] / result_pt['daily_deli_vol_m']

    if isAvg:
        # 计算字段
        if 'daily_stock_qty' in result_pt.columns and 'daily_stock_vol_m' in result_pt.columns:
            result_pt['avg_vol'] = result_pt['daily_stock_vol_m'] / result_pt['daily_stock_qty']
        if 'daily_stock_qty' in result_pt.columns and 'daily_stock_weight' in result_pt.columns:
            result_pt['avg_weight'] = result_pt['daily_stock_weight'] / result_pt['daily_stock_qty']
        result_pt['kg/m3'] = result_pt['avg_weight'] / result_pt['avg_vol']
        if 'current_stockQty' in result_pt.columns and 'current_pickQty' in result_pt.columns and \
                'current_pltStockN' in result_pt.columns and 'current_pltPickN' in result_pt.columns:
            result_pt['avg_pltQty'] = (result_pt['current_stockQty'] + result_pt['current_pickQty']) / \
                                      (result_pt['current_pltStockN'] + result_pt['current_pltPickN'])
    # # 更新透视列数据为千分位形式
    # if 'VOL' in cols:
    #     result_pt['VOL'] = round(result_pt['VOL'], 2)
    # result_pt[cols] = result_pt[cols].applymap(lambda x: '{:,}'.format(x))

    cols = list(result_pt.columns[index_num:])
    result_pt = data_format(result_pt, cols)
    result_pt.columns = trans(result_pt.columns)
    result_pt.index = range(1, len(result_pt) + 1)
    result_pt.index.name = '序号'
    return result_pt


def avg_pltQty_class(df, index, sku=None):
    if sku is None:
        sku = ['SKU_ID']

    tmp1 = pd.pivot_table(df, index=index,
                          values=sku, aggfunc='count',
                          fill_value=0,
                          margins=True).reset_index()

    tmp2 = pd.pivot_table(df, index=index,
                          values=['pltQty', 'fullCaseUnit'], aggfunc='mean',
                          fill_value=0,
                          margins=True).reset_index()

    tmp2.columns = [index, 'avg_pltQty', 'avg_ctnQty']

    # result_pt = pd.merge(tmp1, tmp2, how='outer', sort=False)
    #
    # # 重排列
    # result_pt = result_pt[index + sku + ['avg_pltQty', 'avg_ctnQty'] ]

    # result_pt['SKU_ID%'] = round(result_pt['SKU_ID'] / (result_pt['SKU_ID'].sum() / 2), 4)

    result_pt = tmp2

    index_num = len(index)
    cols = list(result_pt.columns[index_num:])

    # 格式化列
    for i in cols:
        result_pt[i] = pd.to_numeric(result_pt[i]).round(0).astype(int).apply(
            lambda x: '{:,}'.format(x))

    result_pt.columns = trans(result_pt.columns)
    result_pt.index = range(1, len(result_pt) + 1)
    result_pt.index.name = '序号'
    return result_pt


def abc_class(df, index, sku=None, pt_col=None, isCumu=True, isSimple=True):
    if sku is None:
        sku = ['SKU_ID']
    if pt_col is None:
        if isSimple:
            col = ['daily_stock_qty', 'daily_stock_pltN', 'daily_stock_vol_m',
                   'daily_deli_qty', 'daily_deli_pltN', 'daily_deli_vol_m']
        else:
            col = ['daily_stock_sku', 'daily_stock_qty', 'daily_stock_pltN', 'daily_stock_vol_m',
                   'daily_deli_sku', 'daily_deli_qty', 'daily_deli_pltN', 'daily_deli_vol_m']
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
            # result_pt.loc[(result_pt[index[0]] == 'All'), [cols[i] + '%_cumu']] = ''

    # 计算件数周转天数
    if 'daily_deli_qty' in result_pt.columns:
        result_pt['qty_turnover_days'] = round(result_pt['daily_stock_qty'] / result_pt['daily_deli_qty'], 4)

    # 计算体积周转天数
    if 'daily_deli_vol_m' in result_pt.columns:
        result_pt['vol_turnover_days'] = round(result_pt['daily_stock_vol_m'] / result_pt['daily_deli_vol_m'], 4)

    cols = list(result_pt.columns[index_num:])
    result_pt = data_format(result_pt, cols)
    result_pt.columns = trans(result_pt.columns)
    result_pt.index = range(1, len(result_pt) + 1)
    result_pt.index.name = '序号'
    return result_pt


def pc_class(df, index, sku=None, pt_col=None, isCumu=False, isSimple=True):
    if sku is None:
        sku = ['SKU_ID']

    if pt_col is None:
        if isSimple:
            col = ['daily_stock_qty', 'daily_stock_pltN', 'daily_stock_vol_m',
                   'daily_deli_qty', 'daily_deli_pltN', 'daily_deli_vol_m']
        else:
            col = ['daily_stock_sku', 'daily_stock_qty', 'daily_stock_pltN', 'daily_stock_vol_m',
                   'daily_deli_sku', 'daily_deli_qty', 'daily_deli_pltN', 'daily_deli_vol_m']
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
            # result_pt.loc[(result_pt[index[0]] == 'All'), [cols[i] + '%_cumu']] = ''

    # 计算件数周转天数
    if 'daily_deli_qty' in result_pt.columns:
        result_pt['qty_turnover_days'] = round(result_pt['daily_stock_qty'] / result_pt['daily_deli_qty'], 4)

    # 计算体积周转天数
    if 'daily_deli_vol_m' in result_pt.columns:
        result_pt['vol_turnover_days'] = round(result_pt['daily_stock_vol_m'] / result_pt['daily_deli_vol_m'], 4)

    cols = list(result_pt.columns[index_num:])
    result_pt = data_format(result_pt, cols)
    result_pt.columns = trans(result_pt.columns)
    result_pt.index = range(1, len(result_pt) + 1)
    result_pt.index.name = '序号'
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
    result_pt['SKU_ID%'] = result_pt['SKU_ID'] / (result_pt['SKU_ID'].sum() / 2)
    result_pt['daily_stock_sku%'] = result_pt['daily_stock_sku'] / (
            result_pt['daily_stock_sku'].sum() / 2)
    result_pt['current_shelfD300_num%'] = result_pt['current_shelfD300_num'] / (
            result_pt['current_shelfD300_num'].sum() / 2)
    result_pt['current_shelfD500_num%'] = result_pt['current_shelfD500_num'] / (
            result_pt['current_shelfD500_num'].sum() / 2)
    result_pt['current_shelfD600_num%'] = result_pt['current_shelfD600_num'] / (
            result_pt['current_shelfD600_num'].sum() / 2)
    result_pt['current_shuttle_num%'] = result_pt['current_shuttle_num'] / (
            result_pt['current_shuttle_num'].sum() / 2)
    result_pt['current_pltPickN%'] = result_pt['current_pltPickN'] / \
                                     (result_pt['current_pltPickN'].sum() / 2)
    result_pt['current_pltStockN%'] = result_pt['current_pltStockN'] /(result_pt['current_pltStockN'].sum() / 2)


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

    cols = list(result_pt.columns[index_num:])
    result_pt = data_format(result_pt, cols)
    result_pt.columns = trans(result_pt.columns)
    result_pt.index = range(1, len(result_pt) + 1)
    result_pt.index.name = '序号'
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

    cols = list(result_pt.columns[index_num:])
    result_pt = data_format(result_pt, cols)
    result_pt.columns = trans(result_pt.columns)
    result_pt.index = range(1, len(result_pt) + 1)
    result_pt.index.name = '序号'
    return result_pt


def out_sku_pivot(df, index, sku=None, pt_col=None, isCumu=True):
    if sku is None:
        sku = ['SKU_ID']

    # SKU的非重复计数
    dist_count_sku = df[index + sku].groupby(index).SKU_ID.nunique()
    df_disCount = (pd.DataFrame(dist_count_sku)).reset_index()
    df_disCount = pd.pivot_table(df_disCount, index=index,
                                 aggfunc='sum',
                                 fill_value=0,
                                 margins=True).reset_index()
    df_disCount.columns = index + ['sku_dist_count']

    if pt_col is None:
        pt_col = ['total_qty', 'total_qty2pltN', 'total_qty2ctnN', 'VOL']

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
    result_pt = result_pt[index + ['sku_dist_count', 'line_count'] + pt_col]

    index_num = len(index)
    cols = list(result_pt.columns[index_num:])

    # 更新合计值
    for i in range(len(pt_col)):
        result_pt.loc[result_pt[index[0]] == 'All', [pt_col[i]]] = df[pt_col[i]].sum()

    # 计算比例
    for i in range(len(cols)):
        # result_pt[cols[i] + '%'] = round(result_pt[cols[i]] / (result_pt[cols[i]].sum() / 2), 4)
        result_pt[cols[i] + '%'] = result_pt[cols[i]] / (result_pt[cols[i]].sum() / 2)

    # 判断是否计算累计比例，若计算，一般为件数及体积的累计比例
    if isCumu:
        for i in range(len(cols)):
            # result_pt[cols[i] + '%_cumu'] = result_pt[cols[i] + '%'].cumsum().apply(lambda x: '%.2f%%' % (x * 100))
            result_pt[cols[i] + '%_cumu'] = result_pt[cols[i] + '%'].cumsum()
            # result_pt.loc[(result_pt[index[0]] == 'All'), [cols[i] + '%_cumu']] = ''

    # # 更新比例为百分数
    # for i in range(len(cols)):
    #     result_pt[cols[i] + '%'] = result_pt[cols[i] + '%'].apply(lambda x: '%.2f%%' % (x * 100))

    # result_pt['daily_deli_qty_perSKU'] = round(result_pt['total_qty'] / result_pt['sku_dist_count'], 2).apply(
    #     lambda x: '{:,}'.format(x))
    # result_pt['daily_deli_line_perSKU'] = round(result_pt['line_count'] / result_pt['sku_dist_count'], 2).apply(
    #     lambda x: '{:,}'.format(x))
    # if 'VOL' in result_pt.columns:
    #     result_pt['daily_deli_vol_perSKU'] = round(result_pt['VOL'] / result_pt['sku_dist_count'], 2).apply(
    #         lambda x: '{:,}'.format(x))

    result_pt['daily_deli_qty_perSKU'] = result_pt['total_qty'] / result_pt['sku_dist_count']
    result_pt['daily_deli_line_perSKU'] = result_pt['line_count'] / result_pt['sku_dist_count']
    if 'VOL' in result_pt.columns:
        result_pt['daily_deli_vol_perSKU'] = result_pt['VOL'] / result_pt['sku_dist_count']

    # # 更新透视列数据为千分位形式
    # if 'VOL' in cols:
    #     result_pt['VOL'] = round(result_pt['VOL'], 2)
    # result_pt[cols] = result_pt[cols].applymap(lambda x: '{:,}'.format(x))

    # result_pt.style.set_precision(2)
    # pct_cols = [x for x in list(result_pt.columns) if '%' in x ]
    # result_pt.style.format("{:.2%}", subset= pct_cols, na_rep='')
    cols = list(result_pt.columns[index_num:])
    result_pt = data_format(result_pt, cols)
    result_pt.columns = trans(result_pt.columns)
    # result_pt = result_pt.style.set_properties(**{
    #     'font-size': '10pt',
    #     'bold': 'Microsoft YaHei UI Light'
    # })
    result_pt.index = range(1, len(result_pt) + 1)
    result_pt.index.name = '序号'
    return result_pt


def out_order_pivot(df, index, order=None, pt_col=None, isCumu=True):
    if order is None:
        order = ['orderID']

    dist_count_order = df[index + order].groupby(index).orderID.nunique()
    df_disCount = (pd.DataFrame(dist_count_order)).reset_index()
    df_disCount = pd.pivot_table(df_disCount, index=index,
                                 aggfunc='sum',
                                 fill_value=0,
                                 margins=True).reset_index()
    df_disCount.columns = index + ['order_dist_count']

    if pt_col is None:
        pt_col = ['total_qty', 'total_qty2pltN', 'total_qty2ctnN', 'VOL']

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
    result_pt = result_pt[index + ['order_dist_count', 'line_count'] + pt_col]

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
            # result_pt.loc[(result_pt[index[0]] == 'All'), [cols[i] + '%_cumu']] = ''

    result_pt['qty_per_order'] = result_pt['total_qty'] / result_pt['order_dist_count']
    result_pt['ctn_per_order'] = result_pt['total_qty2ctnN'] / result_pt['order_dist_count']
    result_pt['line_per_order'] = result_pt['line_count'] / result_pt['order_dist_count']
    result_pt['qty_per_line'] = result_pt['total_qty'] / result_pt['line_count']
    result_pt['vol_per_order'] = result_pt['VOL'] / result_pt['order_dist_count']

    cols = list(result_pt.columns[index_num:])
    result_pt = data_format(result_pt, cols)
    result_pt.columns = trans(result_pt.columns)
    result_pt.index = range(1, len(result_pt) + 1)
    result_pt.index.name = '序号'
    return result_pt


def out_order_sku_pivot(df, index, order=None, sku=None, pt_col=None, isCumu=True):
    if order is None:
        order = ['orderID']
    dist_count_order = df[index + order].groupby(index).orderID.nunique()
    df_disCount_order = (pd.DataFrame(dist_count_order)).reset_index()
    df_disCount_order = pd.pivot_table(df_disCount_order, index=index,
                                       aggfunc='sum',
                                       fill_value=0,
                                       margins=True).reset_index()
    df_disCount_order.columns = index + ['order_dist_count']

    if sku is None:
        sku = ['SKU_ID']
    # SKU的非重复计数
    dist_count_sku = df[index + sku].groupby(index).SKU_ID.nunique()
    df_disCount_sku = (pd.DataFrame(dist_count_sku)).reset_index()
    df_disCount_sku = pd.pivot_table(df_disCount_sku, index=index,
                                     aggfunc='sum',
                                     fill_value=0,
                                     margins=True).reset_index()
    df_disCount_sku.columns = index + ['sku_dist_count']

    if pt_col is None:
        pt_col = ['total_qty', 'total_qty2pltN', 'total_qty2ctnN', 'VOL']

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
    result_pt = result_pt[index + ['order_dist_count', 'sku_dist_count', 'line_count'] + pt_col]

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
            # result_pt.loc[(result_pt[index[0]] == 'All'), [cols[i] + '%_cumu']] = ''

    result_pt['qty_per_order'] = round(result_pt['total_qty'] / result_pt['order_dist_count'], 2)
    result_pt['line_per_order'] = round(result_pt['line_count'] / result_pt['order_dist_count'], 2)
    result_pt['qty_per_line'] = result_pt['total_qty'] / result_pt['line_count']
    if 'VOL' in result_pt.columns:
        result_pt['daily_deli_vol_perSKU'] = result_pt['VOL'] / result_pt['sku_dist_count']

    cols = list(result_pt.columns[index_num:])
    result_pt = data_format(result_pt, cols)
    result_pt.columns = trans(result_pt.columns)
    result_pt.index = range(1, len(result_pt) + 1)
    result_pt.index.name = '序号'
    return result_pt


def out_sku_qty_pivot(df, index, sku=None, pt_col=None, isCumu=False):
    if sku is None:
        sku = ['SKU_ID']
    # SKU的非重复计数
    dist_count_sku = df[index + sku].groupby(index).SKU_ID.nunique()
    df_disCount_sku = (pd.DataFrame(dist_count_sku)).reset_index()
    df_disCount_sku = pd.pivot_table(df_disCount_sku, index=index,
                                     aggfunc='sum',
                                     fill_value=0,
                                     margins=True).reset_index()
    df_disCount_sku.columns = index + ['sku_dist_count']

    if pt_col is None:
        pt_col = ['pltN', 'ctnN', 'piece2ctnN', 'pltQ', 'ctnQ', 'pieceQ', 'total_qty', 'total_qty2pltN',
                  'total_qty2ctnN', 'VOL']

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
    result_pt = result_pt[index + ['sku_dist_count', 'line_count'] + pt_col]

    index_num = len(index)
    cols = list(result_pt.columns[index_num:])

    # 更新合计值
    for i in range(len(pt_col)):
        result_pt.loc[result_pt[index[0]] == 'All', [pt_col[i]]] = df[pt_col[i]].sum()

    # 计算整托数、整箱数、散件数占总件数的比例
    pct_col = ['pltQ', 'ctnQ', 'pieceQ', 'total_qty']
    for item in pct_col:
        result_pt[item + '/total_qty%'] = result_pt[item] / (result_pt['total_qty'].sum() / 2)

    # 计算比例
    for i in range(len(cols)):
        result_pt[cols[i] + '%'] = round(result_pt[cols[i]] / (result_pt[cols[i]].sum() / 2), 4)

    # 判断是否计算累计比例，若计算，一般为件数及体积的累计比例
    if isCumu:
        for i in range(len(cols)):
            result_pt[cols[i] + '%_cumu'] = result_pt[cols[i] + '%'].cumsum()
            # result_pt.loc[(result_pt[index[0]] == 'All'), [cols[i] + '%_cumu']] = ''

    result_pt['daily_deli_qty_perSKU'] = result_pt['total_qty'] / result_pt['sku_dist_count']
    result_pt['daily_deli_line_perSKU'] = result_pt['line_count'] / result_pt['sku_dist_count']
    if 'VOL' in result_pt.columns:
        result_pt['daily_deli_vol_perSKU'] = result_pt['VOL'] / result_pt['sku_dist_count']

    cols = list(result_pt.columns[index_num:])
    result_pt = data_format(result_pt, cols)
    result_pt.columns = trans(result_pt.columns)
    result_pt.index = range(1, len(result_pt) + 1)
    result_pt.index.name = '序号'
    return result_pt


def out_sku_qtyCtnPlt(df, index=None, sku=None):
    if index is None:
        index = ['order_ZS_tag', 'line_PCB_tag']
    if sku is None:
        sku = ['SKU_ID']

    pt_col = ['pltN', 'pltQ', 'ctnN', 'ctnQ', 'pieceQ',
              'piece2ctnN', 'piece2ctn_qty', 'piece2ctn_remainder', 'ctn2pltN',
              'total_qty']

    order_pt_col = ['pltN', 'pltQ', 'ctnN', 'ctnQ']
    # sku_pt_col = ['pieceQ', 'piece2ctnN', 'piece2ctn_qty', 'piece2ctn_remainder', 'ctn2pltN']
    sku_C_pt_col = ['ctn2pltN']
    sku_B_pt_col = ['pieceQ', 'piece2ctnN', 'piece2ctn_qty', 'piece2ctn_remainder']
    df_temp = df[['orderID', 'SKU_ID', 'order_ZS_tag', 'pltN', 'pltQ', 'ctnN', 'ctnQ', 'pieceQ']]

    new_outbound = pd.DataFrame()
    for i, row in df_temp.iterrows():
        if row['pieceQ'] > 0:
            if row['ctnQ'] > 0:
                if row['pltQ'] > 0:
                    row['line_PCB_tag'] = 'P'
                    new_outbound = new_outbound.append(row[['orderID', 'SKU_ID', 'order_ZS_tag',
                                                            'pltN', 'pltQ', 'line_PCB_tag']], ignore_index=True)
                row['line_PCB_tag'] = 'C'
                new_outbound = new_outbound.append(row[['orderID', 'SKU_ID', 'order_ZS_tag',
                                                        'ctnN', 'ctnQ', 'line_PCB_tag']], ignore_index=True)
            else:
                if row['pltQ'] > 0:
                    row['line_PCB_tag'] = 'P'
                    new_outbound = new_outbound.append(row[['orderID', 'SKU_ID', 'order_ZS_tag',
                                                            'pltN', 'pltQ', 'line_PCB_tag']], ignore_index=True)
            row['line_PCB_tag'] = 'B'
            new_outbound = new_outbound.append(row[['orderID', 'SKU_ID', 'order_ZS_tag',
                                                    'pieceQ', 'line_PCB_tag']], ignore_index=True)
        elif row['ctnQ'] > 0:
            if row['pltQ'] > 0:
                row['line_PCB_tag'] = 'P'
                new_outbound = new_outbound.append(row[['orderID', 'SKU_ID', 'order_ZS_tag',
                                                        'pltN', 'pltQ', 'line_PCB_tag']], ignore_index=True)
            row['line_PCB_tag'] = 'C'
            new_outbound = new_outbound.append(row[['orderID', 'SKU_ID', 'order_ZS_tag',
                                                    'ctnN', 'ctnQ', 'line_PCB_tag']],
                                               ignore_index=True)
        else:
            if row['pltQ'] > 0:
                row['line_PCB_tag'] = 'P'
                new_outbound = new_outbound.append(row[['orderID', 'SKU_ID', 'order_ZS_tag',
                                                        'pltN', 'pltQ', 'line_PCB_tag']],
                                                   ignore_index=True)
    new_outbound.reset_index().fillna(0)
    for col in order_pt_col:
        if col not in list(new_outbound.columns):
            new_outbound[col] = 0

    # print(new_outbound)
    # print('new_outbound rows: ', new_outbound.shape[0])
    #
    # writer = pd.ExcelWriter('D:/Work/Project/09蜜思肤/Output/msf_0000_new_outbound.xlsx')
    # workbook = writer.book
    # fmt = workbook.add_format({'font_name': 'Microsoft YaHei Light',
    #                            'align': 'center',
    #                            'valign': 'vcenter',
    #                            'font_size': 9
    #                            })
    # border_format = workbook.add_format({'border': 1})
    # percent_fmt = workbook.add_format({'num_format': '0.00%'})
    # amt_fmt = workbook.add_format({'num_format': '#,##0'})
    #
    # l_end = len(new_outbound.index)
    # new_outbound.index = range(1, len(new_outbound) + 1)
    # new_outbound.index.name = '序号'
    # new_outbound.to_excel(excel_writer=writer, sheet_name='01-new_outbound')
    # worksheet1 = writer.sheets['01-new_outbound']
    # worksheet1.set_column('A:Z', 12, fmt)
    # worksheet1.conditional_format('A0:Z{}'.format(l_end), {'type': 'no_blanks', 'format': border_format})
    # #
    # # for col_num, value in enumerate(new_outbound.columns.values):
    # #     worksheet1.write(1, col_num, value, fmt)
    # # new_outbound.to_excel(excel_writer=writer, sheet_name='01-new_outbound')
    # writer.save()
    # writer.close()

    lineCount = pd.pivot_table(new_outbound, index=index,
                               values=sku, aggfunc='count',
                               fill_value=0,
                               margins=True).reset_index()

    lineCount.columns = index + ['line_count']
    # print(lineCount.columns)
    # print(lineCount)
    order_dim_pt = pd.pivot_table(new_outbound, index=index,
                                  values=order_pt_col,
                                  aggfunc='sum', fill_value=0,
                                  margins=True).reset_index()

    order_dim_pt = pd.merge(lineCount, order_dim_pt, on=index, how='outer', sort=False)

    ### 提取整箱订购行，按SKU维度聚合，计算整箱折合整托数
    outbound_C = new_outbound[new_outbound['line_PCB_tag'] == 'C'].reset_index()
    sku_dim_C = outbound_C.groupby(['order_ZS_tag', 'SKU_ID']).agg(ctnN=pd.NamedAgg(column='ctnN',
                                                                                    aggfunc='sum')).reset_index()
    sku_dim_C = pd.merge(sku_dim_C, df[['SKU_ID', 'pltQty', 'fullCaseUnit']], on='SKU_ID', how='left', sort=False)
    sku_dim_C = sku_dim_C.drop_duplicates().reset_index().fillna(0)
    sku_dim_C['line_PCB_tag'] = 'C'
    sku_dim_C['ctn2pltN'] = 0
    sku_dim_C.loc[(sku_dim_C['pltQty'] > 0), ['ctn2pltN']] = round(sku_dim_C['ctnN'] *
                                                                   sku_dim_C['fullCaseUnit'] / sku_dim_C['pltQty'], 2)
    # sku_dim_C.to_excel(excel_writer=writer, sheet_name='02-sku_dim_C')

    ### 提取散件订购行，按SKU维度聚合，计算散件折合整箱数
    outbound_B = new_outbound[new_outbound['line_PCB_tag'] == 'B'].reset_index()
    sku_dim_B = outbound_B.groupby(['order_ZS_tag', 'SKU_ID']).agg(pieceQ=pd.NamedAgg(column='pieceQ',
                                                                                      aggfunc='sum')).reset_index()
    sku_dim_B = pd.merge(sku_dim_B, df[['SKU_ID', 'pltQty', 'fullCaseUnit']], on='SKU_ID', how='left', sort=False)
    sku_dim_B = sku_dim_B.drop_duplicates().reset_index().fillna(0)
    # print('sku_dim_C rows: ', sku_dim_B.shape[0])
    sku_dim_B['line_PCB_tag'] = 'B'
    sku_dim_B['piece2ctnN'] = 0
    sku_dim_B.loc[(sku_dim_B['fullCaseUnit'] > 0),
                  ['piece2ctnN']] = np.floor(sku_dim_B['pieceQ'] / sku_dim_B['fullCaseUnit'])
    sku_dim_B['piece2ctn_qty'] = 0
    sku_dim_B.loc[(sku_dim_B['piece2ctnN'] > 0),
                  ['piece2ctn_qty']] = sku_dim_B['piece2ctnN'] * sku_dim_B['fullCaseUnit']
    sku_dim_B['piece2ctn_remainder'] = sku_dim_B['pieceQ'] - sku_dim_B['piece2ctn_qty']
    # sku_dim_B.to_excel(excel_writer=writer, sheet_name='03-sku_dim_B')

    ### 汇总SKU维度数据
    sku_dim_C_pt = pd.pivot_table(sku_dim_C, index=index,
                                  values=sku_C_pt_col,
                                  aggfunc='sum', fill_value=0,
                                  margins=True).reset_index()

    sku_dim_B_pt = pd.pivot_table(sku_dim_B, index=index,
                                  values=sku_B_pt_col,
                                  aggfunc='sum', fill_value=0,
                                  margins=True).reset_index()

    sku_dim_pt = pd.merge(sku_dim_B_pt, sku_dim_C_pt, on=index, how='outer', sort=False).fillna(0)
    # print('-'*20)
    # print(sku_dim_pt)

    # for i in sku_pt_col:
    #     sku_dim_pt.loc[sku_dim_pt[index[0]] == 'All', [i]] = sku_dim_pt[i].sum()

    result_pt = pd.merge(order_dim_pt, sku_dim_pt, on=index, how='left', sort=False).fillna(0)

    result_pt['total_qty'] = result_pt['pltQ'] + result_pt['ctnQ'] + result_pt['pieceQ']
    # print('-' * 20)
    # print(result_pt)
    # 重排列
    result_pt = result_pt[index + ['line_count'] + pt_col]
    # print(result_pt)

    ### 计算各分项件数占总件数的比
    pct_col = ['pltQ', 'ctnQ', 'piece2ctn_qty', 'piece2ctn_remainder']
    for col in pct_col:
        result_pt[col + '/总件数%'] = result_pt[col] / (result_pt['total_qty'].sum() / 2)

    # 计算件数, 折合箱数/托数比例
    result_pt['总件数%'] = result_pt['total_qty'] / (result_pt['total_qty'].sum() / 2)
    result_pt['箱数%(原箱+散件折算成箱)'] = (result_pt['ctnN'] + result_pt['piece2ctnN']) / \
                                  ((result_pt['ctnN'].sum() + result_pt['piece2ctnN'].sum()) / 2)
    result_pt['托数%(整托+原箱折算成托)'] = (result_pt['pltN'] + result_pt['ctn2pltN']) / \
                                  ((result_pt['pltN'].sum() + result_pt['ctn2pltN'].sum()) / 2)
    # writer.save()
    # writer.close()

    index_num = len(index)
    cols = list(result_pt.columns[index_num:])
    result_pt = data_format(result_pt, cols)
    result_pt.columns = trans(result_pt.columns)
    result_pt.index = range(1, len(result_pt) + 1)
    result_pt.index.name = '序号'
    return result_pt


def out_zs_qty(df_zs, index=None, sku=None):
    if sku is None:
        sku = ['SKU_ID']

    pt_col = ['pltN', 'pltQ', 'ctnN', 'ctnQ', 'pieceQ',
              'piece2ctnN', 'piece2ctn_qty', 'piece2ctn_remainder', 'ctn2pltN',
              'total_qty']
    order_pt_col = ['pltN', 'pltQ', 'ctnN', 'ctnQ']
    sku_pt_col = ['pieceQ', 'piece2ctnN', 'piece2ctn_qty', 'piece2ctn_remainder', 'ctn2pltN']

    lineCount = pd.pivot_table(df_zs, index=index,
                               values=sku, aggfunc='count',
                               fill_value=0,
                               margins=True).reset_index()
    # print(lineCount.columns)
    lineCount.columns = index + ['line_count']

    order_dim_pt = pd.pivot_table(df_zs, index=index,
                                  values=order_pt_col,
                                  aggfunc='sum', fill_value=0,
                                  margins=True).reset_index()
    order_dim_pt = pd.merge(lineCount, order_dim_pt, on=index, how='outer', sort=False)

    sku_dim = df_zs.groupby(['order_ZS_tag', 'SKU_ID']).agg(ctnN=pd.NamedAgg(column='ctnN', aggfunc='sum'),
                                                            pieceQ=pd.NamedAgg(column='pieceQ', aggfunc='sum')
                                                            ).reset_index()
    # print('*' * 20)
    # print(sku_dim)

    sku_dim = pd.merge(sku_dim, df_zs[['SKU_ID', 'pltQty', 'fullCaseUnit'] + index],
                       on=['SKU_ID', 'order_ZS_tag'], how='left')
    sku_dim = sku_dim.drop_duplicates().reset_index().fillna(0)
    sku_dim['ctn2pltN'] = 0
    sku_dim.loc[(sku_dim['pltQty'] > 0), ['ctn2pltN']] = round(sku_dim['ctnN'] *
                                                               sku_dim['fullCaseUnit'] / sku_dim['pltQty'], 2)
    sku_dim['piece2ctnN'] = 0
    sku_dim.loc[(sku_dim['fullCaseUnit'] > 0),
                ['piece2ctnN']] = np.floor(sku_dim['pieceQ'] / sku_dim['fullCaseUnit'])
    sku_dim['piece2ctn_qty'] = 0
    sku_dim.loc[(sku_dim['piece2ctnN'] > 0),
                ['piece2ctn_qty']] = sku_dim['piece2ctnN'] * sku_dim['fullCaseUnit']
    sku_dim['piece2ctn_remainder'] = sku_dim['pieceQ'] - sku_dim['piece2ctn_qty']

    sku_dim_pt = pd.pivot_table(sku_dim, index=index,
                                values=sku_pt_col,
                                aggfunc='sum', fill_value=0,
                                margins=True).reset_index()

    # print('-'*20)
    # print(sku_dim)

    result_pt = pd.merge(order_dim_pt, sku_dim_pt, on=index, how='left')
    result_pt['total_qty'] = result_pt['pltQ'] + result_pt['ctnQ'] + result_pt['pieceQ']
    # 重排列
    result_pt = result_pt[index + ['line_count'] + pt_col]

    # pt_col = ['pltN', 'pltQ', 'ctnN', 'ctnQ', 'pieceQ',
    #           'piece2ctnN', 'piece2ctn_qty', 'piece2ctn_remainder', 'ctn2pltN',
    #           'total_qty']
    ### 计算各分项件数占总件数的比
    pct_col = ['pltQ', 'ctnQ', 'piece2ctn_qty', 'piece2ctn_remainder']
    for col in pct_col:
        result_pt[col + '/总件数%'] = result_pt[col] / (result_pt['total_qty'].sum() / 2)

    # 计算件数, 折合箱数/托数比例
    result_pt['总件数%'] = result_pt['total_qty'] / (result_pt['total_qty'].sum() / 2)
    result_pt['箱数%(原箱+散件折算成箱)'] = (result_pt['ctnN'] + result_pt['piece2ctnN']) / \
                                  ((result_pt['ctnN'].sum() + result_pt['piece2ctnN'].sum()) / 2)
    result_pt['托数%(整托+原箱折算成托)'] = (result_pt['pltN'] + result_pt['ctn2pltN']) / \
                                  ((result_pt['pltN'].sum() + result_pt['ctn2pltN'].sum()) / 2)

    index_num = len(index)
    cols = list(result_pt.columns[index_num:])
    result_pt = data_format(result_pt, cols)
    result_pt.columns = trans(result_pt.columns)
    result_pt.index = range(1, len(result_pt) + 1)
    result_pt.index.name = '序号'
    return result_pt


def order_num(df, index, toteV):
    order = ['orderID']

    dist_count_order = df[index + order].groupby(index).orderID.nunique()
    df_disCount = (pd.DataFrame(dist_count_order)).reset_index()
    df_disCount = pd.pivot_table(df_disCount, index=index,
                                 aggfunc='sum',
                                 fill_value=0,
                                 margins=True).reset_index()
    df_disCount.columns = index + ['order_N']

    df['pieceVol'] = df['pieceQ'] * df['corrVol']

    df_order = df[index + order + ['pieceVol']].groupby(index + order).agg(
        sumPieceVol=pd.NamedAgg(column='pieceVol', aggfunc='sum')).reset_index()
    # print(toteV)
    df_order['piece2toteN'] = df_order['sumPieceVol'] / toteV

    pt_col = ['pltN', 'ctnN', 'piece2toteN']
    order_pt_col = ['pltN', 'ctnN']

    tmp1 = pd.pivot_table(df, index=index,
                          values=order_pt_col,
                          aggfunc='sum', fill_value=0,
                          margins=True).reset_index()

    tmp2 = pd.pivot_table(df_order, index=index,
                          values=['piece2toteN'],
                          aggfunc='sum', fill_value=0,
                          margins=True).reset_index()

    result_pt = pd.merge(df_disCount, tmp1, how='left', sort=False)
    result_pt = pd.merge(result_pt, tmp2, how='left', sort=False)

    # 重排列
    result_pt = result_pt[index + ['order_N'] + pt_col]

    index_num = len(index)
    cols = list(result_pt.columns[index_num:])
    result_pt = data_format(result_pt, cols)
    result_pt.columns = trans(result_pt.columns)
    result_pt.index = range(1, len(result_pt) + 1)
    result_pt.index.name = '序号'
    return result_pt


def out_order_qty_pivot(df, index, order=None, sku=None, pt_col=None, isCumu=False):
    if order is None:
        order = ['orderID']
    dist_count_order = df[index + order].groupby(index).orderID.nunique()
    df_disCount_order = (pd.DataFrame(dist_count_order)).reset_index()
    df_disCount_order = pd.pivot_table(df_disCount_order, index=index,
                                       aggfunc='sum',
                                       fill_value=0,
                                       margins=True).reset_index()
    df_disCount_order.columns = index + ['order_dist_count']

    if sku is None:
        sku = ['SKU_ID']
    # SKU的非重复计数
    dist_count_sku = df[index + sku].groupby(index).SKU_ID.nunique()
    df_disCount_sku = (pd.DataFrame(dist_count_sku)).reset_index()
    df_disCount_sku = pd.pivot_table(df_disCount_sku, index=index,
                                     aggfunc='sum',
                                     fill_value=0,
                                     margins=True).reset_index()
    df_disCount_sku.columns = index + ['sku_dist_count']

    if pt_col is None:
        pt_col = ['pltN', 'ctnN', 'piece2ctnN', 'pltQ', 'ctnQ', 'pieceQ', 'total_qty', 'total_qty2pltN',
                  'total_qty2ctnN', 'VOL']

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
    result_pt = result_pt[index + ['order_dist_count', 'sku_dist_count', 'line_count'] + pt_col]

    index_num = len(index)
    cols = list(result_pt.columns[index_num:])

    # 更新合计值
    for i in range(len(pt_col)):
        result_pt.loc[result_pt[index[0]] == 'All', [pt_col[i]]] = df[pt_col[i]].sum()

    # 计算整托数、整箱数、散件数占总件数的比例
    pct_col = ['pltQ', 'ctnQ', 'pieceQ', 'total_qty']
    for item in pct_col:
        result_pt[item + '/total_qty%'] = result_pt[item] / (result_pt['total_qty'].sum() / 2)

    # 计算比例
    for i in range(len(cols)):
        result_pt[cols[i] + '%'] = round(result_pt[cols[i]] / (result_pt[cols[i]].sum() / 2), 4)

    # 判断是否计算累计比例，若计算，一般为件数及体积的累计比例
    if isCumu:
        for i in range(len(cols)):
            result_pt[cols[i] + '%_cumu'] = result_pt[cols[i] + '%'].cumsum()
            # result_pt.loc[(result_pt[index[0]] == 'All'), [cols[i] + '%_cumu']] = ''

    result_pt['qty_per_order'] = result_pt['total_qty'] / result_pt['order_dist_count']
    result_pt['line_per_order'] = result_pt['line_count'] / result_pt['order_dist_count']
    if 'VOL' in result_pt.columns:
        result_pt['daily_deli_vol_perSKU'] = result_pt['VOL'] / result_pt['sku_dist_count']

    cols = list(result_pt.columns[index_num:])
    result_pt = data_format(result_pt, cols)
    result_pt.columns = trans(result_pt.columns)
    result_pt.index = range(1, len(result_pt) + 1)
    result_pt.index.name = '序号'
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

            # col = col.replace('I_class', '一级类目')
            # col = col.replace('II_class', '二级类目')
            # col = col.replace('III_class', '三级类目')
            # col = col.replace('IV_class', '四级类目')
            col = col.replace('fullCaseUnit', '原箱装箱数(件)')

            col = col.replace('order_ZS_tag', '订单整箱/散件订购标识')
            col = col.replace('line_PCB_tag', '订单行订购单元标识')
            col = col.replace('EQ', '订单件数')
            col = col.replace('EN', '订单行数')
            col = col.replace('EV', '订单体积')
            col = col.replace('inline_tag', '订单行整箱/散件订购标识')
            col = col.replace('_Z', '-整箱订购')
            col = col.replace('_S', '-散件订购')

            col = col.replace('class', '分级')
            col = col.replace('current', '现状')
            col = col.replace('design', '规划')
            col = col.replace('pick', '拣选')
            col = col.replace('equiSize', '设备规格')
            col = col.replace('shelf', '轻架')
            col = col.replace('shuttle', '多穿')
            col = col.replace('num', '数量')
            col = col.replace('equipment', '设备')
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
            col = col.replace('qty', '件数')
            col = col.replace('Qty', '件数')
            col = col.replace('N', '数量')
            col = col.replace('Q', '件数')
            col = col.replace('ctn', '原箱')
            col = col.replace('piece', '散件')
            col = col.replace('total', '总')
            col = col.replace('2', '折合')
            col = col.replace('remainder', '余数')
            col = col.replace('skuClassInOrder', '订单内sku分级')

            # 出库透视表字段翻译
            col = col.replace('SKU_ID', 'SKU数')
            col = col.replace('orderID', '订单数')
            col = col.replace('order', '订单')
            col = col.replace('dist_count', '非重复计数')
            col = col.replace('_', '')
            col = col.replace('vol', '体积')
            col = col.replace('Vol', '体积')
            col = col.replace('VOL', '体积')
            col = col.replace('size', '件型')
            col = col.replace('line', '行')
            col = col.replace('rele', '关联')
            col = col.replace('structure', '结构')
            col = col.replace('count', '数')
            col = col.replace('cumu', '累计')
            col = col.replace('per', '/')
            col = col.replace('ZStag', '拆单标识')
            col = col.replace('PCBtag', '行订购标识')

            new_col.append(col)

    return new_col


def data_format(df, columns):
    # print(columns)
    # print('-' * 30)
    for col in columns:
        # df.loc[np.isinf(df[col]), col] = np.NAN
        if '%' in col:
            # print('%%%', col)
            df.loc[(df[col] > 0), col] = df.loc[(df[col] > 0), col].apply(lambda x: '%.2f%%' % (x * 100))
        elif 'vol' in col or 'Vol' in col or 'VOL' in col or 'avg_weight' in col:
            # print('4位小数,千分位', col)
            df.loc[(df[col] > 0), col] = df.loc[(df[col] > 0), col].apply(lambda x: round(x, 4)).apply(
                lambda x: '{:,}'.format(x))
        elif 'piece2ctn_remainder' in col or 'kg/m3' in col or 'avg_pltQty' in col:
            # print('整数,千分位', col)
            df[col] = pd.to_numeric(df[col]).round(0).astype(int).apply(lambda x: '{:,}'.format(x))
        elif 'per' in col or 'days' in col or 'avg' in col:
            # print('2位小数,千分位', col)
            df.loc[(df[col] > 0), col] = df.loc[(df[col] > 0), col].apply(lambda x: round(x, 2)).apply(
                lambda x: '{:,}'.format(x))
        elif ('N' in col or 'Q' in col) and ('2' not in col) and ('daily' not in col):
            # print('整数,千分位', col)
            df[col] = pd.to_numeric(df[col]).round(0).astype(int).apply(lambda x: '{:,}'.format(x))
        elif ('count' in col or 'qty' in col or 'SKU_ID' in col or 'sku' in col) and ('2' not in col):
            # print('整数,千分位', col)
            df[col] = pd.to_numeric(df[col]).round(0).astype(int).apply(lambda x: '{:,}'.format(x))
        else:
            # print('2位小数,千分位', col)
            df.loc[df[col] > 0, col] = df.loc[(df[col] > 0), col].apply(lambda x: round(x, 2)).apply(
                lambda x: '{:,}'.format(x))
        if 'cumu' in col:
            df.loc[(df[df.columns[0]] == 'All'), [col]] = ''
        df.loc[(df[col] == 'inf'), [col]] = ''
    return df


def layout_format(writer):
    cap_list = [chr(i) for i in range(65, 91)]
    # writer = pd.ExcelWriter(file)
    workbook = writer.book

    # 设置格式
    fmt = workbook.add_format({'font_name': 'Microsoft YaHei Light', 'font_size': 9})
    percent_fmt = workbook.add_format({'num_format': '0.00%'})
    amt_fmt = workbook.add_format({'num_format': '#,##0'})
    dec2_fmt = workbook.add_format({'num_format': '#,##0.00'})
    dec4_fmt = workbook.add_format({'num_format': '#,##0.0000'})
    border_format = workbook.add_format({'border': 1})

    note_fmt = workbook.add_format(
        {'bold': True, 'font_name': 'Microsoft YaHei Light', 'font_size': 9,
         'font_color': 'red', 'align': 'center', 'valign': 'vcenter'})
    date_fmt = workbook.add_format({'bold': False, 'font_name': u'微软雅黑', 'num_format': 'yyyy-mm-dd'})

    col_fmt = workbook.add_format(
        {'bold': True, 'font_size': 9, 'font_name': u'微软雅黑', 'num_format': 'yyyy-mm-dd', 'bg_color': '#9FC3D1',
         'valign': 'vcenter', 'align': 'center'})
    highlight_fmt = workbook.add_format({'bg_color': '#FFD7E2', 'num_format': '0.00%'})
    fmt = workbook.add_format({'font_name': 'Microsoft YaHei Light',
                               'align': 'center',
                               'valign': 'vcenter',
                               'font_size': 9
                               })
    border_format = workbook.add_format({'border': 1})
    worksheets = writer.sheets
    # print(worksheets)
    # print(type(worksheets))
    for sheet in worksheets.values():
        # rows = sheet.get_row()
        # cols = sheet.get_col()
        # cols_name = cap_list[cols]
        sheet.set_column('A:Z', 12, fmt)
        sheet.conditional_format('A1:Z20', {'type': 'no_blanks', 'format': border_format})
        # sheet.conditional_format('A0:{}{}'.format('M', 10), {'format': border_format})

    writer.save()


def format_data(writer, df, sheet_name, index=None):
    # book = load_workbook(writer.path)
    # writer.book = book
    if index is None:
        index_n = 0
    else:
        index_n = len(index)

    workbook = writer.book

    for col in list(df.columns):
        if 'cumu' in col:
            df.loc[(df[df.columns[0]] == 'All'), [col]] = ''
        df.loc[(df[col] == 'inf'), [col]] = ''

    # 设置格式
    fmt = workbook.add_format({'font_name': 'Microsoft YaHei Light', 'font_size': 9,
                               'align': 'center', 'valign': 'vcenter'})
    percent_fmt = workbook.add_format({'num_format': '0.00%'})
    amt_fmt = workbook.add_format({'num_format': '#,##0'})
    dec2_fmt = workbook.add_format({'num_format': '#,##0.00'})
    dec4_fmt = workbook.add_format({'num_format': '#,##0.0000'})
    border_format = workbook.add_format({'border': 1})
    col_fmt = workbook.add_format(
        {'font_size': 9, 'font_name': 'Microsoft YaHei Light', 'num_format': 'yyyy-mm-dd',
         'valign': 'vcenter', 'align': 'center'})
    # 'bg_color': '#9FC3D1','bold': True,

    ### df写入表格
    df.to_excel(excel_writer=writer, sheet_name=sheet_name, encoding='utf8', header=True, index=False)
    worksheet1 = writer.sheets[sheet_name]

    ### 数据源行数，和列数
    rows = df.shape[0] + 1
    cols = df.shape[1]

    cap_list = get_char_list(100)

    ### 设置列宽
    worksheet1.set_column('A:{}'.format(cap_list[cols]), 15, fmt)

    ### 添加边框
    worksheet1.conditional_format('A1:{}{}'.format(cap_list[cols], rows),
                                  {'type': 'no_blanks', 'format': border_format})
    # 'type': 'cell','criteria': '>', 'value': 0, 'format': border_format

    ### 按列名设备列的格式
    for i, col in enumerate(df.columns.values):
        worksheet1.write(0, i, col, col_fmt)
        # print(i, index_n, col)
        if i > index_n:
            if '%' in col:
                # print(col, '百分数')
                worksheet1.conditional_format('{}1:{}{}'.format(cap_list[i], cap_list[i], rows),
                                              {'type': 'cell', 'criteria': '<=', 'value': 1, 'format': percent_fmt})
            elif 'vol' in col or 'Vol' in col or 'VOL' in col or 'avg_weight' in col:
                # print(col, '4位小数，千分位')
                worksheet1.conditional_format('{}1:{}{}'.format(cap_list[i], cap_list[i], rows),
                                              {'type': 'cell', 'criteria': '>', 'value': 0, 'format': dec4_fmt})
            elif 'per' in col or 'days' in col or 'avg' in col:
                # print(col, '2位小数，千分位')
                worksheet1.conditional_format('{}1:{}{}'.format(cap_list[i], cap_list[i], rows),
                                              {'type': 'cell', 'criteria': '>', 'value': 0, 'format': dec2_fmt})
            elif 'piece2ctn_remainder' in col or 'kg/m3' in col or 'avg_pltQty' in col:
                # print(col, '千分位')
                worksheet1.conditional_format('{}1:{}{}'.format(cap_list[i], cap_list[i], rows),
                                              {'type': 'cell', 'criteria': '>', 'value': 0, 'format': amt_fmt})
            elif ('N' in col or 'Q' in col) and ('2' not in col) and ('daily' not in col):
                # print(col, '千分位')
                worksheet1.conditional_format('{}1:{}{}'.format(cap_list[i], cap_list[i], rows),
                                              {'type': 'cell', 'criteria': '>', 'value': 0, 'format': amt_fmt})
            elif ('count' in col or 'qty' in col or 'SKU_ID' in col or 'sku' in col) and ('2' not in col):
                # print(col, '千分位')
                worksheet1.conditional_format('{}1:{}{}'.format(cap_list[i], cap_list[i], rows),
                                              {'type': 'cell', 'criteria': '>', 'value': 0, 'format': amt_fmt})
            else:
                # print(col, '2位小数，千分位')
                worksheet1.conditional_format('{}1:{}{}'.format(cap_list[i], cap_list[i], rows),
                                              {'type': 'cell', 'criteria': '>', 'value': 0, 'format': dec2_fmt})

    worksheet1.conditional_format('A1:{}{}'.format(cap_list[cols], rows),
                                  {'type': 'no_blanks', 'format': border_format})


def get_char_list(n):
    char_list = [chr(i) for i in range(65, 91)]

    for i in range(65, 91):
        for j in range(65, 91):
            char_list.append(chr(i) + chr(j))
            if len(char_list) > n:
                break
        if len(char_list) > n:
            break

    return char_list
