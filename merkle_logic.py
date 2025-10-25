# imports


# get merkle tree
"""
input: file
output: merkle tree root, merkle tree array

Ex:
i: algo.txt
output: ()
"""

def get_merkle_tree(file):
    # divide into blocks of 4kB
    # if not power of 2
    # add padding to last block or new block

    # for i to n make hash h(xi)
    # for i to n-1 make hash(y_2i-1 ,y2i)

    # append each hash to main array
    return 




# get merkle proof
"""
input: array with index of blocks
output: merkle proof, the intermediate blocks required to 
compute merkle tree root
"""

def get_merkle_proof(blocks):
    return
