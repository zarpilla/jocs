#!/usr/bin/env python3
"""Veus dels diàlegs amb ElevenLabs: `npm run veus -- <opcions>` des de `games/<joc>/`.

Llegeix el contingut que fa servir el joc (`<projecte Benne>/src/game/narrative/content.generated.json`, el posa
al dia `npm run benne:sync`) i la configuració `game/audio/veus.json`:

    {
      "actiu": true,      // true: sonen sempre; "url": només amb ?voices=on; false: el sync no les posa al joc
      "model": "eleven_v3", "language": "ca", "format": "mp3_44100_64",
      "voices": { "mare": "<voice_id>", "vet": "<voice_id>" },   // personatge nostre → veu d'ElevenLabs
      "text": { "dlg.mare.hola": "[cheerfully] Hola, interna 9! ..." },  // opcional: el que es diu, si no és el text
      "pronuncia": { "BCMU": "Be, ce, ema, u", "4.200 €": "quatre mil dos-cents euros" },  // opcional: substitucions
      "codi": { "tub.envia": ["vet"], "sync.aeroport.reinici1": "narrator" },  // opcional: línies del codi del joc
      "sense_veu": ["sala.bcmu_escombraries.llibre.bip"],  // opcional: claus (o començaments de clau) que no es diuen
      "veu": { "obj.nota_vet.text": "vet" },  // opcional: línies del narrador dites amb la veu d'un personatge (notes, hologrames)
      "variables": { "observacions": [0, 1, 2] },   // opcional: valors de les variables, per gravar-ne cada versió
      "etiqueta": { "narrator": "[central Catalan accent]" },   // opcional: etiqueta del v3 davant de cada línia d'una veu
      "tempo": { "narrator": 1.15 },   // opcional: accelera (o alenteix) les preses d'una veu amb ffmpeg, sense canviar-ne el to
      "jugadora": { "bosc_obert": "vet", "walkie.e3": "vet" }   // opcional: qui juga a una sala compartida, a un
                                                              // diàleg o a un node d'un diàleg (si no, es dedueix)
    }

Escriu `game/audio/voice/<personatge de Benne><número>.mp3` (el número és l'FNV-1a de la clau del text, el mateix
que calcula `voiceNumber` a adapters/benne/runtime/narrative.ts) i `game/audio/voice/veus.lock.json`, amb una
empremta del que s'ha enviat: només es torna a generar el que ha canviat (text, veu o model).
Després, `npm run benne:sync` les copia al joc.

Què es genera (es poden combinar; sense cap, res):
    --sala <sala>      les línies de la sala i dels diàlegs que s'hi comencen
    --dialeg <id>      les línies d'un diàleg
    --clau <clau>      una línia concreta (es pot repetir)
    --final <id>       les línies d'un final (escena, crèdits i tancament)
    --defecte          les respostes per defecte (`ui.defecte.*`)
    --codi             les línies que diu el codi del joc (`game/logic/*.ts`)
    --pistes           les pistes (cada nivell) i el que es diu quan no n'hi ha cap (`ui.pista.*`)
    --tot              tot el joc (també els finals, les respostes per defecte i el codi; les pistes, no: --pistes)
    --qui <pj>         només les d'aquest personatge (`player` = les protagonistes)
    --refes            torna a generar encara que no hagi canviat (una presa nova)
    --prova            no genera res: diu què faria i quants caràcters costaria

La clau d'API es llegeix d'ELEVENLABS_API_KEY o de ~/.elevenlabs.env.
El narrador també té veu, si n'hi ha a `voices` (`"narrator": "<voice_id>"`; fitxers `narrator<número>.mp3`, que
el motor fa sonar des de `display`). No es diuen les de títol, les que tenen variables (`{objecte}`)
ni les de `sense_veu` (el que surt escrit en una pantalla, per exemple).
Les línies del codi del joc que hi surten com a `{ who: 'bonfill', text: 'clau' }` (als .ts, o en un .json de
`game/logic`) es troben soles; la resta (qui diu
`'tub.envia'`?) s'indiquen a `codi` de veus.json. `pronuncia` canvia trossos del text abans d'enviar-lo (sigles, imports,
codis), sense tocar el text del joc. `veu` fa que una línia del narrador (una nota, un holograma, una veu per megafonia) es
gravi amb la veu d'un personatge: el text surt igual a la pantalla, i el fitxer continua sent `narrator<número>`. Les acotacions es treuen, i
les que diuen com es parla queden com a etiqueta del v3: «(al walkie, xiuxiuejant) Iri.» → «[whispers] Iri.» (ETIQUETES).
Una línia que només és acotació («(Tus, tus.)») no té veu. El que hi ha a `text` de veus.json s'envia tal qual.
"""
import argparse, glob, hashlib, itertools, json, os, pathlib, re, subprocess, sys, urllib.error, urllib.request

