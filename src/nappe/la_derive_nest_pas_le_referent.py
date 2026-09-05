#!/usr/bin/env python3
"""La dérive de la chaîne est-elle l'erreur du RÉFÉRENT ? — décomposée, sans ajustement.

⚠⚠ POURQUOI CE FICHIER EXISTE. `77` §10 mesure que la surface publiée est elle-même à ~20 µm
de la matière, et en conclut que l'écart de la chaîne mesuré **contre elle** est **gonflé** :
69,2 µm deviennent ~66,4 en retirant le référent **en quadrature**. Le registre `75` A5 bis
nomme le contrôle qui trancherait — *« refaire la mesure contre la surface recalée ; si l'écart
tombe, le budget est bien gonflé ; sinon, mon §10 ne s'applique pas à cette échelle-là »*.

⭐⭐⭐ **Et il se tranche sans recaler quoi que ce soit, parce qu'un biais est CONSTANT.** Une
erreur de référent se décompose en deux parts qui ne se corrigent pas de la même façon :

| part | ce qu'elle fait à l'écart mesuré | comment elle se retire |
|---|---|---|
| **biais** — le référent est décalé d'un côté | ajoute la MÊME chose à tous les maillons | il **s'annule dans les différences** |
| **dispersion** — le référent bruite autour de la matière | ajoute une variance | en **quadrature**, ce que `77` a fait |

Donc la part de l'écart final qu'aucun biais ne peut expliquer est **exactement**

$$\\frac{|e_N - e_1|}{|e_N|}$$

— aucun ajustement, aucun seuil, aucune fenêtre choisie. Mesuré : **99,4 %**.

⚠ La borne n'est valide qu'à une condition, et elle est **vérifiée** : tous les écarts médians
doivent porter le **même signe**, sinon un biais de signe opposé à la dérive pourrait dépasser
@f$|e_1|@f$. Les dix maillons sont négatifs.

⚠⚠ Ce fichier ne remplace pas la correction en quadrature de `77`, il la **borne par l'autre
bout** : la dispersion en retire ~4 %, le biais au plus 0,6 %. Ce qui reste — l'essentiel — est
une dérive de la **chaîne**, et le contrôle d'A5 bis est répondu **par la forme** du signal
plutôt que par un recalage qu'il aurait fallu construire.

Usage :
    uv run python src/nappe/la_derive_nest_pas_le_referent.py --verifier
    uv run python src/nappe/la_derive_nest_pas_le_referent.py \\
        --json docs/mesures/la_derive_nest_pas_le_referent.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]

COUVERTURE = RACINE / "docs" / "mesures" / "couverture_publiee.json"
REFERENT = RACINE / "docs" / "mesures" / "la_surface_et_la_feuille.json"


def serie(couverture: dict) -> list[dict]:
    """Les maillons, dans l'ordre de ce qu'ils ont parcouru.

    ⚠ Triés sur `parcouru_um` et non sur l'indice de maillon : les deux coïncident ici, et
    s'appuyer sur l'indice ferait dépendre la mesure d'une convention de nommage.
    """
    m = couverture.get("maillons") or []
    return sorted(m, key=lambda x: float(x["parcouru_um"]))


def meme_signe(ecarts: list[float]) -> bool:
    """Tous les écarts vont-ils du même côté ?

    ⚠⚠ C'est la condition de validité de la borne : si la dérive et un biais éventuel avaient
    des signes opposés, le premier maillon montrerait leur **différence** et bornerait le biais
    par en dessous au lieu d'en dessus. Sans ce contrôle, la borne serait une affirmation.
    """
    positifs = sum(1 for e in ecarts if e > 0)
    return positifs == 0 or positifs == len(ecarts)


def part_hors_biais(ecarts: list[float]) -> float:
    """
    @brief La part de l'écart final qu'aucun BIAIS constant ne peut expliquer.

    ⚠ Le premier maillon a déjà parcouru un peu, donc @f$|e_1|@f$ **majore** le biais : il
    contient le biais plus un peu de dérive. La borne est donc conservatrice, ce qui est le bon
    sens de l'erreur — elle sous-estime ce que la chaîne fait, jamais l'inverse.
    """
    if len(ecarts) < 2 or ecarts[-1] == 0:
        return 0.0
    return abs(ecarts[-1] - ecarts[0]) / abs(ecarts[-1])


def part_hors_dispersion(ecart_um: float, referent_um: float) -> float:
    """La part restante après retrait du référent EN QUADRATURE, comme `77` §10.

    ⚠ La quadrature suppose les deux erreurs **indépendantes** — hypothèse que `77` déclare et
    ne peut pas vérifier. Elle est reprise telle quelle ici, et nommée.
    """
    if ecart_um <= 0:
        return 0.0
    reste2 = ecart_um * ecart_um - referent_um * referent_um
    return (reste2 ** 0.5) / ecart_um if reste2 > 0 else 0.0


def decomposer(couverture: dict, referent_um: float, um_par_voxel: float | None = None) -> dict:
    """Ce que le référent peut expliquer de l'écart final, par ses deux parts."""
    maillons = serie(couverture)
    if len(maillons) < 2:
        raise SystemExit(f"au moins deux maillons sont requis, {len(maillons)} vu(s)")
    um = um_par_voxel or float(couverture.get("um_par_voxel", 0.0))
    if not um:
        raise SystemExit("la couverture ne déclare pas son µm par voxel")
    ecarts = [float(m["ecart_signe_median_vox"]) * um for m in maillons]
    if not meme_signe(ecarts):
        raise SystemExit("les écarts changent de signe : la borne sur le biais ne tient pas")
    hb = part_hors_biais(ecarts)
    hd = part_hors_dispersion(abs(ecarts[-1]), referent_um)
    return {"maillons": len(maillons), "um_par_voxel": um,
            "parcouru_um": [float(m["parcouru_um"]) for m in maillons],
            "ecart_um": [round(e, 2) for e in ecarts],
            "meme_signe": True,
            "monotone": all(abs(b) >= abs(a) - 1e-9 for a, b in zip(ecarts, ecarts[1:])),
            "ecart_final_um": round(abs(ecarts[-1]), 2),
            "referent_um": referent_um,
            "borne_du_biais_um": round(abs(ecarts[0]), 2),
            "part_hors_biais": round(hb, 4),
            "part_expliquable_par_un_biais": round(1.0 - hb, 4),
            "part_hors_dispersion": round(hd, 4),
            "ecart_corrige_um": round(abs(ecarts[-1]) * hd, 2),
            "part_expliquable_par_le_referent": round(1.0 - hb * hd, 4)}


