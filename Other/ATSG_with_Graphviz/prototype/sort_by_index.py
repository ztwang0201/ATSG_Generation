import json

data_list = [
    'pole',
    'pole',
    'pole',
    'shelf',
    'shelf',
    'bolt',
    'sleeve',
    'nut',
    'nut',
    'nut',
    'washer'
]
product_name = None
file_path = '../hierarchical_order_list.json'


def sort_by_index(data_list, product_name, file_path):
    with open(file_path) as f:
        order_list = json.load(f)

    if order_list.get(product_name):
        order = order_list[product_name]
        print('order:')
        print(order)
    else:
        order = order_list["all_components"]
        print('order:')
        print(order)

    for item in data_list:
        if not item in order:
            order.append(item)
            print('modified order:')
            print(order)

    print('sorted:')
    sorted_data_list = sorted(set(data_list), key=order.index)
    print(sorted_data_list)


    return sorted_data_list[0]


parent = sort_by_index(data_list, product_name, file_path)
print(parent)