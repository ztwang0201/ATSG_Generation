import json
from graphviz import Digraph
# object -> components（部品)とツール。物体検出で見られるもの全て
# components -> 組み立て部品。部品間で親子関係が存在
from pprint import pprint


class SubGraph():
    def __init__(self, step, detected_objects):
        self.step = step
        self.detected_objects = detected_objects


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


# 部品の上下関係から親部品を決定(便宜上、親部品をparent componentと呼ぶ)
def set_parent_component(components_hierarchy, ob_nodes, step_index, object_name, hierarchy_data):
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

    # 親部品がリストに存在しない場合
    if parent is None:
        parent = object_name
    return parent


# 　_modと旧プログラム差し替える？（8/13時点では未使用）
def set_parent_component_mod(components_hierarchy, ob_nodes, step_index, object_name, hierarchy_data):
    parent = None
    ob_list = []
    for item in ob_nodes[step_index]:  # ob_nodes = [step number][0:object name, 1:node_index]
        if item not in ob_list:  # _mod ではこの処理を追加
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

    # 親部品がリストに存在しない場合
    if parent is None:
        parent = object_name
    return parent


# sub-graph生成用子部品設定
def set_child_components(step_index, ob_nodes, parent):
    # 子部品情報を抽出
    children = ""
    for child in ob_nodes[step_index]:  # ob_nodes = [step number][0:object name, 1:node_index]
        child_name = child[0]
        child_node_num = child[1]

        # 子部品と既出の親部品と同名の部品（1つめの親部品以外を子部品扱いする）
        if child_name != parent or child_node_num > 1:
            children += " " + str(child_name)

    return children

def set_child_components_list(step_index, ob_nodes, parent, child_components_list):
    # 子部品情報を抽出
    for child in ob_nodes[step_index]:  # ob_nodes = [step number][0:object name, 1:node_index]
        child_name = child[0]
        child_node_num = child[1]
        # 子部品と既出の親部品と同名の部品（1つめの親部品以外を子部品扱いする）
        if child_name != parent or child_node_num > 1:
            child_base_name = set_object_base_name(child_name, child_node_num)
            if child_base_name not in child_components_list:
                child_components_list.append(set_object_base_name(child_name, child_node_num))

    # グラフが枝分かれした状態で、同時に複数の親部品が存在したいる場合、問題が生じる
    # -> child_components_listを多次元化して、各支流ごとに子部品情報を保持
    # -> 支流の発生、合流はどのように判断する？　発生：inputに子部品を持つノードが存在しない。 合流: inputに子部品を持つノードが複数存在
    # -> （グラフ生成中）各支流の最下流にある（子部品を持つ）親部品をリスト化？　各支流毎にクラスを生成して、情報を保持させる？
    child_components_list = sorted(child_components_list)
    children = ""
    # for item in child_components_list:
    #     children += " " + item
    run_once = True
    for item in child_components_list:
        if run_once:
            children += item
            run_once = False
        else:
            if str(1) in item:
                children += "|" + item
            else:
                children += " " + item

    return children, child_components_list


def set_child_components_list_mod(step_index, ob_nodes, parent, child_components_list, parent_components_list):
    # 子部品情報を抽出
    child_components_list_for_new_parent = []  # 枝分かれ構造用（暫定プログラム）
    for child in ob_nodes[step_index]:  # ob_nodes = [step number][0:object name, 1:node_index]
        child_name = child[0]
        child_node_num = child[1]
        # 子部品と既出の親部品と同名の部品（1つめの親部品以外を子部品扱いする）
        if child_name != parent or child_node_num > 1:
            child_base_name = set_object_base_name(child_name, child_node_num)
            if child_base_name not in child_components_list:
                child_components_list.append(set_object_base_name(child_name, child_node_num))

            # 枝分かれ構造用（暫定プログラム）
            if parent not in parent_components_list:
                child_components_list_for_new_parent.append(set_object_base_name(child_name, child_node_num))

    # -> child_components_listを多次元化して、各支流ごとに子部品情報を保持
    # -> 支流の発生、合流はどのように判断する？　発生：inputに子部品を持つノードが存在しない。 合流: inputに子部品を持つノードが複数存在
    # -> （グラフ生成中）各支流の最下流にある（子部品を持つ）親部品をリスト化？　各支流毎にクラスを生成して、情報を保持させる？
    child_components_list = sorted(child_components_list)
    children = ""
    for item in child_components_list:
        children += " " + item

    # 枝分かれ構造用（暫定プログラム）
    if parent not in parent_components_list:
        child_components_list_for_new_parent = sorted(child_components_list_for_new_parent)
        children = ""
        for item in child_components_list_for_new_parent:
            children += " " + item

    return children, child_components_list


