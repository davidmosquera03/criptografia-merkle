import requests, json

url = "http://localhost:8000/api/upload"

with open("./files/test_file_merkle.json") as f:
    nodes = json.load(f)       # full array

payload = {
    "id": "subtitulos",
    "merkleTreeModel": nodes
}

files = {
    "data": (None, json.dumps(payload)),
    "file": ("test_file.srt", open("./files/test_file.srt_blocks.bin","rb"))
}

resp = requests.post(url, files=files)
print(resp.json())
