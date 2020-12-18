# -*- coding:UTF-8 -*-
import pandas as pd


class treeNode:
    def __init__(self, nameValue, numOccur, parentNode):
        self.name = nameValue
        self.count = numOccur
        self.nodeLink = None
        self.parent = parentNode
        self.children = {}

    def inc(self, numOccur):
        self.count += numOccur

    def disp(self, ind=1):
        print('  ' * ind, self.name, ' ', self.count)
        for child in self.children.values():
            child.disp(ind + 1)


def updateHeader(nodeToTest, targetNode):
    while nodeToTest.nodeLink != None:
        nodeToTest = nodeToTest.nodeLink
    nodeToTest.nodeLink = targetNode


def updateFPtree(items, inTree, headerTable, count):
    if items[0] in inTree.children:
        # 判断items的第一个结点是否已作为子结点
        inTree.children[items[0]].inc(count)
    else:
        # 创建新的分支
        inTree.children[items[0]] = treeNode(items[0], count, inTree)
        # 更新相应频繁项集的链表，往后添加
        if headerTable[items[0]][1] == None:
            headerTable[items[0]][1] = inTree.children[items[0]]
        else:
            updateHeader(headerTable[items[0]][1], inTree.children[items[0]])
    # 递归
    if len(items) > 1:
        updateFPtree(items[1::], inTree.children[items[0]], headerTable, count)


def createFPtree(dataSet, minSup=1):
    headerTable = {}
    for trans in dataSet:
        for item in trans:
            headerTable[item] = headerTable.get(item, 0) + dataSet[trans]
    for k in list(headerTable.keys()):
        if headerTable[k] < minSup:
            del (headerTable[k])  # 删除不满足最小支持度的元素
    freqItemSet = set(headerTable.keys())  # 满足最小支持度的频繁项集
    if len(freqItemSet) == 0:
        return None, None
    for k in headerTable:
        headerTable[k] = [headerTable[k], None]  # element: [count, node]

    retTree = treeNode('Null Set', 1, None)
    for tranSet, count in dataSet.items():
        # dataSet：[element, count]
        localD = {}
        for item in tranSet:
            if item in freqItemSet:  # 过滤，只取该样本中满足最小支持度的频繁项
                localD[item] = headerTable[item][0]  # element : count
        if len(localD) > 0:
            # 根据全局频数从大到小对单样本排序
            orderedItem = [v[0] for v in sorted(localD.items(), key=lambda p: p[1], reverse=True)]
            # 用过滤且排序后的样本更新树
            updateFPtree(orderedItem, retTree, headerTable, count)
    return retTree, headerTable


# 数据集
def load_test_data():
    simDat = [['r', 'z', 'h', 'j', 'p'],
              ['z', 'y', 'x', 'w', 'v', 'u', 't', 's'],
              ['z'],
              ['r', 'x', 'n', 'o', 's'],
              ['y', 'r', 'x', 'z', 'q', 't', 'p'],
              ['y', 'z', 'x', 'e', 'q', 's', 't', 'm']]
    return simDat


def load_out_data(file_name):
    df = pd.read_excel(file_name)
    df.columns = ['warehouse', 'order_date', 'order_week', 'order_state', 'm_orderID',
                  'orderID', 'isSplit', 'order_type', 'operation_mode', 'SKU_ID', 'total_qty',
                  'deli_type', 'package_size', 'package_weight', 'package_long', 'package_width',
                  'package_height', 'package_num', 'province', 'city']
    order_dict = df.groupby('orderID')['SKU_ID'].apply(list).to_dict()

    # order_list = df.groupby('orderID')['SKU_ID'].apply(list).to_list()
    data = []
    for v in order_dict.values():
        data.append(v)
    return data

# 构造成 element : count 的形式
def createInitSet(dataSet):
    retDict = {}
    for trans in dataSet:
        key = frozenset(trans)
        if key in retDict:
            retDict[frozenset(trans)] += 1
        else:
            retDict[frozenset(trans)] = 1
    return retDict


# 递归回溯
def ascendFPtree(leafNode, prefixPath):
    if leafNode.parent != None:
        prefixPath.append(leafNode.name)
        ascendFPtree(leafNode.parent, prefixPath)


# 条件模式基
def findPrefixPath(basePat, myHeaderTab):
    treeNode = myHeaderTab[basePat][1]  # basePat在FP树中的第一个结点
    condPats = {}
    while treeNode != None:
        prefixPath = []
        ascendFPtree(treeNode, prefixPath)  # prefixPath是倒过来的，从treeNode开始到根
        if len(prefixPath) > 1:
            condPats[frozenset(prefixPath[1:])] = treeNode.count  # 关联treeNode的计数
        treeNode = treeNode.nodeLink  # 下一个basePat结点
    return condPats


