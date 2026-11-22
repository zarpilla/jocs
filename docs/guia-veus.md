# Guia: posar veus a un joc

Com es posen veus a un joc amb ElevenLabs, en l'ordre en què es va fer amb L'Última Arrel (el primer joc sencer amb
veu). Les opcions de l'eina són a l'explicació del principi de [tools/veus.py](../tools/veus.py); aquí només hi ha
el procés i les decisions.

Les ordres s'executen des de `games/<joc>/`.

## Resum

| Pas | Què en surt | Qui ho revisa |
|---|---|---|
| 1. Abans de començar | Pla i crèdits comprovats | — |
| 2. Les veus | Una veu d'ElevenLabs per personatge, a `game/audio/veus.json` | **L'usuari, escoltant-les** |
| 3. Qui parla on | `jugadora`, `pronuncia`, `sense_veu`, `variables`… a `veus.json` | — |
| 4. Una sala de mostra | Una sala amb veu, escoltada al navegador | **L'usuari** |
| 5. La resta del joc | Tot el joc amb veu (`--tot`) | — |
| 6. El to (si cal) | Les veus d'un personatge més agudes o més greus, amb els originals guardats | L'usuari, amb una prova abans |
| 7. Comprovar que no falta res | Cap línia que s'hauria de sentir sense veu | — |
| 8. Activar-les | `"actiu": true` i commit | L'usuari, jugant-hi |

---

## 1. Abans de començar

- La clau és a `~/.elevenlabs.env` (`ELEVENLABS_API_KEY=...`). No s'escriu mai al xat ni al repo.
- Amb el pla gratuït, les veus de la biblioteca d'ElevenLabs no funcionen per API; només les que es creen al web
  (Voice Design). L'àudio del pla gratuït no té llicència comercial: s'ha de tornar a generar (`--refes`) abans de
  publicar el joc comercialment.
- El model `eleven_v3` cobra una mica menys d'un crèdit per lletra. Un joc sencer són unes 700 frases i uns 20.000
  crèdits. Abans de generar molt, sempre `--prova` (diu quants caràcters costarà) i mirar els crèdits que queden.
- Jocs per a infants (L'Última Arrel és per a nenes de 8 a 12 anys): la política d'ElevenLabs demana la seva aprovació
  per escrit per a productes adreçats a menors, i no permet clonar veus a partir de gravacions de menors. Cal tenir-ho
  resolt abans de publicar-lo.

## 2. Les veus

La Iri i la Vet canvien d'edat i de rol a cada joc (nenes d'11 i 9 anys a L'Última Arrel, una lladre adulta a
Ferro-9), així que **cada joc té les seves veus**. Es fan al web d'ElevenLabs i s'apunta l'identificador de cada una a
`game/audio/veus.json`:

```json
{
  "actiu": "url",
  "model": "eleven_v3", "language": "ca", "format": "mp3_44100_64",
  "voices": { "iri": "<voice_id>", "vet": "<voice_id>", "narrator": "<voice_id>", "bufo": "<voice_id>" }
}
```

- La clau de `voices` és el personatge del contingut; les protagonistes, pel seu nom (`iri`, `vet`).
- El narrador també pot tenir veu (`"narrator"`). Si no en té, les seves línies surten només escrites.
- Un personatge sense veu a `voices` no es grava: `--prova` ho diu a la llista «(sense veu)».
- Mentre es prova, `"actiu": "url"`: les veus només sonen amb `?voices=on` a l'adreça.

Les veus d'adults joves fetes al web solen sonar més grans del que toca per a una nena. Es pot arreglar després amb el
to (pas 6), sense tornar-les a fer.

- [ ] Cada personatge que parla té veu, i l'usuari les ha escoltat.

## 3. Qui parla on

`veus.py` dedueix qui diu cada línia del contingut. On no ho pot saber, s'hi ajuda des de `veus.json`:

- **`jugadora`**: a una sala compartida, a un diàleg d'un personatge o a un node d'un diàleg (el walkie), quina
  protagonista hi juga (`"bosc_obert": "vet"`, `"walkie.e1": "iri"`). Sense això, es grava amb totes dues.
- **`pronuncia`**: sigles, xifres i noms que el model llegeix malament (`"Bosc 2.0": "Bosc dos punt zero"`). Només
  canvia el que s'envia; el text del joc queda igual.
- **`sense_veu`**: claus (o començaments de clau) que no s'han de dir, com el que surt escrit en una pantalla.
- **`veu`**: línies del narrador dites amb la veu d'un personatge (una nota, un holograma, una megafonia).
- **`variables`**: els valors possibles de les variables d'una línia (`{observacions} de 12`): es grava una versió
  per valor.
- **`codi`**: línies que diu el codi del joc (`game/logic`) i que `veus.py` no troba sol.
- **`text`**: el que s'ha de dir exactament, si no és el text del joc (amb etiquetes del v3: `[whispers]`).

