# Diseño de la SDD (Item 3)

> Este documento es la plantilla de trabajo para los Pasos 1 a 4 de la
> Sección 3 del enunciado. Su contenido final (ya resuelto) debe pasar
> también al informe PDF (Sección 4.1). Mientras tanto, `src/sdd.py`
> contiene la SDD de ejemplo del libro (profundidad de paréntesis
> balanceados) **solo como referencia de formato**: no se puede entregar.

## Paso 1: Elegir la gramática

Requisitos (G1–G3 del enunciado):

- [ ] Sigue las convenciones de la Sección 2.2 (S inicial, no terminales en
      mayúscula, terminales de un carácter, `e` para épsilon).
- [ ] Es LL(1) o SLR(1) según el propio programa (Item 2).
- [ ] Tiene al menos 3 no terminales y al menos 6 producciones.
- [ ] Al menos un no terminal es recursivo.
- [ ] No es ninguna gramática del libro ni del enunciado (incluida la de
      ejemplo de profundidad de paréntesis).

Gramática elegida:

```
(pendiente)
```

## Paso 2: Definir la SDD en papel

### Tabla de atributos

| Símbolo | Atributo | Tipo (sintetizado/heredado) | Dominio | Significado |
|---|---|---|---|---|
| | | | | |

Reglas a verificar (Sección 5.1.1):

- [ ] Al menos dos atributos distintos, con al menos uno sintetizado y uno heredado.
- [ ] `S` (símbolo inicial) no tiene atributos heredados.
- [ ] Cada regla define exactamente un atributo (sintetizado del head o
      heredado de un símbolo del cuerpo), usando solo atributos de esa misma producción.
- [ ] Cada atributo sintetizado del head y cada atributo heredado de cada no
      terminal del cuerpo se define exactamente una vez por producción.

### Reglas semánticas (formato Fig. 5.1 del libro)

| Producción | Reglas semánticas |
|---|---|
| | |

## Paso 3: Ejemplo a mano

Cadena elegida (mínimo 4 terminales): `(pendiente)`

- Árbol de derivación anotado: *(adjuntar dibujo/diagrama en el informe)*
- Grafo de dependencias: un vértice por atributo de cada nodo, una arista
  desde cada atributo usado hacia el atributo que lo usa para definirse
  (Sección 5.2.1). *(adjuntar dibujo/diagrama en el informe)*
- Orden de evaluación válido (orden topológico, Sección 5.2.2): `(pendiente)`

## Paso 4: Clasificación de la SDD

- ¿Es S-attributed? (todos los atributos son sintetizados) `(pendiente)`
- ¿Es L-attributed? (Sección 5.2.4: cada atributo heredado de un símbolo
  del cuerpo depende solo de atributos de símbolos a su izquierda y de
  atributos heredados del head) `(pendiente)`
- Justificación: `(pendiente)`

> Aunque la SDD resulte L-attributed (o S-attributed), el enunciado exige
> implementar igualmente el método general de evaluación por grafo de
> dependencias (Paso 5), no una evaluación recursiva de orden fijo.

## Paso 6: Plan de pruebas

Mínimo 5 cadenas, incluyendo:

- [ ] La cadena más corta del lenguaje.
- [ ] Una cadena que NO pertenece al lenguaje.
- [ ] Una cadena con anidamiento o recursión profunda.
- [ ] Evidencia de detección de SDD circular (modificar temporalmente una
      regla para introducir un ciclo y mostrar la salida del programa).

| # | Cadena | Resultado esperado |
|---|---|---|
| 1 | | |
| 2 | | |
| 3 | | |
| 4 | | |
| 5 | | |
