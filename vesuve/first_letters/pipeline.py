"""Le pipeline First Letters : une zone de 4 cm² sur un rouleau où rien n'a été lu, rendue, encrée, et
accompagnée de ce qui la rend crédible.

Le prix : dix lettres dans 4 cm², une image programmatique statique, barre d'échelle de 1 cm, nommée
d'après son maillage, les rangées annotées, l'encre sur un rendu où les fibres se voient, et la preuve que
le texte n'est pas halluciné. Humain dans la boucle permis : ce pipeline ne lit AUCUNE lettre, il rend ce
qu'un œil devra lire, et il dit ce que valent ses témoins.

    F0 l'objet        éligible ? et à quel régime de scan (nombre de Fresnel)
    F1 la surface     la pile de couches et le maillage
    F2 la fenêtre     4 cm² choisis sur la seule couverture de papyrus, et une région tenue à l'écart
    F3 les fibres     la couche médiane étirée : le rendu où les fibres se voient
    F4 sans modèle    la projection maximale des couches centrales : « l'encre visible sans modèle »
    F5 le modèle      une carte d'encre (fournie, ou inférée avec --modele)
    F6 les témoins    les rangées contre le mélange, la région tenue à l'écart, le recouvrement d'entraînement
    F7 l'emballage    les images nommées d'après le maillage, et ce qui reste à faire par un humain
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import numpy as np
from PIL import Image

from vesuve import catalogue, images
from vesuve.rapport import Rapport
from vesuve.rendu import couches, fenetres, rangees
from vesuve.rendu.modele import COUCHES, EncreIndisponible, charger, inferer, la_pile

LA_GRAINE_DU_MELANGE = 20260924


def _nom_du_maillage(surface: Path) -> str:
    return Path(surface).name.removesuffix(".tifxyz")


def _encre_en_octets(carte: np.ndarray) -> np.ndarray:
    """Des logits en 0..255 par la sigmoïde, 0 hors de ce qui est vu (NaN)."""
    p = 1.0 / (1.0 + np.exp(-np.nan_to_num(carte, nan=-50.0)))
    return np.where(np.isfinite(carte), np.clip(p * 254 + 1, 1, 255), 0).astype(np.uint8)


def _superposer_lencre(fibres: np.ndarray, encre: np.ndarray, trace: np.ndarray | None) -> Image.Image:
    base = np.stack([fibres] * 3, axis=-1).astype(np.float32)
    a = (encre.astype(np.float32) / 255.0)[..., None]
    rouge = np.array([255.0, 70.0, 40.0])
    out = base * (1 - 0.65 * a) + rouge * 0.65 * a
    if trace is not None:
        out[trace] = [80, 200, 255]
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGB")


def _temoin_de_rangees(encre: np.ndarray, papyrus: np.ndarray) -> dict:
    b = rangees.binariser_encre(encre, papyrus & (encre > 0))
    m = papyrus & (encre > 0)
    reel = rangees.interligne(b, m)
    melange = rangees.interligne(rangees.melanger(b, m, LA_GRAINE_DU_MELANGE), m)
    return {"le_reel": reel, "le_melange": melange, "binaire": b, "masque": m}


def lancer(dossier_des_couches: Path, surface: Path, rouleau: str, sortie: Path = Path("sorties/first-letters"),
           cote_mm: float = 20.0, modele: Path | None = None, carte: Path | None = None,
           etiquettes: Path | None = None, journal=None) -> Rapport:
    sortie, nom = Path(sortie), _nom_du_maillage(surface)
    r = Rapport("first-letters", {"les_couches": str(dossier_des_couches), "la_surface": str(surface),
                                  "le_rouleau": rouleau, "le_cote_mm": cote_mm,
                                  "le_modele": str(modele) if modele else None,
                                  "la_carte": str(carte) if carte else None}, journal)
    v = catalogue.le_volume("first-letters", rouleau)

    with r.etage("F0", "l'objet et son régime") as e:
        if v is None:
            e.arreter(f"{rouleau} n'est pas un des 23 rouleaux de First Letters")
        else:
            f = e.appliquer("F31", v.pixel_um, v.distance_m, v.energie_kev, pixel_um=v.pixel_um,
                            distance_m=v.distance_m, energie_kev=v.energie_kev)
            p = catalogue.LA_PRODUCTION
            fp = e.appliquer("F31", p.pixel_um, p.distance_m, p.energie_kev, regime="production",
                             pixel_um=p.pixel_um, distance_m=p.distance_m, energie_kev=p.energie_kev)
            e.noter(le_volume=v.volume, le_rapport_au_regime_de_production=round(f / fp, 3),
                    la_consequence=("un scan de repérage : les modèles d'encre publiés ont été entraînés au régime "
                                    "de production, et au régime du prix leur accord avec la carte publiée est plat "
                                    "(`R1-F20`). Leur sortie ici est une vue, pas une preuve."))
    if r.arrete:
        r.ecrire(sortie)
        return r

    with r.etage("F1", "la surface") as e:
        fs = couches.les_couches(dossier_des_couches)
        milieu = len(fs) // 2
        a = couches.la_couche(fs[milieu])
        papyrus = couches.le_papyrus(a)
        e.noter(les_couches=len(fs), la_couche_mediane=milieu, la_forme=list(a.shape), le_type=str(a.dtype),
                la_part_de_papyrus=round(float(papyrus.mean()), 4), le_maillage=nom,
                le_maillage_existe=(Path(surface) / "x.tif").exists())

    cote = int(round(cote_mm * 1000.0 / v.pixel_um))
    with r.etage("F2", "la fenêtre de 4 cm²") as e:
        f = fenetres.la_meilleure_fenetre(papyrus, cote)
        if f is None:
            cote = (min(papyrus.shape) // 16) * 16
            f = fenetres.la_meilleure_fenetre(papyrus, cote)
            e.partiel(f"la surface ne porte pas {cote_mm} mm d'un seul tenant : la plus grande fenêtre carrée fait "
                      f"{cote * v.pixel_um / 1000:.1f} mm de côté ({(cote * v.pixel_um / 1e4) ** 2:.2f} cm²)")
        tenue = fenetres.la_fenetre_tenue_a_lecart(papyrus, cote, f)
        e.noter(le_cote_px=cote, le_cote_mm=round(cote * v.pixel_um / 1000, 2), la_fenetre=f,
                la_fenetre_tenue_a_lecart=tenue,
                la_regle=("choisies sur la SEULE couverture de papyrus, jamais sur l'encre : une fenêtre élue là où "
                          "l'encre paraît forte ferait des lettres avec n'importe quel bruit"))

    def _dans(fe):
        return (fe["r0"], fe["c0"], fe["cote"], fe["cote"])

    with r.etage("F3", "le rendu où les fibres se voient") as e:
        couche_f = couches.la_couche(fs[milieu], _dans(f))
        fibres = np.asarray(images.niveaux(couche_f))
        sortie.mkdir(parents=True, exist_ok=True)
        images.barre_dechelle(Image.fromarray(fibres), v.pixel_um).save(sortie / f"{nom}_fibres.png")
        e.noter(limage=f"{nom}_fibres.png", la_regle="la couche médiane étirée entre 1 et 99 % (`couche_de_rendu.py:35`)")

    with r.etage("F4", "l'encre sans modèle") as e:
        centrales = list(range(max(0, milieu - 3), min(len(fs), milieu + 4)))
        proj = couches.projection_maximale(couches.la_pile(dossier_des_couches, _dans(f), centrales))
        images.barre_dechelle(images.niveaux(proj), v.pixel_um).save(sortie / f"{nom}_sans_modele.png")
        e.noter(limage=f"{nom}_sans_modele.png", les_couches=centrales,
                la_regle=("« sometimes ink is visible directly in the flattened render, with no model at all — usually "
                          "bright areas » : la projection maximale des sept couches centrales. Une vue, pas un détecteur."))

    encre_f = encre_t = None
    with r.etage("F5", "l'encre du modèle", "B3") as e:
        try:
            if carte is not None:
                c = np.load(carte, mmap_mode="r")
                if c.shape != papyrus.shape:
                    raise EncreIndisponible(f"la carte {c.shape} n'a pas la forme de la pile {papyrus.shape}")
                cf = np.asarray(c[f["r0"]:f["r0"] + cote, f["c0"]:f["c0"] + cote])
                ct = np.asarray(c[tenue["r0"]:tenue["r0"] + tenue["cote"], tenue["c0"]:tenue["c0"] + tenue["cote"]]) if tenue else None
                e.noter(la_carte=str(carte), sa_provenance="une carte inférée par ailleurs, fournie avec --carte")
            elif modele is not None:
                m = charger(modele)
                debut = max(0, (len(fs) - COUCHES) // 2)
                cf, n = inferer(la_pile(dossier_des_couches, debut, _dans(f)), m)
                ct = inferer(la_pile(dossier_des_couches, debut, _dans(tenue)), m)[0] if tenue else None
                e.noter(le_modele=str(modele), les_fenetres_balayees=n, les_couches=[debut, debut + COUCHES - 1])
            else:
                raise EncreIndisponible("ni --carte ni --modele : l'encre du modèle n'est pas calculée")
            encre_f, encre_t = _encre_en_octets(cf), (_encre_en_octets(ct) if ct is not None else None)
            e.noter(la_part_vue=round(float(np.isfinite(cf).mean()), 4),
                    la_part_au_dessus_de_0=round(float((np.nan_to_num(cf, nan=-1) > 0).mean()), 4))
        except EncreIndisponible as x:
            e.sauter(str(x))

    with r.etage("F6", "les témoins", "B3") as e:
        if encre_f is None:
            e.sauter("sans carte d'encre, les rangées n'ont rien à mesurer ; les rendus F3 et F4 restent à regarder")
        else:
            papyrus_f = papyrus[f["r0"]:f["r0"] + cote, f["c0"]:f["c0"] + cote]
            encre_f = np.where(papyrus_f, encre_f, 0).astype(np.uint8)  # hors papyrus, le modèle a vu du noir
            t = _temoin_de_rangees(encre_f, papyrus_f)
            trace = rangees.les_rangees(t["binaire"], t["masque"], t["le_reel"])
            _superposer_lencre(fibres, encre_f, trace if trace.any() else None).save(sortie / f"{nom}_encre.png")
            images.barre_dechelle(Image.open(sortie / f"{nom}_encre.png"), v.pixel_um).save(sortie / f"{nom}_encre.png")
            ref = {k: t[k] for k in ("le_reel", "le_melange")}
            if encre_t is not None:
                pt = papyrus[tenue["r0"]:tenue["r0"] + tenue["cote"], tenue["c0"]:tenue["c0"] + tenue["cote"]]
                tt = _temoin_de_rangees(encre_t, pt)
                ref["la_region_tenue_a_lecart"] = tt["le_reel"]
                ref["son_melange"] = tt["le_melange"]
            e.noter(les_rangees=ref, les_rangees_tracees=int(trace.any()),
                    limage=f"{nom}_encre.png",
                    la_regle=("`typographie.py` : l'encre binarisée par Otsu, la densité par rangée autocorrélée, "
                              "périodique quand la netteté dépasse 2√(2 ln k)/√n ; le mélange doit perdre la période"))
            vus = (sorted(p.name.split("_")[0] for p in Path(etiquettes).glob("*_inklabels.png"))
                   if etiquettes is not None and Path(etiquettes).exists() else None)
            ident = re.findall(r"\d{14}", nom)
            e.noter(le_recouvrement_dentrainement=(
                "non vérifiable ici : la liste des étiquettes d'entraînement n'est pas présente" if vus is None else
                ("AUCUN : ce segment n'est pas parmi les %d segments étiquetés du modèle de 2023" % len(vus)
                 if not set(ident) & set(vus) else "⚠ CE SEGMENT EST DANS L'ENTRAÎNEMENT")))

    with r.etage("F7", "l'emballage") as e:
        (sortie / "fenetres.json").write_text(json.dumps({"la_fenetre": f, "la_fenetre_tenue_a_lecart": tenue,
                                                          "le_pixel_um": v.pixel_um}, indent=1))
        e.noter(les_produits=sorted(p.name for p in sortie.glob(f"{nom}_*.png")) + ["fenetres.json"],
                ce_quil_reste_a_un_humain=("lire : compter dix lettres dans la fenêtre, et vérifier qu'elles tiennent "
                                           "sur la région tenue à l'écart. Le pipeline dit où regarder et ce que valent "
                                           "ses témoins ; il ne lit pas."))

    reel = (r.donnees["les_etages"][-2]["sorties"].get("les_rangees") or {}).get("le_reel") or {}
    melange = (r.donnees["les_etages"][-2]["sorties"].get("les_rangees") or {}).get("le_melange") or {}
    r.exigence("un des 23 rouleaux éligibles", "atteinte", f"{rouleau}, volume {v.volume}")
    r.exigence("dix lettres dans 4 cm²", "non mesurée", "aucune lettre n'est lue par ce pipeline : c'est le travail d'un œil")
    r.exigence("une image programmatique statique, nommée d'après son maillage", "atteinte", f"{nom}_encre.png, {nom}_fibres.png")
    r.exigence("barre d'échelle de 1 cm", "atteinte", f"10 mm = {int(round(10000 / v.pixel_um))} px à {v.pixel_um} µm")
    r.exigence("rangées annotées", "atteinte" if reel.get("periodique") else "non atteinte",
               ("sans carte d'encre" if not reel else
                "aucun pic intérieur d'autocorrélation, à aucun angle de ±12° : pas de rangées dans l'encre du modèle"
                if reel.get("periode_px") is None else
                f"interligne {reel['periode_px']} px, netteté {reel['nettete']:.3f} contre un plancher {reel['plancher']:.3f}"))
    r.exigence("encre sur un rendu où les fibres se voient", "atteinte" if encre_f is not None else "non atteinte",
               f"{nom}_encre.png")
    r.exigence("montrer que le texte n'est pas halluciné", "partiel" if reel.get("periodique") and not melange.get("periodique")
               else "non atteinte",
               "le mélange des mêmes pixels perd l'interligne ; la région tenue à l'écart est mesurée à part ; aucune "
               "vérité de terrain sur ce rouleau")
    r.ecrire(sortie)
    return r