def set_child_components_list_for_branches(step_index, ob_nodes, parent, parent_components_list,
                                           components_of_each_branch):
    # 新規のparentのbranch
    if parent not in parent_components_list:
        child_components_list = []
        for child in ob_nodes[step_index]:  # ob_nodes = [step number][0:object name, 1:node_index]
            child_name = child[0]
            child_node_num = child[1]
            # 子部品と既出の親部品と同名の部品（1つめの親部品以外を子部品扱いする）
            if child_name != parent or child_node_num > 1:
                child_base_name = set_object_base_name(child_name, child_node_num)
                if child_base_name not in child_components_list:
                    child_components_list.append(set_object_base_name(child_name, child_node_num))

        components_of_each_branch.append([parent, child_components_list])
        current_branch = len(components_of_each_branch) - 1

    # 既出のparentのbranch
    else:
        for index, item in enumerate(components_of_each_branch):
            # 現在のparentへ子部品を追加
            if parent == item[0]:
                child_components_list = components_of_each_branch[index][1]
                for child in ob_nodes[step_index]:  # ob_nodes = [step number][0:object name, 1:node_index]
                    child_name = child[0]
                    child_node_num = child[1]
                    # 子部品と既出の親部品と同名の部品（1つめの親部品以外を子部品扱いする）
                    if child_name != parent or child_node_num > 1:
                        child_base_name = set_object_base_name(child_name, child_node_num)
                        if child_base_name not in child_components_list:
                            child_components_list.append(set_object_base_name(child_name, child_node_num))

                components_of_each_branch[index] = [parent, child_components_list]
                current_branch = index
                break

    current_child_components_list = components_of_each_branch[current_branch][1]
    current_child_components_list = sorted(current_child_components_list)
    children = ""
    # for item in current_child_components_list:
    #     children += " " + item

    # 名前の設定形式に依存しないプログラムにしたい...
    run_once = True
    for item in current_child_components_list:
        if run_once:
            children += item
            run_once = False
        else:
            if "1" in item:
                children += "|" + item
            else:
                children += " " + item

            # if "shelf" in item and "2" in item:
            #     children += "|" + item
            # else:
            #     children += " " + item

    # print(step_index + 1)
    # print(parent, current_child_components_list)
    # pprint(components_of_each_branch)
    # print('----------------------------------------------')
    return children, current_child_components_list, components_of_each_branch


def expand_assembly_unit(ob_nodes):
    ob_list = []
    new_ob_nodes = []
    # 別ファイルで管理する？
    fastener_list = ["screw"]

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

    # pprint(ob_nodes)
    # print("--------------------------")
    # pprint(new_ob_nodes)
    return new_ob_nodes


def estimate_motion(step_index, ob_nodes):
    for item in ob_nodes[step_index]:
        object_name = item[0]
        if object_name == "back_rest":
            motion = "place"
            break
        else:
            motion = "insert"

    # print(motion, object_name)
    return motion


def estimate_motion_mod(step_index, ob_nodes, pre_step_child_components_list):
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

    # print(motion, object_name)
    return motion


def set_object_base_name(object_name, object_index):
    base_name_format = "%s(%s)"  # %(object_name, obeject_index)
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
    # label = "%s. " % step + motion
    label = motion
    dg.attr('node', shape='oval')
    dg.node(name, label=label)


def create_in_node(dg, step, object_name, object_index):
    name = set_in_node_name(step, object_name, object_index)
    label = object_name + "(%s)" % object_index
    dg.attr('node', shape='record')
    dg.node(name, label=label)


def create_out_node(dg, step, object_name, object_index, children):
    name = set_out_node_name(step, object_name, object_index)
    label = object_name + "(%s)" % object_index
    dg.attr('node', shape='record')
    dg.node(name, label='{' + '{' + label + '}' + '|' + '{' + children + '}' + '}')


def in2motion_edge(dg, step, motion, object_name, object_index):
    in_node = set_in_node_name(step, object_name, object_index)
    motion_node = set_motion_node_name(step, motion)
    dg.edge(in_node, motion_node)


def motion2out_edge(dg, step, motion, object_name, object_index):
    out_node = set_out_node_name(step, object_name, object_index)
    motion_node = set_motion_node_name(step, motion)
    dg.edge(motion_node, out_node)