SENSE_VEU = {"title"}

# Acotacions → etiquetes d'emoció del model v3. Una acotació és el parèntesi del començament de la línia
# («(al walkie, xiuxiuejant) Iri…»), o un del mig que digui com es parla («Per si de cas. (sospira) Això…»).
# Es treuen totes; les que diuen com es parla deixen l'etiqueta. La resta del parèntesi del mig es diu tal qual
# (a les pistes, «(si n'hi ha més d'una, tries)» és text). «Al walkie», «per ràdio», «per l'interfon»… no deixen etiqueta:
# el v3 no fa so de ràdio de manera fiable; si cal, és un filtre del joc.
ETIQUETES = [
    (r"xiuxiuej|\bfluix\b|\bbaix\b|veu baixa|tapant el micròfon", "[whispers]"),
    (r"sospir", "[sighs]"),
    (r"somri", "[smiles]"),
    (r"rondin", "[grumbling]"),
    (r"\bofès\b|\bofesa\b", "[offended]"),
    (r"avergony", "[embarrassed]"),
    (r"boca plena", "[mouth full]"),
    (r"fortíssim|cridant|\bcrida\b", "[shouting]"),
    (r"de lluny", "[shouting from afar]"),
    (r"^des de (dins|la porta)|^des del públic", "[from afar]"),
    (r"\ba part\b", "[quietly]"),
    (r"veu sintètica", "[robotic]"),
    (r"silenci", "[pause]"),
]


def etiquetes(acotacio: str) -> str:
    return " ".join(tag for pat, tag in ETIQUETES if re.search(pat, acotacio, re.I))


def per_dir(text: str) -> str:
    """El text tal com s'ha d'enviar: sense acotacions, amb les etiquetes que en surtin. Buit si no hi queda res a dir."""
    m = re.match(r"\s*\(([^)]*)\)\s*", text)
    if m:
        tag = etiquetes(m.group(1))
        text = (tag + " " if tag else "") + text[m.end():]

    def mig(m):
        tag = etiquetes(m.group(1))
        return f" {tag} " if tag else m.group(0)

    text = re.sub(r"\s*\(([^)]*)\)\s*", mig, text)
    text = re.sub(r"\s+", " ", text).strip()
    return text if re.search(r"\w", re.sub(r"\[[^\]]*\]", "", text)) else ""


def fnv1a(key: str) -> str:
    h = 0x811C9DC5
    for b in key.encode("utf-8"):
        h = ((h ^ b) * 0x01000193) & 0xFFFFFFFF
    return str(h)


def api_key() -> str:
    if os.environ.get("ELEVENLABS_API_KEY"):
        return os.environ["ELEVENLABS_API_KEY"]
    env = pathlib.Path.home() / ".elevenlabs.env"
    if env.exists():
        for line in env.read_text().splitlines():
            if line.startswith("ELEVENLABS_API_KEY="):
                return line.split("=", 1)[1].strip().strip("'\"")
    sys.exit("Falta la clau: ELEVENLABS_API_KEY o ~/.elevenlabs.env")


def protagonists_in(cond, out: set):
    """Les protagonistes que demana una condició (`{"protagonist": "vet"}` en qualsevol lloc)."""
    if isinstance(cond, dict):
        if isinstance(cond.get("protagonist"), str):
            out.add(cond["protagonist"])
        for v in cond.values():
            protagonists_in(v, out)
    elif isinstance(cond, list):
        for v in cond:
            protagonists_in(v, out)


