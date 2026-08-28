#!/usr/bin/env python3
"""L'encre est-elle lisible à 9 µm ? — la question de `M1ter`, posée contre de vraies étiquettes.

⚠⚠ POURQUOI CE FICHIER EXISTE. `M1ter` (`29` §6) demande depuis des semaines *« l'encre
est-elle lisible à 9 µm ? »*, et tout ce que le dépôt savait en dire passait par des σ et des
comparaisons entre objets. [`63`](../../docs/63_la_premiere_verite_terrain.md) §2 a rendu les
premiers chiffres contre de **vraies étiquettes** — 0,693 à 6,48 µm, 0,686 à 9,72 — mais les
a publiés pour répondre à une **autre** question : *la résolution explique-t-elle l'écart aux
0,925 ?* La réponse était non, et la question de `M1ter` est restée ouverte à côté de sa
propre réponse.

  ⭐⭐ Les deux questions ne sont pas la même, et une seule des deux est établissable :
     « 9,72 est-il PIRE que 3,24 ? »  → [`64`](../../docs/64_la_dispersion_netait_pas_un_effet.md)
       dit qu'il faudrait 79 tuiles par condition ; on en a 16.
     « 9,72 est-il AU-DESSUS DU HASARD ? » → c'est un intervalle contre 0,5, et 16 tuiles
       suffisent largement.

⚠⚠⚠ ET LA RÉSERVE QUI VOYAGE AVEC LE RÉSULTAT, écrite dans `63` §3 : la décimation
**conserve le détail en profondeur** qu'un vrai scan grossier n'aurait pas, puisqu'un voxel
plus large intègre aussi dans cette direction. Ce qui est mesuré ici est donc un **majorant**
de ce qu'un vrai scan à 9,72 µm rendrait. Un majorant qui reste au-dessus du hasard répond
« oui, à cette borne près » ; il ne répondrait rien s'il tombait dessous.

⚠ La maille de tuile est **une fraction de la surface**, pas un nombre de pixels : à chaque
échelle, 4 × 4 tuiles couvrant chacune le seizième du même morceau de papyrus. Une maille en
pixels ferait porter chaque tuile sur trois fois plus de terrain à 9,72 µm qu'au natif, donc
les intervalles ne seraient plus comparables — et c'est exactement le genre d'écart qu'on
prendrait ensuite pour un effet de la résolution.

Usage :
    uv run python src/encre/lisible_a_neuf_microns.py --verifier
    uv run python src/encre/lisible_a_neuf_microns.py --json docs/mesures/lisible_a_neuf_microns.json
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src"))

from volume.evaluate_segment import auc, load_pair  # noqa: E402

ECHELLES = (
    ("natif", 1, 3.24, "data/out/ink_frag1_54keV.npy", "data/frag1/labels_fenetre.png"),
    ("×2", 2, 6.48, "data/out/ink_frag1_d2.npy", "data/frag1/labels_d2.png"),
    ("×3", 3, 9.72, "data/out/ink_frag1_d3.npy", "data/frag1/labels_d3.png"),
)
"""Les trois échelles, écrites plutôt que découvertes.

⚠ ×2 et ×3 **encadrent** les 7,91 µm de l'entraînement du modèle, et ×3 est celle que
`M1ter` nomme. Une quatrième doit être ajoutée ici, donc vue.
"""

COTES = 4
"""Le nombre de tuiles par côté — donc 16 tuiles, à toutes les échelles.

⚠⚠ C'est ce nombre qui est tenu constant, pas la taille en pixels. Voir l'en-tête : une
taille en pixels constante ferait porter les tuiles sur des surfaces différentes selon
l'échelle, et rendrait les intervalles incomparables pour une raison étrangère au papyrus.
"""

MINIMUM = 32
"""Pixels d'encre minimaux pour qu'une tuile ait une AUC définie.

