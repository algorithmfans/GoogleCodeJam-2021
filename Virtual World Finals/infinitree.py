# Copyright (c) 2021 kamyu. All rights reserved.
#
# Google Code Jam 2021 Virtual World Finals- Problem E. Infinitree
# https://codingcompetitions.withgoogle.com/codejam/round/0000000000436329/000000000084fc01
#
# Time:  O(N^3.5 * logB) at worst, pass in PyPy2 but Python2
# Space: O(N^2.5 * logB) at worst
#

from itertools import izip

# Template:
# https://github.com/kamyu104/GoogleCodeJam-2018/blob/master/World%20Finals/swordmaster.py
def strongly_connected_components(graph):  # Time: O(|V| + |E|) = O(N + 2N) = O(N), Space: O(|V|) = O(N)
    def strongconnect(v, index_counter, index, lowlinks, stack, stack_set, result):
        index[v] = index_counter[0]
        lowlinks[v] = index_counter[0]
        index_counter[0] += 1
        stack_set.add(v)
        stack.append(v)
        for w in (graph[v] if v in graph else []):
            if w not in index:
                strongconnect(w, index_counter, index, lowlinks, stack, stack_set, result)
                lowlinks[v] = min(lowlinks[v], lowlinks[w])
            elif w in stack_set:
                lowlinks[v] = min(lowlinks[v], index[w])
        if lowlinks[v] == index[v]:
            connected_component = []
            w = None
            while w != v:
                w = stack.pop()
                stack_set.remove(w)
                connected_component.append(w)
            result.append(set(connected_component))

    index_counter, index, lowlinks = [0], {}, {}
    stack, stack_set = [], set()
    result = []
    for v in graph:
        if v not in index:
            strongconnect(v, index_counter, index, lowlinks, stack, stack_set, result)
    return result

def find_cycles(graph):  # Time: O(N), Space: O(N)
    cycle_id = 0
    adj, cycle_length = {}, {}
    for scc in strongly_connected_components(graph):
        if next(iter(scc)) == 0:
            continue
        if any(sum(int(x in scc) for x in graph[node]) != 1 for node in scc):
            continue
        cycle_id += 1
        node = next(iter(scc))
        for node in scc:
            cycle_length[node] = len(scc)
        node = next(iter(scc))
        for _ in xrange(len(scc)):
            adj[node] = [(x, side, cycle_id) for side, x in enumerate(graph[node]) if x in scc][0]
            cycle_length[node] = len(scc)
            node = adj[node][0]
    return adj, cycle_length

def ceil_log2_x(x):
    return (x-1).bit_length()

def identity_matrix(N):  # Time: O(N)
    return [[int(i == j) for j in xrange(N)] for i in xrange(N)]

def e(i, N):
    return [int(j == i) for j in xrange(N)]

def vector_mult(A, B, INF):  # Time: O(N^2), A is a N-d vector, B is a N x N matrix
    result = [0]*len(B[0])
    B_T = zip(*B)
    for i, B_T_i in enumerate(B_T):
        for _, (A_j, B_T_i_j) in enumerate(izip(A, B_T_i)):
            result[i] += A_j*B_T_i_j
            if result[i] > INF:
                result[i] = INF
                break
    return result

def matrix_mult(A, B, INF):  # Time: O(N^3), A, B are both N x N matrixs
    result = [[0]*len(B[0]) for _ in xrange(len(A))]
    B_T = zip(*B)
    for result_i, A_i in izip(result, A):
        for j, B_T_i in enumerate(B_T):
            for A_i_j, B_T_i_j in izip(A_i, B_T_i):
                result_i[j] += A_i_j*B_T_i_j
                if result_i[j] > INF:
                    result_i[j] = INF
                    break
    return result

def vector_add(A, B, INF):  # Time: O(N)
    result = [0]*len(A)
    for i, (A_i, B_i) in enumerate(izip(A, B)):
        result[i] = A_i+B_i
        if result[i] > INF:
            result[i] = INF
    return result

def matrix_add(A, B, INF):  # Time: O(N^2)
    result = [[0]*len(B[0]) for _ in xrange(len(A))]
    for result_i, A_i, B_i in izip(result, A, B):
        for j in xrange(len(result_i)):
            result_i[j] = A_i[j]+B_i[j]
            if result_i[j] > INF:
                result_i[j] = INF
    return result

