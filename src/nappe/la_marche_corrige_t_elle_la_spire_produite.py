"""Sans le juge, la marche de fenêtre en fenêtre désigne-t-elle où la spire produite a glissé, et la corrige-t-elle ?

⚠⚠⚠ CE FICHIER EST ÉCRIT AVANT QU'UNE SEULE CORRECTION NE SOIT FAITE NI JUGÉE. Ce qui était vu avant d'écrire : tout ce que
`257` à `260` publient, dont les cartes de la différence des marches sur les deux blocs, et leur accord avec le juge.

⭐⭐⭐⭐ POURQUOI CETTE TRANCHE, ET C'EST `R4-P95`. `260` a trouvé une mesure faite du seul scan qui voit où la spire produite
glisse, mais il l'a évaluée avec le juge. Ce qui remplace l'humain du transfert doit se passer du juge : désigner les chunks
qui ont glissé, et les remettre en place.

## La règle, sans le juge

1. LE SIGNE : poussée le long de sa normale, une surface change la marche dans un sens que la rampe RENDUE de `257` fixe, lue de
   fenêtre en fenêtre ; il doit être positif, sinon rien ne suit.
2. L'ANCRE : la médiane, sur le bloc, de la marche de la spire produite moins celle du segment ; la majorité des chunks est
   supposée sur la bonne spire, et c'est une hypothèse.
3. LE SIGNALEMENT : un point de la maille est signalé si l'écart de cette différence à l'ancre, interpolé entre les centres
   des chunks, atteint un demi-feuillet.
4. LA CORRECTION : chaque point signalé est ramené de cet écart le long de la normale du segment, à pleine valeur ; les
   autres ne bougent pas. Puis la spire corrigée est rendue et relue de même.

## Ce qui se mesure, le juge ne servant qu'à juger

Sur chacun des deux blocs : les ratés que le signalement trouve et les justes qu'il accuse ; la part des points notés sur la
bonne spire avant et après la correction ; et la différence des marches relue sur la spire corrigée.

## Les issues, exclusives

- la rampe rendue donne un signe négatif ou nul : rien ne suit ;
- le signalement ne trouve pas les ratés mieux que les justes, sur les deux blocs : la marche ne désigne rien sans le juge ;
- il les trouve, et la correction ne relève la part juste sur aucun bloc : désigner ne suffit pas à corriger ;
- elle la relève sur un bloc au moins : la marche corrige la spire produite là, sans le juge.

⚠⚠ CE QUE CETTE TRANCHE NE DIRA PAS : une boucle, un autre côté, `ps256`, ni ce que vaut l'ancre là où la majorité a raté.

Usage :
    uv run python src/nappe/la_marche_corrige_t_elle_la_spire_produite.py --verifier
    uv run python src/nappe/la_marche_corrige_t_elle_la_spire_produite.py \\
        --json docs/mesures/la_marche_corrige_t_elle_la_spire_produite.json
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src" / "nappe"))
sys.path.insert(0, str(RACINE / "src" / "commun"))

from la_spire_produite_se_lit_elle_dans_le_treillis import (LA_MAILLE, LA_PREDICTION, LE_BLOC,  # noqa: E402
                                                            LE_COTE, LE_COTE_DU_CHUNK, LE_DOSSIER,
                                                            LE_DOSSIER_DE_LA_RAMPE, LES_JUGES, ecrire_tifxyz,
                                                            la_part_retrouvee, laccord_des_paires, le_cadre,
                                                            le_maillage_produit, lerreur_aux_chunks, lerreur_jugee,
                                                            lire_la_pile, rendre)
from la_spire_voisine_est_elle_a_un_pas import (DEMI_PAS_EN_VOXELS, LE_CACHE, LE_SEGMENT,  # noqa: E402
                                                lire_tifxyz, telecharger)
from le_pas_de_fenetre_en_fenetre_voit_il_la_rampe import la_grille, la_marche  # noqa: E402

LES_MESURES = RACINE / "docs" / "mesures"
CE_QUE_260_A_PUBLIE = LES_MESURES / "le_pas_de_fenetre_en_fenetre_voit_il_la_rampe.json"
CE_QUE_257_A_PUBLIE = LES_MESURES / "la_spire_produite_se_lit_elle_dans_le_treillis.json"
LE_PAS_DE_GRILLE = 20


def la_carte_aux_points(carte: np.ndarray, by: int, bx: int, forme: tuple, maille: int = LA_MAILLE,
                        chunk: int = LE_COTE_DU_CHUNK) -> tuple[np.ndarray, np.ndarray]:
    """Une carte donnée aux centres des chunks d'un bloc, portée aux points de la maille DANS le bloc : bilinéaire entre
    les centres, tenue au bord entre le dernier centre et le bord du bloc. Rend la carte sur la maille (NaN hors du bloc
    et là où l'un des centres manque) et le masque des points du bloc."""
    cote = carte.shape[0]
    px = LE_PAS_DE_GRILLE * maille
    out = np.full(forme, np.nan)
    dedans = np.zeros(forme, dtype=bool)
    for i in range(forme[0]):
        y = i * px / chunk - by - 0.5
        if not (-0.5 <= y < cote - 0.5):
            continue
        for j in range(forme[1]):
            x = j * px / chunk - bx - 0.5
            if not (-0.5 <= x < cote - 0.5):
                continue
            dedans[i, j] = True
            yc, xc = min(max(y, 0.0), cote - 1.0), min(max(x, 0.0), cote - 1.0)
            y0, x0 = min(int(np.floor(yc)), cote - 2), min(int(np.floor(xc)), cote - 2)
            q = carte[y0:y0 + 2, x0:x0 + 2]
            if not np.isfinite(q).all():
                continue
            fy, fx = yc - y0, xc - x0
            out[i, j] = (1 - fy) * ((1 - fx) * q[0, 0] + fx * q[0, 1]) + fy * ((1 - fx) * q[1, 0] + fx * q[1, 1])
    return out, dedans


def corriger(tau: np.ndarray, ecart: np.ndarray, seuil: float = DEMI_PAS_EN_VOXELS) -> tuple[np.ndarray, np.ndarray]:
    """La correction de la règle : là où l'écart à l'ancre atteint `seuil`, le point est ramené de cet écart."""
    with np.errstate(invalid="ignore"):
        signale = np.isfinite(ecart) & (np.abs(ecart) >= seuil)
    t = tau.copy()
    t[signale] = tau[signale] - ecart[signale]
    return t, signale


def la_part_juste(tau: np.ndarray, verite: np.ndarray, masque: np.ndarray) -> dict:
    e = tau - verite
    note = masque & np.isfinite(e)
    return {"les_points_notes": int(note.sum()),
            "la_part_sur_la_bonne_spire": round(float((np.abs(e[note]) < DEMI_PAS_EN_VOXELS).mean()), 4) if note.any() else None}


def le_signalement(signale: np.ndarray, rate: np.ndarray, note: np.ndarray) -> dict:
    """Les ratés que le signalement trouve, et les justes qu'il accuse, parmi les points notés du bloc."""
    r, j = note & rate, note & ~rate
    return {"les_rates": int(r.sum()), "les_justes": int(j.sum()),
            "la_part_des_rates_signales": round(float(signale[r].mean()), 4) if r.any() else None,
            "la_part_des_justes_signales": round(float(signale[j].mean()), 4) if j.any() else None}


def le_signe(by: int, bx: int) -> dict:
    """La pente de la marche de fenêtre en fenêtre de la rampe RENDUE de `257`, moins celle du segment, contre la rampe."""
    d = json.loads(CE_QUE_257_A_PUBLIE.read_text())
    rampe = la_grille(d["les_cartes"]["la_rampe"])
    mz = la_marche(lire_la_pile(LE_DOSSIER / LE_DOSSIER_DE_LA_RAMPE / f"bloc_{by}_{bx}"), by, bx)
    ms = la_marche(lire_la_pile(LE_DOSSIER / "le_segment_reduit" / f"bloc_{by}_{bx}"), by, bx)
    return la_part_retrouvee(mz["la_profondeur"], ms["la_profondeur"], rampe)


def mesurer(cache: Path = LE_CACHE) -> dict:
    debut = time.monotonic()
    d260 = json.loads(CE_QUE_260_A_PUBLIE.read_text())
    b7 = d260["les_blocs"]["le_bloc_de_257"]
    out = {"le_signe": le_signe(b7["la_rangee"], b7["la_colonne"]), "les_blocs": {}}
    if not out["le_signe"].get("decidable") or out["le_signe"]["la_pente"] <= 0.0:
        return {**out, "decidable": True}
    dd = telecharger(LE_SEGMENT, cache)
    ref, valide, esp = lire_tifxyz(dd)
    tau = np.load(cache / f"transfert_suivante_{LE_SEGMENT}_{LA_PREDICTION}_{LE_COTE}.npy")
    juges = [np.load(cache / f"verite_{LE_SEGMENT}_{j}_{LE_COTE}.npy") for j in LES_JUGES]
    err = lerreur_jugee(tau, juges)
    verite = tau - err
    ms_cache = {}
    for nom, b in d260["les_blocs"].items():
        by, bx = b["la_rangee"], b["la_colonne"]
        diff = la_grille(b["les_cartes"]["la_difference"])
        ancre = float(np.nanmedian(diff))
        ecart, dedans = la_carte_aux_points(diff - ancre, by, bx, tau.shape)
        tau_c, signale = corriger(tau, np.where(dedans, ecart, np.nan))
        note = dedans & np.isfinite(err)
        with np.errstate(invalid="ignore"):
            rate = np.abs(err) >= DEMI_PAS_EN_VOXELS
        r = {"la_rangee": by, "la_colonne": bx, "lancre_voxels": round(ancre, 4),
             "les_points_du_bloc": int(dedans.sum()), "les_points_signales": int((signale & dedans).sum()),
             "le_signalement": le_signalement(signale, rate, note),
             "avant": la_part_juste(tau, verite, dedans), "apres": la_part_juste(tau_c, verite, dedans)}
        with np.errstate(invalid="ignore"):
            e_c = tau_c - verite
            r["les_rates_rendus_justes"] = int((note & rate & (np.abs(e_c) < DEMI_PAS_EN_VOXELS)).sum())
            r["les_justes_rendus_rates"] = int((note & ~rate & (np.abs(e_c) >= DEMI_PAS_EN_VOXELS)).sum())
        pc, vc = le_maillage_produit(ref, valide, tau_c)
        tif = ecrire_tifxyz(LE_DOSSIER / f"la_spire_corrigee_{by}_{bx}" / "maillage", pc, vc,
                            1.0 / (esp * LA_MAILLE), "la_spire_corrigee")
        sortie = LE_DOSSIER / f"la_spire_corrigee_{by}_{bx}" / f"bloc_{by}_{bx}"
        rendu = rendre(tif, sortie, le_cadre(by, bx, LE_BLOC))
        r["le_rendu"] = rendu
        if rendu["rendue"]:
            if nom not in ms_cache:
                ms_cache[nom] = la_marche(lire_la_pile(LE_DOSSIER / "le_segment_reduit" / f"bloc_{by}_{bx}"), by, bx)
            mc = la_marche(lire_la_pile(sortie), by, bx)
            diff_c = mc["la_profondeur"] - ms_cache[nom]["la_profondeur"]
            e_ch = lerreur_aux_chunks(np.where(np.isfinite(e_c), e_c, np.nan), by, bx, LE_BLOC)
            r["relue"] = {"lecart_type_de_la_difference_avant": round(float(np.nanstd(diff)), 4),
                          "lecart_type_de_la_difference_apres": round(float(np.nanstd(diff_c)), 4),
                          "laccord_des_paires_avec_lerreur_restante": laccord_des_paires(diff_c, e_ch)}
            r["les_cartes"] = {k: [[None if not np.isfinite(x) else round(float(x), 2) for x in rr] for rr in a]
                               for k, a in (("la_difference_avant", diff), ("la_difference_apres", diff_c),
                                            ("lerreur_avant", la_grille(b["les_cartes"]["lerreur"])),
                                            ("lerreur_apres", e_ch))}
        out["les_blocs"][nom] = r
    out["les_secondes"] = round(time.monotonic() - debut, 1)
    out["decidable"] = True
    return out


def le_verdict(r: dict) -> dict:
    s = r.get("le_signe") or {}
    if not s.get("decidable") or s["la_pente"] <= 0.0:
        return {"lissue": "la rampe rendue donne un signe négatif ou nul : rien ne suit"}
    blocs = r["les_blocs"].values()
    trouve = [b["le_signalement"] for b in blocs
              if (b["le_signalement"].get("la_part_des_rates_signales") or 0.0)
              > (b["le_signalement"].get("la_part_des_justes_signales") or 0.0)]
    if not trouve:
        return {"lissue": "le signalement ne trouve pas les ratés mieux que les justes : la marche ne désigne rien sans le juge"}
    releve = [n for n, b in r["les_blocs"].items()
              if (b["apres"]["la_part_sur_la_bonne_spire"] or 0.0) > (b["avant"]["la_part_sur_la_bonne_spire"] or 0.0)]
    if not releve:
        return {"lissue": "il les trouve, et la correction ne relève la part juste sur aucun bloc : désigner ne suffit pas à "
                          "corriger"}
    return {"lissue": f"elle la relève sur {', '.join(releve)} : la marche corrige la spire produite là, sans le juge"}


def verifier() -> int:
    echecs, faits = [], 0

    def v(nom, ok, detail=""):
        nonlocal faits
        faits += 1
        try:
            res = ok() if callable(ok) else ok
        except Exception as exc:  # noqa: BLE001
            echecs.append(f"{nom} — LEVÉE {type(exc).__name__}: {exc}")
            return
        if not res:
            echecs.append(f"{nom}{(' — ' + detail) if detail else ''}")

    # La carte aux points : une carte linéaire aux centres des chunks se retrouve aux points de la maille.
    carte = np.add.outer(np.arange(16.0), 10.0 * np.arange(16.0))
    au, dedans = la_carte_aux_points(carte, 16, 32, (60, 60))
    ii, jj = np.nonzero(dedans)
    y = ii * 160 / 128 - 16 - 0.5
    x = jj * 160 / 128 - 32 - 0.5
    attendu = np.clip(y, 0, 15) + 10.0 * np.clip(x, 0, 15)
    v("★★★★ une carte aux centres des chunks se retrouve, interpolée, aux points de la maille du bloc",
      lambda: dedans.sum() > 100 and np.allclose(au[ii, jj], attendu), str(dedans.sum()))
    v("★★★ hors du bloc, rien", lambda: np.isnan(au[~dedans]).all() and not dedans[:10].any())
    v("★★★ les points du bloc sont ceux dont le pixel tombe dans le bloc",
      lambda: all(16 * 128 <= i * 160 < 32 * 128 and 32 * 128 <= j * 160 < 48 * 128 for i, j in zip(ii, jj)))
    tau = np.full((5, 5), 72.0)
    ecart = np.zeros((5, 5))
    ecart[1, 1], ecart[2, 2], ecart[3, 3] = 40.0, -50.0, 20.0
    tc, sg = corriger(tau, ecart)
    v("★★★★ seuls les points à un demi-feuillet ou plus sont ramenés, de leur écart",
      lambda: tc[1, 1] == 32.0 and tc[2, 2] == 122.0 and tc[3, 3] == 72.0 and sg.sum() == 2)
    # Un cas fabriqué où la différence suit l'erreur : la correction ramène les ratés sur la bonne spire.
    verite = np.full((5, 5), 72.0)
    tau2 = verite + np.where(np.arange(25).reshape(5, 5) % 5 == 0, -60.0, 3.0)
    t2, s2 = corriger(tau2, (tau2 - verite) - np.median(tau2 - verite))
    v("★★★★ quand la différence suit l'erreur et que la majorité est juste, la correction relève la part juste",
      lambda: la_part_juste(t2, verite, np.ones((5, 5), bool))["la_part_sur_la_bonne_spire"] == 1.0
      and la_part_juste(tau2, verite, np.ones((5, 5), bool))["la_part_sur_la_bonne_spire"] == 0.8)
    t3, _ = corriger(tau2, np.full((5, 5), 50.0))
    v("★★★ et une différence qui ne suit pas l'erreur peut la ruiner",
      lambda: la_part_juste(t3, verite, np.ones((5, 5), bool))["la_part_sur_la_bonne_spire"] < 0.8)
    rate = np.zeros((4, 4), bool)
    rate[:2] = True
    sig = np.zeros((4, 4), bool)
    sig[0] = True
    sig[3, 0] = True
    s = le_signalement(sig, rate, np.ones((4, 4), bool))
    v("★★★★ le signalement compte les ratés trouvés et les justes accusés",
      lambda: s["la_part_des_rates_signales"] == 0.5 and s["la_part_des_justes_signales"] == 0.125)
    base = {"le_signe": {"decidable": True, "la_pente": 0.4},
            "les_blocs": {"a": {"le_signalement": {"la_part_des_rates_signales": 0.1, "la_part_des_justes_signales": 0.3},
                                "avant": {"la_part_sur_la_bonne_spire": 0.6}, "apres": {"la_part_sur_la_bonne_spire": 0.7}}}}
    v("★★★★ un signalement qui accuse plus de justes que de ratés arrête tout, même si la part monte",
      lambda: "ne désigne rien" in le_verdict(base)["lissue"])
    v("★★★ un signe négatif arrête tout",
      lambda: "rien ne suit" in le_verdict({"le_signe": {"decidable": True, "la_pente": -0.2}, "les_blocs": {}})["lissue"])

    for x in echecs:
        print(f"  ÉCHEC {x}")
    print(f"{Path(__file__).name}   {'ALL PASS' if not echecs else 'DES SONDES ONT ÉCHOUÉ'} "
          f"({len(echecs)} failures, {faits} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--json", type=Path)
    a = p.parse_args()
    if a.verifier:
        return verifier()
    r = mesurer()
    r["le_verdict"] = le_verdict(r)
    texte = json.dumps(r, indent=1, ensure_ascii=False)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(texte + "\n")
    print(json.dumps({"le_signe": r.get("le_signe"), "le_verdict": r.get("le_verdict"),
                      **{n: {k: b.get(k) for k in ("lancre_voxels", "le_signalement", "avant", "apres")}
                         for n, b in r.get("les_blocs", {}).items()}}, ensure_ascii=False))
    return 0 if r.get("decidable") else 2


if __name__ == "__main__":
    raise SystemExit(main())
