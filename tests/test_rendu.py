"""Le rendu partagé par First Letters et Paris 4 : fenêtres choisies sans l'encre, et rangées sans lire."""
from __future__ import annotations

import numpy as np

from conftest import recherche
from vesuve.rendu import fenetres, rangees


def _page(periode=30, epaisseur=4, cote=400, bruit=0.0, graine=0):
    rng = np.random.default_rng(graine)
    img = np.full((cote, cote), 60, dtype=np.uint8)
    for r in range(40, cote - 40, periode):
        img[r:r + epaisseur, 40:cote - 40] = 220
    if bruit:
        img = np.clip(img + rng.normal(0, bruit, img.shape), 1, 255).astype(np.uint8)
    return img


@recherche
def test_linterligne_est_celui_du_producteur():
    import typographie as ref
    rng = np.random.default_rng(1)
    vus = 0
    for graine in range(30):
        img = _page(int(rng.integers(12, 40)), int(rng.integers(2, 7)), bruit=float(rng.uniform(0, 60)), graine=graine)
        if graine % 3 == 0:
            img = rng.integers(1, 255, size=img.shape).astype(np.uint8)  # du bruit pur
        m = img > 0
        b = rangees.binariser_encre(img, m)
        assert np.array_equal(b, ref.binariser_encre(img, m))
        assert rangees.interligne(b, m) == ref.interligne(b, m)
        vus += 1
    assert vus == 30


def test_une_page_lignee_est_periodique_et_son_melange_ne_lest_plus():
    img = _page(30, 4, bruit=20)
    m = img > 0
    b = rangees.binariser_encre(img, m)
    x = rangees.interligne(b, m)
    assert x["periodique"] and abs(x["periode_px"] - 30) <= 1
    assert not rangees.interligne(rangees.melanger(b, m, 7), m)["periodique"]


def test_la_fenetre_se_choisit_sur_le_papyrus_et_la_tenue_a_lecart_ne_la_chevauche_pas():
    m = np.zeros((600, 900), dtype=bool)
    m[50:550, 100:850] = True
    f = fenetres.la_meilleure_fenetre(m, 256)
    assert f["la_part_de_papyrus"] == 1.0 and (f["r0"], f["c0"]) == (64, 112)  # la première pleine en lecture
    t = fenetres.la_fenetre_tenue_a_lecart(m, 256, f)
    assert not (t["r0"] < f["r0"] + 256 and f["r0"] < t["r0"] + 256 and t["c0"] < f["c0"] + 256 and f["c0"] < t["c0"] + 256)
    assert t["le_cote_reduit"] is False
    assert fenetres.la_meilleure_fenetre(m, 1000) is None


def test_les_rangees_tracees_tombent_sur_les_lignes_meme_inclinees():
    from scipy import ndimage
    img = _page(28, 5, cote=500, bruit=15)
    img = ndimage.rotate(img, 6, order=0, reshape=False, mode="constant", cval=60)
    m = np.ones(img.shape, dtype=bool)
    m[:60, :] = m[-60:, :] = m[:, :60] = m[:, -60:] = False  # un bord : la rotation y laisse du fond
    b = rangees.binariser_encre(img, m)
    x = rangees.interligne(b, m)
    assert x["periodique"]
    assert abs(abs(rangees.linclinaison_des_rangees(b, m)) - 6) <= 1  # l'angle où les lignes contrastent
    trace = rangees.les_rangees(b, m, x)
    sur_lencre = b[trace].mean()
    assert trace.sum() > 0 and sur_lencre > 2 * b[m].mean()  # les lignes tracées sont sur l'encre
