# imports
import hashlib
import json, os
import random

def hash_data(data):
    return hashlib.sha256(data).digest()


def is_power_of_2(n):
     """
     checks if number is power of 2

     input: n
     output: true or false

     bin(N) & bin(N-1) should be 0
     if power of 2
     as it shares no bits
     """
     return n > 0 and (n & (n - 1)) == 0

# USADA POR SERVIDOR
def corrupt_file(file_path, percentage):
    """
    Corrupts a percentage of a file by flipping random bits
    
    input: 
        file_path: path to file
        percentage: 0 to 1, % of file to corrupt
    
    output: path to corrupted file
    """
    # Read entire file
    with open(file_path, 'rb') as f:
        data = bytearray(f.read())
    
    file_size = len(data)
    num_bits_to_corrupt = int(file_size * 8 * percentage)
    print(f"Corrupting {num_bits_to_corrupt} bits out of {file_size * 8} total bits")
    
    # Corrupt random bits
    corrupted_positions = random.sample(range(file_size * 8), num_bits_to_corrupt)
    
    for bit_pos in corrupted_positions:
        byte_idx = bit_pos // 8
        bit_idx = bit_pos % 8
        data[byte_idx] ^= (1 << bit_idx)
    
    # Save corrupted file
    out_path = os.path.splitext(file_path)[0] + "_corrupted" + os.path.splitext(file_path)[1]
    with open(out_path, 'wb') as f:
        f.write(data)
    
    print(f"Corrupted file saved to {out_path}")
    return out_path


# USADA POR CLI y SERVIDOR
def get_merkle_tree(file_path):
    """
    input: file_path
    output: merkle tree root, merkle tree array

    Ex:
    i: algo.txt
    output: []
    """

    data = []
    SIZE = 4096
    # open file
    with open(file_path, 'rb') as f:
        while True:
            chunk = f.read(SIZE)
            # divide into blocks of 4kB
            if not chunk:
                break
            data.append(chunk)
    length = len(data)
    last_block_len = len(data[-1])

    # if last block is not 4096, add padding
    if last_block_len<SIZE:
        print(f"{last_block_len}b in last block not right size")
        data[-1] += b'\x00' * (SIZE - last_block_len)
        print(f"size now {len(data[-1])}b")
    else:
        print("Final block ok.")

    if not is_power_of_2(length):
        print(f"Block no. {length} is not power of 2")
        closest_pow = 1 << length.bit_length()
        blocks_needed = closest_pow - length
        data += [b'\x00' * SIZE] * blocks_needed
        print(f"length now {len(data)}")
    else:
        print("Block no. ok.")

    # first n elements are leaves
    # for i to n make hash h(xi)
    merkle_tree = []
    n = len(data)
    for i in range(0,n):
        merkle_tree.append({"index":i,
            "data":hash_data(data[i]).hex()
            })
    # for i to n-1 make hash(y_2i-1 ,y2i)=y_i+n
    for i in range(0,n-1):
        left = merkle_tree[2*i]["data"]
        right = merkle_tree[2*i+1]["data"]
        parent = hash_data(bytes.fromhex(left) + bytes.fromhex(right)).hex()
        merkle_tree.append({"index":i+n,"data":parent})
    print(f"Nodes=2*n-1: {len(merkle_tree)==(2*n-1)}")
    print(merkle_tree[-1])

    # save merkle tree
    out_path = os.path.splitext(file_path)[0] + "_merkle.json"
    with open(out_path, "w") as out:
        json.dump(merkle_tree, out, indent=2)
    print(f"Merkle tree saved to {out_path}")

    # save binary blocks
    blocks_path = file_path + "_blocks.bin"
    with open(blocks_path, "wb") as bf:
        for b in data:
            bf.write(b)
    return merkle_tree

# USADA POR CLI Y SERVIDOR
def get_merkle_proof(indexes, tree_json):
    """
    inputs:
        indexes: array of index of blocks for verification
        tree_json: the merkle tree loaded from JSON

    returns: (leaf_nodes, proof)
    leaf_nodes: [{"index": i, "data": hash}, ...] for each index
    proof:      [{"index": s, "data": hash}, ...] 
    """
    tree = {node["index"]: node["data"] for node in tree_json}
    n = (len(tree_json) + 1) // 2
    idx = set(indexes)
    proof = []

    # walk internal nodes to gather sibling hashes needed
    # idx will hold indices currently "covered"
    covered = set(indexes)
    for i in range(n - 1):
        l, r, p = 2 * i, 2 * i + 1, i + n
        left, right = tree[l], tree[r]

        if l in covered and r not in covered:
            proof.append({"index": r, "data": right})
            covered.add(p)
        elif r in covered and l not in covered:
            proof.append({"index": l, "data": left})
            covered.add(p)
        elif l in covered and r in covered:
            covered.add(p)
    return proof

# USADA POR CLI Y SERVIDOR
def recompute_merkle_root(leaf_nodes, merkle_proof, n):
    """
    recomputes the merkle tree root
    based on the merkle proof and leaf nodes
    """
    # merge both lists (proof + leaves) and sort
    merged = sorted(leaf_nodes + merkle_proof, key=lambda x: x["index"])
    print("merged start:", [m["index"] for m in merged])

    while len(merged) > 1:
        l, r = merged.pop(0), merged.pop(0)

        parent_idx = n + (l["index"] // 2)
        parent_hash = hashlib.sha256(
            bytes.fromhex(l["data"]) + bytes.fromhex(r["data"])
        ).hexdigest()

        merged.append({"index": parent_idx, "data": parent_hash})
        merged.sort(key=lambda x: x["index"])

    return merged[0]

# USADA POR CLI Y SERVIDOR
def get_challenge_blocks(file_path, indexes, nonce, block_size=4096):
    """
    retrieves raw blocks from binary file of original file 
    and hashes with nonce for use in challenge
    """
    out = []
    with open(file_path, "rb") as f:
        for i in indexes:
            f.seek(i * block_size)
            block = f.read(block_size)
            #print("hash normal",hash_data(block).hex())
            h = hashlib.sha256(block + nonce).hexdigest()
            out.append({"index": i, "data": h})
    return out

def get_blocks(file_path,indexes,block_size=4096):
    """
    TEST method to retrieve hash of block given index
    """
    out = []
    with open(file_path, "rb") as f:
        for i in indexes:
            f.seek(i * block_size)
            block = f.read(block_size)
            #print("hash normal",hash_data(block).hex())
            h = hashlib.sha256(block).hexdigest()
            out.append({"index": i, "data": h})
    return out

def test_execution():

    # 1 UPLOAD
    # A. get path and make tree
    file_path = "./files/test_file.srt"
    tree = get_merkle_tree(file_path)
    
    # 2 CHALLENGE
    # A. indexes and nonce
    indexes = [2]
    nonce = os.urandom(32)

    # B. blocks hashes with nonce, get proof
    challenge_blocks = get_challenge_blocks("./files/test_file.srt_blocks.bin",indexes,nonce)
    proof = get_merkle_proof(indexes,tree)
    # C. make new root R'
    n = (len(tree) + 1)//2
    root_prime = recompute_merkle_root(challenge_blocks,proof,n)
    print(root_prime)

    # server will do 2A, 2B, 2C with its own file
    

def test_corrupted(percentage): # THE IMPORTANT ONE

    #DONE BY SERVER
    # Corrupt the file
    corrupt_file("./files/test_file.srt", percentage)

    # Make corrupted file tree
    corrupted_tree = get_merkle_tree("./files/test_file_corrupted.srt")

    # Now proceed with 2 (Challenge)

#test_execution()
#test_corrupted(0.001)