def referent_mesure(chemin: Path = REFERENT) -> float | None:
    """Le référent en µm, LU dans la mesure de `77` §10 plutôt que retapé."""
    if not chemin.is_file():
        return None
    d = json.loads(chemin.read_text())
    cb = d.get("correction_du_budget") or {}
    for cle in ("referent_mesure_um", "referent_um", "referent_conjecture_um"):
        if cb.get(cle):
            return float(cb[cle])
    refs = cb.get("referents_par_rouleau") or {}
    return float(sorted(refs.values())[len(refs) // 2]) if refs else None


def verifier() -> int:
    echecs = controles = 0

    def v(nom: str, ok: bool, detail: str = "") -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    def couv(ecarts_vox, um=2.4):
        return {"um_par_voxel": um,
                "maillons": [{"parcouru_um": 100.0 * (i + 1),
                              "ecart_signe_median_vox": e, "maillon": i}
                             for i, e in enumerate(ecarts_vox)]}

    # ⚠⚠ UN BIAIS PUR : le même écart partout. Aucune dérive, donc la part hors biais est
    # NULLE — et c'est le cas où `77` aurait entièrement raison.
    v("un biais pur laisse 0 % hors biais", part_hors_biais([-10.0] * 5) == 0.0)
    # ⚠⚠ UNE DÉRIVE PURE depuis zéro : tout est hors biais.
    v("une dérive pure depuis zéro laisse 100 % hors biais",
      abs(part_hors_biais([0.0, -5.0, -10.0]) - 1.0) < 1e-9)
    # ⭐ Et un mélange rend exactement la part de la dérive.
    v("un mélange rend exactement la part de la dérive",
      abs(part_hors_biais([-10.0, -20.0, -30.0]) - 20.0 / 30.0) < 1e-9,
      f"{part_hors_biais([-10.0, -20.0, -30.0]):.4f}")

    # ⚠⚠⚠ LA CONDITION DE VALIDITÉ : des signes mêlés interdisent la borne, parce qu'un biais
    # de signe opposé à la dérive dépasserait |e1|. Le refus est ce qui empêche la borne d'être
    # une affirmation.
    v("des écarts de même signe passent", meme_signe([-1.0, -2.0, -3.0]))
    v("... et positifs aussi", meme_signe([1.0, 2.0, 3.0]))
    v("... mais des signes mêlés sont refusés", not meme_signe([-1.0, 2.0, -3.0]))
    v("une série à signes mêlés fait REFUSER la décomposition",
      _leve(lambda: decomposer(couv([-1.0, 2.0, -3.0]), 20.0)))
    v("... et une série d'un seul maillon aussi", _leve(lambda: decomposer(couv([-1.0]), 20.0)))
    v("... et une couverture sans µm par voxel aussi",
      _leve(lambda: decomposer({"maillons": couv([-1.0, -2.0])["maillons"]}, 20.0)))

    # --- la quadrature, reprise de `77` ---
    v("retirer un référent en quadrature réduit l'écart",
      abs(part_hors_dispersion(69.2, 19.5) - (69.2 ** 2 - 19.5 ** 2) ** 0.5 / 69.2) < 1e-9,
      f"{part_hors_dispersion(69.2, 19.5):.4f}")
    # ⚠ Un référent plus grand que l'écart ne laisserait RIEN : le cas est rendu 0, pas une
    # racine négative.
    v("... et un référent plus grand que l'écart ne laisse rien",
      part_hors_dispersion(10.0, 20.0) == 0.0)

    # --- la série est triée sur le PARCOURU, pas sur l'indice ---
    melange = couv([-1.0, -2.0, -3.0])
    melange["maillons"] = list(reversed(melange["maillons"]))
    v("les maillons sont triés sur le parcouru, pas sur leur ordre dans le fichier",
      [m["ecart_signe_median_vox"] for m in serie(melange)] == [-1.0, -2.0, -3.0])

    # --- contre les VRAIES mesures ---
    if not COUVERTURE.is_file():
        print("  ⚠ couverture absente : la partie « vrai arbre » n'a pas tourné")
    else:
        ref = referent_mesure() or 19.5
        r = decomposer(json.loads(COUVERTURE.read_text()), ref)
        v(f"les dix maillons vont tous du même côté et l'écart croît ({r['maillons']})",
          r["meme_signe"] and r["monotone"])
        # ⭐⭐ LA CONCLUSION : un biais de référent ne peut pas expliquer une rampe.
        v(f"un biais de référent explique au plus "
          f"{r['part_expliquable_par_un_biais'] * 100:.1f} % de l'écart final",
          r["part_expliquable_par_un_biais"] < 0.02,
          f"borne du biais {r['borne_du_biais_um']} µm sur {r['ecart_final_um']} µm")
        v(f"... et le référent entier, biais plus dispersion, en explique au plus "
          f"{r['part_expliquable_par_le_referent'] * 100:.1f} %",
          r["part_expliquable_par_le_referent"] < 0.10, f"référent {ref:.1f} µm")
        # ⚠ Le contrôle qui empêche « au plus X % » d'être vide : il faut qu'il reste quelque
        # chose. Un écart final nul rendrait toutes les parts triviales.
        v("... sur un écart final qui n'est pas nul",
          r["ecart_final_um"] > 50.0, f"{r['ecart_final_um']} µm")

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def _leve(f) -> bool:
    try:
        f()
    except SystemExit:
        return True
    except Exception:  # noqa: BLE001
        return False
    return False


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--couverture", type=Path, default=COUVERTURE)
    p.add_argument("--referent-um", type=float,
                   help="défaut : LU dans la mesure de `77` §10")
    p.add_argument("--json", type=Path)
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    if not a.couverture.is_file():
        raise SystemExit(f"couverture absente : {a.couverture}")
    ref = a.referent_um or referent_mesure()
    if ref is None:
        raise SystemExit("référent inconnu : donner --referent-um ou mesurer `77` §10")
    r = decomposer(json.loads(a.couverture.read_text()), ref)
    print(f"{'parcouru µm':>12} {'écart µm':>10}")
    print("-" * 24)
    for d, e in zip(r["parcouru_um"], r["ecart_um"]):
        print(f"{d:>12.0f} {e:>10.1f}")
    print(f"\nécart final          {r['ecart_final_um']:>8.1f} µm")
    print(f"référent (`77` §10)  {r['referent_um']:>8.1f} µm")
    print(f"borne du biais       {r['borne_du_biais_um']:>8.1f} µm  "
          f"→ un biais explique au plus {r['part_expliquable_par_un_biais'] * 100:.1f} %")
    print(f"après quadrature     {r['ecart_corrige_um']:>8.1f} µm  "
          f"→ le référent entier explique au plus "
          f"{r['part_expliquable_par_le_referent'] * 100:.1f} %")
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"écrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
