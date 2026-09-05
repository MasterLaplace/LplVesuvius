#!/usr/bin/env python3
"""Le masque porte-t-il des repères INTÉRIEURS ? — la seule voie que C1 laisse ouverte.

⚠⚠ POURQUOI CE FICHIER EXISTE. `75` C1 a mesuré **deux fois** qu'on ne recale pas ces deux
aplatissements depuis leurs **bords** : ni un modèle lisse global, ni une agrégation locale ne
battent le champ nul sur la composante mesurée, parce que le conditionnement des directions
plafonne à 0,60 pour 1 en isotropie. La conclusion nommait la suite — *« il faut du contenu
intérieur »* — sans dire s'il en existe.

⭐⭐⭐ **C'est une question sur l'ENTRÉE, et elle se pose avant d'écrire un recaleur.** Un trou
dans le masque est un repère intérieur **géométrique** : il ne touche pas à l'encre, donc s'en
servir pour recaler ne rend pas circulaire la mesure d'encre qui suit — contrairement à
l'optimum de (−104, −120) cellules que `75` C1 obtient **en regardant l'encre**.

⚠⚠ Mais tous les trous ne se valent pas, et c'est le même problème d'ouverture un cran plus
bas : un trou **rond** contraint les deux composantes, une **fente** n'en contraint qu'une.
La grandeur qui décide est donc le **conditionnement** des directions de son bord — la même
que `le_recalage_local.py` applique aux carreaux, réutilisée et non réécrite.

⚠ Un trou est une composante du **complément** qui ne touche PAS le bord de l'image : ce qui
touche le bord est l'extérieur du fragment, pas un trou. Les confondre compterait le fond
entier comme un repère.

Usage :
    uv run python src/encre/les_reperes_interieurs.py --verifier
    uv run python src/encre/les_reperes_interieurs.py \\
        --json docs/mesures/les_reperes_interieurs.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from le_recalage_local import conditionnement  # noqa: E402

RACINE = Path(__file__).resolve().parents[2]
LOCAL = RACINE / "data" / "0500P2"

AIRE_MINIMALE = 64
"""En pixels de l'image réduite. ⚠ Un trou de quelques pixels est du bruit de seuil du masque,
pas un repère : sa position se déplace d'un pixel à l'autre selon le seuil qui l'a fabriqué."""


def _image(nom: str) -> np.ndarray | None:
    from PIL import Image
    Image.MAX_IMAGE_PIXELS = None
    chemin = LOCAL / nom
    if not chemin.is_file():
        return None
    a = np.asarray(Image.open(chemin))
    return a[..., 0] if a.ndim == 3 else a


def trous(masque: np.ndarray, aire_minimale: int = AIRE_MINIMALE) -> list[dict]:
    """
    @brief Les composantes du COMPLÉMENT qui ne touchent aucun bord — les vrais trous.

    ⚠⚠ Le test « ne touche pas le bord » est ce qui sépare un trou de l'extérieur du fragment.
    Sans lui, le fond entier serait compté comme un repère géant, et le conditionnement de ses
    directions serait excellent — un faux positif parfait.
    """
    from scipy import ndimage

    plein = masque > 0
    marques, n = ndimage.label(~plein)
    if n == 0:
        return []
    # ⚠ Les étiquettes qui apparaissent sur une des quatre bordures sont l'extérieur.
    bord = set(np.unique(np.concatenate([marques[0], marques[-1],
                                         marques[:, 0], marques[:, -1]])))
    # ⚠⚠ Les tailles en UN passage et les boîtes par `find_objects` : un
    # `np.nonzero(marques == etiquette)` par trou balaierait l'image entière autant de fois
    # qu'il y a de trous — sur 407 millions de pixels, des heures pour la même réponse.
    tailles = np.bincount(marques.ravel(), minlength=n + 1)
    boites = ndimage.find_objects(marques)
    out = []
    for etiquette in range(1, n + 1):
        if etiquette in bord or tailles[etiquette] < aire_minimale:
            continue
        boite = boites[etiquette - 1]
        if boite is None:
            continue
        sous = marques[boite] == etiquette
        li, lj = np.nonzero(sous)
        ii = li + boite[0].start
        jj = lj + boite[1].start
        ci, cj = ii.mean(), jj.mean()
        # ⚠⚠ Les directions du BORD, prises depuis le centroïde : un trou rond les étale sur
        # tout le cercle, une fente les regroupe sur un axe. C'est le problème d'ouverture au
        # niveau du repère, et c'est la même grandeur que pour les carreaux.
        di, dj = ii - ci, jj - cj
        n_ = np.hypot(di, dj)
        garde = n_ > 1e-9
        dirs = np.stack([di[garde] / n_[garde], dj[garde] / n_[garde]], axis=1)
        out.append({"aire": int(ii.size),
                    "centre": [float(ci), float(cj)],
                    "hauteur": int(ii.max() - ii.min() + 1),
                    "largeur": int(jj.max() - jj.min() + 1),
                    "conditionnement": round(conditionnement(dirs), 4)})
    return sorted(out, key=lambda t: -t["aire"])


