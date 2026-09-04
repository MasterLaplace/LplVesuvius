#!/usr/bin/env python3
"""Que rend le détecteur sur une face VIERGE ? — le nul propre, dans la même pile.

⚠⚠⚠ POURQUOI CE FICHIER EXISTE, ET POURQUOI IL EST URGENT. `46` produit un témoin négatif
sur une surface posée **en travers** de l'empilement — donc sans face de papyrus du tout — et
le détecteur y rend **plus** de dispersion que sur une face. Tant qu'on ne sait pas ce qu'il
rend sur une face **vierge**, la phrase « l'encre valide le déroulage » n'est pas utilisable :
un détecteur qui répond pareil au papyrus écrit et au papyrus nu ne valide rien.

⭐⭐⭐ ET LE NUL EST DANS LA MÊME PILE, ce qui supprime tout ce qu'un second rendu ferait
varier. Les `layers-zarr` publiés de `PHerc0139` font **109 couches** (mesuré :
`shape [109, 23280, 32160]`, chunks `[109, 128, 128]` — un morceau est une colonne pleine
profondeur), là où le détecteur n'en lit que **26**. Décaler `--start-layer` suffit donc : même
volume, même segment, même région, même modèle, même pas. Un seul paramètre bouge, et c'est la
conception appariée que `46` réclame.

⭐⭐ LE DÉCALAGE EST MESURÉ, PAS CHOISI. `depth_profile.py` rend le contraste local par couche —
il pique là où les fibres sont nettes, donc à la surface. Sur `w046` : pic **normalisé à 1,000
à la couche 56**, puis chute monotone jusqu'à **0,000 à la couche 100**. La fenêtre nulle est
prise **là où le contraste est le plus bas**, et non à un demi-pas supposé : un demi-pas
nominal peut tomber sur la spire voisine, un minimum mesuré ne le peut pas.

⚠ CE QUE CE CONTRÔLE NE PEUT PAS FAIRE, et `46` le dit déjà de lui-même : à ce pas de balayage
la carte est trop petite pour porter une **typographie**. On compare le **niveau** et la
**dispersion** de la prédiction, jamais son interligne. Prétendre le contraire serait mesurer
du bruit.

⚠⚠⚠ ET IL NE PEUT PAS ÉCARTER LA SPIRE VOISINE, pour une raison **structurelle** et non par
négligence. Le creux mesuré s'étend de la couche ~88 à ~107, soit **une vingtaine de couches**,
et le détecteur en lit **26** : aucune fenêtre de sa taille ne tient entièrement dans le vide.
La fenêtre nulle frôle donc nécessairement la remontée de contraste du voisin (0,096 à la
couche 108). Une troisième fenêtre ne trancherait pas — elle n'existe pas.

⚠ Ce que la corrélation entre les deux cartes établit, et rien de plus : à **+0,001**, la carte
du vide n'est **pas un décalque** de celle de la face, donc ce n'est pas une transparence de la
même colonne. Elle ne dit **rien** de la spire voisine, dont l'encre n'a aucune raison de tomber
là où celle de cette face-ci tombe. J'ai failli écrire l'inverse.

Usage :
    uv run python src/encre/le_nul_verso.py --segment 20260325000000-w046_20260325 \\
        --json docs/mesures/le_nul_verso.json
    uv run python src/encre/le_nul_verso.py --verifier
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
EXTRACTEUR = RACINE / "src" / "volume" / "zarr_vers_couches.py"
PROFIL = RACINE / "src" / "volume" / "depth_profile.py"
INFERENCE = RACINE / "src" / "xpu" / "infer_ink.py"
MODELE = RACINE / "data" / "models" / "timesformer_GP_scroll1"
DEFAUT_JSON = RACINE / "docs" / "mesures" / "le_nul_verso.json"

COUCHES_LUES = 26
"""Ce que le détecteur GP-2023 lit d'une pile (`12` §1, `09` §12). ⚠ C'est une propriété du
modèle, pas un réglage : les deux fenêtres doivent en lire **le même nombre**, sinon on
comparerait deux quantités d'information."""

SURFACE_DANS_LA_FENETRE = 17
"""Où tombe la surface dans la fenêtre du détecteur, en couches depuis son début.

⚠ Dérivé de la convention publiée et non posé : `12` établit qu'une pile de 65 couches porte la
surface à la **32** et que le détecteur lit **15 à 40** — donc la surface est à la 17ᵉ des 26.
La reprendre telle quelle est ce qui rend notre fenêtre « sur face » comparable à la leur."""


