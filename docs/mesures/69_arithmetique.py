"""Arithmétique du docs/69 : nombre de Fresnel, noyau de Paganin, loi de décohérence, coût humain.

Existe pour que chaque chiffre « [calculé] » du document ait son calcul dans l'arbre et non
dans un transcript. Entrées : les régimes de scan lus dans `pdf/main.pdf` (Supplementary
Table, Ext. Data Fig. 2), le pas d'enroulement de `winding-ruler`, les spires de
`atlas_collection_v2.csv`. Aucune donnée volumique n'est lue : ce sont des formules.
"""
import math

HC_EV_M = 1.23984193e-6  # h·c en eV·m


def longueur_donde_m(energie_kev: float) -> float:
    return HC_EV_M / (energie_kev * 1e3)


def nombre_de_fresnel(pas_um: float, distance_m: float, energie_kev: float) -> float:
    return math.sqrt(longueur_donde_m(energie_kev) * distance_m) / (pas_um * 1e-6)


def noyau_de_paganin_um(distance_m: float, energie_kev: float, delta_sur_beta: float = 1000.0) -> float:
    return math.sqrt(longueur_donde_m(energie_kev) * distance_m * delta_sur_beta / (4 * math.pi)) * 1e6


REGIMES = {
    "prix 9.362/1.2/113": (9.362, 1.2, 113),
    "prix 8.640/1.2/116": (8.640, 1.2, 116),
    "production 2.4/0.22/78": (2.4, 0.22, 78),
    "500P2 2.215/0.4/111": (2.215, 0.4, 111),
    "500P2 4.317/1.2/111": (4.317, 1.2, 111),
    "acquisition 4.681/1.2/113": (4.681, 1.2, 113),
    "268 4.32/1.2/133": (4.32, 1.2, 133),
    "268 4.334/0.6/133": (4.334, 0.6, 133),
}

if __name__ == "__main__":
    for nom, (p, d, e) in REGIMES.items():
        f = nombre_de_fresnel(p, d, e)
        lp = noyau_de_paganin_um(d, e)
        print(f"{nom:28s} F={f:.3f} sin(piF^2/4)={math.sin(math.pi * f * f / 4):.3f} "
              f"L_P={lp:5.1f}um ({lp / p:4.1f}px) lamD={longueur_donde_m(e) * d:.3e} "
              f"D/(E^2 p)={d / (e * e * p):.2e} D/(E p)={d / (e * p):.2e}")
    print("gain lamD prix/production :",
          longueur_donde_m(113) * 1.2 / (longueur_donde_m(78) * 0.22))
    print("largeur de decoherence relative D/E^2 prix/production :",
          (1.2 / 113**2) / (0.22 / 78**2))
    for nom, spires in (("PHerc0826", 60), ("PHerc0125", 82), ("PHerc0800", 103), ("PHerc0268", 129)):
        print(f"{nom}: {spires} spires -> {spires * 25} h a 8 cm, {spires * 25 * 20 / 8:.0f} h a 20 cm")


# ── ajouté pour docs/73 ─────────────────────────────────────────────────────────
def tuiles_pour_separer(delta: float, sigma: float = 0.2243, deux_conditions: bool = True,
                        z_alpha: float = 1.96, z_beta: float = 0.84) -> float:
    """Tuiles PAR CONDITION pour séparer un écart d'AUC `delta` au seuil usuel, 80 % de puissance.

    σ = 0,2243 est l'écart-type de tuile à tuile mesuré dans `64` (minorant : les tuiles
    voisines ne sont pas indépendantes). Deux conditions comparées → formule à deux
    échantillons (2σ²) ; une condition contre une valeur fixe (0,5) → un échantillon (σ²).
    Contrôle : δ = 0,171 à deux conditions rend 27, le chiffre de `64`.
    """
    k = 2.0 if deux_conditions else 1.0
    return k * (z_alpha + z_beta) ** 2 * sigma ** 2 / delta ** 2


if __name__ == "__main__":
    print("--- docs/73 ---")
    c = tuiles_pour_separer(0.171)
    assert abs(c - 27) < 1, c
    print("tuiles pour separer 0,171 entre deux fragments (controle de 64) :", round(c, 1))
    print("tuiles pour separer AUC(9,72um)=0,599 de 0,5, une condition :", round(tuiles_pour_separer(0.099, deux_conditions=False), 1))
    print("tuiles PAR CONDITION pour separer 3,24um (0,674) de 9,72um (0,599) :", round(tuiles_pour_separer(0.075), 1))
    for ep in (24, 40, 60):
        print(f"113 um face-a-face + epaisseur {ep} um = {113 + ep} um centre-a-centre (atlas 1447 : 172,8 ; docs/16 : 156)")
