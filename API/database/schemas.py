
def individual_merkle_tree_schema(id, merkle_tree) -> dict:
    return {
        "id": str(id),
        "merkleTreeModel": merkle_tree["merkleTreeModel"],
        "filename": merkle_tree.get("filename", ""),
        "content": merkle_tree.get("content", b"").decode('utf-8', errors='ignore')
    }

    

def list_merkle_trees_schema(merkle_trees) -> list:
    results = []
    for tree in merkle_trees:
        result = individual_merkle_tree_schema(tree.get("id", ""), tree)
        result = {"id": result["id"]}
        results.append(result)
    return results

def get_merkle_tree_index(index, merkle_trees) -> dict:
    try:
        tree = merkle_trees[index]
        return individual_merkle_tree_schema(tree.get("index", ""), tree)
    except IndexError:
        return {}
    
def get_logs_schema(logs) -> list:
    results = []
    for log in logs:
        results.append({
            "challenge_id": log["challenge_id"],
            "result": log["result"]
        })
    return results