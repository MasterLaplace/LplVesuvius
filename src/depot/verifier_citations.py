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
CIT   = re.compile(r"ligne\s+(\d+)[^:]*:\s*[`\"«]?(.+?)[`\"»]?\s*$", re.M)

_p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
_p.add_argument("--verifier", action="store_true", help="lance le contrôle")
_p.parse_args()

total = ok = introuvable = 0
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
        for m in CIT.finditer(bloc[1]):
            n, cit = int(m.group(1)), m.group(2)
            if len(norm(cit)) < 12: continue
            total += 1
            fenetre = " ".join(norm(l) for l in lignes[max(0, n-5):n+4])
            frag = norm(cit)[:70]
            if frag in fenetre:
                ok += 1
            else:
                # deuxieme chance : n'importe ou dans le fichier
                if frag in norm(" ".join(lignes)):
                    ok += 1
                    print(f"  ~ {doc}:{n} trouvee AILLEURS dans le fichier")
                else:
                    introuvable += 1
                    print(f"  ✗ {doc}:{n} INTROUVABLE — « {cit[:70]} »")
print(f"\n{total} citations verifiees · {ok} retrouvees · {introuvable} introuvables")
if introuvable:
    print(f"  ECHEC ({introuvable} failures)")
else:
    print(f"  ALL PASS (0 failures, {total} checks)")
sys.exit(1 if introuvable else 0)
