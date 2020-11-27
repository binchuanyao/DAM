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

    ###  计算出库数据的总天数
    if len(df['order_date'].unique()) == 1:
        mdays = 1
    else:
        mdays = len(df['order_date'].unique())

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
    df['ctnQ'].fillna(0)

    ## 整箱折算成托数
    df['ctn2pltN'] = 0
    df.loc[(df['pltQty'] > 0), ['ctn2pltN']] = df['ctnQ'] / df['pltQty']

    ## 散件订购件数
    df['pieceQ'] = df['total_qty'] - df['pltQ'] - df['ctnQ']

    ## 散件折合箱数
    df['piece2ctnN'] = 0
    df.loc[(df['fullCaseUnit'] > 0), ['piece2ctnN']] = np.floor(df['pieceQ'] / df['fullCaseUnit'])

    ## 散件折合料箱数
    df['piece2toteN'] = round(df['pieceQ'] * df['corrVol'] / config.TOTE['valid_vol'], 2)

    # 散件折合整箱对应件数
    df['piece2ctn_qty'] = 0
    df.loc[(df['fullCaseUnit'] > 0), ['piece2ctn_qty']] = df['piece2ctnN'] * df['fullCaseUnit']

    # 散件折合整箱后余数
    df['piece2ctn_remainder'] = 0
    df.loc[(df['fullCaseUnit'] > 0), ['piece2ctn_remainder']] = df['pieceQ'] - df['piece2ctn_qty']

    ## 总件数折合托盘数
    df['total_qty2pltN'] = 0
    df.loc[(df['pltQty'] > 0), ['total_qty2pltN']] = df['total_qty'] / df['pltQty']

    ## 总件数折合整箱数
    df['total_qty2ctnN'] = 0
    df.loc[(df['fullCaseUnit'] > 0), ['total_qty2ctnN']] = df['total_qty'] / df['fullCaseUnit']

    # 整托订购折算标识
    df['isP'] = ''
    df.loc[(df['pltN'] >= 1), ['isP']] = 'P'

    # 17 R 一级箱规原箱订购折算标识
    df['isC'] = ''
    df.loc[(df['ctnN'] >= 1), ['isC']] = 'C'

    # 散件订购标识
    df['isB'] = ''
    df.loc[(df['pieceQ'] > 0), ['isB']] = 'B'

    ### 订单内SKU订购分级
    df['sku_class'] = ''
    df['order_ZS_tag'] = ''
    for index, row in df.iterrows():
        if row['pltN'] >= 1 and row['ctnN'] == 0 and row['pieceQ'] == 0:
            df.loc[index, ['sku_class']] = 'P'
            df.loc[index, ['order_ZS_tag']] = 'Z'
        if row['pltN'] >= 1 and row['ctnN'] >= 1 and row['pieceQ'] == 0:
            df.loc[index, ['sku_class']] = 'P-C'
            df.loc[index, ['order_ZS_tag']] = 'Z'
        if row['pltN'] >= 1 and row['ctnN'] == 0 and row['pieceQ'] > 0:
            df.loc[index, ['sku_class']] = 'P-B'
            df.loc[index, ['order_ZS_tag']] = 'Z-S'
        if row['pltN'] == 0 and row['ctnN'] >= 1 and row['pieceQ'] == 0:
            df.loc[index, ['sku_class']] = 'C'
            df.loc[index, ['order_ZS_tag']] = 'Z'
        if row['pltN'] == 0 and row['ctnN'] >= 1 and row['pieceQ'] > 0:
            df.loc[index, ['sku_class']] = 'C-B'
            df.loc[index, ['order_ZS_tag']] = 'Z-S'
        if row['pltN'] == 0 and row['ctnN'] == 0 and row['pieceQ'] > 0:
            df.loc[index, ['sku_class']] = 'B'
            df.loc[index, ['order_ZS_tag']] = 'S'
        if row['pltN'] >= 1 and row['ctnN'] >= 1 and row['pieceQ'] > 0:
            df.loc[index, ['sku_class']] = 'P-C-B'
            df.loc[index, ['order_ZS_tag']] = 'Z-S'

    ### 订单内SKU订购件型组合
    df['sku_size_comb'] = ''
    for index, row in df.iterrows():
        if row['ctnN'] >= 1 and row['pieceQ'] == 0:
            df.loc[index, ['sku_size_comb']] = row['ctn_size']
        elif row['ctnN'] >= 1 and row['pieceQ'] > 0:
            df.loc[index, ['sku_size_comb']] = row['ctn_size'] + '-' + row['size']
        elif row['ctnN'] < 1 and row['pieceQ'] > 0:
            df.loc[index, ['sku_size_comb']] = row['size']

    ### 订单订购分级
    df['maxSkuClass'] = df['sku_class'].apply(lambda x: x[:1]).tolist()
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

    # 14 O 订单行内SKU体积分级
    df['EIV_class'] = ''
    toteClassNum = len(config.TOTE_CLASS_INTERVAL) - 1
    PCClassNum = len(config.PC_CLASS)
    for index, row in df.iterrows():
        if row['size'] == config.SIZE['type'][3]:
            df.loc[index, ['EIV_class']] = row['size']
        else:
            for i in range(PCClassNum):
                if i < toteClassNum:
                    if row['size'] == config.SIZE['type'][0] \
                            and row['VOL'] > config.PC_CLASS[i][1] * config.TOTE['valid_vol'] / pow(10, 9) \
                            and row['VOL'] <= config.PC_CLASS[i][2] * config.TOTE['valid_vol'] / pow(10, 9):
                        df.loc[index, ['EIV_class']] = config.PC_CLASS[i][0]
                        break
                else:
                    if row['VOL'] > config.PC_CLASS[i][1] * config.PALLET_PICK['valid_vol'] / pow(10, 9) and \
                            row['VOL'] <= config.PC_CLASS[i][2] * config.PALLET_PICK['valid_vol'] / pow(10, 9):
                        df.loc[index, ['EIV_class']] = config.PC_CLASS[i][0]
                        break

    # 订单行内PC分级标签
    df['order_inline_PC_tag'] = df['EIV_class'].apply(lambda x: x[:1]).tolist()
    # df.loc[type(df['EIV_class']) == np.string ] = df['EIV_class'].apply(lambda x: x[:1]).tolist()

    ### ---------------------------------------------------------------------------------------------------------------
    ### 订单维度基础信息
    order_temp1 = df.groupby('orderID').agg(EN_countSKU=pd.NamedAgg(column='SKU_ID', aggfunc='count')).reset_index()
    order_temp2 = df.groupby('orderID').agg(EQ_sumQty=pd.NamedAgg(column='total_qty', aggfunc='sum'),
                                            EV_sumVol=pd.NamedAgg(column='VOL', aggfunc='sum')).reset_index()
    order_detail = pd.merge(order_temp1, order_temp2, how='left', on='orderID', sort=False)

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

    ### ---------------------------------------------------------------------------------------------------------------
    ### 整箱订购order维度基础信息 order_ZS_tag(整箱/散件标签) line_PCB_tag(行PCB标签）
    ### 新建df_z,选取整箱订购行，添加 order_sku_tag 标签
    # z_cols = ['orderID', 'SKU_ID','pltN', 'pltQ', 'ctnN', 'ctnQ', 'VOL']
    df_z = df[(df['pltQ'] > 0) | (df['ctnQ'] > 0)].copy().reset_index()
    df_z['total_qty'] = df_z['pltQ'] + df_z['ctnQ']
    df_z[['pieceQ', 'piece2ctnN', 'piece2ctn_qty', 'piece2ctn_remainder']] = 0
    df_z['order_ZS_tag'] = 'Z'
    df_z['line_PCB_tag'] = ''
    df_z.loc[(df_z['pltQ'] > 0), ['line_PCB_tag']] = 'P'
    df_z.loc[(df_z['ctnQ'] > 0), ['line_PCB_tag']] = 'C'

    order_temp1 = df_z.groupby('orderID').agg(EN_countSKU_Z=pd.NamedAgg(column='SKU_ID', aggfunc='count')).reset_index()
    order_temp2 = df_z.groupby('orderID').agg(EQ_sumQty_Z=pd.NamedAgg(column='total_qty', aggfunc='sum'),
                                              EV_sumVol_Z=pd.NamedAgg(column='VOL', aggfunc='sum')).reset_index()
    order_detail_z = pd.merge(order_temp1, order_temp2, how='left', on='orderID', sort=False)

    # 整箱订购——订单维度的SKU数分级
    order_detail_z['EN_class_Z'] = 0
    QTY_ClassNum = len(config.QTY_CLASS)
    for i in range(QTY_ClassNum):
        order_detail_z.loc[(order_detail_z['EN_countSKU_Z'] > config.QTY_CLASS[i][1]) &
                           (order_detail_z['EN_countSKU_Z'] <= config.QTY_CLASS[i][2]),
                           ['EN_class_Z']] = config.QTY_CLASS[i][0]

    # 订单维度的件数分级
    order_detail_z['EQ_class_Z'] = 0
    for i in range(QTY_ClassNum):
        order_detail_z.loc[(order_detail_z['EQ_sumQty_Z'] > config.QTY_CLASS[i][1]) &
                           (order_detail_z['EQ_sumQty_Z'] <= config.QTY_CLASS[i][2]),
                           ['EQ_class_Z']] = config.QTY_CLASS[i][0]

    # 订单维度的体积分级
    order_detail_z['EV_class_Z'] = 0
    for index, row in order_detail_z.iterrows():
        for i in range(PCClassNum):
            if i < toteClassNum:
                if row['EV_sumVol_Z'] > config.PC_CLASS[i][1] * config.TOTE['valid_vol'] / pow(10, 9) \
                        and row['EV_sumVol_Z'] <= config.PC_CLASS[i][2] * config.TOTE['valid_vol'] / pow(10, 9):
                    order_detail_z.loc[index, ['EV_class_Z']] = config.PC_CLASS[i][0]
                    break
            else:
                if row['EV_sumVol_Z'] > config.PC_CLASS[i][1] * config.PALLET_PICK['valid_vol'] / pow(10, 9) \
                        and row['EV_sumVol_Z'] <= config.PC_CLASS[i][2] * config.PALLET_PICK['valid_vol'] / pow(10,
                                                                                                                9):
                    order_detail_z.loc[index, ['EV_class_Z']] = config.PC_CLASS[i][0]
                    break

    # order_detail 列重排
    order_detail_z = order_detail_z[['orderID', 'EQ_sumQty_Z', 'EN_countSKU_Z', 'EV_sumVol_Z',
                                     'EQ_class_Z', 'EN_class_Z', 'EV_class_Z']]

    ### ---------------------------------------------------------------------------------------------------------------
    ### 散件订购order维度基础信息
    ### 新建df_s,选取散件订购行，添加 order_sku_tag 标签
    # s_cols = ['orderID', 'SKU_ID', 'pieceQ', 'VOL',
    #           'piece2ctnN', 'piece2ctn_qty', 'piece2ctn_remainder', 'ctn2pltN']
    df_s = df[(df['pieceQ'] > 0)].copy().reset_index()
    df_s['total_qty'] = df_s['pieceQ']
    df_s[['pltN', 'pltQ', 'ctnN', 'ctnQ']] = 0
    df_s['order_ZS_tag'] = 'S'
    df_s['line_PCB_tag'] = 'B'

    order_temp1 = df_s.groupby('orderID').agg(EN_countSKU_S=pd.NamedAgg(column='SKU_ID', aggfunc='count')).reset_index()
    order_temp2 = df_s.groupby('orderID').agg(EQ_sumQty_S=pd.NamedAgg(column='total_qty', aggfunc='sum'),
                                              EV_sumVol_S=pd.NamedAgg(column='VOL', aggfunc='sum')).reset_index()
    order_detail_s = pd.merge(order_temp1, order_temp2, how='left', on='orderID', sort=False)

    # 整箱订购——订单维度的SKU数分级
    order_detail_s['EN_class_S'] = 0
    QTY_ClassNum = len(config.QTY_CLASS)
    for i in range(QTY_ClassNum):
        order_detail_s.loc[(order_detail_s['EN_countSKU_S'] > config.QTY_CLASS[i][1]) &
                           (order_detail_s['EN_countSKU_S'] <= config.QTY_CLASS[i][2]),
                           ['EN_class_S']] = config.QTY_CLASS[i][0]

    # 订单维度的件数分级
    order_detail_s['EQ_class_S'] = 0
    for i in range(QTY_ClassNum):
        order_detail_s.loc[(order_detail_s['EQ_sumQty_S'] > config.QTY_CLASS[i][1]) &
                           (order_detail_s['EQ_sumQty_S'] <= config.QTY_CLASS[i][2]),
                           ['EQ_class_S']] = config.QTY_CLASS[i][0]

    # 订单维度的体积分级
    order_detail_s['EV_class_S'] = 0
    for index, row in order_detail_s.iterrows():
        for i in range(PCClassNum):
            if i < toteClassNum:
                if row['EV_sumVol_S'] > config.PC_CLASS[i][1] * config.TOTE['valid_vol'] / pow(10, 9) \
                        and row['EV_sumVol_S'] <= config.PC_CLASS[i][2] * config.TOTE['valid_vol'] / pow(10, 9):
                    order_detail_s.loc[index, ['EV_class_S']] = config.PC_CLASS[i][0]
                    break
            else:
                if row['EV_sumVol_S'] > config.PC_CLASS[i][1] * config.PALLET_PICK['valid_vol'] / pow(10, 9) \
                        and row['EV_sumVol_S'] <= config.PC_CLASS[i][2] * config.PALLET_PICK['valid_vol'] / pow(10,
                                                                                                                9):
                    order_detail_s.loc[index, ['EV_class_S']] = config.PC_CLASS[i][0]
                    break

    # order_detail_s 列重排
    order_detail_s = order_detail_s[['orderID', 'EQ_sumQty_S', 'EN_countSKU_S', 'EV_sumVol_S',
                                     'EQ_class_S', 'EN_class_S', 'EV_class_S']]

    # ---------------------------------------------------------------------------------------------------------------
    # SKU维度基础信息
    sku_temp1 = df.groupby(['SKU_ID', 'size']).agg(
        EN_count=pd.NamedAgg(column='orderID', aggfunc='count')).reset_index()
    sku_temp2 = df.groupby(['SKU_ID']).agg(EQ_sumQty=pd.NamedAgg(column='total_qty', aggfunc='sum'),
                                           EV_sumVol=pd.NamedAgg(column='VOL', aggfunc='sum')).reset_index()

    sku_detail = pd.merge(sku_temp1, sku_temp2, how='left', on='SKU_ID', sort=False)
    sku_detail['EQ_sumQty'] = sku_detail['EQ_sumQty'] / mdays
    sku_detail['EV_sumVol'] = sku_detail['EV_sumVol'] / mdays
    sku_detail['EN_count'] = sku_detail['EN_count'] / mdays

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
    sku_detail['vol_rate'] = sku_detail['EV_sumVol'] / sku_detail['EV_sumVol'].sum()
    sku_detail['count_rate'] = sku_detail['EN_count'] / sku_detail['EN_count'].sum()

    sku_detail['qty_rank'] = sku_detail['qty_rate'].rank(ascending=False, method='first')
    sku_detail['vol_rank'] = sku_detail['vol_rate'].rank(ascending=False, method='first')
    sku_detail['count_rank'] = sku_detail['count_rate'].rank(ascending=False, method='first')

    sku_detail['ABC_MPDQ'] = 'ZZ' + '_' + config.ABC_CLASS[4]
    for index, row in sku_detail.iterrows():
        cumu_rate = sku_detail[(sku_detail['qty_rank'] <= row['qty_rank'])]['qty_rate'].sum()
        if row['qty_rank'] == 1:
            sku_detail.loc[index, ['ABC_MPDQ']] = 'MPDQ' + '_' + config.ABC_CLASS[0]
        elif cumu_rate <= config.ABC_INTERVAL[0]:
            sku_detail.loc[index, ['ABC_MPDQ']] = 'MPDQ' + '_' + config.ABC_CLASS[0]
        elif cumu_rate <= config.ABC_INTERVAL[1]:
            sku_detail.loc[index, ['ABC_MPDQ']] = 'MPDQ' + '_' + config.ABC_CLASS[1]
        elif cumu_rate <= config.ABC_INTERVAL[2]:
            sku_detail.loc[index, ['ABC_MPDQ']] = 'MPDQ' + '_' + config.ABC_CLASS[2]
        else:
            sku_detail.loc[index, ['ABC_MPDQ']] = 'MPDQ' + '_' + config.ABC_CLASS[3]

    sku_detail['ABC_MPDV'] = 'ZZ' + '_' + config.ABC_CLASS[4]
    for index, row in sku_detail.iterrows():
        cumu_rate = sku_detail[(sku_detail['vol_rank'] <= row['vol_rank'])]['vol_rate'].sum()
        if row['vol_rank'] == 1:
            sku_detail.loc[index, ['ABC_MPDV']] = 'MPDV' + '_' + config.ABC_CLASS[0]
        elif cumu_rate <= config.ABC_INTERVAL[0]:
            sku_detail.loc[index, ['ABC_MPDV']] = 'MPDV' + '_' + config.ABC_CLASS[0]
        elif cumu_rate <= config.ABC_INTERVAL[1]:
            sku_detail.loc[index, ['ABC_MPDV']] = 'MPDV' + '_' + config.ABC_CLASS[1]
        elif cumu_rate <= config.ABC_INTERVAL[2]:
            sku_detail.loc[index, ['ABC_MPDV']] = 'MPDV' + '_' + config.ABC_CLASS[2]
        else:
            sku_detail.loc[index, ['ABC_MPDV']] = 'MPDV' + '_' + config.ABC_CLASS[3]

    sku_detail['ABC_MPDN'] = 'ZZ' + '_' + config.ABC_CLASS[4]
    for index, row in sku_detail.iterrows():
        cumu_rate = sku_detail[(sku_detail['count_rank'] <= row['count_rank'])]['count_rate'].sum()
        if row['count_rank'] == 1:
            sku_detail.loc[index, ['ABC_MPDN']] = 'MPDN' + '_' + config.ABC_CLASS[0]
        elif cumu_rate <= config.ABC_INTERVAL[0]:
            sku_detail.loc[index, ['ABC_MPDN']] = 'MPDN' + '_' + config.ABC_CLASS[0]
        elif cumu_rate <= config.ABC_INTERVAL[1]:
            sku_detail.loc[index, ['ABC_MPDN']] = 'MPDN' + '_' + config.ABC_CLASS[1]
        elif cumu_rate <= config.ABC_INTERVAL[2]:
            sku_detail.loc[index, ['ABC_MPDN']] = 'MPDN' + '_' + config.ABC_CLASS[2]
        else:
            sku_detail.loc[index, ['ABC_MPDN']] = 'MPDN' + '_' + config.ABC_CLASS[3]

    # --------------------------------------------------------------------------------------------
    # 根据 orderID 匹配订单详细信息到原始数据   订单结构标识/EQ/EN/EV/EQ_class/EN_class/EV_class
    df = pd.merge(df, order_detail, how='left', on='orderID', sort=False)
    df = pd.merge(df, order_detail_z, how='left', on='orderID', sort=False)
    df = pd.merge(df, order_detail_s, how='left', on='orderID', sort=False)

    # 根据 orderID 匹配 整箱订购 订单详细信息    订单结构标识/EQ/EN/EV/EQ_class/EN_class/EV_class
    df_z = pd.merge(df_z, order_detail_z, how='left', on='orderID', sort=False)

    # 根据 orderID 匹配 散件订购 订单详细信息    订单结构标识/EQ/EN/EV/EQ_class/EN_class/EV_class
    df_s = pd.merge(df_s, order_detail_s, how='left', on='orderID', sort=False)

    # 根据 SKU_ID 匹配SKU详细信息   DIQ_class/DIK_class/DIV_class
    df = pd.merge(df, sku_detail[['SKU_ID', 'DIQ_class', 'DIK_class', 'DIV_class', 'ABC_MPDQ', 'ABC_MPDV', 'ABC_MPDN']],
                  how='left', on='SKU_ID', sort=False)

    rele_df_source = df[['orderID', 'size', 'order_inline_PC_tag', 'ABC_MPDQ', 'ABC_MPDV', 'ABC_MPDN']]

    order_group = rele_df_source.groupby('orderID')
    order_relevance = {}
    for k, v in order_group:
        # print(k, v)
        order_relevance[k] = []
        t_size = list(filter(None, list(set(v['size']))))
        # t_size = list(filter(None, t_size))
        t_size.sort()
        t_size = '-'.join(t_size)

        t_PC = list(filter(None, list(set(v['order_inline_PC_tag']))))
        # t_PC = list(filter(None, t_PC))
        t_PC.sort()
        t_PC = '-'.join(t_PC)

        t_DQ_ABC = list(filter(None, list(set(v['ABC_MPDQ']))))
        t_DQ_ABC.sort()
        t_DQ_ABC = '-'.join(t_DQ_ABC)

        t_DV_ABC = list(filter(None, list(set(v['ABC_MPDV']))))
        t_DV_ABC.sort()
        t_DV_ABC = '-'.join(t_DV_ABC)

        t_DK_ABC = list(filter(None, list(set(v['ABC_MPDN']))))
        t_DK_ABC.sort()
        t_DK_ABC = '-'.join(t_DK_ABC)

        order_relevance[k].append(t_size)
        order_relevance[k].append(t_PC)
        order_relevance[k].append(t_DQ_ABC)
        order_relevance[k].append(t_DV_ABC)
        order_relevance[k].append(t_DK_ABC)

    order_relevance = pd.DataFrame.from_dict(order_relevance, orient='index',
                                             columns=['size_rele', 'PC_rele', 'DQ_ABC_rele', 'DV_ABC_rele',
                                                      'DK_ABC_rele'])
    order_relevance = order_relevance.reset_index().rename(columns={'index': 'orderID'})

    df = pd.merge(df, order_relevance, how='left', on='orderID', sort=False)

    # ### 新建df,将sku不同订购类型拆分成多行数据，添加 order_sku_tag 标签
    # new_outbound = pd.DataFrame()
    # for index, row in df.iterrows():
    #     if row['pieceQ'] > 0:
    #         if row['ctnQ'] > 0:
    #             if row['pltQ'] > 0:
    #                 row['order_sku_tag'] = 'P'
    #                 new_outbound = new_outbound.append(row[['orderID', 'SKU_ID', 'pltN', 'pltQ', 'order_sku_tag']],
    #                                                    ignore_index=True)
    #             row['order_sku_tag'] = 'C'
    #             new_outbound = new_outbound.append(row[['orderID', 'SKU_ID', 'ctnN', 'ctnQ', 'order_sku_tag']],
    #                                                ignore_index=True)
    #         row['order_sku_tag'] = 'B'
    #         new_outbound = new_outbound.append(row[['orderID', 'SKU_ID', 'pieceQ', 'order_sku_tag']], ignore_index=True)
    #     elif row['ctnQ'] > 0:
    #         if row['pltQ'] > 0:
    #             row['order_sku_tag'] = 'P'
    #             new_outbound = new_outbound.append(row[['orderID', 'SKU_ID', 'pltN', 'pltQ', 'order_sku_tag']],
    #                                                ignore_index=True)
    #         row['order_sku_tag'] = 'C'
    #         new_outbound = new_outbound.append(row[['orderID', 'SKU_ID', 'ctnN', 'ctnQ', 'order_sku_tag']],
    #                                            ignore_index=True)
    #     else:
    #         if row['pltQ'] > 0:
    #             row['order_sku_tag'] = 'P'
    #             new_outbound = new_outbound.append(row[['orderID', 'SKU_ID', 'pltN', 'pltQ', 'order_sku_tag']],
    #                                                ignore_index=True)
    #
    # for col in ['pltN', 'pltQ', 'ctnN', 'ctnQ']:
    #     if col not in list(new_outbound.columns):
    #         new_outbound[col] = 0

    ### --------------------------------------------------------------------------------
    ### 将整箱/散件行组合
    df_zs = df_z.append(df_s).copy().reset_index()
    # print('df_zs rows: ' , df_zs.shape)
    # print('df_zs columns: ', df_zs.columns)

    ## 添加 order维度的 EV_class
    df_zs = pd.merge(df_zs, order_detail[['orderID', 'EV_class']], on='orderID', how='left', sort=False)
    df_zs = pd.merge(df_zs, sku_detail[['SKU_ID', 'DIQ_class', 'DIK_class', 'DIV_class',
                                        'ABC_MPDQ', 'ABC_MPDV', 'ABC_MPDN']],
                     how='left', on='SKU_ID', sort=False)

    df_zs['EQ_class_all'] = ''
    df_zs.loc[(df_zs['order_ZS_tag'] == 'Z'), ['EQ_class_all']] = df_zs['EQ_class_Z']
    df_zs.loc[(df_zs['order_ZS_tag'] == 'S'), ['EQ_class_all']] = df_zs['EQ_class_S']

    df_zs['EN_class_all'] = ''
    df_zs.loc[(df_zs['order_ZS_tag'] == 'Z'), ['EN_class_all']] = df_zs['EN_class_Z']
    df_zs.loc[(df_zs['order_ZS_tag'] == 'S'), ['EN_class_all']] = df_zs['EN_class_S']

    df_zs['EV_class_all'] = ''
    df_zs.loc[(df_zs['order_ZS_tag'] == 'Z'), ['EV_class_all']] = df_zs['EV_class_Z']
    df_zs.loc[(df_zs['order_ZS_tag'] == 'S'), ['EV_class_all']] = df_zs['EV_class_S']

    ### 拆分整箱/散件后的 EIV分级
    df_zs['line_vol'] = df_zs['total_qty'] * df_zs['corrVol']
    df_zs['EIV_class_zs'] = ''
    toteClassNum = len(config.TOTE_CLASS_INTERVAL) - 1
    PCClassNum = len(config.PC_CLASS)
    for index, row in df_zs.iterrows():
        if row['size'] == config.SIZE['type'][3]:
            df_zs.loc[index, ['EIV_class_zs']] = row['size']
        else:
            for i in range(PCClassNum):
                if i < toteClassNum:
                    if row['size'] == config.SIZE['type'][0] \
                            and row['VOL'] > config.PC_CLASS[i][1] * config.TOTE['valid_vol'] / pow(10, 9) \
                            and row['VOL'] <= config.PC_CLASS[i][2] * config.TOTE['valid_vol'] / pow(10, 9):
                        df_zs.loc[index, ['EIV_class_zs']] = config.PC_CLASS[i][0]
                        break
                else:
                    if row['VOL'] > config.PC_CLASS[i][1] * config.PALLET_PICK['valid_vol'] / pow(10, 9) and \
                            row['VOL'] <= config.PC_CLASS[i][2] * config.PALLET_PICK['valid_vol'] / pow(10, 9):
                        df_zs.loc[index, ['EIV_class_zs']] = config.PC_CLASS[i][0]
                        break



    ### ----------------------------------------------------------------------------------
    # 将计算结果写入文件
    time = datetime.now()
    str_time = time.strftime('%Y_%m_%d_%H_%M')
    writer = pd.ExcelWriter('{}outBound1_{}.xlsx'.format(result_path, str_time))
    df.to_excel(excel_writer=writer, sheet_name='00-outBound', inf_rep='')
    df_zs.to_excel(excel_writer=writer, sheet_name='00-outBound_zs', inf_rep='')
    order_detail.to_excel(excel_writer=writer, sheet_name='01-order_detail', inf_rep='')

    ## 计算SKU维度信息
    sku_detail = pd.merge(sku_detail, df[['SKU_ID', 'pltQty', 'fullCaseUnit']])

    sku_detail.to_excel(excel_writer=writer, sheet_name='02-sku_detail', inf_rep='')
    writer.close()
    writer.save()

    ### -----------------------------------------------------------------------------------
    # 提取透视表,写入单独文件
    time = datetime.now()
    str_time = time.strftime('%Y_%m_%d_%H_%M')
    writer = pd.ExcelWriter('{}outBound2_{}.xlsx'.format(result_path, str_time))

    ## 00. order and sku维度整托件数，整箱数，散件数折算

    res = out_sku_qtyCtnPlt(df)
    res.to_excel(excel_writer=writer, sheet_name='00-order_sku_qtyClass', inf_rep='')

    idx00 = ['order_ZS_tag', 'line_PCB_tag']
    res = out_zs_qty(df_zs, index=idx00)
    res.to_excel(excel_writer=writer, sheet_name='00-ZS_PCB', inf_rep='')

    idx001 = ['ABC_MPDV', 'order_ZS_tag']
    res = out_zs_qty(df_zs, index=idx001)
    res.to_excel(excel_writer=writer, sheet_name='00-ABC_MPDV(zs)', inf_rep='')

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

    idx13 = ['sku_class']
    # cols = ['pltN', 'ctnN', 'pltQ', 'ctnQ', 'pieceQ', 'total_qty', 'VOL']
    pt = out_sku_qty_pivot(df, index=idx13)
    pt.to_excel(excel_writer=writer, sheet_name='13-skuClass', inf_rep='')

    idx14 = ['order_class']
    pt = out_order_qty_pivot(df, index=idx14)
    pt.to_excel(excel_writer=writer, sheet_name='14-orderClass', inf_rep='')

    idx15 = ['sku_size_comb']
    # cols = ['pltN', 'ctnN', 'pltQ', 'ctnQ', 'pieceQ', 'total_qty', 'VOL']
    pt = out_sku_qty_pivot(df, index=idx15)
    pt.to_excel(excel_writer=writer, sheet_name='15-sku_size_comb', inf_rep='')

    idx16 = ['EIV_class']
    # cols = ['pltN', 'ctnN', 'pltQ', 'ctnQ', 'pieceQ', 'total_qty', 'VOL']
    pt = out_sku_qty_pivot(df, index=idx16)
    pt.to_excel(excel_writer=writer, sheet_name='16-sku_EIV_class', inf_rep='')

    idx17 = ['ABC_MPDV', 'order_ZS_tag']
    res = out_sku_qty_pivot(df_zs, index=idx17)
    res.to_excel(excel_writer=writer, sheet_name='17-ABC_MPDV(zs)', inf_rep='')

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

    idx23 = ['order_date']
    toteV = config.TOTE['valid_vol']
    daily_order = order_num(df, toteV=toteV, index=idx23)
    daily_order.to_excel(excel_writer=writer, sheet_name='23-dailyOrder', inf_rep='')

    """
    ## 3. ABC透视表
    """
    # DQ-ABC&rele 透视
    idx31 = ['ABC_MPDQ']
    order_type = out_order_pivot(df, index=idx31)
    order_type.to_excel(excel_writer=writer, sheet_name='31-DQ_ABC', inf_rep='')

    idx32 = ['DQ_ABC_rele']
    order_type = out_order_pivot(df, index=idx32)
    order_type.to_excel(excel_writer=writer, sheet_name='32-DQ_ABC_rele', inf_rep='')

    # # DQ-ABC&rele 透视
    # idx33 = ['ABC_MPDQ', 'DQ-ABC_rele']
    # order_type = out_order_pivot(df, index=idx33)
    # order_type.to_excel(excel_writer=writer, sheet_name='32-DQ_ABC&rele', inf_rep='')

    # DK-ABC 透视
    idx34 = ['ABC_MPDN']
    order_releSize = out_order_pivot(df, index=idx34)
    order_releSize.to_excel(excel_writer=writer, sheet_name='33-DK_ABC', inf_rep='')

    idx35 = ['DK_ABC_rele']
    order_type = out_order_pivot(df, index=idx35)
    order_type.to_excel(excel_writer=writer, sheet_name='34-DK_ABC_rele', inf_rep='')

    # # DK-ABC&rele 透视
    # idx36 = ['ABC_MPDN', 'DK-ABC_rele']
    # order_releSize = out_order_pivot(df, index=idx36)
    # order_releSize.to_excel(excel_writer=writer, sheet_name='34-DK_ABC&rele', inf_rep='')

    """
    ## 4. EQ透视表
    """
    # EQ_class 透视
    idx41 = ['EQ_class']
    order_type = out_order_pivot(df, index=idx41)
    order_type.to_excel(excel_writer=writer, sheet_name='41-EQ_class', inf_rep='')

    idx411 = ['EQ_class_Z']
    order_type = out_order_pivot(df_z, index=idx411)
    order_type.to_excel(excel_writer=writer, sheet_name='41.1-EQ_class_Z', inf_rep='')

    idx412 = ['EQ_class_S']
    order_type = out_order_pivot(df_s, index=idx412)
    order_type.to_excel(excel_writer=writer, sheet_name='41.2-EQ_class_S', inf_rep='')

    # EK_class 透视
    idx42 = ['EN_class']
    order_type = out_order_pivot(df, index=idx42)
    order_type.to_excel(excel_writer=writer, sheet_name='42-EN_class', inf_rep='')

    idx421 = ['EN_class_Z']
    order_type = out_order_pivot(df_z, index=idx421)
    order_type.to_excel(excel_writer=writer, sheet_name='42.1-EN_class_Z', inf_rep='')

    idx422 = ['EN_class_S']
    order_type = out_order_pivot(df_s, index=idx422)
    order_type.to_excel(excel_writer=writer, sheet_name='42.2-EN_class_S', inf_rep='')

    # EK_class 透视
    idx43 = ['EV_class']
    order_type = out_order_pivot(df, index=idx43)
    order_type.to_excel(excel_writer=writer, sheet_name='43-EV_class', inf_rep='')

    idx431 = ['EV_class_Z']
    order_type = out_order_pivot(df_z, index=idx431)
    order_type.to_excel(excel_writer=writer, sheet_name='43.1-EV_class_Z', inf_rep='')

    idx432 = ['EV_class_S']
    order_type = out_order_pivot(df_s, index=idx432)
    order_type.to_excel(excel_writer=writer, sheet_name='43.2-EV_class_S', inf_rep='')

    # order-structure & EQ 透视
    # idx44 = ['order_structure', 'EQ_class']
    # order_releSize = out_order_pivot(df, index=idx44)
    # order_releSize.to_excel(excel_writer=writer, sheet_name='44-order&EQ', inf_rep='')
    #
    # # order-structure & EN 透视
    # idx45 = ['order_structure', 'EN_class']
    # order_releSize = out_order_pivot(df, index=idx45)
    # order_releSize.to_excel(excel_writer=writer, sheet_name='45-order&EN', inf_rep='')
    #
    # # order-structure & EN 透视
    # idx46 = ['order_structure', 'EV_class']
    # order_releSize = out_order_pivot(df, index=idx46)
    # order_releSize.to_excel(excel_writer=writer, sheet_name='46-order&EV', inf_rep='')

    # # size & order-structure & EQ 透视
    # idx46 = ['size_rele', 'order_structure', 'EQ_class']
    # order_releSize = out_order_pivot(df, index=idx46)
    # order_releSize.to_excel(excel_writer=writer, sheet_name='45-order&EQ', inf_rep='')
    #
    # # size & order-structure & EQ 透视
    # idx47 = ['size_rele', 'order_structure', 'EN_class']
    # order_releSize = out_order_pivot(df, index=idx47)
    # order_releSize.to_excel(excel_writer=writer, sheet_name='46-order&EN', inf_rep='')

    ## 增加 order维度，订单行整箱/散件拆分的 EQ, EN分级

    idx44 = ['EV_class', 'order_ZS_tag', 'EQ_class_all', 'EN_class_all']
    res = out_order_pivot(df_zs, index=idx44)
    res.to_excel(excel_writer=writer, sheet_name='44-EV_EQ_EN', inf_rep='')

    idx45 = ['EV_class', 'order_ZS_tag', 'EIV_class_zs']
    res = out_order_pivot(df_zs, index=idx45)
    res.to_excel(excel_writer=writer, sheet_name='45-EV_EIV(zs)', inf_rep='')

    """
    ## 5. PC透视表
    """
    # EQ_class 透视
    idx51 = ['EV_class', 'EIV_class']
    order_type = out_order_pivot(df, index=idx51)
    order_type.to_excel(excel_writer=writer, sheet_name='51-EV_EIV_class', inf_rep='')

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

    layout_format(writer)

    writer.save()
    writer.close()