def _lancer(argv: list[str], timeout: float = 7200.0) -> tuple[int, str]:
    r = subprocess.run(argv, capture_output=True, text=True, cwd=RACINE, timeout=timeout)
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def profil_de_profondeur(couches: Path, taille: int) -> list[float] | None:
    """
    @brief Le contraste local par couche, normalisé — d'où sont la face et le vide.

    ⚠ Appelé, jamais réécrit : `depth_profile.py` porte déjà les deux profils et la raison de
    préférer le **contraste** à l'intensité (« le papyrus est épais » — l'intensité voit la
    matière, le contraste voit la structure, et c'est la structure qui localise la face).
    """
    code, sortie = _lancer(["uv", "run", "python", str(PROFIL), str(couches),
                            "--top", "0", "--left", "0", "--size", str(taille)], 1800)
    if code != 0:
        return None
    valeurs: list[tuple[int, float]] = []
    for ligne in sortie.splitlines():
        m = ligne.split()
        if len(m) >= 4 and m[0] == "couche" and m[2] == "contraste":
            try:
                valeurs.append((int(m[1]), float(m[3])))
            except ValueError:
                continue
    if not valeurs:
        return None
    return [v for _, v in sorted(valeurs)]


def fenetres(profil: list[float]) -> dict:
    """
    @brief Les deux `--start-layer` : sur la face, et dans le vide le plus creux.

    ⚠⚠ LA FENÊTRE NULLE EST CHOISIE PAR LE MINIMUM DE CONTRASTE MOYEN, pas par un demi-pas
    nominal. Un demi-pas suppose un empilement régulier ; un minimum mesuré ne suppose rien, et
    il tombe là où il n'y a effectivement pas de structure.

    ⚠ Les deux fenêtres lisent `COUCHES_LUES` couches et restent dans la pile. Une fenêtre qui
    déborderait lirait des zéros de bord, ce qui ferait passer un artefact de découpe pour une
    absence d'encre.
    """
    n = len(profil)
    if n < COUCHES_LUES + 4:
        return {}
    pic = max(range(n), key=lambda i: profil[i])
    debut_face = max(0, min(n - COUCHES_LUES, pic - SURFACE_DANS_LA_FENETRE))

    def moyenne(d: int) -> float:
        return float(np.mean(profil[d:d + COUCHES_LUES]))

    candidats = [d for d in range(0, n - COUCHES_LUES + 1)
                 # ⚠ La fenêtre nulle ne doit pas CHEVAUCHER celle de la face, sinon elle
                 # lirait la face elle-même et le contrôle serait circulaire.
                 if d >= debut_face + COUCHES_LUES or d + COUCHES_LUES <= debut_face]
    if not candidats:
        return {}
    debut_nul = min(candidats, key=moyenne)
    return dict(pic=pic, debut_face=debut_face, debut_nul=debut_nul,
                contraste_face=moyenne(debut_face), contraste_nul=moyenne(debut_nul),
                couches=n)


def _inference(couches: Path, debut: int, taille: int, sortie: Path) -> dict | None:
    code, texte = _lancer(
        ["uv", "run", "python", str(INFERENCE), str(couches), "--model", str(MODELE),
         "--start-layer", str(debut), "--top", "0", "--left", "0",
         "--height", str(taille), "--width", str(taille), "--stride", "21",
         "--device", "cpu", "--sans-progression", "--out", str(sortie)], 7200)
    if code != 0:
        return {"echec": texte.strip().splitlines()[-1][:150] if texte.strip() else "?"}
    # ⚠ Motif ANCRE sur le libellé complet : ce dépôt a déjà payé un grep laxiste qui attrapait
    # deux valeurs d'une même ligne.
    import re
    m = re.search(r"encre\s+min/med/max:\s*(-?[\d.]+)\s*/\s*(-?[\d.]+)\s*/\s*(-?[\d.]+)", texte)
    c = re.search(r"pixels couverts\s*:\s*(\d+)\s*/\s*(\d+)", texte)
    if not m:
        return {"echec": "sortie illisible"}
    return dict(minimum=float(m.group(1)), mediane=float(m.group(2)), maximum=float(m.group(3)),
                couverts=int(c.group(1)) if c else None,
                total=int(c.group(2)) if c else None, sortie=str(sortie))


CARTES = RACINE / "docs" / "mesures" / "nul_verso_cartes"