Les acotacions del text («(xiuxiuejant) Iri.») es converteixen soles en etiquetes del v3; les que no diuen com es
parla es treuen.

## 4. Una sala de mostra

```bash
npm run veus -- --sala <sala> --prova   # què es generaria i quant costa
npm run veus -- --sala <sala>           # ho genera
npm run benne:sync                      # ho copia al projecte Benne
npm run dev                             # i s'escolta amb ?voices=on
```

Es mira sobretot: si les veus encaixen amb els personatges, si s'entenen les pronúncies difícils, i si cada línia la
diu qui toca. Una presa que no agrada es torna a fer amb `--clau <clau> --refes`.

- [ ] L'usuari ha escoltat la sala de mostra i n'ha aprovat les veus.

## 5. La resta del joc

```bash
npm run veus -- --tot --prova
npm run veus -- --tot
npm run benne:sync
```

`veus.py` només genera el que ha canviat: si després es retoca un text, n'hi ha prou de tornar a fer `--tot`.
El pla Creator admet tres peticions alhora; si n'hi ha errors, tornar a executar l'ordre continua on s'havia quedat.

Els MP3 van a `game/audio/voice/` (`<personatge><número>.mp3`, el número és l'empremta de la clau del text) i es
guarden a git, amb `veus.lock.json`.

## 6. El to (si cal)

Si una veu sona massa gran, es pot pujar el to de totes les seves línies. A L'Última Arrel: la Iri un 4% i la Vet un
8% (perquè sembli de 9 o 10 anys).

**Primer, una prova** amb tres o quatre línies i dos o tres percentatges, en una carpeta a part, perquè l'usuari triï:

```bash
mkdir -p game/audio/prova-to-vet
for f in vet1061324067 vet1758226149 vet3792377390; do
  cp game/audio/voice/$f.mp3 game/audio/prova-to-vet/${f}_original.mp3
  for p in 1.04 1.08 1.12; do
    ffmpeg -loglevel error -i game/audio/voice/$f.mp3 -af "rubberband=pitch=$p" \
      -c:a libmp3lame -q:a 2 game/audio/prova-to-vet/${f}_to$p.mp3
  done
done
```

`rubberband=pitch=1.08` puja el to un 8% sense canviar la velocitat, i desplaça també el timbre (sona més jove). Amb
`:formant=preserved` el timbre es manté: és la mateixa veu més aguda, i rejoveneix menys.

**Després, a totes**, guardant abans els originals en una carpeta fora de `voice/` (el joc no la carrega):

```bash
mkdir -p game/audio/voice-vet-originals
cp --update=none game/audio/voice/vet*.mp3 game/audio/voice-vet-originals/
for f in game/audio/voice-vet-originals/vet*.mp3; do
  ffmpeg -loglevel error -y -i $f -af "rubberband=pitch=1.08" -c:a libmp3lame -q:a 2 game/audio/voice/$(basename $f)
done
npm run benne:sync
```

Sempre es parteix de l'original guardat, mai d'un fitxer que ja s'ha canviat (si no, el to s'aniria sumant).

**Compte: `veus.py` no aplica el to.** Cada línia que es torni a generar (un text retocat, una presa nova) surt amb el
to original, i cal fer-li el mateix: guardar-ne l'original i canviar-ne el to. `git status` diu quins MP3 són nous o
han canviat.

- [ ] Els originals són a `game/audio/voice-<personatge>-originals/`.
- [ ] La carpeta de prova s'ha esborrat.

## 7. Comprovar que no falta res

- `npm run veus -- --tot --prova` ha de dir «0 per generar». La llista «(sense veu)» diu què no es grava i per què:
  cal mirar que cada motiu sigui volgut (una acotació, un títol) i no un oblit (un personatge sense veu a `voices`, una
  línia que «no se sap quina protagonista la diu», que es resol amb `jugadora` o `codi`).
- Jugar-hi i fer, a cada protagonista, el que el contingut no diu explícitament: **mirar cada objecte de
  l'inventari** (la seva descripció), provar verbs que no fan res (les respostes per defecte, `ui.defecte.*`) i passar
  pels comptadors i les línies amb variables.
- Si una línia que surt al joc no té veu i `--prova` no la llista, és que `veus.py` no la troba: s'hi ha d'afegir
  (així es van afegir les descripcions dels objectes).

## 8. Activar-les

Quan l'usuari ho ha escoltat jugant, `"actiu": true` a `veus.json` (sonen sempre; `?voices=off` les treu),
`npm run benne:sync` i commit amb els MP3.

- [ ] Partida sencera escoltada al navegador i al mòbil.
- [ ] Si el joc es publica comercialment: les veus són d'un pla de pagament.