def mineFPtree(inTree, headerTable, minSup, preFix, freqItemList):
    # 最开始的频繁项集是headerTable中的各元素
    bigL = [v[0] for v in sorted(headerTable.items(), key=lambda p: p[0])]  # 根据频繁项的总频次排序
    for basePat in bigL:  # 对每个频繁项
        newFreqSet = preFix.copy()
        newFreqSet.add(basePat)
        freqItemList.append(newFreqSet)
        condPattBases = findPrefixPath(basePat, headerTable)  # 当前频繁项集的条件模式基
        myCondTree, myHead = createFPtree(condPattBases, minSup)  # 构造当前频繁项的条件FP树
        if myHead != None:
            # print 'conditional tree for: ', newFreqSet
            # myCondTree.disp(1)
            mineFPtree(myCondTree, myHead, minSup, newFreqSet, freqItemList)  # 递归挖掘条件FP树

 # def FpGrowth(database, minSup=3):
 #        f1, d1 = getFreq(database, minSup)  # 求第一次频繁项集,并返回一个字典存放支持度，且按大到小排序，返回频繁项和存放频繁项支持度的字典
 #        rootNode = createRootNode()  # 创建根节点
 #        # print(f1,d1)        #[['a'], ['b'], ['c'], ['d']]      {'a': 4, 'b': 4, 'c': 4, 'd': 3}
 #
 #        # 第一步建造树
 #        buildTree(database, rootNode, f1)
 #        # indexTableHead = {}     #创建线索的表头，一个链表
 #        indexTableHead = createIndexTableHead(**d1)  # **d1 就是传了个值，给了它一个拷贝，修改函数里面的这个拷贝，不会影响到外面的这个变量的值
 #        buildIndex(rootNode, indexTableHead)  # 创建线索，用这个表头
 #
 #        # print('构建线索后，前序遍历如下：')
 #        # FpNode.checkFirstTree(rootNode)
 #        # print('构建线索后，后序遍历如下：')
 #        # FpNode.checkBehindTree(rootNode)
 #
 #        freAll = []  # 所有频繁项集
 #        freAllDic = {}  # 所有频繁项集的支持度
 #
 #        # 第二步    进行频繁项集的挖掘，从表头header的最后一项开始。
 #        for commonId in f1[-1::-1]:  # 倒叙 从支持度小的到支持度大的，进行挖掘
 #            idK = str(commonId[0])
 #            newDataK = getNewRecord(idK, **indexTableHead)  # 传入这个表头的一个拷贝， 函数返回挖掘出来的新记录
 #            fk, dk = getFreq(newDataK, minSup)  # 对新数据集求频繁项集
 #            # print(fk,dk)
 #            base, itemSup = getAllConditionBase(newDataK, idK, fk, minSup, **dk)  # 得到当前节点的条件频繁模式集，返回
 #            # 有可能会发生这样一种情况，条件基是 a ，然后fk，dk为空，结果这个函数又返回了 a，那么最后的结果中，就会出现 a，a  这种情况，处理方法请往下看
 #
 #            # print(base，idK)
 #            for i in base:
 #                # print(i)
 #                t = list(i)
 #                t.append(idK)
 #                t = set(
 #                    t)  # 为了防止出现 重复 的情况，因为我的getAllConditionBase(newDataK, idK, fk, minSup, **dk)方法的编写，可能会形成重复，如   a，a
 #                t = list(t)
 #
 #                freAll.append(t)
 #                itemSupValue = list(itemSup.values())[0]
 #
 #                x = tuple(t)  # 列表不能做字典的关键字，因为他可变，，而元组可以
 #                # <class 'list'>: ['c', 'd']
 #                # print(t[0])     # t是列表，字典的关键字不能是可变的列表， 所以用 t[0] 来取出里面的值
 #                freAllDic[x] = min(itemSupValue, d1[idK])
 #        # print(freAll)
 #        # print(freAllDic)
 #
 #        return freAll, freAllDic

def get_freq():
    pass


def run_fpGrowth(file_name=None, sup = 3):
    if file_name is None:
        simDat = load_test_data()
    else:
        simDat = load_out_data(file_name)
    initSet = createInitSet(simDat)
    print(initSet)
    myFPtree, myHeaderTab = createFPtree(initSet, sup)
    myFPtree.disp()

    freqItems = []
    mineFPtree(myFPtree, myHeaderTab, 2, set([]), freqItems)
    for x in freqItems:
        print(x)
