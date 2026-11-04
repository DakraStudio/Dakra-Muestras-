# Dakra Studio · Muestras

Cada carpeta es la página de muestra de un prospecto y se publica sola en
`https://dakra-muestras.netlify.app/<carpeta>/` en cuanto se sube un cambio.

- `tools/qa.py`: inspector de calidad. Correr antes de cada subida:
  `python3 tools/qa.py <carpeta>`; solo se publica lo que sale APROBADA.
- Cuando un cliente acepta, su carpeta se pasa a su propio sitio con su dominio.