def create_sub_graph(dg, yolo_data, hierarchy_data, ob_nodes):
    for step_index in range(len(yolo_data)):
        step = step_index + 1
        motion = "assembly"
        create_motion_node(dg, step, motion)

        for item in ob_nodes[step_index]:
            object_name = item[0]
            object_index = item[1]

            create_in_node(dg, step, object_name, object_index)
            in2motion_edge(dg, step, motion, object_name, object_index)

            parent = set_parent_component(components_hierarchy, ob_nodes, step_index, object_name, hierarchy_data)
            if object_name == parent and object_index == 1:
                # children= set_child_components(step_index, ob_nodes, parent)
                child_components_list = []  # 毎回初期化．create_sub_graphでは使用しない．
                children, child_components_list = set_child_components_list(step_index, ob_nodes, parent,
                                                                            child_components_list)

                create_out_node(dg, step, object_name, object_index, children)
                motion2out_edge(dg, step, motion, object_name, object_index)


def create_sequence_graph(dg, hierarchy_data, ob_nodes):
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

    for step_index in range(len(ob_nodes)):
        step = step_index + 1
        motion = estimate_motion_mod(step_index, ob_nodes, pre_step_child_components_list)
        create_motion_node(dg, step, motion)

        for item in ob_nodes[step_index]:
            object_name = item[0]
            object_index = item[1]

            # 子部品になっていないinput nodeとedge生成
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
            parent = set_parent_component(components_hierarchy, ob_nodes, step_index, object_name, hierarchy_data)
            if object_name == parent and object_index == 1:
                children, child_components_list, components_of_each_branch = set_child_components_list_for_branches(
                    step_index, ob_nodes, parent,
                    parent_components_list, components_of_each_branch)
                # print(children, child_components_list)
                create_out_node(dg, step, object_name, object_index, children)
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

                for body_str in dg.body:
                    if removable_node in body_str:
                        inherited_node = inheritable_node_list[out_node_index]
                        if step_of_removable_node[in_node_index] > step_of_inheriable_node[out_node_index]:
                            if inherited_node not in inherited_node_list:

                                dg.body.remove(dg.body[dg.body.index(body_str) + 1])
                                dg.body.remove(body_str)

                                dst_motion_node = dst_motion_node_list[in_node_index]

                                inherited_node_list.append(inherited_node)


def create_exp_sequence_graph(dg, hierarchy_data, ob_nodes):
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

    ob_nodes = expand_assembly_unit(ob_nodes)

    for step_index in range(len(ob_nodes)):
        step = step_index + 1
        motion = estimate_motion_mod(step_index, ob_nodes, pre_step_child_components_list)
        create_motion_node(dg, step, motion)

        for item in ob_nodes[step_index]:
            object_name = item[0]
            object_index = item[1]

            # 子部品になっていないinput nodeとedge生成
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
            parent = set_parent_component(components_hierarchy, ob_nodes, step_index, object_name, hierarchy_data)
            if object_name == parent and object_index == 1:
                children, child_components_list, components_of_each_branch = set_child_components_list_for_branches(
                    step_index, ob_nodes, parent,
                    parent_components_list, components_of_each_branch)

                create_out_node(dg, step, object_name, object_index, children)
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

                for body_str in dg.body:
                    if removable_node in body_str:
                        inherited_node = inheritable_node_list[out_node_index]
                        if step_of_removable_node[in_node_index] > step_of_inheriable_node[out_node_index]:
                            if inherited_node not in inherited_node_list:
                                dg.body.remove(dg.body[dg.body.index(body_str) + 1])
                                dg.body.remove(body_str)
                                dst_motion_node = dst_motion_node_list[in_node_index]
                                dg.edge(inherited_node, dst_motion_node)
                                inherited_node_list.append(inherited_node)


yolo_file_path = './data/office_chair.json'
with open(yolo_file_path) as yf:
    yolo_data = json.load(yf)

hierarchy_file_path = './hierarchical_order_list.json'
with open(hierarchy_file_path) as hf:
    hierarchy_data = json.load(hf)

ob_nodes, ob_list = create_object_node_list(yolo_data)  # ob_node: step毎のオブジェクト情報, ob_list: 全stepでのオブジェクトの種類のリスト
product_name = "office_chair"
components_hierarchy = sort_by_components_hierarchy(ob_list, product_name, hierarchy_data)  # 全部品の親子関係を定義

# sub-graphs
# d_sub_graph = Digraph(format="jpg")
# create_sub_graph(d_sub_graph, yolo_data, hierarchy_data, ob_nodes)
# d_sub_graph.render("assembly-unit")

# Sequence-graph
# d_seq_graph = Digraph(format="jpg")
# create_sequence_graph(d_seq_graph, hierarchy_data, ob_nodes)
# d_seq_graph.render("sequence-graph")

# Expanded Sequence-graph
d_exp_seq_graph = Digraph(format="pdf")
create_exp_sequence_graph(d_exp_seq_graph, hierarchy_data, ob_nodes)
d_exp_seq_graph.render("expanded_sequence-graph")
