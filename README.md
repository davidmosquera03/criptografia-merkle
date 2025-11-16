# criptografia-merkle

Proyecto final de Criptografía, consiste en un servicio práctico para comprobar que un servidor realmente almacena archivos sin descargarlos completos, mediante Pruebas de Almacenamiento tipo Merkle PoR.

# Ejecución

## Servidor

```
cd API
uvicorn main:app --reload
```

## CLI

### client upload <ruta_del_archivo>

- obtiene archivo (f)
- genera Merkle Tree (T)
- Sube T y f al servidor
- tambien almacena T localmente.

### client challenge <file_id>:

- elige índices de bloques hoja aleatoriamente
- almacena indices en indexes
- genera un nonce
- luego:

```
para cada i en indexes
    calcular h(b_i+nonce)
almacenar en challenge_blocks
```

- obtener prueba de merkle merkle

```
get_merkle_proof(indexes, tree_json)
```

- recomputar raiz de merkle (R') dada la prueba de merkle y los hashes con nonce

```
recompute_merkle_root(challenge_blocks, merkle_proof, n)
```

- almacena R'
- enviar informacion de reto a servidor

```
challenge_id
file_id
indexes
nonce
```

### client verify <challenge_id>:

- compara la raiz de merkle local del challenge con la recibida del servidor
- si R'==R\* responder OK al servidor, sino FAIL

### client simulate <file_name> <corruption_percentage>:

- se genera un tipo especial de challenge que se envía al servidor
- el resto del procedimiento es similar a challenge y verify

### client logs <file_id>

- dado archivo, obtiene información de challenges realizados (% de OK vs FAIL)

## API

### /upload

- recibe arbol de merkle T y archivo f
- almacena T y f asignando id especifico al archivo (para evitar repetidos)

body:

```
{
  "id": "string",
  "merkleTreeModel": [
    "MerkleTreeHere"
  ]
}
```

### /challenge:

- recibe challenge y lo almacena
- invoca /prove dando el challenge_id

### /prove:

- para el challange del challenge_id
- busca los bloques hoja mencionados en indexes
- luego

```
para cada i en indexes
    calcular h(b_i+nonce)
almacenar en challenge_blocks
```

- obtener prueba de merkle

```
get_merkle_proof(indexes, tree_json)
```

- recomputar raiz de merkle (R\*) dada la prueba de merkle y los hashes con nonce

```
recompute_merkle_root(challenge_blocks, merkle_proof, n)
```

- enviar R\* al CLI
- recibir OK o FAIL y almacenar en log

### /simulate:

- realizar copia de archivo
- corromper copia en porcentage dado
- seguir instrucciones de challenge
- actuar como en /challenge /verify

### /logs

- recibe file

### /files

-devuelve lista de archivos almacenados
