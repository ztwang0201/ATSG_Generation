######################################## コード記述ルール ##############################
#
# parent_component = main_component parentに統一
# child_component = sub_component 　childに統一
#
# 主要子部品をparent, 従属子部品をchildと呼ぶ（本プログラム内のみでの通り名。論文等とは異なる）
#
# 関数内において、実引数名（グローバル変数）と仮引数（ローカル変数）が重複する場合は、グローバル変数の先頭に "_" を付けて区別
#
#################################################################################

import json
import networkx as nx
from networkx.readwrite import json_graph
import pygraphviz
import pylab as plt
from pprint import pprint


class SubGraph():
    def __init__(self, step, detected_objects):
        self.step = step
        self.detected_objects = detected_objects

# insert -> place + screw
# 全ての留具をplaceした後に、全ての留具をscrewする。
# fixed, unfixed の状態を追加する。後々から拡張せずにはじめから、作ったほうが楽？？
# def add_motion():
#
# # only one arm
# def add_hand():
#
# # pick tool, release tool
# # tool: driver
# def add_tool():

def create_object_node_list(yolo_data):
    sub_graph = []
    ob_list = []
    ob_nodes = []
    for step_index in range(len(yolo_data)):
        step = step_index + 1

        # 1つのstepの, 検出物体, step番号をクラスインスタンスに格納し、リストで管理
        data = yolo_data[step_index]
        sub_graph.append(SubGraph(step, data["frame%d" % step]))

        # 各ステップにおけるsub-graphの検出物体名とその物体番号をリスト化
        ob_name_and_index = []
        object_name = None
        for index, item in enumerate(sub_graph[step_index].detected_objects):
            if object_name == item: # 既出の物体
                node_index += 1

            else: # 新規の物体
                node_index = 1
                object_name = item
                if object_name not in ob_list:
                    ob_list.append(object_name)  # 各sub-graphに含まれるobjectをlist化

            ob_name_and_index.append([item, node_index])

        ob_nodes.append(ob_name_and_index)  # ob_nodes = [step number][0:object name, 1:node_index]

    return ob_nodes, ob_list


def sort_by_comps_hierarchy(ob_list, product_name, hierarchy_data):
    order_list = hierarchy_data  # 事前作成したリスト

    if order_list.get(product_name):
        order = order_list[product_name]

    else:
        order = order_list["all_components"]

    for item in ob_list:
        if not item in order:
            order.append(item)  # リストに存在しない部品があった場合，最下層に追加

    comps_hierarchy = sorted(set(ob_list), key=order.index)

    return comps_hierarchy


# 部品の大小関係から主要子部品を決定(主要子部品をparent, 従属子部品をchildと呼ぶ)
def set_parent_component(comps_hierarchy, ob_nodes, step_index, object_name):
    parent = None
    ob_list = []
    for item in ob_nodes[step_index]:  # ob_nodes = [step number][0:object name, 1:node_index]
        ob_list.append(item[0])
        sorted_ob_list = sort_by_comps_hierarchy(ob_list, None, _hierarchy_data)
    for components_name in sorted_ob_list:
        for parent_candidate in comps_hierarchy:
            if components_name == parent_candidate:
                parent = parent_candidate
                break
        else:
            continue
        break

    # 主要子部品がリストに存在しない場合
    if parent is None:
        parent = object_name
    return parent


