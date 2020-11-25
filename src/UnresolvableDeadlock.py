import itertools

def add_wait_for_edges(v_i_jp, v_ip_jp, Gp, W):
    assert v_i_jp[1] == v_ip_jp[1]
    i = v_i_jp[0]
    ip = v_ip_jp[0]
    jp = v_i_jp[1]
    j_list = []
    for v_i_j, adj in Gp.E.items():
        if v_i_j[0] == i and (i, jp, 1) in adj:
            j_list.append(v_i_j[1])

    jpp_list = [v[1] for v in Gp.E[v_ip_jp] if v[2] == 1]
    for j, jpp in itertools.product(j_list, jpp_list):
        W[(i, j, jp)].add((ip, jp, jpp))

def build_wait_for_graph(Gp):
    W = dict()
    # Construct vertex set
    for src, adj in Gp.E.items():
        for *dst, edge_type in adj:
            dst = tuple(dst)
            if edge_type == 1:
                W[(src[0], src[1], dst[1])] = set()

    # Add edges
    for src, adj in Gp.E.items():
        for *dst, edge_type in adj:
            dst = tuple(dst)
            if edge_type == 2 or edge_type == 3:
                add_wait_for_edges(src, dst, Gp, W)

    return W

def removed_vehicle_from_W(vehicle_id, W):
    for v in list(W.keys()):
        if v[0] == vehicle_id:
            del W[v]
        else:
            for u in list(W[v]):
                if u[0] == vehicle_id:
                    W[v].remove(u)

deadlock = False
def dfs(v, p, W, color, count, removed_vehicle):
    global deadlock
    color[v] = 'GREY'
    count[v] = dict() if p is None else count[p]
    if p is None:
        count[v] = dict()
    else:
        count[v] = dict(count[p])
        if p[0] in count[v]: count[p[0]] += 1
        else: count[p[0]] = 0
    for u in W[v]:
        if color[u] == 'WHITE':
            dfs(u, v, W, color, count, removed_vehicle)
            if deadlock: break
        elif color[u] == 'GREY':
            all_unique = True
            for vehicle, vehicle_cnt in count[v]:
                if vehicle_cnt - count[u].get(vehicle, vehicle_cnt) > 1:
                    all_unique = False
                    break
            if all_unique:
                print(v, u)
                deadlock = True
                removed_vehicle.append(u[0])
                removed_vehicle_from_W(u[0], W)
                break
    color[v] = 'BLACK'

def special_cycle_removal(W):
    global deadlock
    removed_vehicle = []
    while True:
        deadlock = False
        color = {v: 'WHITE' for v in W}
        count = {v: None for v in W}
        for v in W:
            if color[v] == 'WHITE':
                dfs(v, None, W, color, count, removed_vehicle)
                if deadlock: break
        if not deadlock: break
    return removed_vehicle

def remove_unresolvable_deadlock(Gp, config):
    for src, adj in Gp.E.items():
        src_connected = config.get_vehicle_by_id(src[0]).connected
        for *dst, edge_type in adj:
            dst = tuple(dst)
            if edge_type == 3 and (not src_connected or not config.get_vehicle_by_id(dst[0]).connected):
                Gp.try_add_edge(dst, src, 3)

    W = build_wait_for_graph(Gp)
    removed_vehicle = special_cycle_removal(W)
    return removed_vehicle
    