def deriver_des_cartes(segment: str) -> dict:
    """
    @brief Ce que les deux cartes disent l'une de l'autre — sans refaire l'inférence.

    ⚠⚠ SÉPARÉ DE `mesurer` PARCE QUE L'INFÉRENCE COÛTE HUIT MINUTES. Les cartes sont gardées et
    déterministes, donc tout ce qui s'en dérive doit pouvoir être recalculé sans les refaire ;
    sinon la moindre grandeur ajoutée coûte une campagne, et on finit par les calculer au
    terminal — la dette que ce dépôt rembourse en boucle.
    """
    try:
        fa = np.load(CARTES / f"{segment}_face.npy")
        nu = np.load(CARTES / f"{segment}_nul.npy")
    except OSError:
        return {}
    bons = np.isfinite(fa) & np.isfinite(nu)
    if bons.sum() < 1000:
        return {}
    a1, b1 = fa[bons].ravel(), nu[bons].ravel()
    return dict(
        correlation_face_nul=float(np.corrcoef(a1, b1)[0, 1]),
        # ⚠ « Combien du vide se lit comme de l'encre » : la part du nul au-dessus de la MÉDIANE
        # de la face. Le seuil vient de la face et non du nul, sinon il suivrait ce qu'on mesure.
        part_nul_au_dessus_mediane_face=float((b1 > float(np.median(a1))).mean()),
        pixels_compares=int(bons.sum()))


def mesurer(segment: str, zarr: str, top: int, left: int, taille: int = 512) -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        couches = Path(tmp) / "couches"
        code, texte = _lancer(
            ["uv", "run", "python", str(EXTRACTEUR), zarr, "--sortie", str(couches),
             "--top", str(top), "--left", str(left),
             "--hauteur", str(taille), "--largeur", str(taille)], 3600)
        if code != 0:
            raise SystemExit(f"extraction échouée : {texte.strip()[-200:]}")
        profil = profil_de_profondeur(couches, taille)
        if not profil:
            raise SystemExit("profil de profondeur illisible")
        f = fenetres(profil)
        if not f:
            raise SystemExit("pile trop courte pour deux fenêtres disjointes")
        # ⚠⚠ LES CARTES SONT GARDÉES, et c'est `--out` qui écrit un `.npy` : les valeurs
        # BRUTES, pas une image déjà normalisée. Une figure qui rendrait chaque carte à sa
        # propre échelle ferait passer le bruit du nul pour de l'encre — c'est précisément la
        # panne que ce contrôle existe pour montrer, donc l'échelle doit être commune, donc il
        # faut les valeurs.
        CARTES.mkdir(parents=True, exist_ok=True)
        face = _inference(couches, f["debut_face"], taille, CARTES / f"{segment}_face.npy")
        nul = _inference(couches, f["debut_nul"], taille, CARTES / f"{segment}_nul.npy")
    out = dict(segment=segment, zarr=zarr, top=top, left=left, taille=taille,
               profil=profil, **f, face=face, nul=nul)
    # ⚠⚠⚠ LA FIGURE MONTRE CE QUE LES RESUMES NE DISENT PAS : le vide est sombre DANS
    # L'ENSEMBLE mais porte des taches vives, indiscernables d'encre a l'oeil. C'est ce qui
    # explique une etendue qui ne s'effondre pas, et ca ouvre une question que les mediane et
    # etendue ne peuvent pas trancher.
    #
    # ⭐⭐ DEUX LECTURES POSSIBLES, ET ELLES SE SEPARENT PAR UNE CORRELATION. Soit ce sont des
    # FAUX POSITIFS -- le detecteur invente de la structure dans du vide -- soit c'est la
    # SPIRE VOISINE vue au travers, la fenetre nulle la frolant par le bas de la pile. Si les
    # taches du vide tombent la ou la face en a, la seconde lecture est la bonne et le
    # detecteur voit a travers ; si elles sont ailleurs, ce sont des faux positifs.
    if face and nul and not face.get("echec") and not nul.get("echec"):
        out.update(deriver_des_cartes(segment))
        # ⚠⚠ L'ÉTENDUE, PAS LA MÉDIANE. `46` compare le **niveau** ET la **dispersion** ; une
        # médiane seule est satisfaite par un détecteur qui rend la même valeur partout, ce qui
        # est exactement la panne qu'on cherche.
        out["etendue_face"] = face["maximum"] - face["minimum"]
        out["etendue_nul"] = nul["maximum"] - nul["minimum"]
        out["rapport_etendue"] = out["etendue_nul"] / max(1e-9, out["etendue_face"])
    return out


