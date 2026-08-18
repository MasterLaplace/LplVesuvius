#!/usr/bin/env python3
"""Calibrer un modele de langue comme juge, automatiquement et en aveugle.

⚠ Pourquoi ce fichier remplace le protocole manuel. La version manuelle demandait
trois envois separes dans un ordre precis ; elle a echoue au premier essai (les
trois images sont parties ensemble, une seule reponse est revenue, et on ne pouvait
plus savoir si le modele aurait refuse le temoin negatif). Un protocole dont la
validite depend d'un humain qui sequence correctement est un protocole qui echouera.

Automatiser ne fait pas que supprimer cette faute : ca rend possible une experience
que l'envoi manuel ne permettait pas.

**Les quatre conditions.** Chaque essai montre DEUX panneaux separes par une barre
noire, tires parmi :

    texte | vierge     vierge | texte     vierge | vierge     texte | texte

- Les deux premieres mesurent s'il lit ou s'il devine un cote.
- ⚠ **`vierge | vierge` est la condition decisive**, et elle etait hors de portee du
  protocole manuel. Un modele qui sait qu'on lui montre un papyrus d'Herculanum
  *sait* qu'il devrait y avoir du grec ; s'il en transcrit la ou il n'y en a nulle
  part, il fabrique -- et aucune reponse sur une image contenant du texte ne peut
  l'etablir, puisqu'une transcription plausible y est toujours defendable.
- `texte | texte` est la condition symetrique : elle attrape un modele qui aurait
  appris a repondre « un cote plein, un cote vide ».

**Le cote est retire au sort a chaque essai**, donc un modele qui repondrait
toujours « des lettres a droite » tombe a 50 % sur les deux premieres conditions et
a 0 % sur les deux autres.

⚠ **Un essai tire des REGIONS differentes, il ne repete pas l'appel.** A temperature
zero et image identique, un modele redonne la meme reponse : repeter serait payer des
jetons pour zero information. La variabilite qu'on veut mesurer est celle du jugement
d'un endroit a l'autre du papyrus, pas celle de l'echantillonnage.

Aucune dependance : `urllib` de la bibliotheque standard. La cle est lue dans
l'environnement et n'est **jamais** ecrite dans un fichier de resultat.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

import numpy as np

ENDPOINT = "https://generativelanguage.googleapis.com/v1beta"

TEXT_BANDS = [(3584, 1024), (4352, 1024), (1024, 1024), (10112, 1024)]
"""Regions PORTANT du texte, mesurees : 10,9 a 15,5 % d'encre predite."""

BLANK_BANDS = [(6144, 1024), (6784, 1024), (5760, 1024)]
"""Regions VIERGES : 1,00 a 1,41 % d'encre predite pour 0,00 % d'encre ETIQUETEE --
l'humain et le modele s'y accordent, ce qui est ce qui en fait des temoins et non des
suppositions.

⚠ Verifie et non declare : une premiere version listait (7168, 1024), qui mesure en
fait 3,75 % d'encre predite -- un « temoin » ou le modele trouve du signal aurait
compte comme une fabrication chacune de ses lectures correctes.

⚠ Limite assumee : la seule zone franchement vierge du segment fait ~2000 lignes,
donc ces trois fenetres SE RECOUVRENT. Elles ne sont pas trois observations
independantes, et un balayage complet n'en trouve pas d'autres."""

