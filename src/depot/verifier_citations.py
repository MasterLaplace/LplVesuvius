#!/usr/bin/env python3
"""Les agents ont-ils REELLEMENT lu, ou ont-ils fabrique leurs citations ?

Chaque fiche doit porter deux citations verbatim avec leur numero de ligne. Ce script les
extrait et va les chercher DANS le fichier cite. Une citation qu'on ne retrouve pas est le
signe qu'on ne peut pas se fier a la fiche.

⚠ La tolerance est deliberee : on cherche la citation dans une fenetre de +/- 4 lignes
autour du numero annonce, parce qu'un agent peut compter les lignes a une ou deux pres sans
avoir invente quoi que ce soit. Ce qu'on veut attraper est la citation ABSENTE du fichier,
pas le decalage d'index.
"""
import argparse, re, sys, unicodedata
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
RAPPORTS = Path(__file__).resolve().parents[2] / "docs" / "registres"

def norm(t):
    t = unicodedata.normalize("NFKD", t)
    t = t.replace(" ", " ").replace(" ", " ").replace("’", "'")
    return re.sub(r"\s+", " ", t).strip().lower()

FICHE = re.compile(r"^### (\S+\.md)\s*$", re.M)
CIT   = re.compile(r"(?:lignes?|l\.)\s+(\d+)(?:\s*[-–]\s*\d+)?[^:]*:"
                   r"\s*[`\"«]?(.+?)[`\"»]?\s*$", re.M)
"""⚠⚠ LES DEUX ECRITURES, et c'est une correction du 2026-09-03 qui vaut d'etre dite.

Ce motif ne connaissait que « ligne 104 ». Les fiches en portent une seconde, « l. 271 »,
et **44 citations sur 132 n'etaient donc jamais verifiees** -- un tiers. La garde annoncait
« 88 citations verifiees, 88 retrouvees » sans mentir sur les 88, mais son denominateur
etait le sous-ensemble qu'elle savait lire.

C'est le peche capital de ce depot dans un costume neuf : une verification qui ne peut pas
echouer sur ce qu'elle ne voit pas. Le remede n'est donc PAS seulement d'ajouter la seconde
ecriture -- c'est de COMPTER les lignes de preuve qu'on n'a pas su lire, et d'echouer
dessus. Une troisieme ecriture, un jour, fera echouer la garde au lieu de disparaitre.

⚠ La TROISIEME ecriture, trouvee par ce compteur des sa premiere execution : « lignes 89-90 »,
au pluriel, pour une citation a cheval sur deux lignes. Verifiee contre la PREMIERE des deux,
qui est celle ou la citation commence."""

LIGNE_DE_PREUVE = re.compile(r"^\s+- .+$", re.M)
"""Toute puce du bloc de preuve. Ce qui n'est pas capte par `CIT` est un format inconnu."""

_p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
_p.add_argument("--verifier", action="store_true", help="lance le contrôle")
_p.parse_args()

total = ok = introuvable = illisible = derive = 0
for rapport in sorted([RAPPORTS / "fiches_de_lecture.md"]):
    txt = rapport.read_text()
    blocs = FICHE.split(txt)
    for i in range(1, len(blocs), 2):
        doc, corps = blocs[i], blocs[i+1]
        chemin = RACINE / doc
        if not chemin.exists():
            print(f"  ⚠ {rapport.name}: fiche pour un fichier INEXISTANT {doc}"); continue
        lignes = chemin.read_text().splitlines()
        # ⚠ Ne chercher QUE dans le bloc de preuve. Ma premiere version balayait la fiche
        # entiere et attrapait des puces de conclusion contenant « ligne 143 » : deux faux
        # positifs signales comme des citations inventees, ce qui aurait accuse a tort.
        bloc = corps.split("preuve de lecture", 1)
        if len(bloc) < 2:
            print(f"  ⚠ {doc}: AUCUN bloc de preuve de lecture"); continue
        preuve = bloc[1].split("\n---", 1)[0]
        # ⚠ Le denominateur est le nombre de PUCES, pas le nombre de citations reconnues :
        # sinon une ecriture inconnue disparait au lieu de faire echouer.
        puces = len(LIGNE_DE_PREUVE.findall(preuve))
        lues = len(CIT.findall(preuve))
        if puces > lues:
            illisible += puces - lues
            print(f"  ✗ {doc}: {puces - lues} ligne(s) de preuve NON LUE(S) — format inconnu")
        for m in CIT.finditer(preuve):
            n, cit = int(m.group(1)), m.group(2)
            if len(norm(cit)) < 12: continue
            total += 1
            fenetre = " ".join(norm(l) for l in lignes[max(0, n-5):n+4])
            frag = norm(cit)[:70]
            if frag in fenetre:
                ok += 1
            else:
                # ⚠ Deuxieme chance : la citation est-elle AILLEURS dans le fichier ? Un
                # ecart franc veut dire que le document a ete EDITE depuis la fiche, ce qui
                # perime le numero sans perimer la citation. On le nomme et on le compte au
                # lieu de l'avaler : c'est ce qui est arrive au doc 07 le 2026-09-03, quand
                # un bloc de 28 lignes ajoute en tete a decale tout le fichier.
                pos = [i + 1 for i, l in enumerate(lignes) if frag in norm(l)]
                if pos:
                    derive += 1
                    print(f"  ~ {doc}: citation donnee ligne {n}, trouvee ligne "
                          f"{pos[0]} (derive de {pos[0] - n:+d})")
                elif frag in norm(" ".join(lignes)):
                    ok += 1
                    print(f"  ~ {doc}:{n} trouvee AILLEURS (sur plusieurs lignes)")
                else:
                    introuvable += 1
                    print(f"  ✗ {doc}:{n} INTROUVABLE — « {cit[:70]} »")
print(f"\n{total} citations verifiees · {ok} a leur ligne · {derive} derivees · "
      f"{introuvable} introuvables · {illisible} lignes de preuve illisibles")
echecs = introuvable + illisible + derive
if echecs:
    print(f"  ECHEC ({echecs} failures)")
else:
    print(f"  ALL PASS (0 failures, {total} checks)")
sys.exit(1 if echecs else 0)