def _verifier(r: dict | None = None) -> int:
    echecs = comptees = 0

    def v(nom, ok, detail=""):
        nonlocal echecs, comptees
        comptees += 1
        print(f"  {'ok  ' if ok else 'FAIL'}  {nom}" + (f"   [{detail}]" if detail else ""))
        if not ok:
            echecs += 1

    # ⚠⚠ LE CHOIX DES FENÊTRES, testé sur un profil FABRIQUÉ dont on connaît la réponse : une
    # face nette au milieu, un vide franc plus bas. Sans ce contrôle, « la fenêtre nulle est
    # dans le vide » serait une intention.
    faux = [0.2] * 109
    for i in range(50, 63):
        faux[i] = 1.0 - abs(i - 56) * 0.07
    for i in range(88, 109):
        faux[i] = 0.01
    f = fenetres(faux)
    v("la fenêtre sur face est centrée sur le pic de contraste",
      f["pic"] == 56 and f["debut_face"] == 56 - SURFACE_DANS_LA_FENETRE,
      f"pic {f['pic']}, début {f['debut_face']}")
    v("... et la fenêtre nulle tombe dans le creux mesuré",
      f["debut_nul"] >= 83, f"début {f['debut_nul']}, contraste {f['contraste_nul']:.3f}")
    v("... et elle ne chevauche PAS celle de la face",
      f["debut_nul"] >= f["debut_face"] + COUCHES_LUES
      or f["debut_nul"] + COUCHES_LUES <= f["debut_face"],
      f"{f['debut_face']}..{f['debut_face'] + COUCHES_LUES} contre "
      f"{f['debut_nul']}..{f['debut_nul'] + COUCHES_LUES}")
    v("... et les deux restent dans la pile",
      f["debut_face"] >= 0 and f["debut_nul"] + COUCHES_LUES <= len(faux),
      f"pile de {len(faux)}")
    v("... et la face a bien plus de contraste que le nul",
      f["contraste_face"] > 2 * f["contraste_nul"],
      f"{f['contraste_face']:.3f} contre {f['contraste_nul']:.3f}")
    # ⚠⚠ Une pile trop courte pour deux fenêtres disjointes rend {} plutôt qu'un chevauchement.
    # ⚠ Écrit d'abord avec un `or True` qui le rendait incapable d'échouer — le défaut que ce
    # dépôt attrape en boucle, commis ici dans le fichier qui existe pour un contrôle.
    v("une pile trop courte ne rend AUCUNE fenêtre plutôt que deux qui se chevauchent",
      fenetres([0.5] * 30) == {}, str(fenetres([0.5] * 30)))
    court = fenetres([0.5] * 40)
    v("... et si elle en rend deux, elles restent disjointes",
      not court or court["debut_nul"] >= court["debut_face"] + COUCHES_LUES
      or court["debut_nul"] + COUCHES_LUES <= court["debut_face"], str(court))

    if r and r.get("face") and r.get("nul"):
        print("\net la mesure")
        f_, n_ = r["face"], r["nul"]
        v("les deux fenêtres ont rendu une carte",
          not f_.get("echec") and not n_.get("echec"),
          f"{f_.get('echec') or 'ok'} / {n_.get('echec') or 'ok'}")
        if not f_.get("echec") and not n_.get("echec"):
            # ⚠⚠⚠ LE RÉSULTAT, ÉCRIT POUR TOMBER DANS LES DEUX SENS. Si le nul rend autant de
            # dispersion que la face, « l'encre valide le déroulage » n'est pas utilisable ;
            # s'il en rend nettement moins, le détecteur distingue une face vierge d'une face
            # écrite, et c'est ce qu'il fallait établir. Les deux sont publiables.
            # ⚠⚠⚠ MESURÉ, ET C'EST LA BRANCHE ALARMANTE. Le contrôle demandait si la
            # dispersion s'effondre sur une face vierge. Elle ne s'effondre PAS : rapport 0,94
            # sur une fenêtre dont le contraste local est QUATORZE fois plus bas. Donc « il y a
            # de la structure ici » ne discrimine pas, et `46` avait raison de s'en inquiéter.
            v("la dispersion NE s'effondre PAS sur la face vierge",
              r["rapport_etendue"] > 0.8,
              f"étendue nulle {r['etendue_nul']:.3f} contre face {r['etendue_face']:.3f} "
              f"— rapport {r['rapport_etendue']:.2f}, contraste local "
              f"{r['contraste_face']:.3f} contre {r['contraste_nul']:.3f}")
            # ⚠⚠ ET L'AUTRE MOITIÉ, QUI SAUVE LE DÉTECTEUR SUR UN AUTRE CANAL. Le NIVEAU, lui,
            # se déplace franchement : la médiane passe de -0,272 à -1,502. Une lecture par
            # SEUIL distingue donc les deux, là où une lecture par structure ne le peut pas.
            # Les deux assertions ensemble sont le résultat ; l'une sans l'autre le déforme.
            saut = f_["mediane"] - n_["mediane"]
            v("... mais le NIVEAU, lui, se déplace franchement",
              saut > 0.5,
              f"médiane face {f_['mediane']:+.3f} contre nulle {n_['mediane']:+.3f} "
              f"— écart {saut:+.3f}")
            # ⚠⚠⚠ CE QUE LA CORRELATION ETABLIT, ET CE QU'ELLE N'ETABLIT PAS. Elle repond a
            # une seule question : la carte du vide est-elle un DECALQUE de celle de la face --
            # le detecteur voyant a travers la meme colonne ? A +0,001, non.
            #
            # ⚠⚠ Elle ne dit RIEN de la spire VOISINE, et j'ai failli l'ecrire. L'encre de la
            # spire d'a cote n'a aucune raison de tomber la ou celle de cette face-ci tombe,
            # donc une correlation nulle est parfaitement compatible avec « le vide montre
            # l'encre du voisin ». Ce qui trancherait est une TROISIEME fenetre, arretee au
            # minimum de contraste et n'atteignant jamais le voisin.
            if r.get("correlation_face_nul") is not None:
                c = r["correlation_face_nul"]
                v("la carte du vide n'est PAS un décalque de celle de la face",
                  abs(c) < 0.2,
                  f"corrélation face/vide {c:+.3f} — donc pas une transparence de la même "
                  "colonne ; ⚠ ne dit rien de la spire voisine")
            if r.get("part_nul_au_dessus_mediane_face") is not None:
                v("... et une part non négligeable du vide se lit comme de l'encre",
                  r["part_nul_au_dessus_mediane_face"] > 0.01,
                  f"{100 * r['part_nul_au_dessus_mediane_face']:.1f} % du vide dépasse "
                  "la médiane de la face")
            v("... et les deux cartes couvrent la même surface",
              f_.get("couverts") == n_.get("couverts"),
              f"{f_.get('couverts')} contre {n_.get('couverts')}")

    print()
    if echecs:
        print(f"  ECHEC ({echecs} failures)")
    else:
        print(f"  ALL PASS (0 failures, {comptees} checks)")
    return echecs


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--segment", default="20260325000000-w046_20260325")
    p.add_argument("--zarr", default=None,
                   help="clef du surface-volume ; déduite du segment par défaut")
    p.add_argument("--top", type=int, default=11000)
    p.add_argument("--left", type=int, default=15000)
    p.add_argument("--taille", type=int, default=512)
    p.add_argument("--rederiver", action="store_true",
                   help="recalculer ce qui se déduit des cartes gardées, sans refaire l'inférence")
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--json", type=Path)
    a = p.parse_args()

    if a.rederiver:
        cible = a.json or DEFAUT_JSON
        d = json.loads(cible.read_text())
        d.update(deriver_des_cartes(d["segment"]))
        cible.write_text(json.dumps(d, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"corrélation face/vide : {d.get('correlation_face_nul'):+.3f}")
        print(f"part du vide au-dessus de la médiane de la face : "
              f"{100 * d.get('part_nul_au_dessus_mediane_face', 0):.1f} %")
        print(f"écrit : {cible}")
        return 0

    if a.verifier and not a.json:
        garde = json.loads(DEFAUT_JSON.read_text()) if DEFAUT_JSON.is_file() else None
        return 1 if _verifier(garde) else 0

    zarr = a.zarr or (f"PHerc0139/segments/{a.segment}/surface-volumes/"
                      "2.399um-0.22m-78keV-volume-20260102150214.zarr")
    r = mesurer(a.segment, zarr, a.top, a.left, a.taille)
    print(f"{r['segment']} — pile de {r['couches']} couches, pic à {r['pic']}")
    print(f"  fenêtre face : {r['debut_face']}..{r['debut_face'] + COUCHES_LUES}"
          f"   contraste moyen {r['contraste_face']:.3f}")
    print(f"  fenêtre nulle: {r['debut_nul']}..{r['debut_nul'] + COUCHES_LUES}"
          f"   contraste moyen {r['contraste_nul']:.3f}")
    for nom in ("face", "nul"):
        d = r[nom]
        if d.get("echec"):
            print(f"  {nom:5s} ÉCHEC — {d['echec']}", file=sys.stderr)
        else:
            print(f"  {nom:5s} encre min/méd/max {d['minimum']:+.3f} / {d['mediane']:+.3f} / "
                  f"{d['maximum']:+.3f}   ({d['couverts']}/{d['total']} px)")
    if r.get("rapport_etendue") is not None:
        print(f"\n  étendue nulle / étendue face = {r['rapport_etendue']:.2f}")
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"\nécrit : {a.json}")
    if a.verifier:
        print()
        return 1 if _verifier(r) else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
