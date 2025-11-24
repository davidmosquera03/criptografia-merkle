# criptografia-merkle

Proyecto final de Criptografía, consiste en un servicio práctico para comprobar que un servidor realmente almacena archivos sin descargarlos completos, mediante Pruebas de Almacenamiento tipo Merkle PoR.

# Requerimientos

- Python 3.12 y superior
- MongoDB (Atlas o Local)

# Ejecución

## Instalar librerias

```
pip install -r requirements.txt
```

## Base de datos

cambiar .env.example por .env y agregar connection string de MongoDB

## Servidor y CLi

En una terminal ejecutar

```
cd API
uvicorn main:app --reload
```

En otra terminar se ejecutan los comandos del CLI

# CLI

### upload <file_path> --file-id <id>

- Obtiene archivo (f)
- Genera Merkle Tree (T) localmente
- Sube T y f al servidor
- Almacena manifest localmente con metadata (file_id, root_hash, num_blocks, etc.)

**Ejemplo:**

```bash
python CLI/cli.py upload archivo.txt --file-id file1
```

### challenge <file_id> [--k <num_bloques>]

- Elige k índices de bloques hoja aleatoriamente (default: k=3)
- Genera un nonce aleatorio (32 bytes)
- Codifica nonce en base64
- Envía challenge al servidor:
  - challenge_id
  - file_id
  - indexes
  - nonce (base64)
- Almacena metadata del challenge localmente

**Ejemplo:**

```bash
python CLI/cli.py challenge file1 --k 5
```

**Proceso interno:**

```
para cada i en indexes:
    calcular h(b_i || nonce)
almacenar en challenge_blocks
```

### verify <challenge_id>

- Recupera metadata del challenge localmente
- Calcula root local (R'):
  - Obtiene challenge_blocks: `h(b_i || nonce)` para cada índice
  - Obtiene prueba de Merkle: `get_merkle_proof(indexes, tree_json)`
  - Recomputa root: `recompute_merkle_root(challenge_blocks, merkle_proof, n)`
- Solicita root del servidor (R\*) mediante `/prove`
- Compara R' == R\*:
  - Si coinciden: ✔ OK — El servidor tiene los datos
  - Si difieren: ✘ FAIL — El servidor NO tiene los datos
- Envía resultado (OK/FAIL) al log del servidor

**Ejemplo:**

```bash
python CLI/cli.py verify ch_a1b2c3d4e5
```

### simulate <file_id> --percentage <p> [--k <num_bloques>]

- Genera challenge con k índices aleatorios y nonce
- Envía al servidor:
  - challenge_id
  - file_id
  - indexes
  - nonce (base64)
  - percentage (porcentaje de corrupción 0.0-1.0)
- Servidor corrompe archivo en el porcentaje especificado
- Calcula root local (R') con archivo original
- Servidor calcula root (R\*) con archivo corrompido
- Compara R' vs R\*:
  - Si coinciden: ✘ FAIL — No se detectó corrupción (esperado solo con percentage=0)
  - Si difieren: ✔ OK — Corrupción detectada correctamente

### logs

- Obtiene todos los logs de challenges del servidor
- Muestra resultado (OK/FAIL) de cada challenge verificado

**Ejemplo:**

```bash
python CLI/cli.py logs
```

### files

- Lista todos los archivos (Merkle trees) almacenados en el servidor
- Muestra file_id y filename de cada archivo

**Ejemplo:**

```bash
python CLI/cli.py files
```

---

## API

### POST /upload

- Recibe árbol de Merkle (T) y archivo (f)
- Almacena T y f en MongoDB con id único
- Retorna inserted_id y filename

**Body:**

```json
{
  "data": {
    "id": "string",
    "merkleTreeModel": [...],
    "_id": "string"
  },
  "file": "binary_content"
}
```

### POST /challenge

- Recibe y almacena challenge en MongoDB
- Retorna challenge_id

**Body:**

```json
{
  "challenge_id": "string",
  "file_id": "string",
  "indexes": [int],
  "nonce": "base64_string"
}
```

### GET /prove?challenge_id=<id>

- Recupera challenge de MongoDB
- Obtiene archivo y árbol de Merkle
- Calcula challenge_blocks: `h(b_i || nonce)` para cada índice
- Obtiene prueba: `get_merkle_proof(indexes, tree_json)`
- Recomputa root (R\*): `recompute_merkle_root(challenge_blocks, merkle_proof, n)`
- Retorna R\* y nonce

**Response:**

```json
{
  "recomputed_root": {"index": int, "data": "hex_hash"},
  "nonce": "base64_string"
}
```

### POST /simulate

- Recibe challenge con porcentaje de corrupción
- Crea copia del archivo y la corrompe según percentage
- Calcula challenge_blocks con contenido corrompido
- Usa árbol de Merkle **original** para la prueba
- Recomputa root (R\*) con bloques corrompidos y prueba original
- Retorna R\*

**Body:**

```json
{
  "challenge_id": "string",
  "file_id": "string",
  "indexes": [int],
  "nonce": "base64_string",
  "percentage": float
}
```

### POST /logs

- Recibe y almacena resultado de verificación (OK/FAIL)
- Retorna inserted_id

**Body:**

```json
{
  "challenge_id": "string",
  "result": "OK" | "FAIL"
}
```

### GET /logs

- Retorna todos los logs de challenges

**Response:**

```json
{
  "logs": [
    {"challenge_id": "string", "result": "string"},
    ...
  ]
}
```

### GET /

- Retorna lista de todos los Merkle trees (archivos) almacenados

**Response:**

```json
{
  "merkle_trees": [
    {"id": "string", "filename": "string"},
    ...
  ]
}
```
