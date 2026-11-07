# Estudio de códigos de pintura automotriz, 1990–2026

Taller de Color · noviembre 2026

## Resultado

**22,698 códigos de pintura de 60 marcas**, de 1990 a 2025 (13,327 de ellos con los modelos en que se usaron), más los modelos 2026 que siguen usando esos
códigos. Cada código trae:

- marca y código de etiqueta;
- nombre del color y sus otros nombres;
- acabado (sólido, metálico, perlado o tricapa);
- años en que se usó;
- otras formas en que aparece en la etiqueta (por ejemplo, Chevrolet `GBA` = `WA8555` = `U8555` = `41U`;
  Ram `PW7` = `GW7`).

La base está en `colors.json` y la usa el software directamente.

## Fuente y por qué esa

Revisé tres sitios públicos con listas de códigos. Solo usé uno:

| Sitio | Decisión | Motivo |
|---|---|---|
| PaintRef.com | No se usó | Su archivo `robots.txt` bloquea expresamente a los robots de inteligencia artificial (GPTBot, ChatGPT-User y otros). |
| PaintScratch.com | No se usó | Sus términos de servicio prohíben reproducir o usar su contenido con fines comerciales sin permiso por escrito. |
| AutomotiveTouchup.com | **Se usó** | No publica términos de uso y su `robots.txt` permite leer las páginas de códigos. |

Reglas que seguí con AutomotiveTouchup:

- Solo se tomaron **datos**: código, nombre del color y año. No se copiaron imágenes, muestras de color,
  fórmulas, precios ni textos.
- No se descargó nada de las carpetas que su `robots.txt` excluye (por ejemplo, `/images/color-chips/`).
- Lectura lenta: una página a la vez por proceso, con pausa entre páginas.
- Los colores que muestra el software **no vienen de la fuente**: se estiman a partir del nombre del color
  (por ejemplo, "Salsa Red Pearl" → rojo perlado). Por eso el software los marca como "Color estimado".

Los nombres y códigos de color son datos de los fabricantes de autos. Antes de cobrar por el software,
conviene que un abogado revise esta decisión. A largo plazo, lo ideal es licenciar una base oficial (PPG,
Axalta, Sherwin-Williams, BASF o un proveedor de datos de color), que además trae fórmulas reales.

## Cobertura por marca

