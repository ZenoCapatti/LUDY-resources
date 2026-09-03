import numpy as np
import itertools
import time
import os
import sys

# Loop through all subset of lenth n of the set of
# all integers from 0 to set_size-1


def get_next_subset(subset, set_size, bottom_up=True):
    n = len(subset)
    # Move subset forward
    if bottom_up:
        for i in range(n):
            if i+1 == n or subset[i]+1 < subset[i+1]:
                subset[i] += 1
                for j in range(i):
                    subset[j] = j
                return subset[-1] < set_size

    # Move subset backward
    else:
        for i in range(n):
            if subset[i] > i:
                subset[i] -= 1
                for j in range(1, i+1):
                    subset[i-j] = subset[i] - j
                return subset[-1] < set_size
        return False


def get_next_set_pair(subset1, subset2, set_size):
    # Move subset1 forward and subset2 backward
    # if subset1 U subset2 == set
    # then this holds true also after the iteration
    return get_next_subset(subset1, set_size, True) and get_next_subset(subset2, set_size, False)


def partial_fractioning(h_index, e_index, num=[], num_rank=100):
    n_h = len(h_index)-1
    n_e = len(e_index)
    k = h_index[0]
    num += [k]
    if n_e == 0:
        if num_rank == 0 and len(h_index) != 1:
            return []
        else:
            return [[[], h_index.copy()]]
    if n_h == 0:
        return [[[(k, i) for i in e_index], num]]

    res = []
    splits = [n-1 for n in range(n_h)]
    sub_exp = [[] for n in range(n_e+n_h)]
    while get_next_subset(splits, n_e+n_h-1):
        sub_exp[0:splits[0]+1] = [(k, e_index[j]) for j in range(splits[0]+1)]
        for n in range(n_h):
            if n+1 != n_h:
                sub_exp[splits[n]+1: splits[n+1]+1] = [
                    (h_index[n+1], e_index[j-n]) for j in range(splits[n], splits[n+1])]
            else:
                sub_exp[splits[n]+1:] = [(h_index[n+1], e_index[j-n])
                                         for j in range(splits[n], n_e+n_h-1)]
        res += [[sub_exp.copy(), num.copy()]]

    if num_rank >= 1:
        res += partial_fractioning(h_index[1:], e_index, num, num_rank-1)

    return res

# Map the to new triplet


def pf_mapper(den_giver, den_receiver, residue_n):
    den_mapped = {}
    factor = den_receiver['lambdas'][residue_n]/den_giver['lambdas'][residue_n]

    den_mapped['energies'] = den_receiver['energies'] - \
        factor*den_giver['energies']
    den_mapped['shifts'] = den_receiver['shifts'] - \
        factor*den_giver['shifts']
    den_mapped['lambdas'] = den_receiver['lambdas'] - \
        factor*den_giver['lambdas']

    return den_mapped

# Create all the terms that apperar when taking a residue overe the enrgy at one loop
# in addition it is also possible to require the presence of some hyperboloids in the input
# indices as well as ellipsoids.
#
# Example (Triangle):
#  - default:
#      (123|) (12|3) (13|2) (23|1) (12|3) (1|23) (2|13) (3|12) (|123)
#  - require_hs = [1], require_es = [3]
#      (12|3) (1|23)


def partial_fractioning_1L(n_props, num_rank=100, indices=None, require_hs=[], require_es=[]):
    if indices is not None and len(indices) != n_props:
        print("Need to input {} indices in oderd to do the mapping".format(n_props))
        sys.exit()

    res = []
    for ne in range(n_props):
        nh = n_props-ne - 1
        lh = [i for i in range(nh+1)]
        le = [i+nh for i in range(1, ne+1)]
        while True:
            if any([i in require_es for i in lh]) or any([i in require_hs for i in le]):
                print("dump: ", lh, le)
    #        print(lh, le)

            res += partial_fractioning(lh, le, [], num_rank=num_rank)
            if not get_next_set_pair(lh, le, propN):
                break
    # print(res)
    if indices is None:
        return res
    else:
        res_shifted = []
        for d, n in res:
            #        print("@", [d, n], indices)
            res_shifted += [[[[indices[i] for i in e]for e in d],
                             [indices[i] for i in n]]]
    #        print(">", res_shifted[-1])
    return res_shifted


def partial_fractioning_NL(ll_n_props, signatures, n_loops, verbose=False):
    # ll_n_props: number of propagator per loop line
    # signatures: signature of each loop line
    # sigmas: sign coming from closing the contour
    id_to_ll = []
    for n, n_props in enumerate(ll_n_props):
        id_to_ll += [n for _ in range(n_props)]
    n_props = sum(ll_n_props)
    dens_plus = [{'energies': np.array([0 if n != i else 1 for i in range(n_props)]),
                  'shifts': np.array([0 if n != i else 1 for i in range(n_props)]),
                  'lambdas': np.array(signatures[id_to_ll[n]].copy())} for n in range(n_props)]
    dens_minus = [{'energies': np.array([0 if n != i else -1 for i in range(n_props)]),
                   'shifts': np.array([0 if n != i else 1 for i in range(n_props)]),
                   'lambdas': np.array(signatures[id_to_ll[n]].copy())} for n in range(n_props)]

    # for dp, dm in zip(dens_plus, dens_minus):
    #    print(dp)
    #    print(dm)
    #    print("")
    # Take all combination of plus and minus energies from the first E_fractioning
    #    0: positive energy
    #    1: negative energy
    # TODO: the positive enegy component comes with a - sign
    # for choose in itertools.combinations_with_replacement([0, 1], n_props):
    pf_res = []
    for choose in itertools.product([0, 1], repeat=n_props):
        product = []
        if verbose:
            print("\n\nchoose: ", choose)
        for dpm, which in zip(zip(dens_plus, dens_minus), choose):
            product += [dpm[which]]

        # factor coming from the initial partial fractioning into positive and negative energies
        global_factor = (-1)**choose.count(0)
        pf_res += pf_product(product, n_loops,
                             global_factor=global_factor, verbose=verbose)