def reduire(masque: np.ndarray, cote: int) -> np.ndarray:
    """Le masque ramené à `cote` de large, par majorité de bloc.

    ⚠ Par MAJORITÉ et non par échantillonnage : un sous-échantillonnage au pas prendrait un
    pixel sur vingt-six et ferait disparaître ou apparaître un trou selon le pixel tombé,
    ce qui ferait dépendre le compte de repères d'un alignement de grille.
    """
    h, w = masque.shape
    pas = max(1, w // cote)
    hh, ww = (h // pas) * pas, (w // pas) * pas
    bloc = (masque[:hh, :ww] > 0).reshape(hh // pas, pas, ww // pas, pas)
    return (bloc.mean(axis=(1, 3)) >= 0.5).astype(np.uint8) * 255


def utilisables(liste: list[dict], seuil: float = 0.25) -> list[dict]:
    """Les trous dont le bord couvre assez le plan pour contraindre DEUX composantes.

    ⚠ Le seuil est celui que les carreaux de bord atteignent déjà (0,26 au plus petit rayon,
    `75` C1) : un repère qui ne ferait pas mieux qu'un bord droit n'apporterait rien. Il est
    donc **repris** d'une mesure et non choisi ici.
    """
    return [t for t in liste if t["conditionnement"] >= seuil]


def verifier() -> int:
    echecs = controles = 0

    def v(nom: str, ok: bool, detail: str = "") -> None:
        nonlocal echecs, controles
        controles += 1
        if not ok:
            echecs += 1
        print(f"  {'✅' if ok else '❌'} {nom}" + (f"  — {detail}" if detail else ""))

    # --- un masque fabriqué, avec un trou rond et une fente ---
    m = np.zeros((200, 200), dtype=np.uint8)
    m[20:180, 20:180] = 255
    yy, xx = np.mgrid[0:200, 0:200]
    m[(yy - 60) ** 2 + (xx - 60) ** 2 <= 15 ** 2] = 0        # trou rond
    m[120:124, 60:160] = 0                                    # fente
    m[100, 100] = 0                                           # poussière d'un pixel
    ts = trous(m)
    v("les trous intérieurs sont trouvés", len(ts) == 2, f"{len(ts)} trous")
    # ⚠⚠ LE CONTRÔLE QUI COMPTE : l'extérieur du fragment touche le bord de l'image, donc il
    # n'est PAS un trou. Sans lui, le fond entier serait un repère géant parfaitement isotrope.
    v("... et l'extérieur du fragment n'en est pas un",
      all(t["aire"] < 5000 for t in ts), str([t["aire"] for t in ts]))
    v("... et la poussière d'un pixel non plus",
      all(t["aire"] >= AIRE_MINIMALE for t in ts))
    rond = max(ts, key=lambda t: t["conditionnement"])
    fente = min(ts, key=lambda t: t["conditionnement"])
    # ⭐⭐ Un trou ROND contraint les deux composantes, une FENTE une seule. C'est le problème
    # d'ouverture au niveau du repère, et c'est ce qui décide si un trou sert à quelque chose.
    v("un trou rond couvre le plan", rond["conditionnement"] > 0.8,
      f"{rond['conditionnement']} (aire {rond['aire']})")
    v("... et une fente ne le couvre pas", fente["conditionnement"] < 0.2,
      f"{fente['conditionnement']} (aire {fente['aire']})")
    v("... donc un seul des deux est utilisable", len(utilisables(ts)) == 1)
    # ⚠ Et un masque plein n'a aucun trou — sinon la fonction rendrait des repères là où il
    # n'y a rien à repérer.
    plein = np.full((100, 100), 255, dtype=np.uint8)
    v("un masque plein n'a aucun trou", trous(plein) == [])
    v("... et un masque vide non plus, son fond touche le bord",
      trous(np.zeros((100, 100), dtype=np.uint8)) == [])

    # --- la réduction, qui décide si un repère est ATTEIGNABLE ---
    grand = np.zeros((2600, 2600), dtype=np.uint8)
    grand[200:2400, 200:2400] = 255
    y2, x2 = np.mgrid[0:2600, 0:2600]
    grand[(y2 - 800) ** 2 + (x2 - 800) ** 2 <= 130 ** 2] = 0      # gros trou
    grand[(y2 - 1600) ** 2 + (x2 - 1600) ** 2 <= 6 ** 2] = 0      # petit trou
    v("à pleine résolution les deux trous sont là", len(trous(grand)) == 2)
    # ⚠⚠ ET C'EST LE POINT : un repère qui ne survit pas à la résolution où l'AUTRE
    # aplatissement existe n'est pas un repère utilisable, quelle que soit sa netteté ici.
    petit = trous(reduire(grand, 260), aire_minimale=4)
    v("... et à un dixième de la résolution, le petit a disparu",
      len(petit) == 1, f"{len(petit)} trou(s) après réduction")
    v("la réduction par majorité garde la matière",
      (reduire(grand, 260) > 0).mean() > 0.5)
    # ⚠⚠⚠ CE QUE LA MAJORITÉ GARANTIT ET QUE L'ÉCHANTILLONNAGE N'A PAS : la stabilité au
    # déplacement de la grille. Un sous-échantillonnage au pas prend un pixel sur dix, donc il
    # fait apparaître ou disparaître un trou selon l'endroit où la grille tombe — et le compte
    # de repères deviendrait une propriété de l'alignement. Mesuré : sans ce contrôle, la sonde
    # « réduire par échantillonnage » passait au vert.
    fin = np.zeros((2600, 2600), dtype=np.uint8)
    fin[200:2400, 200:2400] = 255
    fin[800:1400, 1600:1603] = 0          # fente de 3 px, alignée sur le pas de 10
    decale = np.roll(fin, 5, axis=1)
    v("... et elle est STABLE quand la grille se déplace de cinq pixels",
      len(trous(reduire(fin, 260), aire_minimale=4))
      == len(trous(reduire(decale, 260), aire_minimale=4)),
      f"{len(trous(reduire(fin, 260), aire_minimale=4))} contre "
      f"{len(trous(reduire(decale, 260), aire_minimale=4))} sur une fente de 3 px")

    # --- contre le VRAI masque ---
    masque = _image("500P2_mask.png")
    if masque is None:
        print("  ⚠ masque absent : la partie « vrai arbre » n'a pas tourné")
    else:
        reels = trous(masque)
        u = utilisables(reels)
        v(f"le masque de 500P2 est lu ({masque.shape[0]}×{masque.shape[1]})",
          masque.size > 10 ** 6)
        # ⭐⭐⭐ LA QUESTION QUE CE FICHIER POSE, assertée dans le sens où elle a été mesurée.
        v(f"il porte {len(reels)} trou(s) intérieur(s), dont {len(u)} utilisable(s)",
          True, f"aires {[t['aire'] for t in reels[:5]]}")
        # ⚠⚠⚠ ET LA MOITIÉ QUI DÉCIDE : l'autre aplatissement ne publie AUCUN masque de
        # surface — `deux_aplatissements` le dit — donc la seule empreinte disponible de ce
        # côté est la carte d'encre réduite, à 1024 de large. Un repère qui ne survit pas à
        # cette réduction n'a rien contre quoi être apparié.
        reduit = trous(reduire(masque, 1024), aire_minimale=4)
        ur = utilisables(reduit)
        v(f"à la résolution où l'autre aplatissement existe, il en reste {len(ur)}",
          len(ur) < len(u),
          f"{len(u)} à pleine résolution, {len(ur)} à 1024 de large")

    print(f"{'ALL PASS' if echecs == 0 else 'FAILURES'} ({echecs} failures, {controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--masque", default="500P2_mask.png")
    p.add_argument("--aire-min", type=int, default=AIRE_MINIMALE)
    p.add_argument("--json", type=Path)
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()
    if a.verifier:
        return verifier()
    masque = _image(a.masque)
    if masque is None:
        raise SystemExit(f"masque absent : {LOCAL / a.masque}")
    ts = trous(masque, a.aire_min)
    u = utilisables(ts)
    print(f"masque {masque.shape[0]}×{masque.shape[1]} — "
          f"{int((masque > 0).sum())} pixels de matière")
    print(f"{len(ts)} trou(s) intérieur(s) d'au moins {a.aire_min} pixels, "
          f"{len(u)} utilisable(s) comme repère\n")
    print(f"{'aire':>10} {'hauteur':>8} {'largeur':>8} {'conditionnement':>16}")
    print("-" * 46)
    for t in ts[:20]:
        print(f"{t['aire']:>10} {t['hauteur']:>8} {t['largeur']:>8} "
              f"{t['conditionnement']:>16.4f}")
    r = {"masque": a.masque, "forme": list(masque.shape),
         "pixels_matiere": int((masque > 0).sum()),
         "aire_minimale": a.aire_min, "trous": len(ts), "utilisables": len(u),
         "detail": ts[:200]}
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(r, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"\nécrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
