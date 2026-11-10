# Revisió de textos

> Generat amb `npm run revisio` a partir de `game/data/`. No l'editis a mà.
>
> Per a cada cosa, les interaccions en l'ordre en què el motor les prova: s'agafa **la primera que encaixa**.
> Una interacció «SEMPRE» que no és l'última amaga les de sota.

## Sala La cuina · `pis_cuina` (vet)

```
PLATS «plats»
    • look — SEMPRE
        JUGADORA: Nou dies. Els he comptat.

```

## Sala L'estudi · `pis_estudi` (iri)

```
CAIXA «caixa» — hi és si NO router_connectat
    • look — SEMPRE
        JUGADORA: La caixa del router nou. El gat ja l'ha reclamat.
    • pickUp — SEMPRE
        JUGADORA: Me l'emporto. Ho sento, Diu.
        ⇒ rep caixa_cartro

ROUTER «router»
    • use + caixa_cartro — SEMPRE
        JUGADORA: Caixa per al gat, cables per a mi. Connectat.
        ⇒ perd caixa_cartro, +router_connectat, FINAL prova
    • look — SEMPRE
        JUGADORA: Tres cables i cap a lloc.

DIU «Diu»
    • talkTo — SEMPRE
        ⇒ diàleg diu
    • look — SEMPRE
        JUGADORA: El gat. Té els ullals posats en el cable de xarxa.

```

## Sala Suma Zero · `portada`

```
```

## Objecte caixa de cartró · `caixa_cartro`

```
• look — SEMPRE
    JUGADORA: Una caixa de cartró. Per al gat, és un palau.
```

## Diàleg `diu` amb Diu

```
COMENÇA A: hola

[hola]
    DIU: Miau.
    ↪ menu

[menu]
    ▸ Deixa els cables, sisplau. → cables
    ▸ Res, res. → adeu · FI

[cables]
    JUGADORA: Diu, els cables no es mengen.
    DIU: Miau.
    ↪ menu

[adeu]
    DIU: Miau.

```

## Pistes

```
iri_router — quan juga iri · fins que router_connectat
    1. El router no es connectarà sol.
    2. Si el gat tingués alguna cosa millor a fer...
    3. Agafo la caixa i la faig servir amb el router.
```

## Finals

```
prova «Prova» — quan router_connectat
    Contingut mínim: el repositori funciona.
```
