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


def fix_object_node_list(yolo_data, comp_diff):
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

        for i in range(len(comp_diff)):
            appended_max_node_index = 0
            for l in range(len(ob_name_and_index)):
                target_object_name = comp_diff[i][0]
                num_of_diff = comp_diff[i][1]
                if target_object_name == ob_name_and_index[l][0]:
                    if appended_max_node_index <= ob_name_and_index[l][1]:
                        appended_max_node_index = ob_name_and_index[l][1]

            for m in range(num_of_diff):
                node_index = appended_max_node_index + m
                ob_name_and_index.append([target_object_name, node_index])

        ob_nodes.append(ob_name_and_index) # ob_nodes = [step number][0:object name, 1:node_index]

    pprint(ob_nodes)
    return ob_nodes, ob_list


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


def fix_object_node_list(yolo_data, comp_diff):
    sub_graph = []
    ob_list = []
    ob_nodes = []
    for step_index in range(len(yolo_data)):
        step = step_index + 1

        # 1つのsteoの, 検出物体, step番号をクラスインスタンスに格納し、リストで管理
        data = yolo_data[step_index]
        sub_graph.append(SubGraph(step, data["step%d" % step]))

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

        # 検出不足の場合のみ対応可能、検出過剰は現状対応不可。num_of_diffの扱い方を変更する！！
        for i in range(len(comp_diff)):
            for l in range(len(ob_name_and_index)):
                target_object_name = comp_diff[i][0] # 物体検出エラーにより過不足がある物体名
                num_of_diff = comp_diff[i][1] # 過不足数

                # すでに存在するインデックスと重複してしまう問題あり
                if target_object_name == ob_name_and_index[l][0]:
                    for m in range(num_of_diff):
                        node_index = ob_name_and_index[l][1] + m + 1
                        ob_name_and_index.append([target_object_name, node_index])

        ob_nodes.append(ob_name_and_index) # ob_nodes = [step number][0:object name, 1:node_index]

    # pprint(ob_nodes)
    return ob_nodes, ob_list

def validate_num_of_ob(num_of_each_ob):
    comp_diff = []
    diff_exists = False
    if _product_name in bom:
        product_bom = bom[_product_name]

        for i in range(len(num_of_each_ob)):
            for l in range(len(product_bom)):
                if num_of_each_ob[i][0] == product_bom[l][0]:
                    object_name = num_of_each_ob[i][0]
                    num_in_graph = num_of_each_ob[i][1]
                    num_in_bom = product_bom[l][1]

                    num_diff = num_in_bom - num_in_graph
                    if not num_diff == 0:
                        comp_diff.append([object_name, num_diff])
                        diff_exists = True

        if diff_exists:
            print("Object Detection Error has occurred.\nThe following must be added to the ATSG:")
            print("['object name', deficiency(+) / excess(-)] = ", comp_diff, "\n")
        else:
            print("The number of all objects corresponds to BOM ")

    else:
        print("There is NO BOM of the product.")


    return comp_diff
