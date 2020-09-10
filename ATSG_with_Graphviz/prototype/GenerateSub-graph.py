import json
from graphviz import Digraph

class SubGraph():
    def __init__(self, step, detected_objects, action):
        self.step = step
        self.detected_objects = detected_objects
        self.action = action

file_path = './data/test_data2.json'
with open(file_path) as f:
    json_data = json.load(f)

sub_graph = []
ob_node = []
G = Digraph(format="jpg")
action = "insert"

for step_index in range(len(json_data)):
    step = step_index + 1

    sub_graph.append(SubGraph(step, json_data["step%d" % step], action))
    #print(vars(sub_graph))

    ob_and_act = []
    object_name = None
    for index, item in enumerate(sub_graph[step_index].detected_objects):
        if object_name == item:
            node_index += 1
        else:
            node_index = 1
            object_name = item

        ob_and_act.append([item, node_index, action])

    # dct型や,classを書くようしてもっと明瞭に記載できないか
    ob_node.append(ob_and_act) # ob_node = [step number][0:object name, 1:node_index, 3:action]

# print(in_ob)
# print(out_ob)

# ネットワークグラフの描画
parent = "frame" # 親部品
drawn_in_ob = [None]
drawn_out_ob = [None]
act_name_format = "--step%d--\n\n%s"  # %(action, step)
in_ob_name_format = "--step%d--\n\n%s[%s]"  # %(object_name, node_num, step)
# steps
for step_index in range(len(json_data)):
    step = step_index + 1
    act_node = act_name_format %(step, action)
    G.node(act_node, shape="circle")

    #objects
    for item in ob_node[step_index]:
        object_name = item[0]
        node_num = item[1]
        action = item[2]
        #print("%s, %s, %s\n" %(object_name, node_num, action))

        # input object
        # sub-graphの結合
        in_ob = in_ob_name_format % (step, object_name, node_num)
        if step > 1:
            # 子部品
            if object_name != parent:
                #print(in_ob, drawn_in_ob)
                # 新規の子部品
                if not object_name in drawn_in_ob:
                    G.node(in_ob, shape="square", style="filled")
                    G.edge(in_ob, act_node)
                    #print("新規の子部品---%s, %s" % (in_ob, drawn_in_ob))
                    drawn_in_ob.append(object_name)

                # 重複する子部品を除外
                elif node_num > drawn_in_ob.count(object_name):
                    G.node(in_ob, shape="square", style="filled")
                    G.edge(in_ob, act_node)
                    #print("名称重複部品---%s, %s" %(in_ob, drawn_in_ob))
                    drawn_in_ob.append(object_name)

            #親部品
            else:
                in_ob = parent_ob_node # 前出のsub-graphの親部品ノード
                G.node(in_ob, shape="square", style="filled")
                G.edge(in_ob, act_node)
        else:
            G.node(in_ob, shape="square", style="filled")
            G.edge(in_ob, act_node)
            drawn_in_ob.append(object_name)


        # # output object
        # # 親部品に子部品を付与
        # if object_name == parent:
        #     children = ""
        #     for child in ob_node[step_index]:
        #         if child[0] != parent:
        #             children += " " + str(child[0])
        #     out_ob_node = "%s\n(%s){%s}" % (in_ob, action, children)
        #     parent_ob_node = out_ob_node
        #     G.node(out_ob_node, shape="square")
        #     G.edge(act_node, out_ob_node)

        # output object
        # 親部品に子部品を付与
        if object_name == parent:
            if step > 1:
                children = ""
                for child in ob_node[step_index]: # ob_node = [step number][0:object name, 1:node_index, 3:action]
                    child_name = child[0]
                    child_node_num = child[1]
                    if child_name != parent:
                        if child_node_num > drawn_out_ob.count(child_name):
                            children += " " + str(child_name)
                            drawn_out_ob.append(child_name)

            else:
                children = ""
                for child in ob_node[step_index]:
                    child_name = child[0]
                    if child_name != parent:
                        children += " " + str(child_name)
                        drawn_out_ob.append(child_name)

            out_ob_node = "%s\n(%s){%s}" % (in_ob, action, children)
            parent_ob_node = out_ob_node
            G.node(out_ob_node, shape="square", style="filled")
            G.edge(act_node, out_ob_node)

G.render("sub-graphs")