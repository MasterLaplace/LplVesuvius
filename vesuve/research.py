"""The border with the research: what the `experimental` branch wrote, in its own words, and our names for them.

The research was written in French, and its published measurements (`docs/mesures/*.json`) keep French keys
and French values. This program is in English. Crossing from one to the other happens in exactly two places:
`tools/extract_from_research.py`, which writes the embedded data, and the parity tests, which compare a port
with the research function that produced a number. Both translate through `to_english` and nowhere else, so
there is one dictionary to keep in step with the research, and a key it does not know stays visibly French
instead of being silently dropped.
"""
from __future__ import annotations

from vesuve.transport import ABSENT, NETWORK

KEYS = {
    # a band, and its reading
    "le_sens": "direction", "le_centre": "centre", "les_lignes": "lines", "de": "start", "a": "end",
    "le_long": "along", "en_travers": "across", "les_lectures": "readings", "refuses": "refused",
    "les_bandes": "bands", "grille_de_chunks": "chunk_grid", "la_rangee": "row", "la_colonne": "column",
    "le_cote_du_chunk": "chunk_side", "la_largeur_du_bord": "edge_width", "les_rangees_lues": "cut_rows",
    "les_colonnes_de_coupe": "cut_columns", "colonnes_demandees": "columns_requested",
    "colonnes_lues": "columns_read", "rangees_demandees": "rows_requested", "rangees_lues": "rows_read",
    "les_reprises_du_reseau": "network_retries", "cle": "key",
    # a control source
    "domaine": "domain", "pas": "steps",
    # the procedure's journal
    "la_boucle": "loop", "le_cote": "side", "la_portion": "portion", "les_exclues": "excluded",
    "letat": "state", "les_coins": "corners", "la_largeur": "width", "le_decoupage": "cutting",
    "les_demandes": "requests", "ce_quelle_coute": "cost", "la_fermeture": "closure", "le_profil": "profile",
    "la_coupe": "cut", "le_cumul_en_voxels": "cumulative_voxels", "le_pic": "peak", "le_departage": "tie_break",
    "la_raison": "reason", "la_troisieme_ligne": "third_line", "la_ligne": "line", "la_plus_proche": "nearest",
    "la_plus_loin": "farthest", "du_cote_du_rectangle": "on_rectangle_side", "lecart": "gap",
    "le_verdict": "verdict", "la_largeur_jugee": "width_judged", "les_boucles_ouvertes": "open_loops",
    "la_plus_serree": "tightest", "tranche": "decides", "la_ligne_qui_derive": "drifting_line",
    "les_marges": "margins", "cest_une_colonne_de_laile": "is_a_wing_column",
    "les_bornes": "bounds", "les_coupes": "cuts", "les_coupes_deja_lues": "cuts_already_read",
    "combien_de_sous_boucles": "sub_loops", "le_plus_grand_ecart": "largest_gap",
    "les_ecarts_au_dela_de_la_portee": "gaps_beyond_reach",
    "le_rectangle": "rectangle", "le_journal": "journal", "les_boucles_qui_tiennent": "holding_loops",
    "ce_qui_reste_a_lire": "left_to_read", "la_couverture": "coverage", "combien": "count", "sur": "of",
    "la_part": "share", "les_boucles": "loops",
    # the analysis of a loop at one width
    "par_largeur": "by_width", "fermable": "closable", "les_trous": "holes", "les_trous_trop_longs": "holes_too_long",
    "le_debut": "start", "la_longueur": "length", "la_fermeture_en_voxels": "closure_voxels",
    "sous_le_demi_pli": "under_half_sheet", "les_cotes": "sides", "la_somme_en_voxels": "sum_voxels",
    "la_dispersion_du_pas_en_voxels": "step_spread_voxels", "le_nul": "null",
    "la_fermeture_mediane_en_valeur_absolue": "median_absolute_closure",
    "la_part_sous_le_demi_pli": "share_under_half_sheet", "la_part_sous_la_fermeture": "share_under_closure",
    # the context of a segment
    "la_procedure": "procedure", "demi": "half", "graine": "seed", "plus_long": "longest", "portee": "reach",
    "tirages": "draws", "la_provenance": "provenance", "le_commit_de_la_recherche": "research_commit",
    "les_fichiers": "files", "le_fichier": "file", "son_empreinte": "digest", "le_budget": "budget",
    "les_coutures_dune_rangee": "seams_of_a_row", "saccorder": "agree", "traverser": "cross",
    "la_moyenne_des_rangees": "mean_of_rows", "le_plancher_de_la_matiere": "material_floor",
    "une_rangee_seule": "single_row", "le_demi_feuillet_voxels": "half_sheet_voxels", "le_pas_um": "step_um",
    "le_segment": "segment", "le_volume": "volume", "le_voxel_um": "voxel_um", "lobjet": "scroll",
    "la_couverture_a_la_main": "hand_coverage", "la_trace": "trace", "les_rangees": "rows",
    "la_grille": "grid",
}

VALUES = {
    "rangees": "rows", "colonnes": "columns",
    "haut": "top", "droite": "right", "bas": "bottom", "gauche": "left",
    "le rectangle": "the rectangle", "l'aile": "the wing",
    "dessous": "under", "franchit": "crosses", "ouverte": "open", "non vue": "unseen", "à lire": "to read",
    "non contrôlée": "unchecked", "indécidable": "undecidable", "aucune aile": "no wing",
    "départagée": "decided", "non départagée": "not decided", "rien ne départage": "nothing decides",
    "laile": "wing", "letroite": "narrow", "la_large": "wide",
    "absent du dépôt": ABSENT, "vide": "empty", "trop peu texturé": "too little texture", "illisible": "unreadable",
}

_NETWORK_FR = "le réseau a échoué"

# A band's key is its direction followed by numbers, `rangees_44_22_243_9`: only the direction is a word.
_KEY_PREFIXES = {"rangees_": "rows_", "colonnes_": "columns_"}


def _value(x):
    if not isinstance(x, str):
        return x
    if x in VALUES:
        return VALUES[x]
    if x.startswith(_NETWORK_FR):
        return NETWORK + x[len(_NETWORK_FR):].replace(" : ", ": ", 1)
    for french, english in _KEY_PREFIXES.items():
        if x.startswith(french) and x[len(french):].replace("_", "").isdigit():
            return english + x[len(french):]
    return x


def to_english(x):
    """The same structure with its known keys and values in English; lists and numbers are untouched."""
    if isinstance(x, dict):
        return {KEYS.get(k, _value(k)): to_english(v) for k, v in x.items()}
    if isinstance(x, list):
        return [to_english(v) for v in x]
    if isinstance(x, tuple):
        return tuple(to_english(v) for v in x)
    return _value(x)
