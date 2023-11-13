from sage.all import *
import struct
import re
import base64
import sys
from collections import deque
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES
from Crypto import Random
from Crypto.Cipher import PKCS1_v1_5

if __name__=="__main__":
    TQDM_ON = False
    if TQDM_ON:
        from tqdm import tqdm
    fpath = "./moduli.sorted"
    if len(sys.argv)>=2:
        fpath = sys.argv[1]
    with open(fpath) as fin:
        lines = fin.readlines()
        ns = list(map(lambda line:int(line.strip(),16),lines))
    nums = ns

    length = len(nums)
    if length<2:
        raise ValueError
    length_padded = 0
    for i in range(32):
        if (1<<i)>=length:
            length_padded = 1<<i
            break
    nums+=[1]*(length_padded-length)
    origin_len,length = length,length_padded

    nums_sage = list(map(lambda x:Integer(x),nums))
    nums_square = list(map(lambda x:x**2,nums_sage))

    index_pair_list = list()
    bfs_queue = deque([(0,length-1)])
    while len(bfs_queue)>0:
        i_pair = bfs_queue.popleft()
        index_pair_list.append(i_pair)
        l,r=i_pair
        if l<r:
            m=(l+r)>>1
            bfs_queue.append((l,m))
            bfs_queue.append((m+1,r))
    # print(index_pair_list)
        
    sq_product_table = [0]*len(index_pair_list)
    irange = range(len(index_pair_list)-1,-1,-1)
    if TQDM_ON:
        irange = tqdm(irange)
    for i in irange:
        l,r = index_pair_list[i]
        if l==r:
            sq_product_table[i] = nums_square[l]
        else:
            sq_product_table[i] = sq_product_table[2*i+1]*sq_product_table[2*i+2]

    
    product_table = [0]*len(index_pair_list)
    irange = range(len(index_pair_list)-1,-1,-1)
    if TQDM_ON:
        irange = tqdm(irange)
    for i in irange:
        l,r = index_pair_list[i]
        if l==r:
            product_table[i] = nums_sage[l]
        else:
            product_table[i] = product_table[2*i+1]*product_table[2*i+2]
    total_product = product_table[0]


    mod_ni_square_table = [0]*len(index_pair_list)
    mod_ni_square_table[0] = total_product
    irange = range(1,len(index_pair_list))
    if TQDM_ON:
        irange = tqdm(irange)
    for i in irange:
        mod_ni_square_table[i] = mod_ni_square_table[(i-1)>>1]%sq_product_table[i]
        
    mod_ni_square = [0]*length
    for i in range(len(index_pair_list)-1,-1,-1):
        l,r = index_pair_list[i]
        if l<r:
            break
        mod_ni_square[l] = mod_ni_square_table[i]
        
    gcd_helper_res= list(gcd(nums_sage[i],mod_ni_square[i]//nums_sage[i]) for i in range(length))[:origin_len]


    have_gcd_lines_i = list()

    for i,r in enumerate(gcd_helper_res):
        if r>1:
            have_gcd_lines_i.append(i)

    a,b = have_gcd_lines_i[:2]
    n_a,n_b = int(lines[a],16),int(lines[b],16)
    print(f"{n_a},{n_b}",end="")