def set_child_components_list(step_index, ob_nodes, parent, parent_components_list,
                                           components_of_each_branch):
    # 新規のparentのbranch
    if parent not in parent_components_list:
        child_components_list = []
        for child in ob_nodes[step_index]:  # ob_nodes = [step number][0:object name, 1:node_index]
            child_name = child[0]
            child_node_num = child[1]
            # 従属子部品と既出の主要子部品と同名の部品（1つめの主要子部品以外を従属子部品扱いする）
            if child_name != parent or child_node_num > 1:
                child_base_name = set_object_base_name(child_name, child_node_num)
                if child_base_name not in child_components_list:
                    child_components_list.append(set_object_base_name(child_name, child_node_num))

        components_of_each_branch.append([parent, child_components_list])
        current_branch = len(components_of_each_branch) - 1

    # 既出のparentのbranch
    else:
        for index, item in enumerate(components_of_each_branch):
            # 現在のparentへ従属子部品を追加
            if parent == item[0]:
                child_components_list = components_of_each_branch[index][1]
                for child in ob_nodes[step_index]:  # ob_nodes = [step number][0:object name, 1:node_index]
                    child_name = child[0]
                    child_node_num = child[1]
                    child_base_name = set_object_base_name(child_name, child_node_num)

                    # 異なるブランチが結合する場合，結合される従属子部品情報を継承
                    if child_name != parent and child_name in parent_components_list:
                        if child_base_name not in child_components_list:
                            for ignore, item_of_comp in enumerate(components_of_each_branch):
                                if item_of_comp[0] == child_name:
                                    for index_of_children in range(len(item_of_comp[1])):
                                        child_components_list.append(item_of_comp[1][index_of_children])

                    # 従属子部品と既出の主要子部品と同名の部品（1つめの主要子部品以外を従属子部品扱いする）
                    if child_name != parent or child_node_num > 1:
                        if child_base_name not in child_components_list:
                            child_components_list.append(child_base_name)



                components_of_each_branch[index] = [parent, child_components_list]
                current_branch = index
                break

    current_child_components_list = components_of_each_branch[current_branch][1]
    current_child_components_list = sorted(current_child_components_list)

    return current_child_components_list, components_of_each_branch


# ob_nodesを2物体ごとのlistに拡張（親部品、子部品の区別も行う）
def expand_au_list(ob_nodes, comps_hierarchy, fastener_list):
    expanded_au_list = []
    assembled_child_comp_list = []

    for step_index in range(len(ob_nodes)):
        # fastenerが複数の場合に未対応！！！
        child_comp_list = []
        run_once = True

        # 主要子部品と留具以外の従属子部品のオブジェクトを抽出
        for item in ob_nodes[step_index]:
            object_name = item[0]
            object_index = item[1]

            parent = set_parent_component(comps_hierarchy, ob_nodes, step_index, "ignore")
            if object_name == parent and run_once:
                parent_comp = [object_name, object_index]
                run_once = False

            elif object_name not in fastener_list:
                child_comp_list.append([object_name, object_index])



        for item in ob_nodes[step_index]:
            object_name = item[0]
            object_index = item[1]
            if object_name in fastener_list:
                child_comp_list.append([object_name, object_index])


        for child_comp in child_comp_list:
            if child_comp not in assembled_child_comp_list:
                expanded_au_list.append([parent_comp, child_comp])
                assembled_child_comp_list.append(child_comp)

    return expanded_au_list


def estimate_motion(step_index, ob_nodes, pre_step_child_components_list):
    insert_ob_list = ["screw", "cylinder", "caster", "pole"]

    for item in ob_nodes[step_index]:
        object_name = item[0]
        object_index = item[1]
        object_base_name = set_object_base_name(object_name, object_index)
        if object_base_name not in pre_step_child_components_list:
            if object_name in insert_ob_list:
                motion = "insert"
                break
            else:
                motion = "place"

    return motion


def set_object_base_name(object_name, object_index):
    base_name_format = "%s#%s"  # %(object_name, obeject_index)
    name = base_name_format % (object_name, object_index)
    return name


def set_motion_node_name(step, motion):
    motion_name_format = "%d-%s"  # %(step, motion)
    name = motion_name_format % (step, motion)
    return name


def set_in_node_name(step, object_name, object_index):
    base_name = set_object_base_name(object_name, object_index)
    in_name_format = "%d-" + base_name + "_in"  # %(step)
    name = in_name_format % step
    return name


def set_out_node_name(step, object_name, object_index):
    base_name = set_object_base_name(object_name, object_index)
    out_name_format = "%d-" + base_name + "_out"  # %(step)
    name = out_name_format % step
    return name


def create_motion_node(dg, step, motion):
    name = set_motion_node_name(step, motion)
    label = motion
    dg.add_node(name, label = label, shape='oval', style='filled', fillcolor='#fbb4ae', fontsize='16', step=step, attr='motion', object_name=None)


def create_in_node(dg, step, object_name, object_index):
    name = set_in_node_name(step, object_name, object_index)
    label = set_object_base_name(object_name, object_index)
    dg.add_node(name, label = label, shape='record', style='filled', fillcolor='#b3cde3', fontsize='16', step=step, attr='in_object', object_name=object_name)


