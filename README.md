# criptografia-merkle

Proyecto final de Criptografía, consiste en un servicio práctico para comprobar que un servidor realmente almacena archivos sin descargarlos completos, mediante Pruebas de Almacenamiento tipo Merkle PoR.

## CLI

- client upload <ruta_del_archivo> : sube archivo y merkle tree al servidor, genera manifest.json

-client challenge <file_name>: genera reto para el servidor

-client verify <challenge_id>: dada respuesta del challenge, recalcula la raiz de merkle y la compara con la del manifest.json

-client simulate <file_id> <corruption_percentage>: prueba si el sistema detecta como integro archivo corrompido (combina challenge y verify)

## API

- /upload

- /challenge: recibe desafio del cliente y lo almacena

- /prove: devuelve prueba de merkle y bloques hoja asociados a challenge

- /simulate: dada simulacion de usuario, corrompe copia de archivo, envia prueba de merkle
