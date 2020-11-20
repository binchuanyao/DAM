# -*- coding: utf-8 -*-


from generate_pivot import *


def outbound(sku_ref, outbound_org, result_path):
    # 加载配置参数
    config = Config()
    config.run()

    rows = outbound_org.shape[0]
    cols = outbound_org.shape[1]

    print('-' * 50)
    print('出库数据行数：', rows)
    print('出库数据原始列数：', cols)

    # 匹配SKU基础信息至订单数据
    df = pd.merge(outbound_org, sku_ref, how='left', on='SKU_ID', sort=False)

    df.columns = ['warehouse', 'order_date', 'order_week', 'order_state', 'm_orderID',
                  'orderID', 'isSplit', 'order_type', 'operation_mode', 'SKU_ID', 'total_qty',
                  'deli_type', 'package_size', 'package_weight', 'package_long', 'package_width',
                  'package_height', 'package_num', 'province', 'city',
                  'fullCaseUnit', 'corrVol', 'CW_isAbnormal_tag', 'toteQty', 'pltQty',
                  'unit_deli_longest_state', 'ctn_deli_longest_state', 'size', 'ctn_size',
                  'current_stock_mode', 'current_stock_equiSize', 'prac_daily_deli_PC_class'
                  ]

    df['size'] = df['size'].fillna('')
    df['ctn_size'] = df['ctn_size'].fillna('')
    df['fullCaseUnit'] = df['fullCaseUnit'].fillna(0)
    df['corrVol'] = df['corrVol'].fillna(0)
    df['toteQty'] = df['toteQty'].fillna(0)
    df['pltQty'] = df['pltQty'].fillna(0)
    # df[['CW_isAbnormal_tag', 'unit_deli_longest_state', 'size', 'ctn_deli_longest_state',
    #     'current_stock_mode', 'current_stock_equiSize', 'prac_daily_deli_PC_class']].fillna('')

    # pprint.pprint(df[['SKU_ID','plt_Qty' , 'size']])

    # 12 M 购买数量折合托盘数
    df['pltN'] = 0
    df.loc[(df['pltQty'] > 0), ['pltN']] = np.floor(df['total_qty'] / df['pltQty'])

    # 15 P 一级箱规原箱订购箱数折算
    df['ctnN'] = 0
    df.loc[(df['fullCaseUnit'] > 0), ['ctnN']] = np.floor(df['total_qty'] / df['fullCaseUnit'])

    ## 整托订购件数
    df['pltQ'] = df['pltN'] * df['pltQty']

    # 16 Q 一级箱规原箱订购件数折算
    df['ctnQ'] = df['ctnN'] * df['fullCaseUnit']

    ## 散件订购件数
    df['pieceQ'] = df['total_qty'] - df['pltQ'] - df['ctnQ']

    ## 散件折合箱数
    df['piece2ctnN'] = 0
    df.loc[(df['fullCaseUnit'] > 0), ['piece2ctnN']] = df['pieceQ'] / df['fullCaseUnit']

    ## 总件数折合托盘数
    df['total_qty2pltN'] = 0
    df.loc[(df['pltQty'] > 0), ['total_qty2pltN']] = df['total_qty'] / df['pltQty']

    ## 总件数折合整箱数
    df['total_qty2ctnN'] = 0
    df.loc[(df['fullCaseUnit'] > 0), ['total_qty2ctnN']] = df['total_qty'] / df['fullCaseUnit']

    # 整托订购折算标识
    df['isPlt'] = 'N'
    df.loc[(df['pltN'] >= 1), ['isPlt']] = 'Y'

    # 17 R 一级箱规原箱订购折算标识
    df['isCtn'] = 'N'
    df.loc[(df['ctnN'] >= 1), ['isCtn']] = 'Y'

    # 散件订购标识
    df['isBox'] = 'N'
    df.loc[(df['pieceQ'] > 0), ['isBox']] = 'Y'

    ### 订单内SKU订购分级
    df['skuClassInOrder'] = ''
    for index, row in df.iterrows():
        if row['pltN'] >= 1 and row['ctnN'] == 0 and row['pieceQ'] == 0:
            df.loc[index, ['skuClassInOrder']] = 'P'
        if row['pltN'] >= 1 and row['ctnN'] >= 1 and row['pieceQ'] == 0:
            df.loc[index, ['skuClassInOrder']] = 'P-C'
        if row['pltN'] >= 1 and row['ctnN'] == 0 and row['pieceQ'] > 0:
            df.loc[index, ['skuClassInOrder']] = 'P-B'
        if row['pltN'] == 0 and row['ctnN'] >= 1 and row['pieceQ'] == 0:
            df.loc[index, ['skuClassInOrder']] = 'C'
        if row['pltN'] == 0 and row['ctnN'] >= 1 and row['pieceQ'] > 0:
            df.loc[index, ['skuClassInOrder']] = 'C-B'
        if row['pltN'] == 0 and row['ctnN'] == 0 and row['pieceQ'] > 0:
            df.loc[index, ['skuClassInOrder']] = 'B'
        if row['pltN'] >= 1 and row['ctnN'] >= 1 and row['pieceQ'] > 0:
            df.loc[index, ['skuClassInOrder']] = 'P-C-B'

    ### 订单内SKU订购件型组合
    df['sizeComb'] = ''
    for index, row in df.iterrows():
        if row['ctnN'] >= 1 and row['pieceQ'] == 0:
            df.loc[index, ['sizeComb']] = row['ctn_size']
        elif row['ctnN'] >= 1 and row['pieceQ'] > 0:
            df.loc[index, ['sizeComb']] = row['ctn_size'] + '-' + row['size']
        elif row['ctnN'] < 1 and row['pieceQ'] > 0:
            df.loc[index, ['sizeComb']] = row['size']

    ### 订单订购分级
    df['maxSkuClass'] = df['skuClassInOrder'].apply(lambda x: x[:1]).tolist()
    order_class = {}
    order_dict = df.groupby('orderID')['maxSkuClass']
    for k, v in order_dict:
        # print(k, v)
        t = list(filter(None, list(set(v))))
        # t_size = list(filter(None, t_size))
        t = '-'.join(t)
        order_class[k] = t
    order_class = pd.DataFrame.from_dict(order_class, orient='index', columns=['order_class'])
    order_class = order_class.reset_index().rename(columns={'index': 'orderID'})

    ### 合并订单分级
    df = pd.merge(df, order_class, how='left', on='orderID', sort=False)

    # 13 N 购买数量折合体积(m3)
    df['VOL'] = 0
    df['VOL'] = df['total_qty'] * df['corrVol'] / pow(10, 9)

    # 14 O 购买体积分级
    df['lineVol'] = ''
    toteClassNum = len(config.TOTE_CLASS_INTERVAL) - 1
    PCClassNum = len(config.PC_CLASS)
    for index, row in df.iterrows():
        if row['size'] == config.SIZE['type'][3]:
            df.loc[index, ['lineVol']] = row['size']
        else:
            for i in range(PCClassNum):
                if i < toteClassNum:
                    if row['size'] == config.SIZE['type'][0] \
                            and row['VOL'] > config.PC_CLASS[i][1] * config.TOTE['valid_vol'] / pow(10, 9) \
                            and row['VOL'] <= config.PC_CLASS[i][2] * config.TOTE['valid_vol'] / pow(10, 9):
                        df.loc[index, ['lineVol']] = config.PC_CLASS[i][0]
                        break
                else:
                    if row['VOL'] > config.PC_CLASS[i][1] * config.PALLET_PICK['valid_vol'] / pow(10, 9) and \
                            row['VOL'] <= config.PC_CLASS[i][2] * config.PALLET_PICK['valid_vol'] / pow(10, 9):
                        df.loc[index, ['lineVol']] = config.PC_CLASS[i][0]
                        break

    # 订单行内PC分级标签
    df['PC_tag'] = df['lineVol'].apply(lambda x: x[:1]).tolist()
    # df.loc[type(df['lineVol']) == np.string ] = df['lineVol'].apply(lambda x: x[:1]).tolist()

    # ---------------------------------------------------------------------------------------------------------------
    # 订单维度基础信息
    order_temp1 = df.groupby('orderID').agg(EN_countSKU=pd.NamedAgg(column='SKU_ID', aggfunc='count')).reset_index()
    order_temp2 = df.groupby('orderID').agg(EQ_sumQty=pd.NamedAgg(column='total_qty', aggfunc='sum'),
                                            EV_sumVol=pd.NamedAgg(column='VOL', aggfunc='sum')).reset_index()
    order_detail = pd.merge(order_temp1, order_temp2, how='left', on='orderID', sort=False)

    print('-' * 30)
    # pprint.pprint(order_detail)

    # 订单维度的SKU数分级
    order_detail['EN_class'] = 0
    QTY_ClassNum = len(config.QTY_CLASS)
    for i in range(QTY_ClassNum):
        order_detail.loc[(order_detail['EN_countSKU'] > config.QTY_CLASS[i][1]) &
                         (order_detail['EN_countSKU'] <= config.QTY_CLASS[i][2]),
                         ['EN_class']] = config.QTY_CLASS[i][0]

    # 订单维度的件数分级
    order_detail['EQ_class'] = 0
    for i in range(QTY_ClassNum):
        order_detail.loc[(order_detail['EQ_sumQty'] > config.QTY_CLASS[i][1]) &
                         (order_detail['EQ_sumQty'] <= config.QTY_CLASS[i][2]),
                         ['EQ_class']] = config.QTY_CLASS[i][0]

    # 订单维度的体积分级
    order_detail['EV_class'] = 0
    for index, row in order_detail.iterrows():
        for i in range(PCClassNum):
            if i < toteClassNum:
                if row['EV_sumVol'] > config.PC_CLASS[i][1] * config.TOTE['valid_vol'] / pow(10, 9) \
                        and row['EV_sumVol'] <= config.PC_CLASS[i][2] * config.TOTE['valid_vol'] / pow(10, 9):
                    order_detail.loc[index, ['EV_class']] = config.PC_CLASS[i][0]
                    break
            else:
                if row['EV_sumVol'] > config.PC_CLASS[i][1] * config.PALLET_PICK['valid_vol'] / pow(10, 9) \
                        and row['EV_sumVol'] <= config.PC_CLASS[i][2] * config.PALLET_PICK['valid_vol'] / pow(10,
                                                                                                              9):
                    order_detail.loc[index, ['EV_class']] = config.PC_CLASS[i][0]
                    break

    order_detail['order_structure'] = ''
    for index, row in order_detail.iterrows():
        if row['EQ_sumQty'] == 1:
            order_detail.loc[index, ['order_structure']] = '01单品单件'
        elif row['EN_countSKU'] == 1:
            order_detail.loc[index, ['order_structure']] = '02单品多件'
        elif row['EN_countSKU'] == row['EQ_sumQty']:
            order_detail.loc[index, ['order_structure']] = '03多品单件'
        else:
            order_detail.loc[index, ['order_structure']] = '04多品多件'

    # order_detail 列重排
    order_detail = order_detail[['orderID', 'order_structure', 'EQ_sumQty', 'EN_countSKU', 'EV_sumVol',
                                 'EQ_class', 'EN_class', 'EV_class']]

    # ---------------------------------------------------------------------------------------------------------------
    # SKU维度基础信息
    sku_temp1 = df.groupby(['SKU_ID', 'size']).agg(
        EN_count=pd.NamedAgg(column='orderID', aggfunc='count')).reset_index()
    sku_temp2 = df.groupby(['SKU_ID']).agg(EQ_sumQty=pd.NamedAgg(column='total_qty', aggfunc='sum'),
                                           EV_sumVol=pd.NamedAgg(column='VOL', aggfunc='sum')).reset_index()

    sku_detail = pd.merge(sku_temp1, sku_temp2, how='left', on='SKU_ID', sort=False)

    # SKU维度的日出库行数分级
    sku_detail['DIK_class'] = 0
    for i in range(QTY_ClassNum):
        sku_detail.loc[(sku_detail['EN_count'] > config.QTY_CLASS[i][1]) &
                       (sku_detail['EN_count'] <= config.QTY_CLASS[i][2]),
                       ['DIK_class']] = config.QTY_CLASS[i][0]

    # SKU维度的日出库件数分级
    sku_detail['DIQ_class'] = 0
    for i in range(QTY_ClassNum):
        sku_detail.loc[(sku_detail['EQ_sumQty'] > config.QTY_CLASS[i][1]) &
                       (sku_detail['EQ_sumQty'] <= config.QTY_CLASS[i][2]),
                       ['DIQ_class']] = config.QTY_CLASS[i][0]

    # SKU维度的日出库体积分级
    sku_detail['DIV_class'] = 0
    for index, row in sku_detail.iterrows():
        if row['size'] == config.SIZE['type'][3]:
            sku_detail.loc[index, ['DIV_class']] = row['size']
        else:
            for i in range(PCClassNum):
                if i < toteClassNum:
                    if row['size'] == config.SIZE['type'][0] \
                            and row['EV_sumVol'] > config.PC_CLASS[i][1] * config.TOTE['valid_vol'] / pow(10, 9) \
                            and row['EV_sumVol'] <= config.PC_CLASS[i][2] * config.TOTE['valid_vol'] / pow(10, 9):
                        sku_detail.loc[index, ['DIV_class']] = config.PC_CLASS[i][0]
                        break
                else:
                    if row['EV_sumVol'] > config.PC_CLASS[i][1] * config.PALLET_PICK['valid_vol'] / pow(10, 9) \
                            and row['EV_sumVol'] <= config.PC_CLASS[i][2] * config.PALLET_PICK['valid_vol'] / pow(10,
                                                                                                                  9):
                        sku_detail.loc[index, ['DIV_class']] = config.PC_CLASS[i][0]
                        break

    # 计算日出库ABC件数分级
    # 添加辅助列 出库件数占比，出库体积占比
    sku_detail['qty_rate'] = sku_detail['EQ_sumQty'] / sku_detail['EQ_sumQty'].sum()
    sku_detail['count_rate'] = sku_detail['EN_count'] / sku_detail['EN_count'].sum()

    sku_detail['qty_rank'] = sku_detail['qty_rate'].rank(ascending=False, method='first')
    sku_detail['count_rank'] = sku_detail['count_rate'].rank(ascending=False, method='first')

    sku_detail['DQ_ABC'] = 'ZZ' + '_' + config.ABC_CLASS[4]
    for index, row in sku_detail.iterrows():
        cumu_rate = sku_detail[(sku_detail['qty_rank'] <= row['qty_rank'])]['qty_rate'].sum()
        if row['qty_rank'] == 1:
            sku_detail.loc[index, ['DQ_ABC']] = 'DQ' + '_' + config.ABC_CLASS[0]
        elif cumu_rate <= config.ABC_INTERVAL[0]:
            sku_detail.loc[index, ['DQ_ABC']] = 'DQ' + '_' + config.ABC_CLASS[0]
        elif cumu_rate <= config.ABC_INTERVAL[1]:
            sku_detail.loc[index, ['DQ_ABC']] = 'DQ' + '_' + config.ABC_CLASS[1]
        elif cumu_rate <= config.ABC_INTERVAL[2]:
            sku_detail.loc[index, ['DQ_ABC']] = 'DQ' + '_' + config.ABC_CLASS[2]
        else:
            sku_detail.loc[index, ['DQ_ABC']] = 'DQ' + '_' + config.ABC_CLASS[3]

    sku_detail['DK_ABC'] = 'ZZ' + '_' + config.ABC_CLASS[4]
    for index, row in sku_detail.iterrows():
        cumu_rate = sku_detail[(sku_detail['count_rank'] <= row['count_rank'])]['count_rate'].sum()
        if row['count_rank'] == 1:
            sku_detail.loc[index, ['DK_ABC']] = 'DK' + '_' + config.ABC_CLASS[0]
        elif cumu_rate <= config.ABC_INTERVAL[0]:
            sku_detail.loc[index, ['DK_ABC']] = 'DK' + '_' + config.ABC_CLASS[0]
        elif cumu_rate <= config.ABC_INTERVAL[1]:
            sku_detail.loc[index, ['DK_ABC']] = 'DK' + '_' + config.ABC_CLASS[1]
        elif cumu_rate <= config.ABC_INTERVAL[2]:
            sku_detail.loc[index, ['DK_ABC']] = 'DK' + '_' + config.ABC_CLASS[2]
        else:
            sku_detail.loc[index, ['DK_ABC']] = 'DK' + '_' + config.ABC_CLASS[3]

    # --------------------------------------------------------------------------------------------
    # 根据 orderID 匹配订单详细信息    订单结构标识/EQ/EN/EV/EQ_class/EN_class/EV_class
    df = pd.merge(df, order_detail, how='left', on='orderID', sort=False)

    # 根据 SKU_ID 匹配SKU详细信息   DIQ_class/DIK_class/DIV_class
    df = pd.merge(df, sku_detail[['SKU_ID', 'DIQ_class', 'DIK_class', 'DIV_class', 'DQ_ABC', 'DK_ABC']],
                  how='left', on='SKU_ID', sort=False)

    rele_df_source = df[['orderID', 'size', 'PC_tag', 'DQ_ABC', 'DK_ABC']]

    order_group = rele_df_source.groupby('orderID')
    order_relevance = {}
    for k, v in order_group:
        # print(k, v)
        order_relevance[k] = []
        t_size = list(filter(None, list(set(v['size']))))
        # t_size = list(filter(None, t_size))
        t_size.sort()
        t_size = '-'.join(t_size)

        t_PC = list(filter(None, list(set(v['PC_tag']))))
        # t_PC = list(filter(None, t_PC))
        t_PC.sort()
        t_PC = '-'.join(t_PC)

        t_DQ_ABC = list(filter(None, list(set(v['DQ_ABC']))))
        t_DQ_ABC.sort()
        t_DQ_ABC = '-'.join(t_DQ_ABC)

        t_DK_ABC = list(filter(None, list(set(v['DK_ABC']))))
        t_DK_ABC.sort()
        t_DK_ABC = '-'.join(t_DK_ABC)

        order_relevance[k].append(t_size)
        order_relevance[k].append(t_PC)
        order_relevance[k].append(t_DQ_ABC)
        order_relevance[k].append(t_DK_ABC)

    order_relevance = pd.DataFrame.from_dict(order_relevance, orient='index',
                                             columns=['size_rele', 'PC_rele', 'DQ_ABC_rele', 'DK_ABC_rele'])
    order_relevance = order_relevance.reset_index().rename(columns={'index': 'orderID'})

    # pprint.pprint(order_relevance.head(100))
    # pprint.pprint(df[['orderID', 'SKU_ID', 'size', 'PC_tag', 'DQ_ABC', 'DK_ABC']].head(100))

    # -------------------------------------------------------------------------------------------
    # 订单关联字段 相关计算

    # # 新建用来存放 order - 关联字段的 字典
    #
    # orderID_list = df['orderID'].unique()
    # dict_size = dict.fromkeys(orderID_list, set())
    # dict_PC = dict.fromkeys(orderID_list, set())
    # dict_DQ_ABC = dict.fromkeys(orderID_list, set())
    # dict_DK_ABC = dict.fromkeys(orderID_list, set())
    #
    #
    # for index, row in df.iterrows():
    #     if row['size'] != '':
    #         dict_size[row['orderID']].add(row['size'])
    #     if row['PC_tag'] != '':
    #         dict_PC[row['orderID']].add(row['PC_tag'])
    #     if row['DQ_ABC'] is not None:
    #         dict_DQ_ABC[row['orderID']].add(row['DQ_ABC'])
    #     if row['DK_ABC'] is not None:
    #         dict_DK_ABC[row['orderID']].add(row['DK_ABC'])
    #
    # # for k, v in dict_size.items():
    # #     print(k, v)
    #
    # for k, v in dict_size.items():
    #     t = list(v)
    #     print(k, t)
    #     t.sort()
    #     dict_size[k] = '-'.join(t)
    #
    #     print(k, dict_PC[k])
    #     v1 = list(dict_PC[k])
    #     v1.sort()
    #     dict_PC[k] = '-'.join(v1)
    #
    #     print(k, dict_DK_ABC[k])
    #     v2 = list(dict_DK_ABC[k])
    #     v2.sort()
    #     dict_DK_ABC[k] = '-'.join(v2)
    #
    #     print(k, dict_DQ_ABC[k])
    #     v3 = list(dict_DQ_ABC[k])
    #     v3.sort()
    #     dict_DQ_ABC = '-'.join(v3)
    #
    # df_size = pd.DataFrame.from_dict(dict_size, orient='index', columns=['relevance_size'])
    # df_size = df_size.reset_index().rename(columns={'index': 'orderID'})
    #
    # df_PC = pd.DataFrame.from_dict(dict_PC, orient='index', columns=['relevance_PC'])
    # df_PC = df_PC.reset_index().rename(columns={'index': 'orderID'})
    #
    # df_DK_ABC = pd.DataFrame.from_dict(dict_DK_ABC, orient='index', columns=['relevance_DK_ABC'])
    # df_DK_ABC = df_DK_ABC.reset_index().rename(columns={'index': 'orderID'})
    #
    # df_DQ_ABC = pd.DataFrame.from_dict(dict_DK_ABC, orient='index', columns=['relevance_DQ_ABC'])
    # df_DQ_ABC = df_DQ_ABC.reset_index().rename(columns={'index': 'orderID'})
    #
    # temp1 = pd.merge(df_size, df_PC, how='inner', on='orderID', sort=False)
    # temp2 = pd.merge(df_DK_ABC, df_DQ_ABC, how='inner', on='orderID', sort=False)
    #
    # order_relevance = pd.merge(temp1, temp2, how='inner', on='orderID', sort=False)

    ###-------------------------------------------------------------------------------
    # 根据 orderID 匹配订单关联字段

    df = pd.merge(df, order_relevance, how='left', on='orderID', sort=False)

    ### ----------------------------------------------------------------------------------
    # 将计算结果写入文件
    writer = pd.ExcelWriter('{}outBound1.xlsx'.format(result_path))
    df.to_excel(excel_writer=writer, sheet_name='00-outBound', inf_rep='')
    order_detail.to_excel(excel_writer=writer, sheet_name='01-order_detail', inf_rep='')
    sku_detail.to_excel(excel_writer=writer, sheet_name='02-sku_detail', inf_rep='')
    writer.close()
    writer.save()

    ### -----------------------------------------------------------------------------------
    # 提取透视表,写入单独文件
    writer = pd.ExcelWriter('{}outBound2.xlsx'.format(result_path))
    ## 1. sku维度透视表
    idx11 = ['size']
    size = out_sku_pivot(df, index=idx11)
    size.to_excel(excel_writer=writer, sheet_name='11-size', inf_rep='')

    idx11 = ['ctn_size', 'size']
    size = out_sku_qty_pivot(df, index=idx11)
    size.to_excel(excel_writer=writer, sheet_name='11-sizeComb', inf_rep='')

    idx12 = ['size_rele']
    size_rele = out_sku_pivot(df, index=idx12)
    size_rele.to_excel(excel_writer=writer, sheet_name='12-size_rele', inf_rep='')

    idx13 = ['skuClassInOrder']
    # cols = ['pltN', 'ctnN', 'pltQ', 'ctnQ', 'pieceQ', 'total_qty', 'VOL']
    pt = out_sku_qty_pivot(df, index=idx13)
    pt.to_excel(excel_writer=writer, sheet_name='13-skuClass', inf_rep='')

    idx14 = ['order_class']
    pt = out_order_qty_pivot(df, index=idx14)
    pt.to_excel(excel_writer=writer, sheet_name='14-orderClass', inf_rep='')

    """
    ## 2. 订单维度透视表
    """
    # 订单结构透视
    idx21 = ['order_structure']
    order_type = out_order_pivot(df, index=idx21)
    order_type.to_excel(excel_writer=writer, sheet_name='21-order_structure', inf_rep='')

    # 订单结构-件型关联 透视
    idx22 = ['order_structure', 'size_rele']
    order_releSize = out_order_pivot(df, index=idx22)
    order_releSize.to_excel(excel_writer=writer, sheet_name='22-order_sizerele', inf_rep='')

    """
    ## 3. ABC透视表
    """
    # DQ-ABC&rele 透视
    idx31 = ['DQ_ABC']
    order_type = out_order_pivot(df, index=idx31)
    order_type.to_excel(excel_writer=writer, sheet_name='31-DQ_ABC', inf_rep='')

    idx32 = ['DQ_ABC_rele']
    order_type = out_order_pivot(df, index=idx32)
    order_type.to_excel(excel_writer=writer, sheet_name='32-DQ_ABC_rele', inf_rep='')

    # # DQ-ABC&rele 透视
    # idx33 = ['DQ_ABC', 'DQ-ABC_rele']
    # order_type = out_order_pivot(df, index=idx33)
    # order_type.to_excel(excel_writer=writer, sheet_name='32-DQ_ABC&rele', inf_rep='')

    # DK-ABC 透视
    idx34 = ['DK_ABC']
    order_releSize = out_order_pivot(df, index=idx34)
    order_releSize.to_excel(excel_writer=writer, sheet_name='33-DK_ABC', inf_rep='')

    idx35 = ['DK_ABC_rele']
    order_type = out_order_pivot(df, index=idx35)
    order_type.to_excel(excel_writer=writer, sheet_name='34-DK_ABC_rele', inf_rep='')

    # # DK-ABC&rele 透视
    # idx36 = ['DK_ABC', 'DK-ABC_rele']
    # order_releSize = out_order_pivot(df, index=idx36)
    # order_releSize.to_excel(excel_writer=writer, sheet_name='34-DK_ABC&rele', inf_rep='')

    """
    ## 4. EQ透视表
    """
    # EQ_class 透视
    idx41 = ['EQ_class']
    order_type = out_order_pivot(df, index=idx41)
    order_type.to_excel(excel_writer=writer, sheet_name='41-EQ_class', inf_rep='')

    # EK_class 透视
    idx42 = ['EN_class']
    order_type = out_order_pivot(df, index=idx42)
    order_type.to_excel(excel_writer=writer, sheet_name='42-EN_class', inf_rep='')

    # order-structure & EQ 透视
    idx43 = ['order_structure', 'EQ_class']
    order_releSize = out_order_pivot(df, index=idx43)
    order_releSize.to_excel(excel_writer=writer, sheet_name='43-order&EQ', inf_rep='')

    # order-structure & EN 透视
    idx44 = ['order_structure', 'EN_class']
    order_releSize = out_order_pivot(df, index=idx44)
    order_releSize.to_excel(excel_writer=writer, sheet_name='44-order&EN', inf_rep='')

    # size & order-structure & EQ 透视
    idx45 = ['size_rele', 'order_structure', 'EQ_class']
    order_releSize = out_order_pivot(df, index=idx45)
    order_releSize.to_excel(excel_writer=writer, sheet_name='45-order&EQ', inf_rep='')

    # size & order-structure & EQ 透视
    idx46 = ['size_rele', 'order_structure', 'EN_class']
    order_releSize = out_order_pivot(df, index=idx46)
    order_releSize.to_excel(excel_writer=writer, sheet_name='46-order&EN', inf_rep='')

    """
    ## 5. PC透视表
    """
    # EQ_class 透视
    idx51 = ['EV_class']
    order_type = out_order_pivot(df, index=idx51)
    order_type.to_excel(excel_writer=writer, sheet_name='51-EV_class', inf_rep='')

    # EK_class 透视
    idx52 = ['EV_class', 'size_rele']
    order_type = out_order_pivot(df, index=idx52)
    order_type.to_excel(excel_writer=writer, sheet_name='52-EV&sizerele', inf_rep='')

    # order-structure & EQ 透视
    idx53 = ['order_structure', 'EV_class']
    order_releSize = out_order_pivot(df, index=idx53)
    order_releSize.to_excel(excel_writer=writer, sheet_name='53-order&EV', inf_rep='')

    # order-structure & EN 透视
    idx54 = ['DIV_class']
    order_releSize = out_order_pivot(df, index=idx54)
    order_releSize.to_excel(excel_writer=writer, sheet_name='54-DIV', inf_rep='')

    # size & order-structure & EQ 透视
    idx55 = ['size', 'DIV_class']
    order_releSize = out_order_pivot(df, index=idx55)
    order_releSize.to_excel(excel_writer=writer, sheet_name='55-size&DIV', inf_rep='')

    # size & order-structure & EQ 透视
    idx56 = ['order_structure', 'DIV_class']
    order_releSize = out_order_pivot(df, index=idx56)
    order_releSize.to_excel(excel_writer=writer, sheet_name='56-order&DIV', inf_rep='')

    idx57 = ['EQ_class', 'DIV_class']
    order_releSize = out_order_pivot(df, index=idx57)
    order_releSize.to_excel(excel_writer=writer, sheet_name='57-EQ&DIV', inf_rep='')

    writer.save()
    writer.close()