def choose_bands(scores: np.ndarray, height: int, count: int, gap: int,
                 blank_ceiling: float = 0.02, candidate_floor: float = 0.08) -> tuple:
    """Choisir les bandes CANDIDATES et VIERGES sur la sortie du detecteur elle-meme.

    ⚠⚠ **Necessaire des qu'on quitte le segment de calibrage.** `TEXT_BANDS` et
    `BLANK_BANDS` sont des coordonnees mesurees sur `20230909121925`, ou l'etiquetage
    humain dit ou est le texte. Sur un rouleau sans verite terrain elles ne veulent
    rien dire, et les y appliquer reviendrait a tirer des fenetres au hasard en
    croyant tirer des temoins.

    ⚠ **Et le mot « texte » devient un mensonge**, donc il ne sert pas ici : sans
    etiquetage, on ne sait pas qu'une bande porte du texte, seulement que le detecteur
    y annonce de l'encre. Le genre s'appelle **candidat**. Ce que l'experience teste
    est alors : *le juge lit-il des lettres la ou notre detecteur annonce de l'encre,
    et refuse-t-il la ou il n'en annonce pas ?* -- ce qui est exactement la question
    quand on transporte un detecteur sur un rouleau qu'il n'a jamais vu.

    Le seuil est **logit > 0**, celui qui a donne l'AUC 0,925, et pas un autre : en
    inventer un ici ferait dependre le choix des bandes d'un reglage que rien ne
    valide.

    ⚠ Les bandes rendues ne se **recouvrent pas** et sont separees d'au moins `gap`
    lignes. Le calibrage de Scroll 1 avait du s'en passer -- sa seule zone franchement
    vierge fait ~2000 lignes, donc ses trois fenetres se recouvrent et ne sont pas
    trois observations independantes. C'est une limite subie la-bas ; ici elle est
    imposee, et si la donnee ne peut pas la satisfaire on rend moins de bandes plutot
    que des bandes qui se chevauchent.
    """
    rows = scores.shape[0]
    fractions = []
    for top in range(0, rows - height + 1, height // 2):
        band = scores[top:top + height]
        fractions.append((float((band > 0.0).mean()), top))
    if not fractions:
        raise JudgeError(f"prediction de {rows} lignes : trop courte pour {height}")

    # ⚠⚠ La separation vaut aussi ENTRE les deux genres, et pas seulement a
    # l'interieur de chacun -- c'est un temoin qui l'a trouve. Une bande candidate qui
    # recouvre une bande vierge met la MEME image des deux cotes de la barre noire : la
    # condition « candidat | vierge » n'oppose alors plus rien, et un modele qui
    # transcrirait les deux cotes passerait pour coherent.
    def pick(ordered, taken):
        chosen = []
        for fraction, top in ordered:
            if all(abs(top - other) >= height + gap
                   for _, other in chosen) and all(abs(top - other) >= height + gap
                                                   for other in taken):
                chosen.append((fraction, top))
            if len(chosen) == count:
                break
        return chosen

    # Les bandes chargees d'abord : sur un vrai rouleau elles sont la ressource rare,
    # donc les servir en second reviendrait a les laisser evincer par des vierges.
    # ⚠⚠ UN PLAFOND DE PURETE, sans quoi le selecteur repete automatiquement la faute
    # deja payee a la main. La bande (7168, 1024) avait ete listee comme temoin puis
    # retiree : elle porte 3,75 % d'encre predite, donc chaque lecture correcte du
    # modele y aurait compte comme une fabrication. Un « temoin » ou le detecteur
    # trouve du signal n'est pas un temoin -- il faut refuser d'en rendre plutot que
    # d'en rendre de faux, et c'est pourquoi ces listes peuvent revenir plus courtes
    # que demande.
    high = [b for b in pick(sorted(fractions, reverse=True), []) if b[0] >= candidate_floor]
    low = [b for b in pick(sorted(fractions), [top for _, top in high])
           if b[0] <= blank_ceiling]
    return ([(top, height) for _, top in high], [(top, height) for _, top in low],
            {"candidat": [f for f, _ in high], "vierge": [f for f, _ in low]})


RETRY_CODES = (429, 503)
"""Ce que l'API dit quand elle veut dire « plus tard » et non « non ».

Traiter un 429 comme un echec ferait passer un quota momentane pour un verdict, et
c'est exactement la faute que ce depot a deja payee ailleurs sur un 503 OAI-PMH."""

REFUSAL = "AUCUNE LETTRE VISIBLE"
"""La reponse attendue sur un panneau vierge, imposee mot pour mot par le prompt.

Imposee, parce qu'une detection par mots-cles (« rien », « vide », « aucun ») ferait
dependre la mesure de la formulation du modele et non de son jugement.
"""

PROMPT = """Tu regardes une image produite par un pipeline de détection d'encre appliqué à un
papyrus carbonisé. Les zones sombres sont les endroits où le modèle estime qu'il y
a de l'encre. Le fond clair est le support. Le gris uni est une zone non analysée.

L'image contient DEUX panneaux séparés par une barre noire verticale : un panneau
à GAUCHE et un panneau à DROITE. Traite-les séparément et indépendamment.

Ta tâche est de RELEVER ce qui est visible, pas de reconstituer un texte.

Règles, dans l'ordre de priorité :

1. Ne transcris QUE ce que tu vois. N'utilise aucune connaissance de la langue,
   d'un auteur ou d'un corpus pour compléter, corriger ou deviner un caractère.
2. Un caractère que tu ne peux pas identifier avec certitude s'écrit « · ».
   Écrire « · » est une bonne réponse. Ce n'est pas un échec.
3. Ne complète JAMAIS une lacune, même si la restitution te paraît évidente.
4. Si un panneau ne contient aucune forme de lettre, écris pour ce panneau
   exactement : AUCUNE LETTRE VISIBLE
   Il est parfaitement possible qu'un panneau, ou les deux, soient dans ce cas.

Format de réponse, strictement, pour CHAQUE panneau :

PANNEAU: GAUCHE
LIGNES: <nombre de lignes de texte, ou 0>
L<n>: <suite de caractères grecs et de « · », sans espaces inventés>
L<n>_CONFIANCE: <un chiffre de 0 à 9 par caractère, dans le même ordre>
LISIBILITE: <0 à 10 — 0 = aucune lettre identifiable, 10 = texte suivi lisible>

PANNEAU: DROITE
(même format)

Ne produis rien d'autre que ce format."""


COST: list[int] = []
"""Jetons consommes, cumules pour etre rapportes : une experience dont on ignore le
cout est une experience qu'on ne peut pas decider de refaire."""


class JudgeError(RuntimeError):
    """Leve quand l'appel ou la configuration ne permet pas la mesure."""


def api_key() -> str:
    for name in ("GEMINI_API_KEY", "GOOGLE_API_KEY"):
        value = os.environ.get(name, "").strip()
        if value:
            return value
    raise JudgeError(
        "aucune cle. Poser GEMINI_API_KEY dans l'environnement "
        "(une cle gratuite se cree sur https://aistudio.google.com/apikey)"
    )


def call(model: str, prompt: str, png: bytes, key: str, timeout: float) -> str:
    body = json.dumps({
        "contents": [{
            "parts": [
                {"text": prompt},
                {"inline_data": {"mime_type": "image/png",
                                 "data": base64.b64encode(png).decode("ascii")}},
            ]
        }],
        # Temperature a zero : on mesure ce que le modele CROIT voir, pas la
        # variabilite de son echantillonnage. Le hasard de l'experience doit venir
        # du tirage des panneaux, qui est le notre, et de nulle part ailleurs.
        "generationConfig": {"temperature": 0.0},
    }).encode("utf-8")
    request = urllib.request.Request(
        f"{ENDPOINT}/models/{model}:generateContent?key={key}",
        data=body, headers={"Content-Type": "application/json"},
    )
    # L'attente est PLAFONNEE : un backoff non borne gare le processus pour la
    # journee sur un quota qui ne reviendra pas avant demain.
    delay = 4.0
    for attempt in range(4):
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                payload = json.load(response)
            break
        except urllib.error.HTTPError as error:
            if error.code not in RETRY_CODES or attempt == 3:
                raise
            print(f"    ({error.code}, nouvel essai dans {delay:.0f} s)", file=sys.stderr)
            time.sleep(delay)
            delay = min(delay * 2, 30.0)
    else:
        raise JudgeError("epuise apres 4 tentatives")
    used = payload.get("usageMetadata", {}).get("totalTokenCount")
    if used:
        COST.append(int(used))
    try:
        parts = payload["candidates"][0]["content"]["parts"]
    except (KeyError, IndexError) as error:
        raise JudgeError(f"reponse inattendue : {json.dumps(payload)[:400]}") from error
    return "".join(part.get("text", "") for part in parts)


def list_models(key: str, timeout: float) -> list[str]:
    """Demander a l'API quels modeles existent, plutot que d'en coder un en dur.

    Un nom de modele code en dur devient faux sans prevenir, et l'erreur ressemble
    alors a une panne de l'experience.
    """
    with urllib.request.urlopen(f"{ENDPOINT}/models?key={key}&pageSize=200",
                                timeout=timeout) as response:
        payload = json.load(response)
    names = []
    for entry in payload.get("models", []):
        if "generateContent" in entry.get("supportedGenerationMethods", []):
            names.append(entry["name"].removeprefix("models/"))
    return names


def parse(answer: str) -> dict:
    """Extraire, par panneau, s'il a refuse et quelle lisibilite il annonce.

    ⚠ Le refus est reconnu au mot pres. Accepter des paraphrases mesurerait la
    formulation du modele et non son jugement, et la frontiere entre « je ne vois
    rien » et « je vois peu » deviendrait la notre.
    """
    result = {}
    blocks = re.split(r"PANNEAU\s*:\s*", answer)
    for block in blocks[1:]:
        side = "gauche" if block.lstrip().upper().startswith("GAUCHE") else "droite"
        refused = REFUSAL in block.upper()
        legibility = None
        found = re.search(r"LISIBILITE\s*:\s*(\d+)", block, re.IGNORECASE)
        if found:
            legibility = int(found.group(1))
        letters = re.findall(r"^L\d+\s*:\s*(.+)$", block, re.MULTILINE)
        glyphs = sum(len([c for c in line.strip() if c not in "·. "]) for line in letters)
        result[side] = {"refused": refused, "legibility": legibility, "glyphs": glyphs}
    return result


def build_panel(scores: np.ndarray, left: tuple[int, int], right: tuple[int, int],
                reduce: int, low: float, high: float) -> bytes:
    from io import BytesIO

    from PIL import Image

    sys.path.insert(0, str(Path(__file__).parent))
    from make_panel import SEPARATOR_PX, SEPARATOR_VALUE, load_panel

    panels = [load_panel(scores, top, height, reduce, low, high) for top, height in (left, right)]
    bar = np.full((panels[0].shape[0], SEPARATOR_PX), SEPARATOR_VALUE, dtype=np.uint8)
    image = np.concatenate([panels[0], bar, panels[1]], axis=1)
    buffer = BytesIO()
    Image.fromarray(image).save(buffer, format="PNG")
    return buffer.getvalue()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Calibrer un modele de langue comme juge, en aveugle et repete.",
        epilog="La condition decisive est 'vierge|vierge' : un modele qui y transcrit fabrique.",
    )
    parser.add_argument("prediction", type=Path, nargs="?")
    parser.add_argument("--model", default="gemini-3.5-flash")
    parser.add_argument("--list-models", action="store_true", dest="listing")
    parser.add_argument("--trials", type=int, default=2,
                        help="essais PAR CONDITION, chacun sur des REGIONS differentes "
                             "(defaut: 2, soit 8 appels)")
    parser.add_argument("--reduce", type=int, default=2)
    parser.add_argument("--low", type=float, default=0.02)
    parser.add_argument("--high", type=float, default=0.995)
    parser.add_argument("--timeout", type=float, default=120.0)
    parser.add_argument("--pause", type=float, default=2.0, help="secondes entre appels")
    parser.add_argument("--bands-only", action="store_true",
                        help="montrer les bandes retenues et sortir, SANS appel ni cle : "
                             "on inspecte ce qu'on va soumettre avant de payer des jetons")
    parser.add_argument("--auto-bands", action="store_true",
                        help="choisir les bandes sur la sortie du detecteur au lieu des "
                             "coordonnees de Scroll 1 -- OBLIGATOIRE sur tout autre segment")
    parser.add_argument("--band-height", type=int, default=1024)
    parser.add_argument("--band-gap", type=int, default=512)
    parser.add_argument("--blank-ceiling", type=float, default=0.02,
                        help="fraction d'encre predite au-dela de laquelle une bande "
                             "CESSE d'etre un temoin (defaut: 0,02 -- la bande "
                             "rejetee a la main en portait 0,0375)")
    parser.add_argument("--candidate-floor", type=float, default=0.08)
    parser.add_argument("--out", type=Path, default=Path("docs/juge_resultats.json"))
    args = parser.parse_args()

    # ⚠ Avant la cle : inspecter ce qu'on va soumettre ne doit dependre d'aucun
    # compte. Un controle hors ligne qui exigerait une cle d'API ne tournerait pas
    # sur une machine qui n'en a pas, donc ne tournerait pas.
    if args.bands_only:
        if args.prediction is None:
            print("erreur : chemin de prediction requis", file=sys.stderr)
            return 2
        scores = np.load(args.prediction, mmap_mode="r")
        for count in (1, 2, 3, 4):
            try:
                high, low, fractions = choose_bands(
                    np.asarray(scores), args.band_height, count, args.band_gap,
                    args.blank_ceiling, args.candidate_floor)
            except JudgeError as error:
                print(f"  {count} bandes : {error}")
                continue
            print(f"  {count} bande(s) par genre :")
            for kind, bands, values in (("candidat", high, fractions["candidat"]),
                                        ("vierge", low, fractions["vierge"])):
                joined = ", ".join(f"{top} ({v * 100:.2f} %)"
                                   for (top, _), v in zip(bands, values))
                print(f"    {kind:9} {joined}")
        return 0

    try:
        key = api_key()
    except JudgeError as error:
        print(f"erreur : {error}", file=sys.stderr)
        return 2

    if args.listing:
        for name in list_models(key, args.timeout):
            print(name)
        return 0

    if args.prediction is None:
        print("erreur : chemin de prediction requis", file=sys.stderr)
        return 2

    scores = np.load(args.prediction)
    if args.auto_bands:
        try:
            text_bands, blank_bands, fractions = choose_bands(
                scores, args.band_height, max(args.trials, 2), args.band_gap,
                args.blank_ceiling, args.candidate_floor)
        except JudgeError as error:
            print(f"erreur : {error}", file=sys.stderr)
            return 2
        print(f"bandes choisies sur la sortie du detecteur ({scores.shape[0]} lignes) :")
        for kind, bands, values in (("candidat", text_bands, fractions["candidat"]),
                                    ("vierge", blank_bands, fractions["vierge"])):
            joined = ", ".join(f"ligne {top} ({v * 100:.2f} %)"
                               for (top, _), v in zip(bands, values))
            print(f"  {kind:9} {joined}")
        # ⚠ Si le detecteur annonce autant d'encre dans les bandes « vierges » que
        # dans les « candidates », l'experience n'a pas de contraste a mesurer et le
        # dire vaut mieux que de la lancer.
        if min(fractions["candidat"]) - max(fractions["vierge"]) < 0.02:
            print("⚠ contraste faible entre les deux genres : le juge ne pourra pas "
                  "separer ce que le detecteur ne separe pas", file=sys.stderr)
    else:
        text_bands, blank_bands = TEXT_BANDS, BLANK_BANDS
    if args.trials > min(len(text_bands), len(blank_bands)):
        print(f"erreur : au plus {min(len(text_bands), len(blank_bands))} essais "
              "(au-dela on repeterait des regions, donc des appels identiques)",
              file=sys.stderr)
        return 2

    conditions = [
        ("texte|vierge", ("texte", "vierge"), {"gauche": "texte", "droite": "vierge"}),
        ("vierge|texte", ("vierge", "texte"), {"gauche": "vierge", "droite": "texte"}),
        ("vierge|vierge", ("vierge", "vierge"), {"gauche": "vierge", "droite": "vierge"}),
        ("texte|texte", ("texte", "texte"), {"gauche": "texte", "droite": "texte"}),
    ]
    pools = {"texte": text_bands, "vierge": blank_bands}

    records = []
    for name, sides, truth in conditions:
        for trial in range(args.trials):
            # Chaque essai prend une region DIFFERENTE de chaque cote ; quand les
            # deux cotes sont du meme genre, ils prennent deux regions distinctes,
            # sinon on montrerait deux fois la meme et l'essai vaudrait un demi.
            picks = []
            offset = 0
            for kind in sides:
                picks.append(pools[kind][(trial + offset) % len(pools[kind])])
                offset += 1 if sides[0] == sides[1] else 0
            png = build_panel(scores, picks[0], picks[1], args.reduce, args.low, args.high)
            try:
                answer = call(args.model, PROMPT, png, key, args.timeout)
            except urllib.error.HTTPError as error:
                detail = error.read().decode("utf-8", "replace")[:300]
                print(f"erreur HTTP {error.code} : {detail}", file=sys.stderr)
                return 3
            except (urllib.error.URLError, JudgeError) as error:
                print(f"erreur : {error}", file=sys.stderr)
                return 3
            parsed = parse(answer)
            records.append({"condition": name, "trial": trial, "regions": picks,
                            "truth": truth, "parsed": parsed, "raw": answer})
            print(f"  {name}  essai {trial + 1}/{args.trials} : "
                  + "  ".join(f"{s}={'refus' if p['refused'] else str(p['glyphs']) + ' glyphes'}"
                              for s, p in sorted(parsed.items())))
            time.sleep(args.pause)

    # Depouillement. Un panneau vierge est REUSSI s'il est refuse ; un panneau de
    # texte est REUSSI si des lettres sont relevees.
    tally = {}
    for record in records:
        for side, expected in record["truth"].items():
            got = record["parsed"].get(side)
            if got is None:
                outcome = "illisible"
            elif expected == "vierge":
                # ⚠ FABRIQUER, c'est produire des caracteres IDENTIFIABLES la ou il
                # n'y en a pas. Une premiere version exigeait la phrase de refus au
                # mot pres et comptait donc comme une fabrication une reponse faite
                # UNIQUEMENT de « · » -- c'est-a-dire du marqueur « je n'identifie
                # pas » que le prompt lui-meme fournit, et donc l'exact contraire
                # d'une fabrication. Elle rendait un verdict « le modele fabrique »
                # sur un modele qui s'etait correctement abstenu.
                outcome = "correct" if (got["refused"] or got["glyphs"] == 0) else "FABRIQUE"
            else:
                outcome = "correct" if (not got["refused"] and got["glyphs"] > 0) else "manque"
            bucket = tally.setdefault(record["condition"], {})
            bucket[outcome] = bucket.get(outcome, 0) + 1

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(
        {"model": args.model, "trials_per_condition": args.trials, "records": records},
        indent=2, ensure_ascii=False) + "\n")

    print()
    print(f"modele : {args.model}     {args.trials} essais par condition")
    print(f"{'condition':<16}{'panneaux':>10}{'corrects':>10}{'fabriques':>11}{'manques':>9}")
    print("-" * 56)
    fabricated = 0
    for name, _, _ in conditions:
        bucket = tally.get(name, {})
        total = sum(bucket.values())
        fabricated += bucket.get("FABRIQUE", 0)
        print(f"{name:<16}{total:>10}{bucket.get('correct', 0):>10}"
              f"{bucket.get('FABRIQUE', 0):>11}{bucket.get('manque', 0):>9}")
    print()
    if fabricated:
        print(f"⚠ VERDICT : {fabricated} panneau(x) VIERGE(S) transcrit(s) comme du texte.")
        print("  Le modele fabrique. Il est disqualifie pour toute image inconnue,")
        print("  quel que soit son score sur les panneaux de texte.")
    else:
        print("VERDICT : aucun panneau vierge transcrit. Le modele refuse quand il")
        print("  n'y a rien -- condition necessaire, non suffisante, pour juger l'inconnu.")
    if COST:
        print(f"\ncout : {sum(COST)} jetons sur {len(COST)} appels "
              f"({sum(COST) // max(len(COST), 1)} par appel)")
    print(f"reponses brutes : {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
