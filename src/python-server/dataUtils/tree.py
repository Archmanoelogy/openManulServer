# -*- coding: UTF-8 -*-
import json
import yaml

"""
node = tuple([manul_id, x, y, w, h, "core"|"father"|"mother"|"f-side"|"m-side"])

+-----------------+   -
|                 |   |
|        + (x,y)  |   | 2h
|                 |   |
+-----------------+   -

|-----------------|
         2w
"""

def __upward(nodes, current_node, litters):
    manul_id = current_node[0]
    litter = [l for l in litters.values() if manul_id in l.get("kittens",[])]
    if len(litter)>1:
        raise Exception("There's more than one litter that contains manul (ID=%s)."%(manul_id,))
    elif len(litter)<1:
        return None
    
    mother = litter[0].get("mother")
    fathers = litter[0].get("father_candidates", [])
    if "father" in litter[0]:
        fathers = [litter[0]["father"]] + fathers
    if mother:
        parents = [mother] + fathers
    else:
        parents = fathers
    
    parent_nodes = []
    n_parent = len(parents)+0.0
    x, y, w, h = current_node[1:5]
    p_w, p_h = w/n_parent, h/2.0
    p_y = y - p_h/2.0
    x0 = x - w
    for idx, p_id in enumerate(parents):
        status = "mother" if mother and idx==0 else "father"
        p_x = x0 + (2*idx+1)*p_w
        p_node = tuple([p_id, p_x, p_y, p_w, p_h, status])
        __upward(nodes, p_node, litters)
        parent_nodes.append(p_node)
    nodes += parent_nodes
    
def __downward(nodes, current_node, litters):
    manul_id = current_node[0]
    litters_given = [ \
        l \
        for l in litters.values() \
        if manul_id == l.get("mother") \
        or manul_id == l.get("father") \
        or manul_id in l.get("father_candidates",[]) \
    ]
    if len(litters_given)<1:
        return None
    status = "m-side" if litters_given[0].get("mother")==manul_id else "f-side"
    
    children = []
    for l in litters_given:
        children += l.get("kittens", [])
    
    child_nodes = []
    n_child = len(children)+0.0
    x, y, w, h = current_node[1:5]
    c_w, c_h = w/n_child, h/2.0
    c_y = y + c_h/2.0
    x0 = x - w
    for idx, c_id in enumerate(children):
        c_x = x0 + (2*idx+1)*c_w
        c_node = tuple([c_id, c_x, c_y, c_w, c_h, status])
        __downward(nodes, c_node, litters)
        child_nodes.append(c_node)
    nodes += child_nodes
    
def __build_family_tree(manul_id, litters):
    core_manul = tuple([manul_id, 0.0, 0.0, 2.0**10, 2.0**10, "core"])
    nodes = [core_manul]
    __upward(nodes, core_manul, litters)
    __downward(nodes, core_manul, litters)
    return(nodes)

def __uniq(nodes):
    ids = [n[0] for n in nodes]
    id_stat = {}
    for id in ids:
        id_stat[id] = id_stat.get(id, 0) + 1
    
    repeated_ids = set()
    new_nodes = []
    for node in nodes:
        id = node[0]
        if id_stat[id]==1:
            new_nodes.append(node)
        else:
            repeated_ids.add(id)
    
    for id in repeated_ids:
        repeated_nodes = [node for node in nodes if node[0]==id]
        statuses = [node[5] for node in repeated_nodes]
        if "mother" in statuses:
            merged_x = min([node[1] for node in repeated_nodes])
            merged_y = min([node[2] for node in repeated_nodes])
            merged_status = "m-merged"
        elif "father" in statuses:
            merged_x = max([node[1] for node in repeated_nodes])
            merged_y = min([node[2] for node in repeated_nodes])
            merged_status = "f-merged"
        elif "m-side" in statuses:
            selected = [node for node in repeated_nodes if node[5]=="m-side"][0]
            merged_x = selected[1]
            merged_y = selected[2]
            merged_status = "c-merged"
        else:
            selected = repeated_nodes[0]
            merged_x = selected[1]
            merged_y = selected[2]
            merged_status = "u-merged"
        new_nodes.append(tuple([id, merged_x, merged_y, None, None, merged_status]))
    
    return(new_nodes)

def __layout(nodes):
    xs = set([n[1] for n in nodes])
    ys = set([n[2] for n in nodes])
    xs = sorted(list(xs))
    ys = sorted(list(ys))
    
    x_map = {}
    for i, x in enumerate(xs):
        x_map[x] = i
    y_map = {}
    for i, y in enumerate(ys):
        y_map[y] = i
    
    layout_nodes = []
    for n in nodes:
        layout_nodes.append(tuple([n[0], x_map[n[1]], y_map[n[2]], *n[3:6]]))
    return(layout_nodes)
    
def family_tree_by_core(manul_id, litters):
    nodes = __build_family_tree(manul_id, litters)
    nodes = __uniq(nodes)
    nodes = __layout(nodes)
    return(nodes)