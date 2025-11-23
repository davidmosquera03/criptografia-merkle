import base64
import os
import sys
import json
import uuid
import random
from pathlib import Path

import click
import requests

# Importación de la implementación de Merkle
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from merkle_implementation import (
    get_merkle_tree,
    get_challenge_blocks,
    get_merkle_proof,
    recompute_merkle_root,
)

DEFAULT_API_URL = "http://localhost:8000/api"
BLOCK_SIZE = 4096

STATE_DIR = Path(".merkle_client")
STATE_DIR.mkdir(exist_ok=True)


def manifest_path(file_id: str) -> Path:
    return STATE_DIR / f"{file_id}_manifest.json"


def challenge_meta_path(challenge_id: str) -> Path:
    return STATE_DIR / f"challenge_{challenge_id}.json"


@click.group()
@click.option(
    "--api-url",
    envvar="MERKLE_API_URL",
    default=DEFAULT_API_URL,
    help="URL base de la API (default: http://localhost:8000/api)",
)
@click.pass_context
def cli(ctx, api_url):
    """Cliente CLI para Merkle Proof-of-Retrievability."""
    ctx.ensure_object(dict)
    ctx.obj["API_URL"] = api_url.rstrip("/")


# ============================================================
#                      UPLOAD
# ============================================================

@cli.command()
@click.argument("file_path", type=click.Path(exists=True))
@click.option("--file-id", "-i", required=True)
@click.pass_context
def upload(ctx, file_path, file_id):

    api = ctx.obj["API_URL"]
    file_path = Path(file_path)

    click.echo(f"[*] Generando Merkle Tree de {file_path}...")

    tree = get_merkle_tree(str(file_path))

    n = (len(tree) + 1) // 2
    root_hash = tree[-1]["data"]

    tree_json_path = Path(str(file_path).split(".")[0] + "_merkle.json")
    blocks_path = str(file_path) + "_blocks.bin"

    manifest = {
        "file_id": file_id,
        "filename": str(file_path),
        "block_size": BLOCK_SIZE,
        "num_blocks": n,
        "root_hash": root_hash,
        "hash_algorithm": "SHA-256",
        "tree_path": str(tree_json_path),
        "blocks_path": blocks_path,
    }

    manifest_path(file_id).write_text(json.dumps(manifest, indent=2))
    click.echo(f"[+] Manifest guardado en {manifest_path(file_id)}")

    payload = {
        "id": file_id,
        "merkleTreeModel": tree,
        "_id": file_id,
    }

    with open(blocks_path, "rb") as fbin:
        form = {
            "data": (None, json.dumps(payload)),
            "file": (file_path.name, fbin),
        }

        click.echo(f"[*] Subiendo árbol y bloques a {api}/upload ...")
        resp = requests.post(f"{api}/upload", files=form)

    resp.raise_for_status()
    click.echo(f"[OK] Respuesta del servidor: {resp.json()}")


# ============================================================
#                      CHALLENGE
# ============================================================

@cli.command()
@click.argument("file_id")
@click.option("--k", default=3, show_default=True, help="Número de bloques a desafiar")
@click.pass_context
def challenge(ctx, file_id, k):

    api = ctx.obj["API_URL"]

    mpath = manifest_path(file_id)
    if not mpath.exists():
        click.echo(f"[X] No existe manifest para {file_id}")
        return

    manifest = json.loads(mpath.read_text())
    num = manifest["num_blocks"]

    if k > num:
        click.echo(f"[X] k no puede ser mayor que {num}")
        return

    indexes = sorted(random.sample(range(num), k))
    click.echo(f"[*] Índices: {indexes}")

    # NONCE como lista JSON-friendly
    raw_nonce = os.urandom(32)
    
    encoded_nonce = base64.b64encode(raw_nonce).decode()

    print("CLI → Nonce RAW (bytes):", raw_nonce)
    print("CLI → Nonce Base64:", encoded_nonce)
    challenge_id = f"ch_{uuid.uuid4().hex[:10]}"

    # Guardar metadata local
    challenge_meta = {
        "challenge_id": challenge_id,
        "file_id": file_id,
        "indexes": indexes,
        "nonce": encoded_nonce,
    }

    challenge_meta_path(challenge_id).write_text(json.dumps(challenge_meta, indent=2))
    click.echo(f"[+] Challenge creado localmente: {challenge_id}")

    # Enviar al backend
    body = {
        "challenge_id": challenge_id,
        "file_id": file_id,
        "indexes": indexes,
        "nonce": encoded_nonce,
    }

    resp = requests.post(f"{api}/challenge", json=body)
    resp.raise_for_status()

    click.echo(f"[*] Challenge enviado al servidor.")
    click.echo(resp.json())


