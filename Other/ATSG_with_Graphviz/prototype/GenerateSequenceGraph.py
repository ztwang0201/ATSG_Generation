import json
from graphviz import Digraph

class SubGraph():
    def __init__(self, step, detected_objects, action):
        self.step = step
        self.detected_objects = detected_objects
        self.action = action

file_path = '../data/output.json'
with open(file_path) as f:
    json_data = json.load(f)

action = "insert"

def sort_by_components_hierarchy(ob_list, product_name, file_path):
    with open(file_path) as f:
        order_list = json.load(f)

    if order_list.get(product_name):
        order = order_list[product_name]

    else:
        order = order_list["all_components"]

    for item in ob_list:
        if not item in order:
            order.append(item)

    # print('sorted:')
    sorted_ob_list = sorted(set(ob_list), key=order.index)
    # print(sorted_ob_list)

    return sorted_ob_list


def create_object_node_list(json_data, action):
    sub_graph = []
    ob_list = []
    ob_node = []
    for step_index in range(len(json_data)):
        step = step_index + 1

        # 1つのsub-graphのaction, 検出物体, step番号をクラスインスタンスに格納し、リストで管理
        #sub_graph.append(SubGraph(step, json_data["step%d" % step], action))
        data = json_data[step_index]
        sub_graph.append(SubGraph(step, data["step%d" % step], action))

        # 1つのsub-graphの検出物体名とその識別番号、actionをリスト化
        ob_and_act = []
        object_name = None
        for index, item in enumerate(sub_graph[step_index].detected_objects):
            if object_name == item:
                node_index += 1
            else:
                node_index = 1
                object_name = item
                ob_list.append(object_name) # 各sub-graphに含まれるobjectをlist化

            ob_and_act.append([item, node_index, action])

        ob_node.append(ob_and_act) # ob_node = [step number][0:object name, 1:node_index, 3:action]

    return ob_node, ob_list

def set_parent_component(components_hierarchy, ob_node, step_index, object_name, file_path):
    parent = None
    ob_list = []
    for item in ob_node[step_index]:
        ob_list.append(item[0])  # ob_node = [step number][0:object name, 1:node_index, 3:action]
        sorted_ob_list = sort_by_components_hierarchy(ob_list, None, file_path)
    #print(sorted_ob_list)
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


ob_node, ob_list = create_object_node_list(json_data,action)

product_name = None
file_path = '../hierarchical_order_list.json'
components_hierarchy = sort_by_components_hierarchy(ob_list, product_name, file_path)


# ネットワークグラフの描画
G = Digraph(format="jpg")
drawn_in_ob = [None]
drawn_out_ob = [None]
act_name_format = "step%d-%s"  # %(step, action)
in_ob_name_format = "step%d-%s[%s]"  # %(step, object_name, node_num)
dot_body_index = 0
dot_body = []

