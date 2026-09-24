"""Le certificat d'un segment embarqué : ce que le Grand Prize et l'audit des Progress Prizes rejouent tous deux."""
from __future__ import annotations

import json
from pathlib import Path

from vesuve import donnees
from vesuve.treillis import certificat as cert


def les_lectures_en_plus(chemins) -> dict:
    """Des bandes lues ailleurs (`la_couverture_sans_main.py --lire`, ou `vesuve … --lire`) : `{clé: bande}`."""
    neuves = {}
    for c in chemins or ():
        neuves.update(json.loads(Path(c).read_text()).get("les_bandes") or {})
    return neuves


def certifier_le_segment(segment: str, neuves: dict | None = None) -> tuple[dict, dict]:
    """(le segment embarqué, le certificat) ; lève `LectureRefusee` si une bande neuve ne retombe pas."""
    s = donnees.le_segment(segment)
    return s, cert.certifier(s["presence"], s["bandes"], s["contexte"]["la_procedure"], neuves=neuves,
                             sources=s["sources"])


def la_carte_dencre_publiee(ctx: dict) -> str:
    """Le chemin, sur le bucket, de la carte d'encre publiée du segment (réduite 8×, sur le volume à 2,4 µm)."""
    o, s = ctx["lobjet"], ctx["le_segment"]
    return (f"{o}/segments/{s}/ink-detection/downsampled/{o}-{s}-2.4um-0.22m-78keV-volume-20260411134726-"
            f"20260417190342-new_canon_autoresearch_recipe-tile256-stride128-ds8.jpg")
