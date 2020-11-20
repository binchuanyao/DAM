# -*- coding: utf-8 -*-
import numpy as np


class Config:
    def __init__(self):

        # PARM1-Basic sheet basic parameter
        # 料箱
        self.TOTE = {
            'long': 600,
            'width': 400,
            'height': 330,
            'valid_height': 0,
            'rate': 0.7,
            'min_wid': 0,
            'max_wid': 0,
            'layer': 1,
            'sku_upper': 1,
            'separate_locs': 2,
            'combine_locs': 1,
            'unit_weight': 3,
            'weight_upper': 27,
            'unit_square': 0
        }

        # 托盘存储
        self.PALLET_STOCK = {
            'long': 1200,
            'width': 1000,
            'plt_height': 150,
            'valid_height': 1300,
            'rate': 0.8,
            'min_wid': 0,
            'max_wid': 0,
            'layer': 1,
            'sku_upper': 1,
            'separate_locs': 0,
            'combine_locs': 0,
            'unit_weight': 10,
            'weight_upper': 990,
            'unit_square': 0
        }

        # 托盘拣选
        self.PALLET_PICK = {
            'long': 1200,
            'width': 1000,
            'height': 150,
            'valid_height': 1300,
            'rate': 0.4,
            'min_wid': 0,
            'max_wid': 0,
            'layer': 1,
            'sku_upper': 1,
            'separate_locs': 2,
            'combine_locs': 1,
            'unit_weight': 10,
            'unit_square': 3.15,
            'to_self.PALLET_PICK': 1.0
        }

        # 轻型货架(D300)
        self.SHELF_D300 = {
            'name': '轻型货架(D300)',
            'long': 1200,
            'width': 300,
            'height': 1600,
            'rate': 0.4,
            'min_wid': 100,
            'max_wid': 400,
            'layer': 4,
            'sku_upper': 2,
            'separate_locs': 2,
            'combine_locs': 1,
            'unit_square': 1.35,
            'replenish': '整箱'
        }

        # 轻型货架(D500)
        self.SHELF_D500 = {
            'name': '轻型货架(D500)',
            'long': 1200,
            'width': 500,
            'height': 1600,
            'rate': 0.4,
            'min_wid': 240,
            'max_wid': 0,
            'layer': 4,
            'sku_upper': 2,
            'separate_locs': 2,
            'combine_locs': 1,
            'unit_square': 1.65,
            'replenish': '整箱'
        }

        # 轻型货架(D600)
        self.SHELF_D600 = {
            'name': '轻型货架(D600)',
            'long': 1200,
            'width': 600,
            'height': 1600,
            'rate': 0.4,
            'min_wid': 240,
            'max_wid': 0,
            'layer': 4,
            'sku_upper': 2,
            'separate_locs': 2,
            'combine_locs': 1,
            'unit_square': 1.8,
            'replenish': '整箱'
        }

        # 多穿(箱式双深)
        self.SHUTTLE = {
            'long': 80000,
            'width': 4000,
            'height': 10500,
            'rate': 0.6,
            'layer': 16,
            'unit_square': 0.05,
            'replenish': '整箱'
        }

        # 托盘单深 ASRS 24米
        self.ASRS_24_SINGLE = {
            'unit_square': 0.376
        }

        self.ASRS_36_SINGLE = {
            'unit_square': 0.218
        }

        self.ASRS_36_DOUBLE = {
            'long': 120000,
            'width': 7150,
            'height': 35000,
            'rate': 0.8,
            'layer': 20,
            'unit_square': 0.17
        }

        # PARM9 异常判断阈值
        self.THRESHOLD = {
            'pltWeight_lower': 25,
            'pltWeight_upper': 2400,
            'longest_upper': 2500,
            'weight_upper': 100
        }

        # PARM2 P&C分级,区间端点
        self.TOTE_CLASS_INTERVAL = [0, 0.5, 1, 2, 5, 7, 10]
        self.PLT_CLASS_INTERVAL = [0, 0.5, 1, 2, 5, 10, 20, 50, 100, 200, 500, 1000, 2000, 3000]
        self.CTN_QTY_INTERVAL = [0, 0.5, 1, 2, 5, 10, 20, 50, 100, 200, 500, 1000, 2000, 3000]
        self.CTN_QTY_CLASS = []
        self.PC_CLASS = []

        # PARM2 EN&EQ&IQ&IK Class 区间
        self.QTY_CLASS_INTERVAL = [0, 1, 5, 10, 20, 50, 100, 200, 500, 1000, 2000, 5000, 10000, 20000, 50000]
        self.QTY_CLASS = []

        # PARM2 days Class 区间
        self.DAYS_CLASS_INTERVAL = [0, 1, 5, 10, 20, 31]
        self.DAYS_CLASS = []

        # PARM3 SIZE_CLASS 件型划分 & 原箱出库阈值
        self.SIZE = {
            'type': ['1S', '2M', '3B', '4H'],
            'ctn_type': ['1CS', '2CM', '3CB', '4CH'],
            'longest': [400, 600, 1200, 1200],
            'l_measure': ['<=', '<=', '<=', '>'],
            'middle': [300, np.NaN, np.NaN, np.NaN],
            'm_measure': ['<=', np.NaN, np.NaN, np.NaN],
            'weight': [3, 10, np.NaN, np.NaN],
            'w_measure': ['<=', '<=', np.NaN, np.NaN],
            'container': ['料箱', '拣货车', '拣货车', '托盘']
        }

        self.ORG_CARTON = {
            'type': ['01未到原箱出库阀值', '02满足原箱阀值可设备分拣', '03满足原箱阀值不可设备分拣'],
            'longest_lower': [0, 400, 650],
            'longest_upper': [400, 650, 1200],
            'l_measure': ['<=', '<=', '<=', '>'],
        }

        # PARM4 ABC_CLASS ABC划分
        self.ABC_INTERVAL = [0.2, 0.5, 0.8, 1]
        self.ABC_CLASS = ['1SA', '20A', '30B', '40C', '50D']

        # PARM5 托盘重量分级,区间端点
        self.PLT_WEIGHT_INTERVAL = [0, 50] + list(range(100, 2100, 100)) + [2400]
        self.PLT_WEIGHT_CLASS = []

        # PARM6 料箱重量分级,区间端点
        self.TOTE_WEIGHT_INTERVAL = list(range(0, 35, 5)) + [50, 80, 100, 200, 500]
        self.TOTE_WEIGHT_CLASS = []

        # PARM7 StockTactic 存储策略相关参数
        # 存储设备,2维列表,[设备，补货单元，件型，对应SKU属性]
        self.STOCK_TACTIC = {
            'isShuttle': 'Y',
            'support_days': 1,
            # 存储设备,2维列表,[0:设备，1:件型，2:对应SKU属性]
            'equipment': [
                ['多穿', ['1S'], ('MADQ_30B', '高值')],
                ['轻架', ['1S'], ()],
                ['托盘', ['2M', '3B', '4H'], ()],
            ],
            'mode': ['存拣合一', '存拣分离'],
            'mode_interval': [0.5, 1],
            'plt_interval': 0.5,
            'tote_interval': 1
        }

        # PARM8 Design 规划相关参数
        self.CURRENT_PARA = {
            'peak_order': 200000,
            'order': 200000,
            'sku': 5000,
            'allot_rate': 0,
            'inventory_days': 102,
            'sku_increase_rate': 0,

            'single_item_single_qty': [1, 0.3],  # 单品单件单均件数，占比
            'single_item_multi_qty': [3, 0.4],  # 单品多件单均件数，占比
            'multi_item_avg_qty': [4, 0.3],  # 多品单均件数，占比
            'avg_qty_per_order': 3.02,  # 全部订单单均件数

            'purchase_rate': 0.03,  # 采购入库散件商品数量占比
        }

        self.DESIGN_PARA = {
            'peak_order': 300000,  # 日峰销售出库单量
            'order': 200000,  # 日均销售出库单量
            'sku': 5000,
            'allot_rate': 0.3,  # 调拨出库件数占比
            'inventory_days': 102,  # 库存天数(ABC)
            'sku_net_growth_rate': 0.0,  # 规划SKU数量净增长率，为0时，件数增长与SKU数量同比增长

            'single_item_single_qty': [1, 0.3],  # 单品单件单均件数，占比
            'single_item_multi_qty': [3, 0.4],  # 单品多件单均件数，占比
            'multi_item_avg_qty': [4, 0.3],  # 多品单均件数，占比
            'avg_qty_per_order': 3.02,  # 全部订单单均件数
        }

        self.DESIGN_COEFFICIENT = {
            'peak_order_coe': 1,  # 规划峰值销售出库/现状均值销售出库
            'sku_num_coe': 1,  # 规划SKU数量(出库件数影响SKU数量变化)/现有SKU数量
            'single_sku_qty_coe': 1,  # 规划单一SKU库存件数变幅(随SKU数量及库存周期改变-含调拨)
            'total_qty_coe': 1,  # 规划总库存件数变幅(随库存周期改变-含调拨)
            'inventory_days_coe': 1  # 规划/现有库存天数
        }

        ## work_hours 工作环节
        self.WORK_HOURS = {
            'outbound_shift': 2,
            'inbound_shift': 2,
            'outbound_hours': 8,
            'inbound_hours': 12,
            'valid_rate': 0.7
        }

        ## 包材 Packing material
        self.PACKAGE_MATERIAL = {
            'carton_rate': 0.95,
            'not_carton_rate': 0.05,
            'carton_pallet': 900,
            'not_carton_pallet': 2000
        }

    def run(self):
        self.calculate_stock_unit()
        self.get_PC_class()
        self.get_ctn_qty_class()
        self.get_qty_class()
        self.get_days_class()
        self.get_pallet_weight_class()
        self.get_tote_weight_class()
        self.update_design_coefficient()

    def calculate_stock_unit(self):
        '''
        根据基础参数计算存储单元参数
        '''
        self.PALLET_STOCK['specified_vol'] = self.PALLET_STOCK['long'] * self.PALLET_STOCK['width'] * self.PALLET_STOCK[
            'valid_height']
        self.PALLET_STOCK['valid_vol'] = self.PALLET_STOCK['specified_vol'] * self.PALLET_STOCK['rate']

        self.PALLET_PICK['specified_vol'] = self.PALLET_PICK['long'] * self.PALLET_PICK['width'] * self.PALLET_PICK[
            'valid_height']
        self.PALLET_PICK['valid_vol'] = self.PALLET_PICK['specified_vol'] * self.PALLET_PICK['rate']

        self.SHELF_D300['specified_vol'] = self.SHELF_D300['long'] * self.SHELF_D300['width'] * self.SHELF_D300[
            'height']
        self.SHELF_D300['valid_vol'] = self.SHELF_D300['specified_vol'] * self.SHELF_D300['rate']
        self.SHELF_D300['2plt'] = ((self.SHELF_D300['valid_vol'] / self.SHELF_D300['unit_square'])
                                   / (self.PALLET_PICK['valid_vol'] / self.PALLET_PICK['unit_square'])) \
                                  * ((self.SHELF_D300['long'] * self.SHELF_D300['width']) / (
                self.PALLET_PICK['long'] * self.PALLET_PICK['width']))
        self.SHELF_D300['unit_square_stock'] = (self.SHELF_D300['valid_vol'] / self.SHELF_D300['unit_square']) / (
                self.PALLET_PICK['valid_vol'] / self.PALLET_PICK['unit_square'])

        self.SHELF_D500['specified_vol'] = self.SHELF_D500['long'] * self.SHELF_D500['width'] * self.SHELF_D500[
            'height']
        self.SHELF_D500['valid_vol'] = self.SHELF_D500['specified_vol'] * self.SHELF_D500['rate']
        self.SHELF_D500['2plt'] = ((self.SHELF_D500['valid_vol'] / self.SHELF_D500['unit_square'])
                                   / (self.PALLET_PICK['valid_vol'] / self.PALLET_PICK['unit_square'])) \
                                  * ((self.SHELF_D500['long'] * self.SHELF_D500['width']) / (
                self.PALLET_PICK['long'] * self.PALLET_PICK['width']))
        self.SHELF_D500['unit_square_stock'] = (self.SHELF_D500['valid_vol'] / self.SHELF_D500['unit_square']) \
                                               / (self.PALLET_PICK['valid_vol'] / self.PALLET_PICK['unit_square'])

        self.SHELF_D600['specified_vol'] = self.SHELF_D600['long'] * self.SHELF_D600['width'] * self.SHELF_D600[
            'height']
        self.SHELF_D600['valid_vol'] = self.SHELF_D600['specified_vol'] * self.SHELF_D600['rate']
        self.SHELF_D600['2plt'] = ((self.SHELF_D600['valid_vol'] / self.SHELF_D600['unit_square'])
                                   / (self.PALLET_PICK['valid_vol'] / self.PALLET_PICK['unit_square'])) \
                                  * ((self.SHELF_D600['long'] * self.SHELF_D600['width']) / (
                self.PALLET_PICK['long'] * self.PALLET_PICK['width']))
        self.SHELF_D600['unit_square_stock'] = (self.SHELF_D600['valid_vol'] / self.SHELF_D600['unit_square']) / (
                self.PALLET_PICK['valid_vol'] / self.PALLET_PICK['unit_square'])

        self.TOTE['specified_vol'] = self.TOTE['long'] * self.TOTE['width'] * self.TOTE['height']
        self.TOTE['valid_vol'] = self.TOTE['specified_vol'] * self.TOTE['rate']
        self.TOTE['2plt'] = ((self.TOTE['long'] * self.TOTE['width'] * self.TOTE['height']) / (
                self.SHELF_D500['long'] * self.SHELF_D500['width'] * self.SHELF_D500['height']) * self.SHELF_D500[
                                 '2plt'])

    def get_PC_class(self):
        '''
        PARM2 P&C Class  
        '''
        len_TOTE = len(self.TOTE_CLASS_INTERVAL) - 1
        len_PALLET = len(self.PLT_CLASS_INTERVAL)

        rank_num = len_TOTE + len_PALLET
        for i in range(rank_num):
            tmp = []
            if i == rank_num - 1:
                tmp.append("P" + str(i - len_TOTE + 1) + "(" + str(self.PLT_CLASS_INTERVAL[i - len_TOTE]) + ",+)")
                tmp.append(self.PLT_CLASS_INTERVAL[i - len_TOTE])
                tmp.append(np.inf)
                # print(tmp)
                self.PC_CLASS.append(tmp)
            elif i < len_TOTE:
                tmp.append("C0" + str(i + 1) + "(" + str(self.TOTE_CLASS_INTERVAL[i]) + "," + str(
                    self.TOTE_CLASS_INTERVAL[i + 1]) + "]")
                tmp.append(self.TOTE_CLASS_INTERVAL[i])
                tmp.append(self.TOTE_CLASS_INTERVAL[i + 1])
                # print(tmp)
                self.PC_CLASS.append(tmp)
            else:
                if i - len_TOTE < 9:
                    tmp.append(
                        "P0" + str(i - len_TOTE + 1) + "(" + str(self.PLT_CLASS_INTERVAL[i - len_TOTE]) + "," + str(
                            self.PLT_CLASS_INTERVAL[i - len_TOTE + 1]) + "]")
                    tmp.append(self.PLT_CLASS_INTERVAL[i - len_TOTE])
                    tmp.append(self.PLT_CLASS_INTERVAL[i - len_TOTE + 1])
                    # print(tmp)
                    self.PC_CLASS.append(tmp)
                else:
                    tmp.append(
                        "P" + str(i - len_TOTE + 1) + "(" + str(self.PLT_CLASS_INTERVAL[i - len_TOTE]) + "," + str(
                            self.PLT_CLASS_INTERVAL[i - len_TOTE + 1]) + "]")
                    tmp.append(self.PLT_CLASS_INTERVAL[i - len_TOTE])
                    tmp.append(self.PLT_CLASS_INTERVAL[i - len_TOTE + 1])
                    # print(tmp)
                    self.PC_CLASS.append(tmp)
        # pprint.pprint(self.PC_CLASS)

    def get_ctn_qty_class(self):
        """
        折合料箱数量分级
        :return:
        """
        len_QTY = len(self.CTN_QTY_INTERVAL)

        for i in range(len_QTY):
            tmp = []
            if i == len_QTY - 1:
                tmp.append("C" + str(i + 1) + "(" + str(self.CTN_QTY_INTERVAL[i]) + ",+)")
                tmp.append(self.CTN_QTY_INTERVAL[i])
                tmp.append("+")
                self.CTN_QTY_CLASS.append(tmp)
            elif i < 9:
                tmp.append(
                    "C0" + str(i + 1) + "(" + str(self.CTN_QTY_INTERVAL[i]) + "," + str(
                        self.CTN_QTY_INTERVAL[i + 1]) + "]")
                tmp.append(self.CTN_QTY_INTERVAL[i])
                tmp.append(self.CTN_QTY_INTERVAL[i + 1])
                self.CTN_QTY_CLASS.append(tmp)
            else:
                tmp.append(
                    "C" + str(i + 1) + "(" + str(self.CTN_QTY_INTERVAL[i]) + "," + str(
                        self.CTN_QTY_INTERVAL[i + 1]) + "]")
                tmp.append(self.CTN_QTY_INTERVAL[i])
                tmp.append(self.CTN_QTY_INTERVAL[i + 1])
                self.CTN_QTY_CLASS.append(tmp)
        # pprint.pprint(self.CTN_QTY_CLASS)

    def get_pallet_weight_class(self):
        '''
        PARM5 PalletWeightClass
        '''
        len_plt_weight = len(self.PLT_WEIGHT_INTERVAL)

        for i in range(len_plt_weight - 1):
            tmp = []
            if i < 9:
                tmp.append(
                    "W-P0" + str(i + 1) + "(" + str(self.PLT_WEIGHT_INTERVAL[i]) + "," + str(
                        self.PLT_WEIGHT_INTERVAL[i + 1]) + "]")
                tmp.append(self.PLT_WEIGHT_INTERVAL[i])
                tmp.append(self.PLT_WEIGHT_INTERVAL[i + 1])
                # print(tmp)
                self.PLT_WEIGHT_CLASS.append(tmp)
            else:
                tmp.append(
                    "W-P" + str(i + 1) + "(" + str(self.PLT_WEIGHT_INTERVAL[i]) + "," + str(
                        self.PLT_WEIGHT_INTERVAL[i + 1]) + "]")
                tmp.append(self.PLT_WEIGHT_INTERVAL[i])
                tmp.append(self.PLT_WEIGHT_INTERVAL[i + 1])
                # print(tmp)
                self.PLT_WEIGHT_CLASS.append(tmp)

    def get_tote_weight_class(self):
        '''
        PARM6 ToteWeightClass
        '''

        len_tote_weight = len(self.TOTE_WEIGHT_INTERVAL)

        for i in range(len_tote_weight - 1):
            tmp = []
            if i < 9:
                tmp.append(
                    "W-T0" + str(i + 1) + "(" + str(self.TOTE_WEIGHT_INTERVAL[i]) + "," + str(
                        self.TOTE_WEIGHT_INTERVAL[i + 1]) + "]")
                tmp.append(self.TOTE_WEIGHT_INTERVAL[i])
                tmp.append(self.TOTE_WEIGHT_INTERVAL[i + 1])
                # print(tmp)
                self.TOTE_WEIGHT_CLASS.append(tmp)
            else:
                tmp.append(
                    "W-T" + str(i + 1) + "(" + str(self.TOTE_WEIGHT_INTERVAL[i]) + "," + str(
                        self.TOTE_WEIGHT_INTERVAL[i + 1]) + "]")
                tmp.append(self.TOTE_WEIGHT_INTERVAL[i])
                tmp.append(self.TOTE_WEIGHT_INTERVAL[i + 1])
                # print(tmp)
                self.TOTE_WEIGHT_CLASS.append(tmp)

    def get_qty_class(self):
        '''
        PARM2 EN&EQ&IQ&IK Class
        '''

        len_QTY = len(self.QTY_CLASS_INTERVAL)

        for i in range(len_QTY):
            tmp = []
            if i == len_QTY - 1:
                tmp.append("Q" + str(i + 1) + "(" + str(self.QTY_CLASS_INTERVAL[i]) + ",+)")
                tmp.append(self.QTY_CLASS_INTERVAL[i])
                tmp.append(np.inf)
                self.QTY_CLASS.append(tmp)
            elif i < 9:
                tmp.append(
                    "Q0" + str(i + 1) + "(" + str(self.QTY_CLASS_INTERVAL[i]) + "," + str(
                        self.QTY_CLASS_INTERVAL[i + 1]) + "]")
                tmp.append(self.QTY_CLASS_INTERVAL[i])
                tmp.append(self.QTY_CLASS_INTERVAL[i + 1])
                self.QTY_CLASS.append(tmp)
            else:
                tmp.append(
                    "Q" + str(i + 1) + "(" + str(self.QTY_CLASS_INTERVAL[i]) + "," + str(
                        self.QTY_CLASS_INTERVAL[i + 1]) + "]")
                tmp.append(self.QTY_CLASS_INTERVAL[i])
                tmp.append(self.QTY_CLASS_INTERVAL[i + 1])
                self.QTY_CLASS.append(tmp)
        # pprint.pprint(self.QTY_CLASS)

    def get_days_class(self):
        '''
        PARM2 DAYS Class
        '''

        len_DAYS = len(self.DAYS_CLASS_INTERVAL)

        for i in range(len_DAYS - 1):
            tmp = []
            if i < 9:
                tmp.append(
                    "D0" + str(i + 1) + "(" + str(self.DAYS_CLASS_INTERVAL[i]) + "," + str(
                        self.DAYS_CLASS_INTERVAL[i + 1]) + "]")
                tmp.append(self.DAYS_CLASS_INTERVAL[i])
                tmp.append(self.DAYS_CLASS_INTERVAL[i + 1])
                self.DAYS_CLASS.append(tmp)
            else:
                tmp.append(
                    "D" + str(i + 1) + "(" + str(self.DAYS_CLASS_INTERVAL[i]) + "," + str(
                        self.DAYS_CLASS_INTERVAL[i + 1]) + "]")
                tmp.append(self.DAYS_CLASS_INTERVAL[i])
                tmp.append(self.DAYS_CLASS_INTERVAL[i + 1])
                self.DAYS_CLASS.append(tmp)

    def update_design_coefficient(self):
        if self.CURRENT_PARA['inventory_days'] != 0:
            self.DESIGN_COEFFICIENT['inventory_days_coe'] = self.DESIGN_PARA['inventory_days'] / self.CURRENT_PARA[
                'inventory_days']

        self.DESIGN_COEFFICIENT['total_qty_coe'] = ((self.DESIGN_PARA['order'] * self.DESIGN_PARA['avg_qty_per_order']
                                                     / (1 - self.DESIGN_PARA['allot_rate']))
                                                    / (self.CURRENT_PARA['order'] * self.CURRENT_PARA[
                    'avg_qty_per_order']
                                                       / (1 - self.CURRENT_PARA['allot_rate']))) \
                                                   * self.DESIGN_COEFFICIENT['inventory_days_coe']

        self.DESIGN_COEFFICIENT['peak_order_coe'] = (self.DESIGN_PARA['order'] * self.DESIGN_PARA['avg_qty_per_order']) \
                                                    / (self.CURRENT_PARA['order'] * self.CURRENT_PARA[
            'avg_qty_per_order'])

        self.DESIGN_COEFFICIENT['sku_num_coe'] = 1 + (
                (self.DESIGN_PARA['peak_order'] * self.DESIGN_PARA['avg_qty_per_order']
                 / (1 - self.DESIGN_PARA['allot_rate']))
                / (self.CURRENT_PARA['peak_order'] * self.CURRENT_PARA['avg_qty_per_order']
                   / (1 - self.CURRENT_PARA['allot_rate'])) - 1) \
                                                 * self.DESIGN_PARA['sku_net_growth_rate']

        self.DESIGN_COEFFICIENT['single_sku_qty_coe'] = ((self.DESIGN_PARA['order'] * self.DESIGN_PARA[
            'avg_qty_per_order']
                                                          / (1 - self.DESIGN_PARA['allot_rate']))
                                                         / (self.CURRENT_PARA['order'] * self.CURRENT_PARA[
                    'avg_qty_per_order']
                                                            / (1 - self.CURRENT_PARA['allot_rate']))) \
                                                        * (self.DESIGN_PARA['inventory_days'] / self.CURRENT_PARA[
            'inventory_days']) \
                                                        / self.DESIGN_COEFFICIENT['sku_num_coe']
