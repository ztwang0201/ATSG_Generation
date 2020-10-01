##################　関数の墓場　###############################
# 修正前の関数
# バックアップ用

def set_child_components_list_for_branches(step_index, ob_nodes, parent, parent_components_list,
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
                    # 従属子部品と既出の主要子部品と同名の部品（1つめの主要子部品以外を従属子部品扱いする）
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
    # print(child_components_list)
    print(parent, current_child_components_list)
    # pprint(components_of_each_branch)
    # print('----------------------------------------------')
    return children, current_child_components_list, components_of_each_branch

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
    children = ""

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
    # print(child_components_list)
    # print(parent, current_child_components_list)
    # pprint(components_of_each_branch)
    # print('----------------------------------------------')
    return children, current_child_components_list, components_of_each_branch


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


def create_out_node(dg, step, object_name, object_index, children):
    name = set_out_node_name(step, object_name, object_index)
    label = object_name + "(%s)" % object_index

    # 個数のみ表示するように変更！！
    # label属性ではなくchildren属性として，従属子部品情報をもたせる
    dg.add_node(name, label = '{' + '{' + label + '}' + '|' + '{' + children + '}' + '}', shape='record', attr = 'object')