"""Les prix, leurs rouleaux éligibles et leurs volumes : ce qu'un pipeline vérifie avant de dépenser quoi que ce soit.

Sources : les règles de `https://scrollprize.org/prizes` téléchargées le 2026-09-11 (`docs/rapports/PRIX.md`),
et l'index `metadata.min.json` du bucket public du 2026-08-29 pour la taille de pixel et l'énergie.
⚠ Les listes changent : First Letters est passé de 13 à 23 rouleaux entre le 16 août et le 11 septembre.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Volume:
    objet: str
    volume: str
    pixel_um: float
    energie_kev: float
    distance_m: float = 1.2


# Grand Prize 2027 : treize volumes, identifiés par leur horodatage (PRIX.md §1).
LE_GRAND_PRIX = tuple(Volume(*v) for v in (
    ("PHerc0125", "20250821151825", 9.362, 113.0), ("PHerc0191", "20250821151635", 9.362, 113.0),
    ("PHerc0211", "20250821151803", 9.362, 113.0), ("PHerc0257", "20250821151750", 9.362, 113.0),
    ("PHerc0268", "20251110183117", 8.64, 116.0), ("PHerc0358", "20250821151737", 9.362, 113.0),
    ("PHerc0800", "20250521135224", 8.64, 116.0), ("PHerc0813", "20250821151723", 9.362, 113.0),
    ("PHerc0826", "20250821151701", 9.362, 113.0), ("PHerc1203", "20250820131727", 9.362, 113.0),
    ("PHerc1218", "20250521120456", 8.64, 116.0), ("PHerc1447", "20250521151220", 8.64, 116.0),
    ("PHerc1545", "20250821151648", 9.362, 113.0),
))

# First Letters : les treize du Grand Prize et dix de plus « where no text has been read yet » (PRIX.md §0, §2).
LES_PREMIERES_LETTRES = LE_GRAND_PRIX + tuple(Volume(*v) for v in (
    ("PHerc0175A", "20250521115057", 8.64, 116.0), ("PHerc0175B", "20250521125822", 8.64, 116.0),
    ("PHerc0306B", "20250521133212", 8.64, 116.0), ("PHerc0343", "20250521140437", 8.64, 116.0),
    ("PHerc0483A", "20250521140913", 8.64, 116.0), ("PHerc0483B", "20251124083638", 8.64, 116.0),
    ("PHerc0490A", "20250521151210", 8.64, 116.0), ("PHerc0490B", "20250521151215", 8.64, 116.0),
    ("PHerc0846A", "20250728152254", 9.362, 113.0), ("PHerc0846B", "20250804142305", 9.362, 113.0),
))

# Le titre de PHerc. Paris 4 : tous les volumes de Scroll 1, haute résolution comprise (PRIX.md §3).
LES_VOLUMES_DE_PARIS4 = tuple(Volume("PHercParis4", *v) for v in (
    ("20260411134726", 2.4, 78.0, 0.2), ("20260323153942", 2.4, 137.0, 0.2), ("20260608103018", 1.129, 78.0, 0.2),
))

# Le régime de production : ce que les modèles d'encre publiés ont vu à l'entraînement (R6-F08).
LA_PRODUCTION = Volume("production", "-", 2.4, 78.0, 0.2)

LES_REGLES = {
    "grand-prize": ("100 % du recto déroulé (les patches extérieurs déconnectés de moins de 10 % peuvent être "
                    "sautés) ; 70 % des caractères lisibles par colonne ; pipeline entièrement automatique, "
                    "au plus 8 h d'humain documentées ; intégré à VC3D ; image Docker ; un maillage par colonne, "
                    "`column_NN.tifxyz` dans l'ordre des spires ; pas de données d'un scan à plus haute "
                    "résolution du même volume ; graines fixées et rapportées."),
    "first-letters": ("10 lettres dans une zone de 4 cm² d'un des 23 rouleaux ; un tifxyz et son aplatissement ; "
                      "une image programmatique statique, barre d'échelle de 1 cm, nommée d'après son maillage, "
                      "rangées annotées, encre sur un rendu où les fibres se voient ; démontrer que le texte n'est "
                      "pas halluciné (lettres plausibles sur une région tenue à l'écart) ; aucun recouvrement "
                      "entre entraînement et prédiction ; humain dans la boucle permis."),
    "paris4-title": ("une image du titre de Scroll 1 que les papyrologues puissent lire ; tout volume de Scroll 1, "
                     "2,4 µm compris ; un tifxyz et son aplatissement ; l'encre dans le contexte de la recherche du "
                     "titre ; validation sur une région tenue à l'écart."),
    "progress": ("outils, résultats, résultats NÉGATIFS et audits ; le jury favorise ce qui détecte les cas "
                 "d'échec des méthodes existantes sur de vraies données de rouleau."),
}


def est_eligible(prix: str, objet: str, volume: str | None = None) -> bool:
    liste = {"grand-prize": LE_GRAND_PRIX, "first-letters": LES_PREMIERES_LETTRES,
             "paris4-title": LES_VOLUMES_DE_PARIS4}.get(prix)
    if liste is None:
        return True
    return any(v.objet == objet and (volume is None or v.volume == volume) for v in liste)


def le_volume(prix: str, objet: str) -> Volume | None:
    liste = {"grand-prize": LE_GRAND_PRIX, "first-letters": LES_PREMIERES_LETTRES,
             "paris4-title": LES_VOLUMES_DE_PARIS4}.get(prix, ())
    return next((v for v in liste if v.objet == objet), None)
