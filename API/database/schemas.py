def individual_merkle_tree_schema(id, merkle_tree) -> dict:
    return {
        "id": str(id),
        "merkleTreeModel": merkle_tree["merkleTreeModel"],
        "filename": merkle_tree.get("filename", ""),
        "content": merkle_tree.get("content", b"").decode('utf-8', errors='ignore')
    }

    

def list_merkle_trees_schema(merkle_trees) -> list:
    return [individual_merkle_tree_schema(merkle_tree) for merkle_tree in merkle_trees]