# steps
for step_index in range(len(json_data)):
    step = step_index + 1
    act_node = act_name_format %(step, action) # action node名の定義
    G.node(act_node, label=action, shape="circle")  # action nodeの生成

    #object information
    for item in ob_node[step_index]:
        object_name = item[0]
        node_num = item[1]
        action = item[2]

        ##　複数個の親部品が存在することを考慮していない
        # # input object
        # # sub-graphの結合
        # in_ob = in_ob_name_format % (step, object_name, node_num)
        # if step > 1:
        #     # 子部品
        #     if object_name != parent:
        #         #print(in_ob, drawn_in_ob)
        #         # 新規の子部品
        #         if not object_name in drawn_in_ob:
        #             G.node(in_ob, shape="square", style="filled")
        #             G.edge(in_ob, act_node)
        #             drawn_in_ob.append(object_name)
        #
        #         # 重複する子部品を除外
        #         elif node_num > drawn_in_ob.count(object_name):
        #             G.node(in_ob, shape="square", style="filled")
        #             G.edge(in_ob, act_node)
        #             drawn_in_ob.append(object_name)
        #
        #     #親部品
        #     else:
        #         in_ob = parent_ob_node # 前出のsub-graphの親部品ノード
        #         G.node(in_ob, shape="square", style="filled")
        #         G.edge(in_ob, act_node)
        # else:
        #     G.node(in_ob, shape="square", style="filled")
        #     G.edge(in_ob, act_node)
        #     drawn_in_ob.append(object_name)
        #
        # if object_name == parent:
        #     if step > 1:
        #         children = ""
        #         for child in ob_node[step_index]: # ob_node = [step number][0:object name, 1:node_index, 3:action]
        #             child_name = child[0]
        #             child_node_num = child[1]
        #             if child_name != parent:
        #                 if child_node_num > drawn_out_ob.count(child_name):
        #                     children += " " + str(child_name)
        #                     drawn_out_ob.append(child_name)
        #
        #     else:
        #         children = ""
        #         for child in ob_node[step_index]:
        #             child_name = child[0]
        #             if child_name != parent:
        #                 children += " " + str(child_name)
        #                 drawn_out_ob.append(child_name)
        #
        #     out_ob_node = "%s-(step%d-%s){%s}" % (in_ob, step, action, children)
        #     parent_ob_node = out_ob_node
        #     G.node(out_ob_node, shape="square", style="filled")
        #     G.edge(act_node, out_ob_node)

        # 複数個の親部品が存在することを考慮
        # input object
        in_ob = in_ob_name_format % (step, object_name, node_num)  # input object node名の定義

        # step2以降のinput objectの描画
        if step > 1:
            # 子部品と重複する親部品
            if object_name != parent or node_num > 1:
                # 一度も描画していない種類の部品を描画
                if not object_name in drawn_in_ob:
                    G.node(in_ob, label=object_name, shape="square", style="filled") # input object nodeの生成
                    G.edge(in_ob, act_node)  # input -> action

                    drawn_in_ob.append(object_name)  # 描画した input object をリスト化

                # すでに描画されている同一種の部品数を考慮し、重複を避けて描画
                elif node_num > drawn_in_ob.count(object_name):
                    G.node(in_ob, label=object_name, shape="square", style="filled")

                    G.edge(in_ob, act_node)

                    drawn_in_ob.append(object_name)

            #1つめ親部品
            else:
                parent = set_parent_component(components_hierarchy, ob_node, step_index, object_name, file_path)
                if parent == pre_parent:
                    in_ob = parent_ob_node  # 前出のsub-graphの親部品ノード
                G.node(in_ob, label=object_name, shape="square", style="filled")  # input parent object nodeの描画
                for body_str in G.body:
                    if in_ob in body_str:
                        print(G.body.index(body_str))
                        print(body_str)
                G.edge(in_ob, act_node)

        # step1のinput objectの描画
        else:
            G.node(in_ob, label=object_name, shape="square", style="filled")
            G.edge(in_ob, act_node)

            drawn_in_ob.append(object_name)

        # output object
        parent = set_parent_component(components_hierarchy, ob_node, step_index, object_name, file_path)
        if object_name == parent:
            # step2以降
            if step > 1:
                # 子部品情報を抽出
                children = ""
                for child in ob_node[step_index]: # ob_node = [step number][0:object name, 1:node_index, 3:action]
                    child_name = child[0]
                    child_node_num = child[1]

                    # 子部品
                    if child_name != parent:
                        # 　部品数を数えて重複記述を防止
                        if child_node_num > drawn_out_ob.count(child_name):
                            children += " " + str(child_name)
                            drawn_out_ob.append(child_name)

                    # 同名の親部品（1つめの親部品以外を子部品扱いする）
                    elif child_node_num > 1:
                        if child_node_num > drawn_out_ob.count(child_name):
                            children += " " + str(child_name)
                            drawn_out_ob.append(child_name)
            # step1
            else:
                children = ""
                for child in ob_node[step_index]:
                    child_name = child[0]
                    child_node_num = child[1]
                    if child_name != parent or child_node_num > 1:
                        children += " " + str(child_name)
                        drawn_out_ob.append(child_name)

            #　1つめの親部品のみoutput nodeとして出力
            if node_num == 1:
                pre_parent = object_name
                out_ob_node = "%s-(step%d-%s){%s}" % (in_ob, step, action, children)
                parent_ob_node = out_ob_node

                # G.attr('node', shape='record')
                # print(G.body[dot_body_index], dot_body_index)
                # dot_body_index += 1

                G.node(out_ob_node, label='{' + '{' + object_name + '}' + '|' + '{' + children + '}' + '}', shape='record')


                G.edge(act_node, out_ob_node)


# G.body.remove(G.body[1])
# G.body.remove(G.body[1])
G.render("sub-graphs")