def build_powers_and_prefix_powers(N, M, p, INF):  # Time: O(N^3 * p)
    I = identity_matrix(N)
    # M_powers[i] for i in xrange(1+p):
    # 0: M
    # 1: M^2
    # ...
    # p: M^(2^p)
    M_powers = [M]
    for _ in xrange(p):  # Time: O(N^3 * p)
        M_powers.append(matrix_mult(M_powers[-1], M_powers[-1], INF))
    # prefix_M_powers[i] for i in xrange(1+(1+p)):
    # 0: I
    # 1: (I + M) * I = I + M
    # 2: (I + M^2) * (I + M) = I + M + M^2 + M^3
    # ...
    # p+1: (I + M^(2^p)) * (I + M + ... + M^(2^p-1))= I + M + ... M^(2^(p+1)-1)
    prefix_M_powers = [I]
    for M_power in M_powers:  # Time: O(N^3 * p)
        matrix = matrix_add(I, M_power, INF)
        prefix_M_powers.append(matrix_mult(matrix, prefix_M_powers[-1], INF))
    return M_powers, prefix_M_powers

# M^x by matrix exponentiation
def get_M_power_x(N, M_powers, x, INF):  # Time: O(N^3 * logx)
    matrix = identity_matrix(N)
    basis, i = 1, 0
    while basis <= x:
        if x&basis:
            matrix = matrix_mult(matrix, M_powers[i], INF)
        i += 1
        basis <<= 1
    return matrix

# ei * M^x by vector-matrix exponentiation
def get_vector_M_power_x(M_powers, INF, ec, x):  # Time: O(N^2 * logx)
    u = ec
    basis, i = 1, 0
    while basis <= x:
        if x&basis:
            u = vector_mult(u, M_powers[i], INF)  # u*M^i
        i += 1
        basis <<= 1
    return u

# ei * (I + M + M^2 + ... + M^x) by vector-matrix exponentiation
def get_vector_sum_M_power_x(N, M_powers, prefix_M_powers, INF, ec, x):  # Time: O(N^2 * logx)
    x += 1
    u = [0]*N
    basis, i = 1, 0
    while basis <= x:
        if x&basis:
            # new_Pr = Pi + Pr*Mi
            # new_u = ec * new_Pr = ec * (Pi + Pr*Mi) = ec*Pi + u*Mi
            v1 = vector_mult(u, M_powers[i], INF)  # u*M^i
            v2 = vector_mult(ec, prefix_M_powers[i], INF)  # ec*Pi
            u = vector_add(v1, v2, INF)  # u*M^i + ec*Pi
        i += 1
        basis <<= 1
    return u

def get_depth(N, M_powers, prefix_M_powers, INF, B):  # Time: O(N^2 * logB)
    result = 0
    e1 = e(1, N)
    u = [0]*N
    basis = 1 << (len(M_powers)-1)
    for i in reversed(xrange(len(M_powers))):  # O(N^2 * logB)
        # new_Pr = Pi + Pr*Mi
        # new_u = e1 * new_Pr = e1 * (Pi + Pr*Mi) = e1*Pi + u*Mi
        v1 = vector_mult(u, M_powers[i], INF)  # u*M^i
        v2 = vector_mult(e1, prefix_M_powers[i], INF)  # e1*Pi
        new_u = vector_add(v1, v2, INF)  # u*M^i + e1*Pi
        if sum(new_u) < B:
            u = new_u
            result |= basis
        basis >>= 1
    return result

def get_step_position(M_powers, INF, ec, h, x):  # Time: O(N^2 * logB)
    if h == 0:
        return (LEFT, 0)
    cnt = sum(get_vector_M_power_x(M_powers, INF, ec, h-1))
    return (LEFT, x) if x < cnt else (RIGHT, x-cnt)

def get_multiple_steps_position(M_powers, prefix_M_H_powers, INF, log_p, vector, delta_h, ec, x):  # Time: O(N^2 * log(delta_h))
    left_cnt = sum(get_vector_M_power_x(M_powers, INF, vector_mult(vector, prefix_M_H_powers[log_p], INF), delta_h))
    mid_cnt = sum(get_vector_M_power_x(M_powers, INF, ec, delta_h))
    return 0 <= x-left_cnt < mid_cnt, x-left_cnt