| Marca | Códigos | Años | Sólidos | Metálicos | Perlados | Tricapa | Sin tono en el nombre |
|---|---:|---|---:|---:|---:|---:|---:|
| Acura | 409 | 1990–2025 | 33 | 178 | 197 | 1 | 12 |
| Alfa Romeo | 249 | 1990–2025 | 46 | 161 | 38 | 4 | 35 |
| Aston Martin | 142 | 1990–2024 | 11 | 79 | 52 | 0 | 1 |
| Audi | 416 | 1990–2025 | 72 | 222 | 122 | 0 | 133 |
| BMW | 604 | 1990–2025 | 134 | 433 | 37 | 0 | 221 |
| Bentley | 141 | 1990–2024 | 25 | 83 | 33 | 0 | 29 |
| Buick | 385 | 1990–2025 | 39 | 326 | 16 | 4 | 108 |
| Cadillac | 385 | 1990–2025 | 57 | 296 | 30 | 2 | 94 |
| Chevrolet | 879 | 1990–2025 | 153 | 661 | 62 | 3 | 171 |
| Chrysler | 455 | 1990–2025 | 101 | 203 | 151 | 0 | 55 |
| Daewoo | 199 | 1990–2014 | 37 | 108 | 54 | 0 | 5 |
| Daihatsu | 317 | 1990–2024 | 79 | 128 | 110 | 0 | 5 |
| Dodge | 492 | 1990–2025 | 147 | 165 | 179 | 1 | 28 |
| Eagle | 118 | 1990–1999 | 23 | 54 | 41 | 0 | 4 |
| Ferrari | 107 | 1990–2025 | 30 | 58 | 19 | 0 | 19 |
| Fiat | 958 | 1990–2024 | 323 | 514 | 120 | 1 | 207 |
| Ford | 1,010 | 1990–2025 | 253 | 536 | 217 | 4 | 118 |
| GMC | 916 | 1990–2025 | 216 | 622 | 77 | 1 | 204 |
| Genesis | 106 | 2009–2025 | 10 | 59 | 37 | 0 | 1 |
| Geo | 79 | 1990–1999 | 17 | 49 | 13 | 0 | 1 |
| Honda | 788 | 1990–2025 | 88 | 358 | 342 | 0 | 19 |
| Hummer | 84 | 2002–2010 | 22 | 56 | 6 | 0 | 4 |
| Hyundai | 1,035 | 1990–2025 | 136 | 603 | 296 | 0 | 44 |
| Infiniti | 204 | 1990–2025 | 23 | 115 | 66 | 0 | 2 |
| Isuzu | 333 | 1990–2025 | 74 | 158 | 101 | 0 | 17 |
| Jaguar | 331 | 1990–2025 | 63 | 196 | 72 | 0 | 37 |
| Jeep | 289 | 1990–2025 | 67 | 103 | 118 | 1 | 26 |
| Kia | 554 | 1990–2025 | 100 | 326 | 128 | 0 | 8 |
| Lamborghini | 159 | 1990–2024 | 37 | 64 | 58 | 0 | 31 |
| Land Rover | 463 | 1990–2025 | 81 | 279 | 103 | 0 | 37 |
| Lexus | 331 | 1990–2025 | 34 | 145 | 152 | 0 | 17 |
| Lincoln | 267 | 1990–2025 | 36 | 191 | 39 | 1 | 42 |
| Lotus | 137 | 1990–2024 | 24 | 83 | 30 | 0 | 8 |
| MINI | 129 | 1990–2025 | 27 | 96 | 6 | 0 | 3 |
| Maserati | 117 | 1990–2024 | 23 | 66 | 28 | 0 | 18 |
| Maybach | 55 | 1991–2017 | 18 | 34 | 3 | 0 | 33 |
| Mazda | 593 | 1990–2025 | 102 | 305 | 186 | 0 | 22 |
| Mercedes-Benz | 729 | 1990–2025 | 314 | 340 | 75 | 0 | 444 |
| Mercury | 276 | 1990–2019 | 56 | 201 | 18 | 1 | 44 |
| Mitsubishi | 718 | 1990–2025 | 178 | 311 | 228 | 1 | 15 |
| Nissan | 1,071 | 1990–2025 | 191 | 648 | 231 | 1 | 37 |
| Oldsmobile | 222 | 1990–2016 | 47 | 169 | 6 | 0 | 50 |
| Plymouth | 134 | 1990–2011 | 23 | 76 | 35 | 0 | 16 |
| Polestar | 14 | 2019–2025 | 1 | 11 | 2 | 0 | 6 |
| Pontiac | 359 | 1990–2017 | 54 | 287 | 18 | 0 | 57 |
| Porsche | 255 | 1990–2025 | 70 | 163 | 22 | 0 | 77 |
| Ram | 170 | 1991–2025 | 48 | 47 | 75 | 0 | 8 |
| Rivian | 18 | 2021–2025 | 6 | 11 | 1 | 0 | 1 |
| Rolls-Royce | 241 | 1990–2024 | 49 | 141 | 51 | 0 | 30 |
| Saab | 138 | 1990–2012 | 30 | 92 | 15 | 1 | 6 |
| Saturn | 138 | 1991–2010 | 26 | 107 | 5 | 0 | 12 |
| Scion | 89 | 2004–2017 | 12 | 35 | 42 | 0 | 13 |
| Smart | 110 | 1998–2025 | 35 | 60 | 15 | 0 | 5 |
| Subaru | 447 | 1990–2025 | 82 | 189 | 176 | 0 | 8 |
| Suzuki | 650 | 1990–2024 | 120 | 375 | 155 | 0 | 8 |
| Tesla | 39 | 2007–2025 | 8 | 19 | 11 | 1 | 2 |
| Toyota | 1,154 | 1990–2025 | 193 | 538 | 423 | 0 | 70 |
| Volkswagen | 1,078 | 1990–2025 | 341 | 534 | 203 | 0 | 397 |
| Volvo | 399 | 1990–2025 | 182 | 156 | 61 | 0 | 21 |
| Yugo | 13 | 1990–1992 | 11 | 2 | 0 | 0 | 0 |
| **Total** | **22,698** | | | | | | **3,146** |

Cómo leer la tabla:

- **Sin tono en el nombre**: códigos cuyo nombre no dice el color, por ejemplo "Tiefschwarz" (alemán) o un
  nombre de fantasía. Se muestran en gris neutro hasta que alguien corrija el color.
- **Tricapa**: solo cuenta los colores cuyo nombre dice "tri-coat" o "multi-coat". Muchas perlas blancas
  también son tricapa aunque el nombre no lo diga, así que aparecen como "Perlados".

