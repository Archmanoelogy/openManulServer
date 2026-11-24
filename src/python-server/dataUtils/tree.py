# -*- coding: UTF-8 -*-
import json
import yaml

"""
node = tuple([manul_id, x, y, w, h])

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
    parents = [mother] + fathers
    
    parent_nodes = []
    n_parent = len(parents)+0.0
    x, y, w, h = current_node[1:5]
    p_w, p_h = w/n_parent, h/2.0
    p_y = y - p_h/2.0
    x0 = x - w
    for idx, p_id in enumerate(parents):
        p_x = x0 + (2*idx+1)*p_w
        p_node = tuple([p_id, p_x, p_y, p_w, p_h])
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
        c_node = tuple([c_id, c_x, c_y, c_w, c_h])
        child_nodes.append(c_node)
    nodes += child_nodes
    
def build_family_tree(manul_id, litters):
    core_manul = tuple([manul_id, 0.0, 0.0, 2.0**10, 2.0**10])
    nodes = [core_manul]
    __upward(nodes, core_manul, litters)
    __downward(nodes, core_manul, litters)
    return(nodes)