# -*- coding: utf-8 -*-

from load_data import *


def get_category_correction_data(sku_fileName):
    sku_data = rename_sku_detail(sku_fileName)

    #   column_name = ['warehouse_name','SKU_ID','skuName',
    #                  'I_class','II_class','III_class','IV_class',
    #                  'weight','long','width','height',
    #                  'fullCaseUnit','f_long','f_width','f_height']

    # 透视2.1
    I_Class = sku_data.groupby('I_class').agg({'weight': np.max, 'longest_side': np.max})

    # 透视2.5
    IV_Class_W_L = sku_data.groupby('IV_class').agg({'weight': np.max, 'longest_side': np.max})
