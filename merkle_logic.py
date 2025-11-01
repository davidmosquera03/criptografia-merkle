# FIRST VERSION, SAVED FOR REFERENCE
import hashlib

def hash_data(data):
    return hashlib.sha256(data).digest()

def is_power_of_2(n):
     """
     checks if number is power of 2

     bin(N) & bin(N-1) == 0
     as it shares no bits
     """
     return n > 0 and (n & (n - 1)) == 0


def get_merkle_tree(file_path):
    """
    input: file_path
    output: merkle tree root, merkle tree array

    Ex:
    i: algo.txt
    output: []
    """
    data = []
    # open file
    with open(file_path, 'rb') as f:
        while True:
            chunk = f.read(4096)
            # divide into blocks of 4kB
            if not chunk:
                break
            data.append(chunk)
    length = len(data)
    last_block_len = len(data[-1])

    # if last block is not 4096, add padding
    if last_block_len<4096:
        print(f"{last_block_len}b in last block not right size")
        data[-1] += b'\x00' * (4096 - last_block_len)
        print(f"size now {len(data[-1])}b")
    else:
        print("Final block ok.")

    if not is_power_of_2(length):
        print(f"Block no. {length} is not power of 2")
        closest_pow = 1 << length.bit_length()
        blocks_needed = closest_pow - length
        data += [b'\x00' * 4096] * blocks_needed
        print(f"length now {len(data)}")
    else:
        print("Block no. ok.")

    # first n elements are leaves
    # for i to n make hash h(xi)
    merkle_tree = []
    n = len(data)
    for i in range(0,n):
        merkle_tree.append(hash_data(data[i]))
    
    # for i to n-1 make hash(y_2i-1 ,y2i)=y_i+n
    for i in range(0,n-1):
        left = merkle_tree[2*i]
        right = merkle_tree[2*i+1]
        parent = hash_data(left + right)
        merkle_tree.append(parent)
    print(f"Nodes=2*n-1: {len(merkle_tree)==(2*n-1)}")
    print(merkle_tree[-1])
    return  merkle_tree

""" merkle = get_merkle_tree("./files/foto.png")
merkle1 = get_merkle_tree("./files/test_file.srt")
 """



def get_merkle_proof(index,tree):
    """
    input: array with indexes, merkle tree
    output: merkle proof
    """
    proof = []
    indexes = index.copy()
    # l = 2*n-1 
    # n = (l+1)/2
    n = (len(tree)+1)//2

    # move through pairs, ignore root
    for i in range(0,n-1,1):
        left = tree[2*i]
        right = tree[2*i+1]
        parent = tree[i+n]
        #if left and right not in index
        # pass
        if (left not in indexes) and (right not in indexes):
            pass

        # if both in index
        # add parent to indexes
        if (left in indexes) and (right in indexes):
            indexes.append(parent)

        # if (r/l) in index
        # add (l/r) to proof
        # add parent to index
        if (right in indexes) and (left not in indexes):
            proof.append(left)
            indexes.append(parent)
        if (left in indexes) and (right not in indexes):
            proof.append(right)
            indexes.append(parent)
    return proof


print(get_merkle_proof([1,8],[i for i in range(0,31)]))
# recompute merkle root
"""
input: merkle proof
output: merkle root
"""

def recompute_merkle_root(merkle_proof,indexes,n):
    merged = sorted(merkle_proof+indexes)
    print(merged)

    while len(merged)>1:
        l,r = merged.pop(0),merged.pop(0)
        merged.append(n+(l//2))
        merged.sort()
    return merged