def set_child_comp_label(ob_list, child_components_list, parent_name):
    child_comp_label = ''
    num_of_each_ob = []
    for object_name in ob_list:
        ob_index = 1
        for index in range(len(child_components_list)):
            if object_name == parent_name: # 主要子部品と同種の部品が従属子部品となる場合
                ob_base_name = set_object_base_name(object_name, ob_index+1)
            else:
                ob_base_name = set_object_base_name(object_name, ob_index)
            for child in child_components_list:
                if ob_base_name in child:
                    ob_index = ob_index + 1

        num_of_ob = ob_index - 1
        if num_of_ob > 0:
            child_comp_label = child_comp_label + str(object_name) + '×' + str(num_of_ob) + '  '
            num_of_each_ob.append([object_name, num_of_ob])


    # child_comp_label = ""
    # run_once = True
    # for item in child_components_list:
    #     if run_once:
    #         child_comp_label += item
    #         run_once = False
    #     else:
    #         if "1" in item:
    #             child_comp_label += "|" + item
    #         else:
    #             child_comp_label += " " + item


    return child_comp_label, num_of_each_ob


def create_out_node(dg, step, object_name, object_index, child_components_list, ob_list):
    name = set_out_node_name(step, object_name, object_index)
    parent_label = set_object_base_name(object_name, object_index)

    child_comps = child_components_list

    # 子部品に関するnodeのlabel設定と種類別子部品数のカウント
    child_label, num_of_each_ob = set_child_comp_label(ob_list, child_components_list, object_name)
    label = '{' + '{' + parent_label + '}' + '|' + '{' + child_label + '}' + '}'

    # 親部品を種類別部品数の加算
    parent_exists = False
    for i in range(len(num_of_each_ob)):
        if num_of_each_ob[i][0] == object_name:
            num_of_each_ob[i][1] = num_of_each_ob[i][1] + 1
            parent_exists = True

    if not parent_exists:
        num_of_each_ob.append([object_name, 1])

    # 個数のみ表示するように変更！！
    dg.add_node(name, label=label, shape='record', style='filled', fillcolor='#b3cde3', fontsize='16', step=step, attr='out_object',  object_name='object_name',
                parent_comp=parent_label, child_comps=child_comps, num_of_each_ob=num_of_each_ob)

    return  num_of_each_ob

def in2motion_edge(dg, step, motion, object_name, object_index):
    in_node = set_in_node_name(step, object_name, object_index)
    motion_node = set_motion_node_name(step, motion)
    dg.add_edge(in_node, motion_node, fillcolor='#b3cde3')


def motion2out_edge(dg, step, motion, object_name, object_index):
    out_node = set_out_node_name(step, object_name, object_index)
    motion_node = set_motion_node_name(step, motion)
    dg.add_edge(motion_node, out_node, fillcolor='#b3cde3')


def add_hand_node(dg):
    pre_step_out_hand = ''
    pre_step_out_tool = ''
    hand_before_switch = ''

    motion_node_list = [node_name for node_name, attr in dg.nodes(data=True) if attr['attr'] == 'motion']

    for index, motion_node in enumerate(motion_node_list):
        fastener_node = [node_name for node_name, attr in dg.nodes(data=True) if attr['object_name']=='screw' and attr['step']==index + 1]
        if not fastener_node:
            tool = 'gripper'
        else:
            tool = 'wrench'

        label = '{' + '{' + 'hand' + '}' + '|' + '{' + tool + '}' + '}'

        in_name = str(index) + "hand" + "_in"
        dg.add_node(in_name, label=label, shape='record', style='filled', fillcolor='#ccebc5', fontsize='16', step=index, attr='in_hand', object_name='hand', tool=tool)
        dg.add_edge(in_name, motion_node, fillcolor='#ccebc5')

        if pre_step_out_hand:
            if pre_step_out_tool == tool:
                dg.add_edge(pre_step_out_hand, motion_node, fillcolor='#ccebc5')
                dg.remove_node(in_name)
            else:
                if hand_before_switch:
                    dg.add_edge(hand_before_switch, motion_node, fillcolor='#ccebc5')
                    dg.remove_node(in_name)
                hand_before_switch = pre_step_out_hand

        out_name = str(index) + "hand" + "_out"
        dg.add_node(out_name, label=label, shape='record', style='filled', fillcolor='#ccebc5', fontsize='16', step=index, attr='out_hand', object_name='hand', tool=tool)
        dg.add_edge(motion_node, out_name, fillcolor='#ccebc5')

        pre_step_out_hand = out_name
        pre_step_out_tool = tool

