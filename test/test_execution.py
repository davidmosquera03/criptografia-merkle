import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from merkle_implementation import *

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
test_execution()