def infinitree():
    N, A, B = map(int, raw_input().strip().split())
    L = map(int, raw_input().strip().split())
    R = map(int, raw_input().strip().split())
    N += 1
    if A > B:
        A, B, = B, A
    M = [[0]*N for _ in xrange(N)]
    INF = B
    graph = {}
    for i in xrange(1, N):
        M[i][L[i-1]] += 1
        M[i][R[i-1]] += 1
        graph[i] = [L[i-1], R[i-1]]
    M_powers, prefix_M_powers = build_powers_and_prefix_powers(N, M, ceil_log2_x(B), INF)
    h1 = get_depth(N, M_powers, prefix_M_powers, INF, A)
    h2 = get_depth(N, M_powers, prefix_M_powers, INF, B)

    adj, cycle_length = find_cycles(graph)
    M_H_powers, prefix_M_H_powers = {}, {}
    x1 = A-sum(get_vector_sum_M_power_x(N, M_powers, prefix_M_powers, INF, e(1, N), h1-1))-1
    x2 = B-sum(get_vector_sum_M_power_x(N, M_powers, prefix_M_powers, INF, e(1, N), h2-1))-1
    c, p  = 1, 0
    while True:
        if c not in adj or p == 1:  # Time: O(N^2 * logB) => Total Time: O(N^3 * logB)
            side1, new_x1 = get_step_position(M_powers, INF, e(L[c-1], N), h1, x1)
            side2, new_x2 = get_step_position(M_powers, INF, e(L[c-1], N), h2, x2)
            if side1 != side2 or (h1, x1) == (0, 0):  # found lca
                break
            prev_c = c
            c = L[c-1] if side1 == LEFT else R[c-1]
            if p == 1 and (c not in adj or adj[c][2] != adj[prev_c][2]):  # leave prev cycle forever (but may enter other cycles)
                p = 0
            h1, x1 = h1-1, new_x1
            h2, x2 = h2-1, new_x2
            continue
        prev_c = c
        h = cycle_length[c]
        if h not in M_H_powers:  # sum(distinct h) = N => distinct h at most O(sqrt(N)) times, each Time: O(N^3 * logh + N^3 * log(hi)) => Total Time: O(N^3 * logN + N^3.5 * logB) = O(N^3.5 * logB) at worst
            M_H_powers[h], prefix_M_H_powers[h] = build_powers_and_prefix_powers(N, get_M_power_x(N, M_powers, h, INF), ceil_log2_x(min(h1, h2)), INF)
        vector = [0]*N
        for x in reversed(xrange(h)):  # Time: O(h * N^2 * logN) => Total Time O(N^3 * logN)
            if adj[c][1] and adj[c][0] == R[c-1]:
                vector = vector_add(vector, get_vector_M_power_x(M_powers, INF, e(L[c-1], N), x), INF)
                c = R[c-1]
            else:
                c = L[c-1]
        p, log_p = 1, 0
        while (p*2)*h < min(h1, h2):
            log_p += 1
            p *= 2
        while p > 1:  # log(p) times => Total Time: O(N cycles * log(p) times * (N^2 * log(delta_h))) = O(N^3 * (logB)^2) at worst
            if min(h1, h2) - p*h <= 0:
                log_p -= 1
                p //= 2
                continue
            ok1, new_x1 = get_multiple_steps_position(M_powers, prefix_M_H_powers[h], INF, log_p, vector, h1-p*h, e(c, N), x1)
            ok2, new_x2 = get_multiple_steps_position(M_powers, prefix_M_H_powers[h], INF, log_p, vector, h2-p*h, e(c, N), x2)
            if not ok1 or not ok2:
                log_p -= 1
                p //= 2
                continue
            h1, x1 = h1-p*h, new_x1
            h2, x2 = h2-p*h, new_x2
            log_p -= 1
            p //= 2
    return h1+h2

LEFT, RIGHT = range(2)
for case in xrange(input()):
    print 'Case #%d: %s' % (case+1, infinitree())