# def validate_num_of_ob(num_of_each_ob):
#     comp_diff = {}
#     diff_exists = False
#     if _product_name in bom:
#         product_bom = bom[_product_name]
#
#         for i in range(len(num_of_each_ob)):
#             for l in range(len(product_bom)):
#                 if num_of_each_ob[i][0] == product_bom[l][0]:
#                     object_name = num_of_each_ob[i][0]
#                     num_in_graph = num_of_each_ob[i][1]
#                     num_in_bom = product_bom[l][1]
#
#                     num_diff = num_in_bom - num_in_graph
#                     if not num_diff == 0:
#                         comp_diff.update([(object_name, num_diff)])
#                         diff_exists = True
#
#         if diff_exists:
#             print("Object Detection Error has occurred.\nThe following must be added to the ATSG:")
#             print("['object name', deficiency(+) / excess(-)] = ", comp_diff, "\n")
#         else:
#             print("The number of all objects corresponds to BOM ")
#
#     else:
#         print("There is NO BOM of the product.")
#
#
#     return comp_diff

def validate_num_of_ob(num_of_each_ob):
    comp_diff = {}
    diff_exists = False
    if _product_name in bom:
        product_bom = bom[_product_name]

        for i in range(len(num_of_each_ob)):
            object_name = num_of_each_ob[i][0]
            num_in_graph = num_of_each_ob[i][1]
            num_in_bom = product_bom[object_name]

            num_diff = num_in_bom - num_in_graph
            if not num_diff == 0:
                comp_diff.update([(object_name, num_diff)])
                diff_exists = True

        if diff_exists:
            print("Object Detection Error has occurred.\nThe following must be added to the ATSG:")
            print("['object name', deficiency(+) / excess(-)] = ", comp_diff, "\n")
        else:
            print("The number of all objects corresponds to BOM ")

    else:
        print("There is NO BOM of the product.")


    return comp_diff

def generate_atsg(dg):
    in_node_base_name_list = []
    out_node_base_name_list = []
    child_components_list = []
    parent_components_list = []
    pre_step_child_components_list = []
    components_of_each_branch = []

    removable_node_list = []
    inheritable_node_list = []
    dst_motion_node_list = []

    step_of_removable_node = []
    step_of_inheriable_node = []
    inherited_node_list = []

    ob_nodes = expand_au_list(original_ob_nodes, _comps_hierarchy, _fastener_list)

    for step_index in range(len(ob_nodes)):
        step = step_index + 1
        motion = estimate_motion(step_index, ob_nodes, pre_step_child_components_list)
        create_motion_node(dg, step, motion)

        for item in ob_nodes[step_index]:
            object_name = item[0]
            object_index = item[1]

            # 従属子部品になっていないinput nodeとedge生成
            object_base_name = set_object_base_name(object_name, object_index)

            # input object
            if object_base_name not in pre_step_child_components_list:
                create_in_node(dg, step, object_name, object_index)
                in2motion_edge(dg, step, motion, object_name, object_index)

                in_node_base_name_list.append(
                    set_object_base_name(object_name, object_index))  # object_name[object_index]
                removable_node_list.append(set_in_node_name(step, object_name, object_index))
                step_of_removable_node.append(step)
                dst_motion_node_list.append(set_motion_node_name(step, motion))

            # output object (parent component)
            parent = set_parent_component(_comps_hierarchy, ob_nodes, step_index, object_name)
            if object_name == parent and object_index == 1:
                child_components_list, components_of_each_branch = set_child_components_list(
                    step_index, ob_nodes, parent,
                    parent_components_list, components_of_each_branch)

                # out nodeの生成ち、out nodeに含まれる部品の種類別個数: num_ob_each_ob
                num_of_each_ob = create_out_node(dg, step, object_name, object_index, child_components_list, _ob_list)
                motion2out_edge(dg, step, motion, object_name, object_index)

                parent_components_list.append(parent)  # 枝分かれ構造用（算定プログラム）

                out_node_base_name_list.append(
                    set_object_base_name(object_name, object_index))  # object_name[object_index]
                inheritable_node_list.append(set_out_node_name(step, object_name, object_index))
                step_of_inheriable_node.append(step)

        for item in child_components_list:
            if item not in pre_step_child_components_list:
                pre_step_child_components_list.append(item)

    # output nodeと重複するinput nodeを除去
    for out_node_index, out_node_base_name in enumerate(out_node_base_name_list):
        for in_node_index, in_node_base_name in enumerate(in_node_base_name_list):
            if out_node_base_name == in_node_base_name:
                removable_node = removable_node_list[in_node_index]

                remove_node_list = []
                add_edge_list = []
                for object_node in dg.nodes():
                    if object_node == removable_node:
                        inherited_node = inheritable_node_list[out_node_index]
                        if step_of_removable_node[in_node_index] > step_of_inheriable_node[out_node_index]:
                            if inherited_node not in inherited_node_list:
                                remove_node_list.append(object_node)
                                dst_motion_node = dst_motion_node_list[in_node_index]
                                add_edge_list.append([inherited_node, dst_motion_node])
                                inherited_node_list.append(inherited_node)

                for item in remove_node_list:
                    dg.remove_node(item)
                for item in add_edge_list:
                    dg.add_edge(item[0], item[1], fillcolor='#b3cde3')

    # 最後のout nodeの部品数をBill Of Materials(部品表)と比較
    comp_diff = validate_num_of_ob(num_of_each_ob)

    should_regenerate = False
    if not comp_diff == {}:
        should_regenerate = True
    # hand nodeの追加
    add_hand_node(dg)

    return should_regenerate, comp_diff