## Lo que todavía falta

- **Años antes de 1990**: quedan fuera del alcance acordado.
- **Modelos en marcas de lujo y exóticas** (Aston Martin, Bentley, Ferrari, Lamborghini, Lotus, Maserati,
  Maybach, Rolls-Royce) y en Daihatsu y Yugo: no se bajaron por modelo; sus códigos sí están por marca y año.
- **Algunos modelos sin página propia en la fuente**: Chrysler Town & Country y Aspen, Kia Spectra.
- **2026**: la fuente todavía no publica 2026. Los códigos de 2025 siguen vigentes en la mayoría de los
  modelos.
- **Color exacto**: la fuente no da el color, solo el nombre. Cuando el pintor corrige el color en el
  software, queda guardado para ese código. Con una base licenciada esto se resuelve.
- **Ram**: la fuente lo trae dentro de Dodge (modelos "Ram" y "Ram Truck"). Se armó como marca propia con
  esos modelos.
- Si un código no aparece, el pintor lo puede agregar en segundos desde la búsqueda.

## Modelos por código

Segunda etapa del estudio: **42,890 páginas por modelo y año**. Resultado: **13,327 códigos** ya dicen en
qué modelos y años se usaron, para **1,042 modelos**. El software tiene un filtro marca → año → modelo, y cada
código muestra la lista de modelos con sus años.

{tab}

Los códigos sin modelo son, sobre todo, colores de otros mercados (Europa, Asia) o de modelos que la fuente
no tiene por separado. Siguen apareciendo al buscar por marca y año.

### Cómo se detectaron los años que no existieron

Cuando un modelo no existió en un año, la fuente no da error: muestra colores de otro año o la lista
genérica de la marca. Sin limpiar, la base habría dicho, por ejemplo, "Astro 1990–2024" o "Ridgeline 1990".
Se aplicaron estas reglas, en orden:

1. **Número de vehículo**: cada página trae un número interno. Los años reales usan números de hasta unos
   53,300; los inventados usan bloques más altos (cada marca tiene el suyo). Se acepta solo por debajo de
   53,600.
2. **Página genérica de la marca**: si el mismo número de vehículo aparece en varios modelos del mismo año,
   es la lista general de la marca y se descarta.
3. **Copia después de un hueco**: si después de años inexistentes aparece un año con los mismos colores (o
   menos) que los años reales anteriores, es una copia y se descarta. Un regreso real (Camaro 2010, Blazer
   2019, Ranger 2019) trae colores nuevos y sí cuenta.
4. **2022–2024**: solo cuenta si el modelo existía el año anterior, o si es un modelo nuevo con colores
   recientes (Maverick, S10 Max).
5. **Años sueltos**: tramos de 1 o 2 años separados del resto del modelo por 3 años o más se descartan.

Ejemplos verificados: Chevrolet Astro 1991–2005, Volt 2011–2020, SSR 2003–2007; Ford Ranger 1991–2011 y
2017 en adelante, Thunderbird 1991–1997 y 2001–2005; Toyota Supra 1990–1998 y 2020 en adelante; Honda S2000
1999–2009, Ridgeline 2005–2014 y 2016 en adelante; Acura RSX 2002–2006; Nissan 350Z 2003–2010.

Limitaciones: la regla es conservadora. Algunos modelos pierden su último año (por ejemplo, Ridgeline queda
hasta 2022) y quedan detalles menores, como BMW Z3 con años antes de 1996 o Acura SLX con años de más.

## Errores que el estudio corrigió

- Subaru `K1X` es **Crystal White Pearl**; en la versión anterior estaba como negro. Crystal Black Silica
  es `D4S`.
- Toyota `089` aparece como "Platinum White Pearl" en los modelos recientes.
- La fuente lista los códigos de cada color en orden alfabético, no con el de la etiqueta primero (por
  ejemplo, Mercedes "Obsidian Black" viene como `002, 197, 9197`). El armado elige el código con el formato
  de etiqueta de cada marca (`197`).

## Cómo actualizar la base

Los programas están en `herramientas/`:

1. `python3 fetch.py <marcas separadas por coma> A` descarga marca por año y guarda una copia local para no
   repetir consultas.
2. `python3 build.py` arma `colors.json`.
3. `python3 report.py` imprime la tabla de cobertura.
4. `python3 cola.py` baja la etapa por modelo (3 a la vez, reanudable) con `fetch_models.py`; los datos
   quedan en `resultados/` y una copia comprimida en `herramientas/datos/`.
