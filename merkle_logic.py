# imports
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

# get merkle tree
"""
input: file_path
output: merkle tree root, merkle tree array

Ex:
i: algo.txt
output: ()
"""

def get_merkle_tree(file_path):
    data = []
    # open file
    with open(file_path, 'rb') as f:
        while True:
            chunk = f.read(4096)
            # divide into blocks of 4kB
            if not chunk:
                break
            data.append(chunk)
    #print(len(data))
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

    # for i to n make hash h(xi)
    merkle_tree = []
    n = len(data)
    for i in range(0,n):
        merkle_tree.append(hash_data(data[i]))
    
    # for i to n-1 make hash(y_2i-1 ,y2i)
    for i in range(0,n-1):
        left = merkle_tree[2*i]
        right = merkle_tree[2*i+1]
        parent = hash_data(left + right)
        merkle_tree.append(parent)
    print(f"Nodes 2*n-1: {len(merkle_tree)==(2*n-1)}")
    print(merkle_tree[-1])
    return  merkle_tree

merkle = get_merkle_tree("./files/foto.png")
merkle1 = get_merkle_tree("./files/test_file.srt")

# get merkle proof
"""
input: array with index of blocks
output: merkle proof, the intermediate blocks required to 
compute merkle tree root
"""

def get_merkle_proof(blocks):
    return