def add_inserted_fastener2ob_nodes(ob_name_and_index, ob_max_index_dict, fastener_list, product_bom, num_of_fastener_dict):
    if not num_of_fastener_dict:
        for fastener_name in fastener_list:
            num_of_fastener_dict.update([(fastener_name, 0)])

    for ob_item in ob_name_and_index:
        object_name = ob_item[0]
        if object_name in fastener_list:
            max_num_of_fastener = product_bom[object_name] # BOMに記載された部品数
            # BOMの個数以下に設定
            if num_of_fastener_dict[object_name] < max_num_of_fastener:
                new_num = num_of_fastener_dict[object_name] + 1
                num_of_fastener_dict.update([(object_name, new_num)])

    for fastener_name in fastener_list:
        fastener_max_index = num_of_fastener_dict[fastener_name]

        if not ob_max_index_dict.get(fastener_name) is None:
            object_max_index = ob_max_index_dict[fastener_name]

            while object_max_index < fastener_max_index:
                object_max_index += 1
                ob_name_and_index.append([fastener_name, object_max_index])


    # print(num_of_fastener_dict)
    # pprint(ob_name_and_index)
    # print("----------------------------")
    return num_of_fastener_dict, ob_name_and_index

def load_ob_max_index(ob_name_and_index):
    ob_max_index_dict = {}
    max_index = 1
    for item in ob_name_and_index:
        object_name = item[0]
        object_index = item[1]

        if object_index > max_index:
            max_index = object_index
        ob_max_index_dict.update([(object_name, max_index)])

    # pprint(ob_max_index_dict)
    return ob_max_index_dict