⚠ Plus bas que les 64 de `bruit_dune_fenetre` parce que les tuiles sont ici plus petites à
l'échelle ×3 (85 px de côté) : garder 64 y écarterait des tuiles parfaitement mesurables.
Le seuil écarte le dégénéré, jamais le rare."""


def tuiles_par_fraction(prediction: np.ndarray, verite: np.ndarray, cotes: int = COTES,
                        minimum: int = MINIMUM) -> list[dict]:
    """AUC de chaque tuile, la carte étant découpée en `cotes × cotes` parts égales.

    ⚠ Les pixels non couverts sont écartés : `argsort` range les `NaN` en tête, donc les
    garder les classerait comme les mieux notés de la tuile. Défaut réellement payé le
    2026-08-28 sur le fichier voisin.
    """
    out = []
    h, w = prediction.shape
    ph, pw = h // cotes, w // cotes
    if ph < 8 or pw < 8:
        return out
    for i in range(cotes):
        for j in range(cotes):
            p = prediction[i * ph:(i + 1) * ph, j * pw:(j + 1) * pw].ravel()
            t = verite[i * ph:(i + 1) * ph, j * pw:(j + 1) * pw].ravel()
            couvert = np.isfinite(p)
            p, t = p[couvert], t[couvert]
            pos = int(t.sum())
            neg = int(t.size - pos)
            if pos < minimum or neg < minimum:
                continue
            out.append({"i": i, "j": j, "cote_px": ph, "pixels": int(t.size),
                        "encre_%": 100.0 * pos / t.size, "auc": auc(p, t)})
    return out


def intervalle(valeurs: list[float], tirages: int = 4000, graine: int = 0) -> dict:
    """Intervalle de confiance de la moyenne, en rééchantillonnant les TUILES.

    ⚠⚠ Par tuiles et jamais par pixels : les pixels d'une carte d'encre ne sont pas
    indépendants, et un intervalle calculé sur eux serait cent fois trop étroit — mesuré
    dans `bruit_dune_fenetre`, où la formule usuelle rend 109 fois moins large.
    """
    v = np.asarray(valeurs, dtype=np.float64)
    if v.size < 3:
        return {"exploitable": False, "n": int(v.size)}
    rng = np.random.default_rng(graine)
    moy = v[rng.integers(0, v.size, size=(tirages, v.size))].mean(axis=1)
    return {"exploitable": True, "n": int(v.size), "moyenne": float(v.mean()),
            "ic_bas": float(np.percentile(moy, 2.5)),
            "ic_haut": float(np.percentile(moy, 97.5))}


def au_dessus_du_hasard(ic: dict) -> bool:
    """L'intervalle exclut-il 0,5 par le haut ?

    ⚠ Par le HAUT seulement. Un intervalle entièrement sous 0,5 dirait que le modèle range
    l'encre à l'envers — c'est un autre fait, et le confondre avec « lisible » serait
    exactement le genre de test qu'on satisfait pour la mauvaise raison.
    """
    return bool(ic.get("exploitable") and ic["ic_bas"] > 0.5)


def melanger(prediction: np.ndarray, graine: int = 7) -> np.ndarray:
    """La même carte, ses valeurs couvertes permutées — le témoin qui donne l'échelle.

    ⚠⚠ Le mélange se fait SUR LES PIXELS COUVERTS seulement, et remet les non couverts à
    leur place : mélanger tout le tableau déplacerait les `NaN`, donc changerait quelles
    tuiles sont mesurables, et le témoin ne porterait plus sur le même découpage.
    """
    rng = np.random.default_rng(graine)
    out = prediction.copy()
    couvert = np.isfinite(out)
    vals = out[couvert]
    rng.shuffle(vals)
    out[couvert] = vals
    return out


def balayage_de_maille(prediction: np.ndarray, verite: np.ndarray,
                       cotes_a_essayer=(3, 4, 5, 6, 8), tirages: int = 2000) -> list[dict]:
    """L'intervalle se resserre-t-il si on découpe plus fin ?

    ⚠⚠ POURQUOI CETTE QUESTION EST OUVERTE ET NON RHÉTORIQUE. Plus de tuiles rétrécit un
    intervalle en √n, mais des tuiles plus petites portent des AUC plus bruitées, donc
    l'écart-type grandit en même temps. Lequel gagne n'est **pas** décidable sur le papier :
    il dépend de la taille des structures d'encre par rapport à la maille. Si découper plus
    fin resserrait, la carte de 341 px suffirait à trancher la lisibilité à 9,72 µm ; sinon
    il faut rendre plus de surface, ce qui est une campagne.

    ⚠ Une maille trop fine finit par ne plus porter assez d'encre par tuile, et les tuiles
    sont alors **écartées** — donc `n` peut se mettre à DIMINUER quand on découpe plus fin.
    C'est le signal qu'on a dépassé le point utile, et il faut le voir plutôt que de le
    supposer.
    """
    out = []
    for c in cotes_a_essayer:
        lot = tuiles_par_fraction(prediction, verite, cotes=c)
        ic = intervalle([t["auc"] for t in lot], tirages)
        out.append({"cotes": c, "tuiles": len(lot),
                    "cote_px": lot[0]["cote_px"] if lot else 0,
                    "intervalle": ic,
                    "largeur": (ic["ic_haut"] - ic["ic_bas"]) if ic.get("exploitable") else None,
                    "au_dessus": au_dessus_du_hasard(ic)})
    return out


def mesurer(racine: Path = RACINE, tirages: int = 4000) -> dict:
    """Les trois échelles, leur intervalle, et leur témoin par mélange."""
    lignes = []
    for nom, facteur, um, carte, labels in ECHELLES:
        pc, pl = racine / carte, racine / labels
        if not pc.is_file() or not pl.is_file():
            continue
        prediction, verite = load_pair(pc, pl)
        lot = tuiles_par_fraction(prediction, verite)
        temoin = tuiles_par_fraction(melanger(prediction), verite)
        couvert = np.isfinite(prediction)
        lignes.append({
            "echelle": nom, "facteur": facteur, "voxel_um": um,
            "forme": list(prediction.shape),
            "auc_groupee": auc(prediction[couvert], verite[couvert]),
            "tuiles": lot,
            "intervalle": intervalle([t["auc"] for t in lot], tirages),
            "intervalle_melange": intervalle([t["auc"] for t in temoin], tirages, graine=3),
            "balayage_de_maille": balayage_de_maille(prediction, verite),
        })
    return {"tuiles_par_cote": COTES, "echelles": lignes}


def rapporter(m: dict) -> None:
    """La sortie lisible, le témoin à côté de la mesure."""
    print(f"{m['tuiles_par_cote']}×{m['tuiles_par_cote']} tuiles par carte — "
          f"chacune couvre le {m['tuiles_par_cote'] ** 2}e du meme morceau de papyrus\n")
    print(f"{'echelle':8} {'µm':>6} {'groupee':>8} {'moy.tuiles':>11} "
          f"{'IC 95 %':>20} {'n':>3} {'melange':>20}")
    for e in m["echelles"]:
        ic, tm = e["intervalle"], e["intervalle_melange"]
        if not ic.get("exploitable"):
            print(f"{e['echelle']:8} {e['voxel_um']:6.2f} {e['auc_groupee']:8.3f} "
                  f"{'pas assez de tuiles':>32}")
            continue
        s = f"[{ic['ic_bas']:.3f} ; {ic['ic_haut']:.3f}]"
        st = f"[{tm['ic_bas']:.3f} ; {tm['ic_haut']:.3f}]" if tm.get("exploitable") else "—"
        print(f"{e['echelle']:8} {e['voxel_um']:6.2f} {e['auc_groupee']:8.3f} "
              f"{ic['moyenne']:11.3f} {s:>20} {ic['n']:3d} {st:>20}")

    print()
    print("  la maille plus fine resserre-t-elle l'intervalle ?")
    print(f"    {'echelle':8} " + " ".join(f"{c}x{c}".rjust(9) for c in (3, 4, 5, 6, 8)))
    for e in m["echelles"]:
        cases = []
        for b in e.get("balayage_de_maille", []):
            cases.append(f"{b['largeur']:.3f}({b['tuiles']})".rjust(9)
                         if b["largeur"] is not None else "—".rjust(9))
        print(f"    {e['echelle']:8} " + " ".join(cases))
    print("    (largeur de l'IC, et nombre de tuiles gardees entre parentheses)")

    print()
    for e in m["echelles"]:
        oui = au_dessus_du_hasard(e["intervalle"])
        temoin_ok = not au_dessus_du_hasard(e["intervalle_melange"])
        print(f"  {e['voxel_um']:5.2f} µm : "
              + ("AU-DESSUS du hasard" if oui else "non etabli au-dessus du hasard")
              + ("" if temoin_ok else "  ⚠⚠ ET LE MELANGE AUSSI — la mesure ne prouve rien"))


def verifier() -> int:
    """L'instrument peut-il rendre la mauvaise réponse ?"""
    echecs = controles = 0

    def v(nom, cond, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not cond:
            echecs += 1
            print(f"  ECHEC  {nom}" + (f"  — {detail}" if detail else ""))

    rng = np.random.default_rng(9)

    # -- decoupe : le compte de tuiles ne depend PAS de la taille de la carte.
    for taille in (256, 512, 1024):
        p = rng.random((taille, taille)).astype(np.float32)
        t = rng.random((taille, taille)) < 0.3
        lot = tuiles_par_fraction(p, t)
        v(f"une carte de {taille} px rend {COTES ** 2} tuiles", len(lot) == COTES ** 2,
          f"{len(lot)}")
        v(f"... et leur cote vaut {taille // COTES}",
          all(x["cote_px"] == taille // COTES for x in lot))
    # ⚠⚠ LA PROPRIETE QUI PORTE LA COMPARAISON : a deux echelles, la MEME fraction de
    # surface. Une maille en pixels constante la casserait, et l'intervalle a 9,72 µm
    # porterait alors sur trois fois plus de terrain qu'au natif.
    grand = tuiles_par_fraction(rng.random((1024, 1024)).astype(np.float32),
                                rng.random((1024, 1024)) < 0.3)
    petit = tuiles_par_fraction(rng.random((341, 341)).astype(np.float32),
                                rng.random((341, 341)) < 0.3)
    v("la fraction de surface couverte est la meme aux deux echelles",
      len(grand) == len(petit) == COTES ** 2, f"{len(grand)} vs {len(petit)}")

    # -- une carte trop petite ne rend rien plutot que des tuiles minuscules.
    v("une carte trop petite ne rend aucune tuile",
      tuiles_par_fraction(rng.random((12, 12)).astype(np.float32),
                          rng.random((12, 12)) < 0.5) == [])

    # -- NaN : le defaut deja paye une fois.
    troue = rng.random((256, 256)).astype(np.float64)
    ver = rng.random((256, 256)) < 0.3
    troue[ver] = np.nan
    lot = tuiles_par_fraction(troue, ver)
    v("un pixel non couvert n'est pas classe comme le mieux note",
      all(abs(x["auc"] - 1.0) > 0.4 for x in lot), str([round(x["auc"], 3) for x in lot[:3]]))

    # -- balayage de maille : le compte suit la maille, et la sortie est complete.
    p8 = rng.random((512, 512)).astype(np.float32)
    t8 = rng.random((512, 512)) < 0.3
    bal = balayage_de_maille(p8, t8, (2, 4), 200)
    v("le balayage rend une ligne par maille essayee", len(bal) == 2, str(len(bal)))
    v("... et le compte de tuiles suit la maille",
      bal[0]["tuiles"] == 4 and bal[1]["tuiles"] == 16, str([b["tuiles"] for b in bal]))
    v("... et la cote en pixels suit aussi",
      bal[0]["cote_px"] == 256 and bal[1]["cote_px"] == 128,
      str([b["cote_px"] for b in bal]))
    # ⚠ Une maille trop fine sur une carte minuscule doit rendre zero tuile SANS casser.
    minus = balayage_de_maille(rng.random((20, 20)).astype(np.float32),
                               rng.random((20, 20)) < 0.3, (8,), 100)
    v("une maille trop fine rend zero tuile sans casser",
      minus[0]["tuiles"] == 0 and minus[0]["largeur"] is None, str(minus))

    # -- intervalle : encadre, se resserre, reproductible.
    a = list(rng.normal(0.7, 0.1, 8))
    b = list(rng.normal(0.7, 0.1, 200))
    ia, ib = intervalle(a, 2000, 1), intervalle(b, 2000, 1)
    v("l'intervalle encadre la moyenne", ia["ic_bas"] <= ia["moyenne"] <= ia["ic_haut"])
    v("... et se resserre avec n",
      (ib["ic_haut"] - ib["ic_bas"]) < (ia["ic_haut"] - ia["ic_bas"]))
    v("... et il est reproductible", intervalle(a, 2000, 1) == ia)
    v("deux valeurs ne suffisent pas", intervalle([0.6, 0.7])["exploitable"] is False)

    # -- au_dessus_du_hasard : les DEUX sens, et le cas a l'envers.
    v("un intervalle franchement haut est au-dessus du hasard",
      au_dessus_du_hasard({"exploitable": True, "ic_bas": 0.6, "ic_haut": 0.8}))
    v("un intervalle qui contient 0,5 ne l'est pas",
      not au_dessus_du_hasard({"exploitable": True, "ic_bas": 0.45, "ic_haut": 0.7}))
    # ⚠⚠ Le cas qui distingue « lisible » de « lisible a l'envers » : un intervalle
    # entierement SOUS 0,5 ne doit surtout pas passer pour un succes.
    v("un intervalle entierement sous 0,5 n'est PAS au-dessus du hasard",
      not au_dessus_du_hasard({"exploitable": True, "ic_bas": 0.1, "ic_haut": 0.3}))
    v("un intervalle inexploitable non plus",
      not au_dessus_du_hasard({"exploitable": False}))

    # -- melanger : detruit le signal, garde les non couverts en place.
    base = np.zeros((64, 64), dtype=np.float64)
    verite = np.zeros((64, 64), dtype=bool)
    verite[::2, :] = True
    base[verite] = 5.0
    base[:4, :] = np.nan
    m = melanger(base)
    v("le melange garde les non couverts a leur place",
      np.array_equal(np.isnan(m), np.isnan(base)))
    v("... et conserve les valeurs, seulement permutees",
      sorted(m[np.isfinite(m)].tolist()) == sorted(base[np.isfinite(base)].tolist()))
    # ⚠ La propriete qui en fait un temoin : il DETRUIT l'AUC.
    couvert = np.isfinite(base)
    v("... et il ramene l'AUC au hasard",
      abs(auc(m[couvert], verite[couvert]) - 0.5) < 0.15,
      f"{auc(m[couvert], verite[couvert]):.3f} contre "
      f"{auc(base[couvert], verite[couvert]):.3f}")
    v("... alors que la carte d'origine est loin du hasard",
      auc(base[couvert], verite[couvert]) > 0.9)

    print(f"{'ALL PASS' if echecs == 0 else 'ECHEC'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--json", type=Path)
    p.add_argument("--tirages", type=int, default=4000)
    a = p.parse_args()
    if a.verifier:
        return verifier()
    m = mesurer(tirages=a.tirages)
    if not m["echelles"]:
        print("aucune carte — rien a mesurer", file=sys.stderr)
        return 2
    rapporter(m)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(m, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"\n→ {a.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
