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


def corrupt_merkle_tree(file_path, percentage):
    """
    Makes a new merkle_tree based on corrupted file

    input: 
        file_path
        percentage: 0 to 1, % of blocks damaged
    
    output: merkle tree from corrupted data
    """
    data = []
    SIZE = 4096
    
    # Open file and read blocks
    with open(file_path, 'rb') as f:
        while True:
            chunk = f.read(SIZE)
            if not chunk:
                break
            data.append(bytearray(chunk))  # Use bytearray for mutability
    
    length = len(data)
    last_block_len = len(data[-1])

    # Pad last block if needed
    if last_block_len < SIZE:
        #print(f"{last_block_len}b in last block not right size")
        data[-1] += bytearray(SIZE - last_block_len)
        #print(f"size now {len(data[-1])}b")
    else:
        print("Final block ok.")

    # Add padding blocks to make power of 2
    if not is_power_of_2(length):
        print(f"Block no. {length} is not power of 2")
        closest_pow = 1 << length.bit_length()
        blocks_needed = closest_pow - length
        data += [bytearray(SIZE)] * blocks_needed
        print(f"length now {len(data)}")
    else:
        print("Block no. ok.")

    # Corrupt random blocks
    num_blocks_to_corrupt = int(len(data) * percentage)
    blocks_to_corrupt = random.sample(range(len(data)), num_blocks_to_corrupt)
    
    print(f"Corrupting {num_blocks_to_corrupt} blocks: {blocks_to_corrupt}")
    
    for block_idx in blocks_to_corrupt:
        # Choose random byte and bit position
        byte_pos = random.randint(0, SIZE - 1)
        bit_pos = random.randint(0, 7)
        
        # Flip the bit
        data[block_idx][byte_pos] ^= (1 << bit_pos)
        print(f"  Block {block_idx}: flipped bit {bit_pos} in byte {byte_pos}")

    # Build merkle tree from corrupted data
    merkle_tree = []
    n = len(data)
    
    # Hash leaf nodes
    for i in range(n):
        merkle_tree.append({
            "index": i,
            "data": hash_data(bytes(data[i])).hex()
        })
    
    # Build parent nodes
    for i in range(n - 1):
        left = merkle_tree[2*i]["data"]
        right = merkle_tree[2*i+1]["data"]
        parent = hash_data(bytes.fromhex(left) + bytes.fromhex(right)).hex()
        merkle_tree.append({"index": i+n, "data": parent})
    
    print(f"Nodes=2*n-1: {len(merkle_tree)==(2*n-1)}")
    print(f"Corrupted root: {merkle_tree[-1]}")

    # Save corrupted merkle tree
    out_path = os.path.splitext(file_path)[0] + "_corrupted_merkle.json"
    with open(out_path, "w") as out:
        json.dump(merkle_tree, out, indent=2)
    print(f"Corrupted merkle tree saved to {out_path}")
    
    return merkle_tree

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

    out_path = os.path.splitext(file_path)[0] + "_merkle.json"
    with open(out_path, "w") as out:
        json.dump(merkle_tree, out, indent=2)
    print(f"Merkle tree saved to {out_path}")
    return merkle_tree

# USADA POR SERVIDOR
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

    # get the blocks from index
    # NOTA, para pruebas de corrupcion
    # solo usar esta ruta si ya se corrompió el archivo y recomputó su arbol
    leaf_nodes = [{"index": i, "data": tree[i]} for i in indexes]

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
    return leaf_nodes, proof

# USADA POR CLI
def recompute_merkle_root(leaf_nodes, merkle_proof, n):
    """
    recomputes the merkle tree root
    based on the merkle proof and leaf nodes

    IMPORTANTE: esta ruta asume que los leaf_nodes ya han
    sido hasheados al ser entregados

    si se pasan los bloques originales, hashearlos antes de 
    pasarlos en el argumento
    
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

# EXAMPLES

def test_normal():
    # Generate Merkle Tree
    file_path = "./files/test_file.srt"
    get_merkle_tree(file_path)

    # get tree
    tree_path = "./files/test_file_merkle.json"
    with open(tree_path) as f:
        tree = json.load(f)

    # choose index of blocks for test
    # simulates (challenge creation)
    indexes = [2]

    # get index blocks and proof (simulates prove)
    leaf_nodes, proof = get_merkle_proof(indexes, tree)
    print("Merkle Proof:")
    for p in proof:
        print(p)

    n = (len(tree) + 1)//2

    # use merkle proof and blocks to check integrity
    # simulates (verify)
    root = recompute_merkle_root(leaf_nodes, proof, n)
    print("recomputed:", root)
    print("actual   :", tree[-1])
    print("File integrity safe: ",root==tree[-1])

def test_corrupted(percentage):
    # make corrupt tree 
    file_path = "./files/test_file.srt"
    corrupt_merkle_tree(file_path,percentage)

    # get correct tree (simulates whats on manifest.json)
    og_tree_path = "./files/test_file_merkle.json"
    with open(og_tree_path) as f:
        og_tree = json.load(f)

    # get corrupt tree
    tree_path = "./files/test_file_corrupted_merkle.json"
    with open(tree_path) as f:
        tree = json.load(f)

    # choose index of blocks for test (simulates challenge creation)
    indexes = [2]

    # get index blocks and proof (simulates prove)
    leaf_nodes, proof = get_merkle_proof(indexes, tree)
    print("Merkle Proof:")
    for p in proof:
        print(p)

    n = (len(tree) + 1)//2

    # use merkle proof and blocks to check integrity (simulates verify)
    root = recompute_merkle_root(leaf_nodes, proof, n)
    print("recomputed:", root)
    print("actual   :", og_tree[-1])
    print("File integrity safe: ",root==og_tree[-1])

def test_corrupted2(percentage): # THE IMPORTANT ONE
    # Corrupt the file
    corrupt_file("./files/test_file.srt", percentage)
    
    # Get original tree (from manifest)
    og_tree_path = "./files/test_file_merkle.json"
    with open(og_tree_path) as f:
        og_tree = json.load(f)
    
    # Get corrupted file's tree
    corrupted_tree = get_merkle_tree("./files/test_file_corrupted.srt")
    
    # Choose blocks to challenge
    indexes = [2]
    
    # Get proof from corrupted file
    leaf_nodes, proof = get_merkle_proof(indexes, corrupted_tree)
    
    n = (len(corrupted_tree) + 1) // 2
    
    # Recompute root and compare to original
    recomputed_root = recompute_merkle_root(leaf_nodes, proof, n)
    
    print("Recomputed root:", recomputed_root)
    print("Original root  :", og_tree[-1])
    print("File integrity safe:", recomputed_root == og_tree[-1])


#test_normal()
#test_corrupted(0.2)
#test_corrupted2(0.0001)
