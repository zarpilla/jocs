#!/usr/bin/env python3
"""Veus dels diàlegs amb ElevenLabs: `npm run veus -- <opcions>` des de `games/<joc>/`.

Llegeix el contingut que fa servir el joc (`<projecte Benne>/src/game/narrative/content.generated.json`, el posa
al dia `npm run benne:sync`) i la configuració `game/audio/veus.json`:

    {
      "actiu": true,      // si el sync les posa al joc (mentre és false, es generen però no sonen)
      "model": "eleven_v3", "language": "ca", "format": "mp3_44100_64",
      "voices": { "mare": "<voice_id>", "vet": "<voice_id>" },   // personatge nostre → veu d'ElevenLabs
      "text": { "dlg.mare.hola": "[cheerfully] Hola, interna 9! ..." }  // opcional: el que es diu, si no és el text
    }

Escriu `game/audio/voice/<personatge de Benne><número>.mp3` (el número és l'FNV-1a de la clau del text, el mateix
que calcula `voiceNumber` a adapters/benne/runtime/narrative.ts) i `game/audio/voice/veus.lock.json`, amb una
empremta del que s'ha enviat: només es torna a generar el que ha canviat (text, veu o model).
Després, `npm run benne:sync` les copia al joc.

Què es genera (es poden combinar; sense cap, res):
    --sala <sala>      les línies de la sala i dels diàlegs que s'hi comencen
    --dialeg <id>      les línies d'un diàleg
    --clau <clau>      una línia concreta (es pot repetir)
    --tot              tot el joc
    --qui <pj>         només les d'aquest personatge (`player` = les protagonistes)
    --refes            torna a generar encara que no hagi canviat (una presa nova)
    --prova            no genera res: diu què faria i quants caràcters costaria

La clau d'API es llegeix d'ELEVENLABS_API_KEY o de ~/.elevenlabs.env.
No es diuen les línies del narrador ni de títol, les acotacions (`(Tus, tus.)`) ni les que tenen variables (`{objecte}`).
"""
import argparse, glob, hashlib, json, os, pathlib, sys, urllib.error, urllib.request

SENSE_VEU = {"narrator", "title"}


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


def collect(content):
    """Totes les línies dites: (who, clau, sala, diàleg, protagonistes possibles si who és player)."""
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
        ps = set().union(*(room_protas(r) for r in starts)) if starts else set()
        walk(d, None, did, ps)
        # Les opcions es diuen en veu alta (si no són `silent`): les diu la protagonista.
        for node in d.get("nodes", {}).values():
            for ch in node.get("choices") or []:
                if not ch.get("silent") and isinstance(ch.get("text"), str):
                    lines.append(("player", ch["text"], None, did, ps))
    for kind in ("items", "characters"):
        for _id, o in content.get(kind, {}).items():
            walk(o, None, None, set())
    # Per a les línies sense pista, si la clau diu de qui és (`.vet1`, `.iri.2`), en fem cas.
    out = []
    for who, key, room, dialog, ps in lines:
        if who == "player" and not ps:
            parts = key.replace("_", ".").split(".")
            ps = {p for p in protas if any(x == p or (x.startswith(p) and x[len(p):].isdigit()) for x in parts)}
        out.append((who, key, room, dialog, frozenset(ps)))
    return out, dialog_rooms


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sala", action="append", default=[])
    ap.add_argument("--dialeg", action="append", default=[])
    ap.add_argument("--clau", action="append", default=[])
    ap.add_argument("--qui", action="append", default=[])
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
    model, language, fmt = cfg.get("model", "eleven_v3"), cfg.get("language", "ca"), cfg.get("format", "mp3_44100_64")

    lines, dialog_rooms = collect(content)

    def chosen(who, key, room, dialog):
        if a.tot or key in a.clau or (dialog and dialog in a.dialeg):
            return True
        return any(room == s or (dialog and s in dialog_rooms.get(dialog, ())) for s in a.sala)

    # (stem, personatge, clau, text a dir, veu)
    jobs, skipped, seen = [], [], set()
    for who, key, room, dialog, ps in lines:
        if who in SENSE_VEU or not chosen(who, key, room, dialog):
            continue
        if a.qui and who not in a.qui:
            continue
        speakers = sorted(ps) if who == "player" else [who]
        if not speakers:
            skipped.append((key, "no se sap quina protagonista la diu"))
            continue
        text = overrides.get(key, table.get(key, ""))
        if not text or "{" in text:
            skipped.append((key, "sense text" if not text else "té variables"))
            continue
        if text.startswith("(") and text.endswith(")"):
            skipped.append((key, "és una acotació"))
            continue
        for sp in speakers:
            if sp not in voices:
                skipped.append((key, f"{sp} no té veu a veus.json"))
                continue
            stem = f"{to_benne.get(sp, sp)}{fnv1a(key)}"
            if stem in seen:
                continue
            seen.add(stem)
            jobs.append((stem, sp, key, text, voices[sp]))

    todo = []
    for stem, sp, key, text, vid in jobs:
        print_ = hashlib.sha1(json.dumps([vid, model, language, text]).encode()).hexdigest()[:16]
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
                (out_dir / f"{stem}.mp3").write_bytes(r.read())
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