def fix_object_node_list(yolo_data, comp_diff):
    sub_graph = []
    ob_list = []
    ob_nodes = []
    # BOM情報の取得
    if _product_name in bom:
        product_bom = bom[_product_name]
    else:
        print("No BOM of ", _product_name, "!")

    for step_index in range(len(yolo_data)):
        step = step_index + 1

        # 1つのsteoの, 検出物体, step番号をクラスインスタンスに格納し、リストで管理
        data = yolo_data[step_index]
        sub_graph.append(SubGraph(step, data["frame%d" % step]))

        # 各ステップのsub-graphの検出物体名とその物体番号をリスト化
        ob_name_and_index = []
        object_name = None
        for index, item in enumerate(sub_graph[step_index].detected_objects):
            if object_name == item:
                node_index += 1
            else:
                node_index = 1
                object_name = item
                if object_name not in ob_list:
                    ob_list.append(object_name)  # 各sub-graphに含まれるobjectをlist化

            ob_name_and_index.append([item, node_index])

        # 各オブジェクトの最大のindexを抽出
        ob_max_index_dict = load_ob_max_index(ob_name_and_index)

        if step_index == 0:
            num_of_fastener_dict = {}
        # ひとまず枝分かれで留め具が用いられる場合は無視
        num_of_fastener_dict, ob_name_and_index \
            = add_inserted_fastener2ob_nodes(ob_name_and_index, ob_max_index_dict, _fastener_list, product_bom, num_of_fastener_dict)

        # fastenerのcomp_diffをupdate
        for fastener_name in _fastener_list:
            if not comp_diff.get(fastener_name) is None:
                if not num_of_fastener_dict.get(fastener_name) is None:
                    if not product_bom.get(fastener_name) is None:
                        updated_num = product_bom[fastener_name] - num_of_fastener_dict[fastener_name]
                        comp_diff.update([(fastener_name, updated_num)])

        # 留具以外
        for l in range(len(ob_name_and_index)):
            dst_object_name = ob_name_and_index[l][0]
            if not dst_object_name in _fastener_list: # 対処療法的対応（はっきりと描画されている留具が認識できていない場合は対応不可）
                if not comp_diff.get(dst_object_name) is None:
                    num_of_diff = comp_diff.get(dst_object_name)  # 過不足数
                    for m in range(num_of_diff):
                        node_index = ob_name_and_index[l][1] + m + 1
                        ob_name_and_index.append([dst_object_name, node_index])


        # # 検出不足の場合のみ対応可能、検出過剰は現状対応不可。num_of_diffの扱い方を変更する！！
        # for i in range(len(comp_diff)):
        #     for l in range(len(ob_name_and_index)):
        #         target_object_name = comp_diff[i][0]  # 物体検出エラーにより過不足がある物体名
        #         num_of_diff = comp_diff.get(target_object_name)  # 過不足数
        #
        #         # すでに存在するインデックスと重複してしまう問題あり
        #         if target_object_name == ob_name_and_index[l][0]:
        #             for m in range(num_of_diff):
        #                 node_index = ob_name_and_index[l][1] + m + 1
        #                 ob_name_and_index.append([target_object_name, node_index])

        ob_nodes.append(ob_name_and_index)  # ob_nodes = [step number][0:object name, 1:node_index]

    # 留具
    there_is_add = False
    for fastener_name in _fastener_list:
        if not comp_diff.get(fastener_name) is None:
            if comp_diff[fastener_name] > 0: # 不足の場合のみ対応
                ob_name_and_index = []
                for i in range(comp_diff[fastener_name] + num_of_fastener_dict[fastener_name]):
                    fastener_index = i + 1
                    ob_name_and_index.append([fastener_name, fastener_index])
                add_inserted_fastener2ob_nodes(ob_name_and_index, ob_max_index_dict, _fastener_list, product_bom,
                                               num_of_fastener_dict)
                there_is_add = True

    if there_is_add:
        new_ob_name_and_index = ob_nodes[len(ob_nodes)-1]
        for item in ob_name_and_index:
            new_ob_name_and_index.append(item)
        ob_nodes.append(new_ob_name_and_index)

    return ob_nodes, ob_list


# load files
yolo_file_path = './data/yolo/incorrect_work_chair_for_exp.json'
with open(yolo_file_path) as yf:
    _yolo_data = json.load(yf)

hierarchy_file_path = './conf/hierarchical_order_list.json'
with open(hierarchy_file_path) as hf:
    _hierarchy_data = json.load(hf)

bom_file_path = './conf/bom.json'
with open(bom_file_path) as bf:
    bom = json.load(bf)

# set conf
_fastener_list = ["screw"] #留具を定義
_product_name = "work_chair"
#下1行のコードは関数内に入れるべきでは？？
original_ob_nodes, _ob_list = create_object_node_list(_yolo_data)  # ob_node: step毎のオブジェクト情報, ob_list: 全stepでのオブジェクトの種類のリスト
_comps_hierarchy = sort_by_comps_hierarchy(_ob_list, _product_name, _hierarchy_data)  # 全部品の親子関係を定義



# ATSG
G = nx.DiGraph()
should_regenerate, _comp_diff = generate_atsg(G)
ag = nx.nx_agraph.to_agraph(G)
ag.write('./data/result/atsg.dot')
ag.draw('./data/result/atsg.pdf', prog='dot')

#　Yolo dataを補完してATSG再生成
if should_regenerate:
    print("***Execute ATSG regeneration***")
    original_ob_nodes, _ob_list = fix_object_node_list(_yolo_data, _comp_diff)
    _comps_hierarchy = sort_by_comps_hierarchy(_ob_list, _product_name, _hierarchy_data)
    G = nx.DiGraph()
    should_regenerate, _comp_diff = generate_atsg(G)

    ag = nx.nx_agraph.to_agraph(G)
    ag.write('./data/result/atsg_fixed.dot')
    ag.draw('./data/result/atsg_fixed.pdf', prog='dot')


j_graph_data = json_graph.node_link_data(G)
with open('./data/result/graph_data.json', 'w') as gf:
    json.dump(j_graph_data, gf, indent=4)