#        for n, res in enumerate(pf_product(product, n_loops)):
#            print("PF RESULT :: %d" %n)
#            for d in res[1]:
#                print("\t", d)
    return pf_res

# Perform partial fractioning on a single product for an arbitrary number of loops


def pf_product(product, n_loops, r=0, global_factor=1.0, numerator=[], verbose=False):
    if r == n_loops:
        # Return the result with the corresponding factor in the case that all
        # the momenta have been removed by the procedure
        if not all([all(den['lambdas'] == 0) for den in product]):
            raise("There are still some loop momenta left")
        return [(global_factor, [{k: v for k, v in x.items() if k != 'lambdas'} for x in product], numerator)]

    if verbose:
        print("="*40)
        print("{}LOOP {}".format(" "*15, r))
        print("="*40)
    indices = []
    h_index = []
    e_index = []
    left_product = []
    for n, den in enumerate(product):
        factor = den['lambdas'][r]
        if factor != 0:  # Element depneds on the loop momenta
            # Extract the factor in front of the loop momenta in order to
            # to have a consistent unit factor before taking the residue
            global_factor /= factor
            den['energies'] = den['energies'] / factor
            den['shifts'] = den['shifts'] / factor
            den['lambdas'] = den['lambdas'] / factor

            indices += [n]
            if all(den['energies'] >= 0):
                e_index += [n]
            else:
                h_index += [n]
        else:
            left_product += [den]
    if verbose:
        print("  idx: ", indices, "hdx: ", h_index, "edx: ", e_index)
    # factor coming from applying partial fractioning to remove hyperboloids
    global_factor *= (-1)**len(h_index)
    if len(h_index) == 0:  # no pole
        return []
    else:  # apply residue and partial fractioni)g
        res = partial_fractioning(h_index, e_index, num=[], num_rank=0)
    if verbose:
        print(res)
    if res == []:
        return res

    result = []
    for mapping in res:
        new_product = left_product.copy()
        if verbose:
            print("\t   > ", mapping)
        for pair in mapping[0]:
            new_product += [pf_mapper(product[pair[0]], product[pair[1]], r)]

        if verbose:
            for prod in new_product:
                print("\t   @ ", prod)

        num = numerator + [mapping[1]]
        result += pf_product(new_product, n_loops, r+1,
                             global_factor=global_factor, numerator=num, verbose=verbose)
    return result


if __name__ == '__main__':

    #########################################
    #              1-LOOP                   #
    #########################################
    n_loops = 1
    signatures = [[1]]

    print("1-LOOP :")
    t0 = time.time()
    res = partial_fractioning_NL([2], signatures, n_loops, verbose=False)
    print(len(res))
    print(":{}:\n".format(time.time()-t0))

    for fact, prod, num in res:
        print(":: {}\t{}".format(fact, num))
        # print(fact)
        # print(prod)
        for r in prod:
            print("\t", r)

#    sys.exit(0)
    #########################################
    #              2-LOOP                   #
    #########################################
    n_loops = 2
    signatures = [[1, 0], [1, -1], [0, 1]]

    print("2-LOOP :")
    t0 = time.time()
    res = partial_fractioning_NL([2, 1, 1], signatures, n_loops, verbose=True)
    print(len(res))
    print(":{}:\n".format(time.time()-t0))

    for fact, prod, num in res:
        print(":: {}\t{}".format(fact, num))
        # print(fact)
        # print(prod)
        for r in prod:
            print("\t", r)

 
    #########################################
    #              FISHNET                  #
    #########################################
    n_loops = 4
    signatures = [[1, 0, 0, 0],
                  [0, 1, 0, 0],
                  [1, -1, 0, 0],
                  [-1, 0, -1, 0],
                  [0, -1, 0, -1],
                  [0, 0, 1, 0],
                  [0, 0, -1, 1],
                  [0, 0, 0, -1]]


    #    print(r)
    print("FISHNET :")
    t0 = time.time()
    res = partial_fractioning_NL([2,2,1,1,1,2,1,2], signatures, n_loops)
    print(len(res))
    print(":{}:\n".format(time.time()-t0))
    #for fact, prod, num in res:
    #    print(":: {}\t{}".format(fact, num))
    #    # print(fact)
    #    # print(prod)
    #    for r in prod:
    #        print("\t", r)


    #########################################
    #           OLD 1-LOOP                   #
    #########################################
    propN = 10
    t0 = time.time()
    # , indices=[[1], [2], [3]])
    res = partial_fractioning_1L(propN, num_rank=1000)
    print("1L: ", len(res))
    # for r in res:
    #    print(r)
    print(":{}:".format(time.time()-t0))

    counter = 0
    for (d, n) in res:
        if len(d) == propN-1:
            counter += 1

    print(counter)
    # Store into a file
    print("RESULT SPLIT:")
    t0 = time.time()
    ss = "{"
    for x, num in res:
        ss += "\n{"
        if len(x) == 0:
            ss += "{}{},num{}".format('{', '}', num)
        for i, t in enumerate(x):
            if i+1 == len(x):
                ss += "{}{},{}{},num{}".format('{', *t, '}', num)
            else:
                ss += "{}{},{}{},".format('{', *t, '}')
        ss += "},"
    ss = ss[:-1] + "}"
    print(":{}:".format(time.time()-t0))

    # print(ss)
    with open("part_frac.m", 'w') as f:
        f.write(ss)
