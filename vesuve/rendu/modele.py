"""L'encre du modèle : le TimeSformer du Grand Prize 2023, balayé sur une pile de 26 couches (optionnel).

Port de `src/xpu/infer_ink.py` (`load_layer_stack`, `fenetres_avec_matiere`, `infer`). Trois règles gardées,
chacune payée par le producteur :

- la pile est normalisée par le maximum de SON type (`/ 65535` en dur divisait une pile uint8 par 257 de
  trop, et le modèle rendait une constante sur du noir) ;
- une fenêtre sans aucun voxel non nul est sautée, et ses pixels restent non couverts (NaN) : « pas de
  papyrus » et « pas d'encre » cessent d'être la même valeur ;
- les bords jamais balayés valent NaN, jamais zéro.

⚠ Au régime des treize rouleaux, le modèle publié ne sépare pas la feuille du vide (`R1-F20`) : sa sortie
y est une vue, pas une preuve, et le pipeline le dit à côté de chaque carte.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import tifffile

from vesuve.rendu.couches import les_couches

TUILE, COUCHES = 64, 26
LA_PLEINE_ECHELLE_MINIMALE = 1.0 / 64.0


class EncreIndisponible(RuntimeError):
    """torch ou le modèle manque ici : l'encre du modèle ne peut pas être calculée, et c'est dit."""


def la_pile(dossier: Path, debut: int, fenetre, pas: int = 1) -> np.ndarray:
    """26 couches `debut + i × pas` sur `(r0, c0, h, w)`, en float32 normalisé par le type de la pile."""
    fs = {int(__import__("re").search(r"(\d+)", p.stem).group(1)): p for p in les_couches(dossier)}
    r0, c0, h, w = fenetre
    pile = np.zeros((COUCHES, h, w), dtype=np.float32)
    type_ = None
    for i in range(COUCHES):
        n = debut + i * pas
        if n not in fs:
            raise EncreIndisponible(f"couche {n} absente de {dossier}")
        a = tifffile.imread(fs[n])
        if type_ is not None and a.dtype != type_:
            raise EncreIndisponible(f"couche {n} en {a.dtype}, la pile en {type_}")
        type_ = a.dtype
        pile[i] = a[r0:r0 + h, c0:c0 + w].astype(np.float32)
    pile /= float(np.iinfo(type_).max)
    if float(pile.max()) < LA_PLEINE_ECHELLE_MINIMALE:
        raise EncreIndisponible(f"pile presque noire (max {pile.max():.4g}) : le modèle rendrait une constante")
    return pile


def charger(dossier_du_modele: Path):
    try:
        import torch  # noqa: F401
        from transformers import AutoModel
    except ImportError as e:
        raise EncreIndisponible(f"{e.name} manque : `uv sync --extra encre`") from e
    if not (Path(dossier_du_modele) / "config.json").exists():
        raise EncreIndisponible(f"pas de modèle sous {dossier_du_modele}")
    return AutoModel.from_pretrained(str(dossier_du_modele), trust_remote_code=True).eval()


def inferer(pile: np.ndarray, modele, pas: int = 21, lot: int = 4, fils: int = 16) -> tuple[np.ndarray, int]:
    """(la carte d'encre en logits, NaN hors de ce qui est vu ; le nombre de fenêtres balayées)."""
    import torch
    import torch.nn.functional as F
    torch.set_num_threads(fils)
    _, h, w = pile.shape
    if h < TUILE or w < TUILE:
        raise EncreIndisponible(f"fenêtre {h}×{w} plus petite que la tuile {TUILE}")
    carte, recouvrement = np.zeros((h, w), dtype=np.float32), np.zeros((h, w), dtype=np.float32)
    positions = [(y, x) for y in range(0, h - TUILE + 1, pas) for x in range(0, w - TUILE + 1, pas)
                 if pile[:, y:y + TUILE, x:x + TUILE].any()]
    with torch.no_grad():
        for debut in range(0, len(positions), lot):
            morceau = positions[debut:debut + lot]
            x_ = torch.from_numpy(np.stack([pile[:, y:y + TUILE, x:x + TUILE] for y, x in morceau])).unsqueeze(1)
            sortie = F.interpolate(modele(x_).float(), scale_factor=16, mode="bilinear").squeeze(1).numpy()
            for (y, x), tuile in zip(morceau, sortie):
                carte[y:y + TUILE, x:x + TUILE] += tuile
                recouvrement[y:y + TUILE, x:x + TUILE] += 1.0
    carte /= np.clip(recouvrement, 1.0, None)
    carte[recouvrement == 0] = np.nan
    return carte, len(positions)