def collect(content, table, joc: pathlib.Path, codi_cfg: dict, jugadora: dict | None = None):
    """Totes les línies dites: (who, clau, sala, diàleg, protagonistes possibles si who és player, grup).

    El grup diu d'on surt: `None` (sales, diàlegs, objectes), `final:<id>`, `defecte`, `codi` o `pistes`."""
    rooms = content["rooms"]
    protas = content["manifest"]["protagonists"]
    # On comença cada diàleg (per saber qui és la `player` i per a --sala).
    dialog_rooms: dict[str, set] = {}

    def find_dialogs(o, room):
        if isinstance(o, dict):
            if isinstance(o.get("dialogue"), str) and room:
                dialog_rooms.setdefault(o["dialogue"], set()).add(room)
            for v in o.values():
                find_dialogs(v, room)
        elif isinstance(o, list):
            for v in o:
                find_dialogs(v, room)

    for rid, r in rooms.items():
        find_dialogs(r, rid)
    jugadora = jugadora or {}

    # Els diàlegs que es comencen parlant amb un personatge: si la interacció diu amb quina protagonista
    # (`"if": {"protagonist": "vet"}`), és ella.
    dialog_protas: dict[str, set] = {}
    for ch in content.get("characters", {}).values():
        for inter in ch.get("interactions") or []:
            if isinstance(inter.get("dialogue"), str):
                found = set()
                protagonists_in(inter.get("if"), found)
                dialog_protas.setdefault(inter["dialogue"], set()).update(found or protas)

    lines = []

    def room_protas(room):
        r = rooms.get(room) or {}
        if r.get("protagonist"):
            return {r["protagonist"]}
        return set(r.get("protagonists") or [])

    def walk(o, room, dialog, cond_protas):
        if isinstance(o, dict):
            here = set(cond_protas)
            if "if" in o:
                found = set()
                protagonists_in(o["if"], found)
                if found:
                    here = found
            if isinstance(o.get("who"), str) and isinstance(o.get("text"), str):
                lines.append((o["who"], o["text"], room, dialog, here))
            for k, v in o.items():
                if k != "if":
                    walk(v, room, dialog, here)
        elif isinstance(o, list):
            for v in o:
                walk(v, room, dialog, cond_protas)

    for rid, r in rooms.items():
        walk(r, rid, None, room_protas(rid))
    for did, d in content["dialogues"].items():
        starts = dialog_rooms.get(did, set())
        # Qui hi parla: el que digui `jugadora` de veus.json (per al diàleg, o per a un node: "walkie.e3"); si no, les
        # protagonistes de les sales on comença, o la de la interacció del personatge. Un diàleg que no comença enlloc
        # (el d'un objecte: el walkie, el quadern) el pot obrir qualsevol de les dues.
        if did in jugadora:
            ps = {jugadora[did]}
        elif starts:
            ps = set().union(*(room_protas(r) for r in starts))
        else:
            ps = dialog_protas.get(did) or set(protas)
        walk({k: v for k, v in d.items() if k != "nodes"}, None, did, ps)
        for nid, node in d.get("nodes", {}).items():
            node_ps = {jugadora[f"{did}.{nid}"]} if f"{did}.{nid}" in jugadora else ps
            walk(node, None, did, node_ps)
            # Les opcions es diuen en veu alta (si no són `silent`): les diu la protagonista.
            for ch in node.get("choices") or []:
                if not ch.get("silent") and isinstance(ch.get("text"), str):
                    found = set()
                    protagonists_in(ch.get("if"), found)
                    lines.append(("player", ch["text"], None, did, found or node_ps))
    for kind in ("items", "characters"):
        for _id, o in content.get(kind, {}).items():
            walk(o, None, None, set(protas))   # un objecte el pot portar (i mirar) qualsevol de les dues
            # Mirar un objecte de l'inventari sense cap "look" propi: la protagonista en diu la descripció.
            if kind == "items" and isinstance(o.get("description"), str):
                lines.append(("player", o["description"], None, None, set(protas)))
    lines = [(*l, None) for l in lines]

    # Els finals: l'escena, els crèdits i la frase de tancament (narrador).
    for eid, e in content.get("endings", {}).items():
        for part in ("scene", "credits"):
            for line in e.get(part) or []:
                if isinstance(line.get("who"), str) and isinstance(line.get("text"), str):
                    lines.append((line["who"], line["text"], line.get("room"), None, set(), f"final:{eid}"))
        if isinstance(e.get("text"), str):
            lines.append(("narrator", e["text"], e.get("textRoom"), None, set(), f"final:{eid}"))

    # Les respostes per defecte: `ui.defecte.<verb>.<protagonista>[.n]` les diu ella; les generals, qualsevol.
    for key in table:
        if key == "ui.defecte" or key.startswith("ui.defecte."):
            ps = {p for p in protas if p in key.split(".")} or set(protas)
            lines.append(("player", key, None, None, ps, "defecte"))

    # Les pistes: cada nivell el diu qui diu la pista (`who`) o, si no, la protagonista que juga (la que demani la
    # condició `when`, o qualsevol). «No hi ha cap pista» (`ui.pista.cap`) el diu qualsevol; «ara li toca a l'altra»
    # (`ui.pista.altra.<qui>`), la que no és <qui>.
    for _id, h in (content.get("hints") or {}).items():
        found = set()
        protagonists_in(h.get("when"), found)
        for key in h.get("levels") or []:
            if isinstance(h.get("who"), str):
                lines.append((h["who"], key, None, None, set(), "pistes"))
            else:
                lines.append(("player", key, None, None, found or set(protas), "pistes"))
    for key in table:
        if key == "ui.pista.cap":
            lines.append(("player", key, None, None, set(protas), "pistes"))
        elif key.startswith("ui.pista.altra."):
            lines.append(("player", key, None, None, set(protas) - {key.rsplit(".", 1)[1]}, "pistes"))

    # El codi del joc: `{ who: 'x', text: 'clau' }` als .ts, i el que digui `codi` de veus.json (que mana).
    trobades = {}
    for ts in sorted((joc / "game/logic").glob("*.ts")):
        for who, key in re.findall(r"who:\s*'([\w-]+)'(?:\s*as const)?\s*,\s*text:\s*'([\w.]+)'", ts.read_text()):
            trobades.setdefault(key, set()).add(who)

    # I els textos que la lògica llegeix de fitxers .json (transicions, sincronies): `{"who": ..., "text": ...}`.
    def json_linies(o):
        if isinstance(o, dict):
            if isinstance(o.get("who"), str) and isinstance(o.get("text"), str):
                trobades.setdefault(o["text"], set()).add(o["who"])
            for v in o.values():
                json_linies(v)
        elif isinstance(o, list):
            for v in o:
                json_linies(v)

    for js in sorted((joc / "game/logic").glob("*.json")):
        json_linies(json.loads(js.read_text()))
    ja_hi_son = {l[1] for l in lines}
    for key, who in codi_cfg.items():
        if key not in ja_hi_son:            # les que ja són a les sales només diuen qui les diu (vegeu a sota)
            trobades[key] = {who} if isinstance(who, str) else set(who)
    for key, whos in trobades.items():
        for who in whos:
            if who in protas:
                lines.append(("player", key, None, None, {who}, "codi"))
            else:
                lines.append((who, key, None, None, set(protas) if who == "player" else set(), "codi"))
    # Per a les línies sense pista: si `codi` de veus.json diu qui la diu (p. ex. una sala sense protagonista), aquesta;
    # si no, si la clau diu de qui és (`.vet1`, `.iri.2`), en fem cas.
    out = []
    for who, key, room, dialog, ps, grup in lines:
        if who == "player" and not ps and key in codi_cfg:
            qui = codi_cfg[key]
            ps = {qui} if isinstance(qui, str) else set(qui)
        if who == "player" and not ps:
            parts = key.replace("_", ".").split(".")
            ps = {p for p in protas if any(x == p or (x.startswith(p) and x[len(p):].isdigit()) for x in parts)}
        out.append((who, key, room, dialog, frozenset(ps), grup))
    return out, dialog_rooms


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sala", action="append", default=[])
    ap.add_argument("--dialeg", action="append", default=[])
    ap.add_argument("--clau", action="append", default=[])
    ap.add_argument("--qui", action="append", default=[])
    ap.add_argument("--final", action="append", default=[])
    ap.add_argument("--defecte", action="store_true")
    ap.add_argument("--codi", action="store_true")
    ap.add_argument("--pistes", action="store_true")
    ap.add_argument("--tot", action="store_true")
    ap.add_argument("--refes", action="store_true")
    ap.add_argument("--prova", action="store_true")
    a = ap.parse_args()

    joc = pathlib.Path.cwd()
    found = glob.glob(str(joc / "*/src/game/narrative/content.generated.json"))
    if not found:
        sys.exit("Executa'l des de games/<joc>/ (i fes abans npm run benne:sync).")
    bundle = json.loads(pathlib.Path(found[0]).read_text())
    content, table = bundle["content"], bundle["locales"][bundle["locale"]]
    cfg_path = joc / "game/audio/veus.json"
    if not cfg_path.exists():
        sys.exit("Aquest joc encara no té game/audio/veus.json (vegeu el de Ferro-9).")
    cfg = json.loads(cfg_path.read_text())
    mapping_path = joc / "adapters/benne/mapping.json"
    to_benne = json.loads(mapping_path.read_text()).get("characters", {}) if mapping_path.exists() else {}
    out_dir = joc / "game/audio/voice"
    out_dir.mkdir(parents=True, exist_ok=True)
    lock_path = out_dir / "veus.lock.json"
    lock = json.loads(lock_path.read_text()) if lock_path.exists() else {}
    voices, overrides = cfg["voices"], cfg.get("text", {})
    pronuncia = sorted(cfg.get("pronuncia", {}).items(), key=lambda kv: -len(kv[0]))   # els trossos llargs, primer
    sense_veu = cfg.get("sense_veu", [])
    veu_de = cfg.get("veu", {})
    jugadora = cfg.get("jugadora", {})
    variables = cfg.get("variables", {})
    etiqueta = cfg.get("etiqueta", {})   # veu → etiqueta davant de cada línia (p. ex. per fixar l'accent)
    tempo = cfg.get("tempo", {})     # veu → factor d'atempo (el v3 no fa cas de `speed`)

    def veu_narrador(key):
        """El personatge amb la veu del qual es diu una línia del narrador (`veu` de veus.json), o el narrador."""
        for k, pj in veu_de.items():
            if key == k or key.startswith(k):
                return pj
        return "narrator"
    model, language, fmt = cfg.get("model", "eleven_v3"), cfg.get("language", "ca"), cfg.get("format", "mp3_44100_64")

    lines, dialog_rooms = collect(content, table, joc, cfg.get("codi", {}), cfg.get("jugadora", {}))

    def chosen(who, key, room, dialog, grup):
        if grup == "pistes":            # només amb --pistes (o --clau): no entren a --tot
            return a.pistes or key in a.clau
        if a.tot or key in a.clau or (dialog and dialog in a.dialeg):
            return True
        if grup == "defecte":
            return a.defecte
        if grup == "codi":
            return a.codi
        if grup and grup.startswith("final:"):
            return grup[6:] in a.final
        return any(room == s or (dialog and s in dialog_rooms.get(dialog, ())) for s in a.sala)

    # (stem, personatge, clau, text a dir, veu)
    jobs, skipped, seen = [], [], set()
    for who, key, room, dialog, ps, grup in lines:
        if who in SENSE_VEU or not chosen(who, key, room, dialog, grup):
            continue
        if any(key == k or key.startswith(k) for k in sense_veu):
            continue
        if a.qui and who not in a.qui:
            continue
        speakers = sorted(ps) if who == "player" else [who]
        if who == "player" and len(speakers) != 1:
            # Sala compartida (o on no es dedueix qui hi juga, com una pantalla de primer pla): qui hi juga, si
            # veus.json ho diu (`jugadora`). També per als diàlegs que s'hi comencen.
            sales = {room} if room else set(dialog_rooms.get(dialog, ())) if dialog else set()
            if sales and sales <= jugadora.keys():
                speakers = sorted({jugadora[s] for s in sales})
        if not speakers:
            skipped.append((key, "no se sap quina protagonista la diu"))
            continue
        base = overrides.get(key, table.get(key, ""))
        if not base:
            skipped.append((key, "sense text"))
            continue
        # Les línies amb variables (`{observacions} de 12`) es graven un cop per valor (`variables` de veus.json). El
        # número de la veu surt de la clau i el text com el mostra el joc (`clau|5 de 12`); vegeu `voiced` al pont.
        noms = re.findall(r"\{(\w+)\}", base)
        if noms and not all(n in variables for n in noms):
            skipped.append((key, "té variables"))
            continue
        variants = [(key, base, base)]
        if noms:
            variants = []
            for valors in itertools.product(*(variables[n] for n in noms)):
                dit = vist = base
                for n, v in zip(noms, valors):
                    dit, vist = dit.replace("{" + n + "}", str(v)), vist.replace("{" + n + "}", str(v))
                vist = table.get(key, "")
                for n, v in zip(noms, valors):
                    vist = vist.replace("{" + n + "}", str(v))
                variants.append((f"{key}|{vist}", dit, vist))
        for vkey, text, _vist in variants:
            if key not in overrides:
                text = per_dir(text)
                if not text:
                    skipped.append((key, "és una acotació"))
                    break
                for tros, dit in pronuncia:
                    text = text.replace(tros, dit)
                text = re.sub(r"\s+", " ", text).strip()
            for sp in speakers:
                amb = veu_narrador(key) if sp == "narrator" else sp      # de qui és la veu
                if amb not in voices:
                    if amb != "narrator":                # un joc sense veu de narrador: no cal dir-ho línia a línia
                        skipped.append((key, f"{amb} no té veu a veus.json"))
                    continue
                stem = f"{to_benne.get(sp, sp)}{fnv1a(vkey)}"
                if stem in seen:
                    continue
                seen.add(stem)
                dit = f"{etiqueta[amb]} {text}" if amb in etiqueta and not text.startswith(etiqueta[amb]) else text
                jobs.append((stem, amb, key, dit, voices[amb]))

    todo = []
    for stem, sp, key, text, vid in jobs:
        empremta = [vid, model, language, text] + ([tempo[sp]] if tempo.get(sp, 1) != 1 else [])
        print_ = hashlib.sha1(json.dumps(empremta).encode()).hexdigest()[:16]
        if not a.refes and (out_dir / f"{stem}.mp3").exists() and lock.get(stem, {}).get("hash") == print_:
            continue
        todo.append((stem, sp, key, text, vid, print_))

    chars = sum(len(t[3]) for t in todo)
    print(f"{len(jobs)} línies triades, {len(todo)} per generar ({chars} caràcters); {len(jobs) - len(todo)} ja fetes.")
    for key, why in sorted(set(skipped)):
        print(f"  (sense veu) {key}: {why}")
    if a.prova:
        for stem, sp, key, text, *_ in todo:
            print(f"  {sp:10} {key}: {text}")
        return
    if not todo:
        return

    k = api_key()
    for i, (stem, sp, key, text, vid, print_) in enumerate(todo, 1):
        body = json.dumps({"text": text, "model_id": model, "language_code": language}).encode()
        req = urllib.request.Request(
            f"https://api.elevenlabs.io/v1/text-to-speech/{vid}?output_format={fmt}",
            data=body, headers={"xi-api-key": k, "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                audio = r.read()
            if tempo.get(sp, 1) != 1:
                kbps = fmt.rsplit("_", 1)[-1]
                audio = subprocess.run(["ffmpeg", "-v", "error", "-f", "mp3", "-i", "pipe:0", "-filter:a",
                                        f"atempo={tempo[sp]}", "-ar", fmt.split("_")[1], "-b:a", f"{kbps}k", "-f", "mp3", "pipe:1"],
                                       input=audio, capture_output=True, check=True).stdout
            (out_dir / f"{stem}.mp3").write_bytes(audio)
        except urllib.error.HTTPError as e:
            print(f"  ERROR {e.code} a {key}: {e.read()[:300]!r}")
            if e.code in (401, 402, 403, 429):
                break
            continue
        lock[stem] = {"who": sp, "key": key, "hash": print_}
        lock_path.write_text(json.dumps(lock, ensure_ascii=False, indent=1, sort_keys=True) + "\n")
        print(f"  [{i}/{len(todo)}] {sp}: {key}")
    print("Fet. Ara: npm run benne:sync")


if __name__ == "__main__":
    main()
