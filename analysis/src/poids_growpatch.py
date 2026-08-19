#!/usr/bin/env python3
"""Extraire du SOURCE de villa la table des poids de perte de GrowPatch.

⚠ Pourquoi ce script existe. La table du `26` §4 a d'abord ete transcrite a la main
depuis une lecture de terminal, et elle etait FAUSSE : elle annoncait dix poids au lieu
de douze, et nommait `surface_sdt_weight` et `spaceline_weight`, deux cles qui n'ont
aucune occurrence dans villa. Une table de correspondance recopiee a la main est une
table qui se desaccorde de sa source des que la source bouge -- et rien ne le dit.

Ce script derive la table. Il rend donc trois choses qu'une transcription ne rend pas :
  1. les cles JSON REELLEMENT lues par applyJsonWeights() ;
  2. leur valeur par defaut, lue dans le constructeur de LossSettings ;
  3. la GARDE de chaque terme -- la condition sous laquelle il rend zero quelle que soit
     la valeur du poids. C'est le fait qui explique nos trois negatifs : NORMAL pese 10,
     soit dix fois DIST, et il ne cree AUCUN residu tant qu'aucune grille de normales
     n'est chargee.

⚠ Le nom IMPRIME au demarrage par vc_grow_seg_from_seed n'est PAS la cle JSON. C'est
exactement ce qui a produit l'erreur : la ligne affiche SURFACE_SDT, la cle est
`sdt_weight`. Le lecteur est muet sur une cle inconnue -- ni erreur, ni avertissement,
ni effet -- donc une faute de nom est invisible a l'execution.

Usage :
    python3 analysis/src/poids_growpatch.py [--source repos/villa] [--json sortie.json]
    python3 analysis/src/poids_growpatch.py --verifier   # sort 3 si la doc et le source
                                                          # ne s'accordent pas
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
GROWPATCH = "volume-cartographer/core/src/GrowPatch.cpp"

# La garde de chaque terme : le fichier ou la lire, et le motif qui la porte.
# ⚠ Ces gardes ne sont pas dans applyJsonWeights : chaque generateur de perte commence
# par un `return 0` conditionnel. Un poids reglable dont la garde n'est pas satisfaite
# est un poids sans effet, et rien ne le signale.
GARDES = {
    "NORMAL": ("gen_normal_loss", r"if \(!trace_data\.ngv && !trace_data\.patch_normals\) return 0;"),
    # ⚠ La garde de DIRECTION n'est PAS dans gen_direction_loss (le generateur, l. 2185)
    # mais dans conditional_direction_loss (l. 2316), le seul appelant. Chercher dans le
    # generateur rendait "garde absente" sur un source ou elle est bien la : deux fonctions
    # dont le nom se ressemble, et c'est la SECONDE qui court-circuite.
    "DIRECTION": ("conditional_direction_loss", r"if \(!direction_fields\.size\(\)\)"),
}


def lire_source(racine_villa: Path) -> str:
    chemin = racine_villa / GROWPATCH
    if not chemin.is_file():
        sys.exit(f"source introuvable : {chemin}\n"
                 f"⚠ le depot villa doit etre clone (voir tools/clone_repos.sh)")
    return chemin.read_text(encoding="utf-8", errors="replace")


def cles_lues(src: str) -> list[tuple[str, str]]:
    """Les cles JSON reellement lues, dans l'ordre du source.

    Rend (terme imprime, cle json). Le terme est le LossType, la cle est la chaine.
    """
    return [(t, k) for k, t in re.findall(r'set_weight\("([a-z0-9_]+)",\s*LossType::([A-Z0-9_]+)\)', src)]


def defauts(src: str) -> dict[str, float]:
    """Les valeurs par defaut, lues dans le constructeur de LossSettings."""
    bloc = re.search(r"LossSettings\(\)\s*\{(.*?)\}", src, re.S)
    if not bloc:
        sys.exit("⚠ constructeur LossSettings introuvable — le source a change de forme")
    return {t: float(v) for t, v in
            re.findall(r"w\[LossType::([A-Z0-9_]+)\]\s*=\s*([0-9.]+)f?", bloc.group(1))}


def silencieux_sur_cle_inconnue(src: str) -> bool:
    """Une cle inconnue produit-elle un avertissement ?

    ⚠ C'est ce qui rend une faute de nom invisible. On le MESURE au lieu de le supposer :
    on lit le corps de la lambda set_weight et on cherche s'il ecrit quoi que ce soit
    avant de sortir.
    """
    m = re.search(r"const auto set_weight = \[.*?\]\(.*?\)\s*\{(.*?)\n\s*\};", src, re.S)
    if not m:
        return True  # forme inconnue : on ne peut pas prouver qu'il avertit
    corps = m.group(1)
    tete = corps.split("return")[0] if "return" in corps else corps
    return not re.search(r"(cerr|cout|WARNING|warn)", tete)


def garde_de(src: str, terme: str) -> str | None:
    """La garde d'un terme, cherchee dans la DEFINITION de son generateur.

    ⚠ Piege paye en ecrivant ce script : `src.find("gen_normal_loss")` tombe sur la
    DECLARATION AVANCEE (ligne 1581), qui n'a pas de corps -- la garde vit dans la
    definition, 467 lignes plus bas. Une recherche naive rendait donc "garde absente"
    sur un source ou elle est bien la, et le controle echouait sur du code correct.
    On distingue les deux par ce qui suit la parenthese fermante : `;` pour une
    declaration, `{` pour une definition.
    """
    if terme not in GARDES:
        return None
    fonction, motif = GARDES[terme]
    for m_def in re.finditer(re.escape(fonction) + r"\s*\(", src):
        # avancer jusqu'a la parenthese fermante appariee, puis regarder le caractere suivant
        i, prof = m_def.end() - 1, 0
        while i < len(src):
            if src[i] == "(":
                prof += 1
            elif src[i] == ")":
                prof -= 1
                if prof == 0:
                    break
            i += 1
        suite = src[i + 1:i + 200].lstrip()
        if not suite.startswith("{"):
            continue                      # declaration avancee, pas la definition
        m = re.search(motif, src[i:i + 2000])
        if m:
            return m.group(0)
    return None


def table(racine_villa: Path) -> dict:
    src = lire_source(racine_villa)
    d = defauts(src)
    lignes = []
    for terme, cle in cles_lues(src):
        lignes.append({
            "terme_imprime": terme,
            "cle_json": cle,
            "defaut": d.get(terme),
            "garde": garde_de(src, terme),
        })
    return {
        "source": str(racine_villa / GROWPATCH),
        "nb_cles": len(lignes),
        "silencieux_sur_cle_inconnue": silencieux_sur_cle_inconnue(src),
        "poids": lignes,
    }


# ⚠ Ce que le `26` §4 affirme. Le controle compare la doc au source, dans les deux sens :
# une cle du source absente d'ici est une cle que la doc a ratee, et une cle d'ici absente
# du source est une cle inventee -- c'est exactement l'erreur qui a ete commise.
ATTENDU = {
    "dist_weight", "straight_weight", "direction_weight", "snap_weight",
    "normal_weight", "normal3dline_weight", "reference_ray_weight",
    "sdt_weight", "space_line_weight", "sdir_weight",
    "correction_weight", "patch_normal_weight",
}
# ⚠ Les deux noms qui avaient ete ecrits a tort. Le controle verifie qu'ils restent
# ABSENTS : si l'un reapparaissait dans le source, notre correction serait a revoir.
JAMAIS = {"surface_sdt_weight", "spaceline_weight"}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--source", default=str(RACINE / "repos" / "villa"),
                    help="racine du depot villa clone")
    ap.add_argument("--json", help="ecrire la table en JSON")
    ap.add_argument("--verifier", action="store_true",
                    help="comparer au contenu documente ; sortie 3 si desaccord")
    a = ap.parse_args()

    t = table(Path(a.source))
    cles = {p["cle_json"] for p in t["poids"]}

    largeur = max(len(p["cle_json"]) for p in t["poids"])
    print(f"{t['nb_cles']} poids lus dans {t['source']}\n")
    print(f"  {'cle du seed.json':<{largeur}}  {'terme imprime':<14} {'defaut':>7}  garde")
    for p in t["poids"]:
        g = "—" if p["garde"] is None else "rend 0 si : " + p["garde"]
        print(f"  {p['cle_json']:<{largeur}}  {p['terme_imprime']:<14} "
              f"{p['defaut']:>7}  {g}")
    print(f"\n  cle inconnue : {'IGNOREE EN SILENCE' if t['silencieux_sur_cle_inconnue'] else 'signalee'}")

    if a.json:
        Path(a.json).write_text(json.dumps(t, indent=2, ensure_ascii=False) + "\n",
                                encoding="utf-8")
        print(f"  ecrit : {a.json}")

    if not a.verifier:
        return 0

    echecs = []
    manquantes = ATTENDU - cles
    inventees = cles - ATTENDU
    revenues = JAMAIS & cles
    if manquantes:
        echecs.append(f"cles documentees absentes du source : {sorted(manquantes)}")
    if inventees:
        echecs.append(f"cles du source absentes de la doc : {sorted(inventees)}")
    if revenues:
        echecs.append(f"cles corrigees qui REAPPARAISSENT dans le source : {sorted(revenues)}")
    # ⚠ La garde de NORMAL porte l'explication de trois negatifs mesures : si elle
    # disparaissait, le `26` §4 cesserait d'etre vrai sans que rien ne le dise.
    normal = next((p for p in t["poids"] if p["terme_imprime"] == "NORMAL"), None)
    if not normal or not normal["garde"]:
        echecs.append("la garde de NORMAL n'est plus lisible dans le source")
    if normal and normal["defaut"] != 10.0:
        echecs.append(f"NORMAL ne vaut plus 10 mais {normal['defaut']}")

    print()
    if echecs:
        # ⚠ NE PAS imprimer "ALL PASS" ici. tools/temoins.sh reconnait une batterie
        # reussie en cherchant cette chaine : la premiere version de ce bloc l'imprimait
        # AUSSI en echec, sous la forme "ALL PASS (1 failures, ...)". La batterie serait
        # passee au vert en signalant ses propres echecs. C'est le piege nº1 du depot,
        # ecrit ici dix minutes apres l'avoir documente ailleurs.
        for e in echecs:
            print(f"  ECHEC : {e}")
        print(f"\n{len(echecs)} desaccord(s) entre la doc et le source")
        return 3
    print(f"  la table du 26 §4 s'accorde au source : {len(ATTENDU)} cles, "
          f"aucune inventee, garde de NORMAL en place, defaut 10")
    print(f"\nALL PASS (0 failures, {len(ATTENDU) + 3} checks)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
