import hashlib

def hash_data(data):
    return hashlib.sha256(data).digest()

def is_power_of_2(n):
    return (n & (n-1) == 0) and n != 0

# Your original function
def get_merkle_tree(file_path):
    # ... your code exactly as written ...
    data = []
    with open(file_path, 'rb') as f:
        while True:
            chunk = f.read(4096)
            if not chunk:
                break
            data.append(chunk)
    
    length = len(data)
    last_block_len = len(data[-1])

    if last_block_len < 4096:
        data[-1] += b'\x00' * (4096 - last_block_len)

    if not is_power_of_2(length):
        closest_pow = 1 << length.bit_length()
        blocks_needed = closest_pow - length
        data += [b'\x00' * 4096] * blocks_needed

    merkle_tree = []
    n = len(data)
    for i in range(0,n):
        merkle_tree.append(hash_data(data[i]))
    
    for i in range(0,n-1):
        left = merkle_tree[2*i]
        right = merkle_tree[2*i+1]
        parent = hash_data(left + right)
        merkle_tree.append(parent)
    
    print(f"Total nodes: {len(merkle_tree)} (2*n-1 = {2*n-1})")
    return merkle_tree

# Create a test file with 4 blocks
test_data = [b'block0', b'block1', b'block2', b'block3']
with open('./test/test.txt', 'wb') as f:
    for block in test_data:
        f.write(block.ljust(4096, b'\x00'))

# Test your function
tree = get_merkle_tree('./test/test.txt')

# Let's manually verify the tree structure
print("\nManual verification:")
n = 4  # After padding to power of 2
leaves = tree[:n]
print(f"Leaves (0-{n-1}): {[h.hex()[:8] for h in leaves]}")

# Check if parent calculations are correct
for i in range(n-1):
    expected_parent = hash_data(tree[2*i] + tree[2*i+1])
    actual_parent = tree[n + i]
    print(f"Parent {i}: expected={expected_parent.hex()[:8]} actual={actual_parent.hex()[:8]} match={expected_parent == actual_parent}")