# ============================================================
#                      VERIFY
# ============================================================

@cli.command()
@click.argument("challenge_id")
@click.pass_context
def verify(ctx, challenge_id):

    api = ctx.obj["API_URL"]

    meta = json.loads(challenge_meta_path(challenge_id).read_text())
    file_id = meta["file_id"]

    manifest = json.loads(manifest_path(file_id).read_text())
    tree = manifest["tree_path"]
    tree_json = json.loads(Path(tree).read_text())
    blocks_path = manifest["blocks_path"]
    indexes = meta["indexes"]
    nonce = meta["nonce"].encode()
    n = manifest["num_blocks"]

    # ----------------------------
    # CLIENT CALCULA SU RAÍZ LOCAL
    # ----------------------------
    click.echo("[*] Calculando root local...")

    challenge_blocks = get_challenge_blocks(blocks_path, indexes, nonce)
    proof = get_merkle_proof(indexes, tree_json)
    local_root = recompute_merkle_root(challenge_blocks, proof, n)
    click.echo(f"[*] nonce local: {nonce}")
    click.echo(f"[*] Root local: {local_root}")

    # ----------------------------
    # SERVIDOR CALCULA SU RAÍZ
    # ----------------------------
    click.echo("[*] Consultando /prove en servidor...")
    resp = requests.get(f"{api}/prove", params={"challenge_id": challenge_id})
    resp.raise_for_status()

    server_root = resp.json()["recomputed_root"]
    click.echo(f"[*] nonce servidor: {resp.json()['nonce']}")
    click.echo(f"[*] Root servidor: {server_root}")

    # ----------------------------
    # COMPARAR
    # ----------------------------
    if server_root["data"] == local_root["data"]:
        click.echo("[RESULTADO] ✔ OK — El servidor sí tiene tus datos.")
    else:
        click.echo("[RESULTADO] ✘ FAIL — El servidor NO tiene tus datos.")

    # Registrar en logs
    log_body = {
        "challenge_id": challenge_id,
        "result": "OK" if server_root["data"] == local_root["data"] else "FAIL",
    }
    r2 = requests.post(f"{api}/logs", json=log_body)
    r2.raise_for_status()

    click.echo("[+] Log guardado.")


# ============================================================
#                      LOGS
# ============================================================

@cli.command()
@click.pass_context
def logs(ctx):
    api = ctx.obj["API_URL"]
    resp = requests.get(f"{api}/logs")
    resp.raise_for_status()

    logs = resp.json().get("logs", [])
    if not logs:
        click.echo("[*] No hay logs")
        return

    for l in logs:
        click.echo(f"- {l}")


# ============================================================
#                      FILES
# ============================================================

@cli.command()
@click.pass_context
def files(ctx):
    api = ctx.obj["API_URL"]
    resp = requests.get(f"{api}/")
    resp.raise_for_status()

    data = resp.json().get("merkle_trees", [])

    if not data:
        click.echo("[X] No hay archivos almacenados")
        return

    for item in data:
        click.echo(f"- {item['id']}   |   {item['filename']}")


if __name__ == "__main__":
    cli()
