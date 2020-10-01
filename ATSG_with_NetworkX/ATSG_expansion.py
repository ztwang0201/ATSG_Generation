# parent_component = main_component parentに統一
# child_component = sub_component 　childに統一
# 主要子部品をparent, 従属子部品をchildと呼ぶ

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

        # 1つのsteoの, 検出物体, step番号をクラスインスタンスに格納し、リストで管理
        data = yolo_data[step_index]
        sub_graph.append(SubGraph(step, data["step%d" % step]))

        # 1つのsub-graphの検出物体名とその物体番号リスト化
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

        ob_nodes.append(ob_name_and_index)  # ob_nodes = [step number][0:object name, 1:node_index]

    return ob_nodes, ob_list


def sort_by_components_hierarchy(ob_list, product_name, hierarchy_data):
    order_list = hierarchy_data  # 事前作成したリスト

    if order_list.get(product_name):
        order = order_list[product_name]

    else:
        order = order_list["all_components"]

    for item in ob_list:
        if not item in order:
            order.append(item)  # リストに存在しない部品があった場合，最下層に追加

    components_hierarchy = sorted(set(ob_list), key=order.index)

    return components_hierarchy


# 部品の大小関係から主要子部品を決定(主要子部品をparent, 従属子部品をchildと呼ぶ)
def set_parent_component(components_hierarchy, ob_nodes, step_index, object_name):
    parent = None
    ob_list = []
    for item in ob_nodes[step_index]:  # ob_nodes = [step number][0:object name, 1:node_index]
        ob_list.append(item[0])
        sorted_ob_list = sort_by_components_hierarchy(ob_list, None, hierarchy_data)
    for components_name in sorted_ob_list:
        for parent_candidate in components_hierarchy:
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


def expand_assembly_unit(ob_nodes):
    ob_list = []
    new_ob_nodes = []
    # 別ファイルで管理する？

    for step_index in range(len(ob_nodes)):
        for item in ob_nodes[step_index]:
            if item[0] not in ob_list:
                ob_list.append(item[0])

        # fastenerが複数の場合に未対応
        ob_name_and_index = []
        for item in ob_nodes[step_index]:
            object_name = item[0]
            object_index = item[1]

            if object_name not in fastener_list:
                pre_step = len(ob_name_and_index)
                ob_name_and_index.append([object_name, object_index])

        new_ob_nodes.append(ob_name_and_index)

        ob_name_and_index = []
        for item in ob_nodes[step_index]:
            object_name = item[0]
            object_index = item[1]

            current_step = len(ob_name_and_index)
            ob_name_and_index.append([object_name, object_index])

        if not ob_name_and_index[current_step] == ob_name_and_index[pre_step]:
            new_ob_nodes.append(ob_name_and_index)

    return new_ob_nodes


def expand_au_list(ob_nodes, components_hierarchy):
    # 別ファイルで管理する？
    fastener_list = ["screw"]
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

            parent = set_parent_component(components_hierarchy, ob_nodes, step_index, "ignore")
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
    dg.add_node(name, label = label, shape='oval', step=step, attr='motion', object_name=None)


def create_in_node(dg, step, object_name, object_index):
    name = set_in_node_name(step, object_name, object_index)
    label = set_object_base_name(object_name, object_index)
    dg.add_node(name, label = label, shape='record', color='red',step=step, attr='in_object', object_name=object_name)


def set_child_comp_label(ob_list, child_components_list):
    child_comp_label = ''
    for object_name in ob_list:
        ob_index = 1
        for index in range(len(child_components_list)):
            ob_base_name = set_object_base_name(object_name, ob_index)
            for child in child_components_list:
                if ob_base_name in child:
                    ob_index = ob_index + 1

        num_of_ob = ob_index - 1
        if num_of_ob > 0:
            child_comp_label = child_comp_label + str(object_name) + '×' + str(num_of_ob) + '  '


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


    return child_comp_label


def create_out_node(dg, step, object_name, object_index, child_components_list):
    name = set_out_node_name(step, object_name, object_index)
    parent_label = set_object_base_name(object_name, object_index)

    child_comps = child_components_list
    child_label = set_child_comp_label(ob_list, child_components_list)
    label = '{' + '{' + parent_label + '}' + '|' + '{' + child_label + '}' + '}'

    # 個数のみ表示するように変更！！
    dg.add_node(name, label=label, shape='record', color='red', step=step, attr='out_object',  object_name='object_name',
                parent_comp=parent_label, child_comps=child_comps)


def in2motion_edge(dg, step, motion, object_name, object_index):
    in_node = set_in_node_name(step, object_name, object_index)
    motion_node = set_motion_node_name(step, motion)
    dg.add_edge(in_node, motion_node, color='red')


def motion2out_edge(dg, step, motion, object_name, object_index):
    out_node = set_out_node_name(step, object_name, object_index)
    motion_node = set_motion_node_name(step, motion)
    dg.add_edge(motion_node, out_node, color='red')


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
        dg.add_node(in_name, label=label, shape='record', color='blue', step=index, attr='in_hand', object_name='hand', tool=tool)
        dg.add_edge(in_name, motion_node, color='blue')

        if pre_step_out_hand:
            if pre_step_out_tool == tool:
                dg.add_edge(pre_step_out_hand, motion_node, color='blue')
                dg.remove_node(in_name)
            else:
                if hand_before_switch:
                    dg.add_edge(hand_before_switch, motion_node, color='blue')
                    dg.remove_node(in_name)
                hand_before_switch = pre_step_out_hand

        out_name = str(index) + "hand" + "_out"
        dg.add_node(out_name, label=label, shape='record', color='blue', step=index, attr='out_hand', object_name='hand', tool=tool)
        dg.add_edge(motion_node, out_name, color='blue')

        pre_step_out_hand = out_name
        pre_step_out_tool = tool



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

    ob_nodes = expand_au_list(original_ob_nodes, components_hierarchy)

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
            parent = set_parent_component(components_hierarchy, ob_nodes, step_index, object_name)
            if object_name == parent and object_index == 1:
                child_components_list, components_of_each_branch = set_child_components_list(
                    step_index, ob_nodes, parent,
                    parent_components_list, components_of_each_branch)

                create_out_node(dg, step, object_name, object_index, child_components_list)
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
                    dg.add_edge(item[0], item[1], color='red')

    add_hand_node(dg)


yolo_file_path = './data/work_chair.json'
with open(yolo_file_path) as yf:
    yolo_data = json.load(yf)

hierarchy_file_path = './hierarchical_order_list.json'
with open(hierarchy_file_path) as hf:
    hierarchy_data = json.load(hf)

original_ob_nodes, ob_list = create_object_node_list(yolo_data)  # ob_node: step毎のオブジェクト情報, ob_list: 全stepでのオブジェクトの種類のリスト
product_name = "work_chair"
components_hierarchy = sort_by_components_hierarchy(ob_list, product_name, hierarchy_data)  # 全部品の親子関係を定義
fastener_list = ["screw"] #留具を定義


# ATSG
G = nx.DiGraph()
generate_atsg(G)
ag = nx.nx_agraph.to_agraph(G)
ag.write('./data/atsg.dot')
ag.draw('./data/atsg.pdf', prog='dot')

j_graph_data = json_graph.node_link_data(G)
with open('./data/graph_data.json', 'w') as gf:
    json.dump(j_graph_data, gf, indent=4)