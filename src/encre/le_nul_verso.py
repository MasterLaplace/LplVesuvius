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

SEGMENTS = ("20260325000000-w046_20260325",
            "20260210000000-w058_2026021020",
            "20260115000001-w056_2026011514")
"""Les trois segments `w` de `PHerc0139` sur lesquels le contrôle tourne.

⚠⚠ TROIS, ET LA LISTE EST DU CODE PLUTÔT QU'UNE BOUCLE DE TERMINAL. Un seul segment ne peut
pas dire si un résultat est une propriété du **détecteur** ou un accident de **cette
fenêtre-là** ; et une liste tapée au terminal se perd, donc personne ne peut refaire la mesure
sur exactement le même corpus.

⚠ Ils partagent le rouleau, la campagne de scan et la taille de voxel : ce qui varie d'un à
l'autre est la région, ce qui est précisément la chose qu'on veut faire varier."""

COUCHES_LUES = 26
"""Ce que le détecteur GP-2023 lit d'une pile (`12` §1, `09` §12). ⚠ C'est une propriété du
modèle, pas un réglage : les deux fenêtres doivent en lire **le même nombre**, sinon on
comparerait deux quantités d'information."""

SURFACE_DANS_LA_FENETRE = 17
"""Où tombe la surface dans la fenêtre du détecteur, en couches depuis son début.

⚠ Dérivé de la convention publiée et non posé : `12` établit qu'une pile de 65 couches porte la
surface à la **32** et que le détecteur lit **15 à 40** — donc la surface est à la 17ᵉ des 26.
La reprendre telle quelle est ce qui rend notre fenêtre « sur face » comparable à la leur."""


VERROU = RACINE / "docs" / "mesures" / ".le_nul_verso.verrou"


def prendre_le_verrou():
    """
    @brief Refuse de démarrer si une campagne écrit déjà — et rend le fichier verrou ouvert.

    ⚠⚠⚠ ÉCRIT PARCE QUE ÇA VIENT D'ARRIVER, POUR LA TROISIÈME FOIS DANS CE DÉPÔT. Deux
    campagnes ont tourné en parallèle sur les mêmes JSON et les mêmes cartes `.npy` : la
    première avait survécu à un `nohup` que je croyais mort, parce que `ps -C python` ne voit
    pas un processus nommé `python3` — une vérification incapable de détecter ce qu'elle
    cherchait. Le résultat aurait été des cartes moitié d'un run, moitié de l'autre, avec des
    résumés parfaitement plausibles.

    ⚠ Le verrou est tenu par le NOYAU (`flock`), pas par un fichier témoin : un témoin survit à
    un `kill -9` et bloque alors tout run suivant, ce qui pousse à le supprimer à la main, ce
    qui le rend inutile. Un verrou `flock` est relâché quand le processus meurt, quelle que soit
    la façon dont il meurt.
    """
    import fcntl
    import os
    # ⚠ `--tous` tient déjà le verrou pour toute la campagne et lance ses trois mesures en
    # sous-processus : sans cette porte, l'enfant se ferait refuser par son propre parent.
    if os.environ.get("LPL_NUL_VERSO_VERROU") == "1":
        return None
    VERROU.parent.mkdir(parents=True, exist_ok=True)
    fh = VERROU.open("w")
    try:
        fcntl.flock(fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        raise SystemExit(
            f"une autre campagne écrit déjà dans {VERROU.parent} — refusé.\n"
            "  ⚠ Deux campagnes concurrentes mélangeraient les cartes de deux runs sans que "
            "rien ne le dise. Attendre, ou tuer l'autre PAR SON PID.") from None
    fh.write(str(__import__("os").getpid()))
    fh.flush()
    return fh


def _lancer(argv: list[str], timeout: float = 7200.0) -> tuple[int, str]:
    r = subprocess.run(argv, capture_output=True, text=True, cwd=RACINE, timeout=timeout)
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def profil_de_profondeur(couches: Path, taille: int) -> dict | None:
    """
    @brief Les DEUX profils par couche, normalisés — intensité et contraste local.

    ⚠⚠⚠ ET C'EST L'INTENSITÉ QUI LOCALISE ICI, PAS LE CONTRASTE. `depth_profile.py` porte la
    raison, écrite dans le module que ce fichier appelait déjà : *« sur les piles à 7,91 µm les
    deux coïncident ; sur un volume à 2,4 µm qui résout les fibres, le contraste devient un U —
    maximal aux DEUX bords, minimal dans la feuille — parce qu'il suit les interfaces et le
    bruit, pas la matière »*. Les surface-volumes de `PHerc0139` sont à **2,399 µm**.

    ⚠⚠ Je lisais la mauvaise série, et le prix est mesuré : sur `w058` et `w056` le contraste
    pique aux couches **0** et **104** d'une pile de 109, avec son minimum au milieu. La fenêtre
    « face » tombait donc sur une **interface de bord**, et la fenêtre « nulle », choisie au
    minimum, tombait **dans la feuille**. Le couple était inversé, et il rendait une AUC de 0,50
    que j'ai failli publier comme « le détecteur ne distingue pas le papyrus du vide ».

    ⚠ Le contraste reste lu et gardé : c'est le diagnostic qui montre le U, donc ce qui rend la
    correction vérifiable au lieu d'être affirmée.
    """
    code, sortie = _lancer(["uv", "run", "python", str(PROFIL), str(couches),
                            "--top", "0", "--left", "0", "--size", str(taille)], 1800)
    if code != 0:
        return None
    # ⚠ Motif ANCRÉ sur les deux étiquettes de la même ligne (`couche N contraste C moyenne M`) :
    # un parseur qui n'en lit qu'une prend la première venue, et c'est exactement ce qui vient
    # de coûter deux mesures.
    valeurs: list[tuple[int, float, float]] = []
    for ligne in sortie.splitlines():
        m = ligne.split()
        if len(m) >= 6 and m[0] == "couche" and m[2] == "contraste" and m[4] == "moyenne":
            try:
                valeurs.append((int(m[1]), float(m[3]), float(m[5])))
            except ValueError:
                continue
    if not valeurs:
        return None
    valeurs.sort()
    return dict(contraste=[c for _, c, _ in valeurs], moyenne=[m for _, _, m in valeurs])


def pic_sur_la_feuille(pic: int, couches: int) -> bool:
    """
    @brief Le pic de contraste tombe-t-il sur la feuille TRACÉE, ou sur une spire voisine ?

    ⚠⚠⚠ LA GARDE QUI MANQUAIT, ET ELLE A REFUSÉ DEUX MESURES DÉJÀ PAYÉES. Un surface-volume est
    construit AUTOUR de la feuille suivie : elle est au milieu de la pile, et les bords sont à
    une demi-épaisseur d'écart, donc chez les VOISINES. Sur `w046` le profil pique à la couche
    56 d'une pile de 109 — au milieu, ce à quoi ressemble une feuille. Sur `w058` et `w056` il
    pique à **0** et à **104**, avec son MINIMUM au milieu : la feuille tracée y est sans
    structure et ce qu'on voit est la spire d'à côté.

    ⚠⚠ Conséquence, et c'est pourquoi c'est une garde et pas une note : la fenêtre « face » y
    tombait sur une voisine et la fenêtre « nulle » sur la feuille elle-même. Le couple
    face/vide était **inversé**, et l'AUC de 0,50 qu'il rendait n'était pas « le détecteur ne
    distingue pas le papyrus du vide » mais « deux fenêtres sans structure se ressemblent ».
    J'ai failli publier la première phrase.

    ⚠ La moitié centrale, pas un voisinage étroit : la feuille n'est pas exactement au milieu
    (le suivi la décale), mais un pic dans le quart extérieur ne peut pas être elle.
    """
    return abs(pic - (couches - 1) / 2.0) < couches / 4.0


def fenetres(profil: dict) -> dict:
    """
    @brief Les deux `--start-layer` : sur la feuille, et dans le vide le plus creux.

    ⚠⚠⚠ LES DEUX FENÊTRES SE CHOISISSENT SUR L'INTENSITÉ, jamais sur le contraste. Voir
    `profil_de_profondeur` : à 2,4 µm le contraste est un **U** dont les maxima sont les deux
    interfaces de la feuille et dont le minimum est son intérieur, donc s'en servir met la face
    au bord et le vide dans le papyrus. Le contraste reste calculé et gardé pour que ce U soit
    **visible** dans le dossier plutôt que raconté.

    ⚠⚠ LA FENÊTRE NULLE EST CHOISIE PAR LE MINIMUM DE MATIÈRE, pas par un demi-pas nominal. Un
    demi-pas suppose un empilement régulier ; un minimum mesuré ne suppose rien, et il tombe là
    où il n'y a effectivement rien.

    ⚠ Les deux fenêtres lisent `COUCHES_LUES` couches et restent dans la pile. Une fenêtre qui
    déborderait lirait des zéros de bord, ce qui ferait passer un artefact de découpe pour une
    absence d'encre.
    """
    intensite, contraste = profil["moyenne"], profil["contraste"]
    n = len(intensite)
    if n < COUCHES_LUES + 4:
        return {}
    pic = max(range(n), key=lambda i: intensite[i])
    debut_face = max(0, min(n - COUCHES_LUES, pic - SURFACE_DANS_LA_FENETRE))

    def moyenne(serie: list[float], d: int) -> float:
        return float(np.mean(serie[d:d + COUCHES_LUES]))

    candidats = [d for d in range(0, n - COUCHES_LUES + 1)
                 # ⚠ La fenêtre nulle ne doit pas CHEVAUCHER celle de la face, sinon elle
                 # lirait la face elle-même et le contrôle serait circulaire.
                 if d >= debut_face + COUCHES_LUES or d + COUCHES_LUES <= debut_face]
    if not candidats:
        return {}
    debut_nul = min(candidats, key=lambda d: moyenne(intensite, d))
    return dict(pic=pic, debut_face=debut_face, debut_nul=debut_nul,
                intensite_face=moyenne(intensite, debut_face),
                intensite_nul=moyenne(intensite, debut_nul),
                contraste_face=moyenne(contraste, debut_face),
                contraste_nul=moyenne(contraste, debut_nul),
                pic_contraste=max(range(n), key=lambda i: contraste[i]),
                couches=n, pic_central=pic_sur_la_feuille(pic, n))


def niveau_le_plus_grossier(zarr: str, plafond: int = 12) -> tuple[int, list[int]]:
    """
    @brief Le niveau de pyramide le plus grossier publié, et sa forme.

    ⚠⚠ DÉCOUVERT, PAS FIGÉ. Les volumes de surface n'ont pas tous la même profondeur de
    pyramide — `w046` s'arrête au niveau 3, `w058` va jusqu'au 5 — donc un niveau écrit en dur
    chercherait au mauvais endroit sur la moitié des segments, et l'échelle de retour au
    niveau 0 serait fausse d'un facteur quatre.
    """
    import json as _json
    import sys as _sys
    _sys.path.insert(0, str(RACINE / "src" / "commun"))
    from zarr_depth import BUCKET, get  # noqa: PLC0415

    dernier, forme = 0, None
    for lvl in range(plafond):
        try:
            b = _json.loads(get(f"{BUCKET}/{zarr.rstrip('/')}/{lvl}/.zarray", 30))
        except Exception:  # noqa: BLE001 — l'absence d'un niveau EST la réponse
            break
        dernier, forme = lvl, list(b["shape"])
    if forme is None:
        raise SystemExit(f"aucun niveau lisible sous {zarr}")
    return dernier, forme


def chercher_fenetre(zarr: str, taille: int = 512, tuiles: int = 8) -> dict:
    """
    @brief Où poser la fenêtre : la tuile dont la FEUILLE est centrée dans la pile.

    ⚠⚠⚠ LE PIÈGE Nº27 DE CE DÉPÔT, PUIS SA VERSION PROFONDE. Un volume est surtout du
    remplissage, donc une fenêtre choisie au jugé a une chance sur quinze de contenir du
    papyrus — c'est le premier piège, et chercher la tuile la plus **pleine** le règle. Mais
    « pleine » ne veut pas dire « la feuille tracée est là » : un surface-volume est construit
    autour de la feuille, elle est au milieu de la pile, et une tuile peut être pleine de bout
    en bout avec son pic de matière à la couche 93 sur 109. Mesuré sur `w046` : la tuile la plus
    pleine du plan pique à **93**, donc la fenêtre « face » y tombe sur une spire voisine.

    ⚠⚠ LE SCORE EST DONC LE MÊME CRITÈRE QUE LA GARDE, et c'est délibéré : chercher sur un
    critère et refuser sur un autre garantit de trouver ce qui sera refusé. On ne retient que
    les tuiles dont le pic d'intensité tombe dans la moitié centrale, et parmi elles la plus
    chargée.

    ⚠ Une seule couche ne suffit donc plus : le profil est accumulé **couche par couche** au
    niveau le plus grossier, où le plan tient en quelques mégapixels. Rien n'est gardé en
    mémoire au-delà de `couches × tuiles` moyennes.
    """
    import tifffile

    niveau, forme = niveau_le_plus_grossier(zarr)
    facteur = 2 ** niveau
    # ⚠ La tuile de recherche a la TAILLE DE LA FENÊTRE ramenée à ce niveau : chercher avec une
    # tuile plus grande trouverait une région globalement pleine dont la fenêtre réelle pourrait
    # tomber dans un trou.
    pas = max(2, taille // facteur)
    with tempfile.TemporaryDirectory() as tmp:
        vue = Path(tmp) / "vue"
        code, texte = _lancer(
            ["uv", "run", "python", str(EXTRACTEUR), zarr, "--sortie", str(vue),
             "--level", str(niveau), "--top", "0", "--left", "0",
             "--hauteur", str(forme[1]), "--largeur", str(forme[2])], 5400)
        if code != 0:
            raise SystemExit(f"vue d'ensemble échouée : {texte.strip()[-200:]}")
        fichiers = sorted(vue.glob("*.tif"), key=lambda q: int(q.stem))
        if not fichiers:
            raise SystemExit("vue d'ensemble vide")
        profils = None
        for k, fichier in enumerate(fichiers):
            plan = tifffile.imread(fichier)
            lignes, colonnes = plan.shape[0] // pas, plan.shape[1] // pas
            if lignes == 0 or colonnes == 0:
                raise SystemExit(f"plan {plan.shape} trop petit pour des tuiles de {pas}")
            bloc = plan[:lignes * pas, :colonnes * pas].astype(np.float32)
            moyennes = bloc.reshape(lignes, pas, colonnes, pas).mean(axis=(1, 3))
            if profils is None:
                profils = np.zeros((len(fichiers), lignes, colonnes), dtype=np.float32)
            profils[k] = moyennes

    n = profils.shape[0]
    pics = profils.argmax(axis=0)
    charge = profils.mean(axis=0)
    central = np.abs(pics - (n - 1) / 2.0) < n / 4.0
    # ⚠⚠ Aucune tuile centrée est un FAIT sur le segment, pas un défaut du chercheur : la trace
    # y passe hors du milieu de sa propre pile partout. On le dit, et la garde refusera ensuite.
    admis = np.where(central, charge, -1.0)
    i, j = np.unravel_index(int(admis.argmax()), admis.shape)
    return dict(top=int(i) * pas * facteur, left=int(j) * pas * facteur,
                part_matiere=float(charge[i, j] / max(1e-9, float(charge.max()))),
                pic_tuile=int(pics[i, j]), couches_vues=n,
                tuiles_centrees=int(central.sum()), tuiles=int(central.size),
                niveau_cherche=niveau, vue=[int(x) for x in profils.shape[1:]])


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


def aire_sous_la_courbe(a: np.ndarray, b: np.ndarray) -> float:
    """
    @brief P(une valeur de `a` dépasse une valeur de `b`) — la séparabilité, sans seuil.

    ⚠⚠⚠ POURQUOI CETTE GRANDEUR ET PAS LES DEUX PRÉCÉDENTES. Le contrôle comparait un
    **niveau** (les médianes) et une **dispersion** (les étendues), donc deux nombres dont
    aucun ne répond à la question posée : *peut-on, en regardant une valeur, dire si elle
    vient de la face ou du vide ?* Une médiane qui se déplace n'est utile que si les
    distributions ne se recouvrent pas, et deux étendues égales n'interdisent pas une
    séparation parfaite. L'aire sous la courbe répond directement, elle est **sans seuil**, et
    elle est dans l'unité que le domaine publie déjà pour l'encre — donc comparable.

    ⚠ Rangs MOYENS sur les ex æquo : les sorties du détecteur se répètent, et des rangs
    arbitraires y feraient dépendre le résultat de l'ordre du tableau.

    ⚠ Écrite ici plutôt qu'importée de `scipy`, comme `rho_de_rangs` de
    `le_bruit_de_lechantillon.py` et pour la même raison : la mesure publiée doit être lisible
    dans l'arbre, pas déléguée à une version de bibliothèque que personne ne note.
    """
    a = np.asarray(a, dtype=float).ravel()
    b = np.asarray(b, dtype=float).ravel()
    na, nb = a.size, b.size
    if na == 0 or nb == 0:
        return float("nan")
    tout = np.concatenate([a, b])
    ordre = np.argsort(tout, kind="mergesort")
    trie = tout[ordre]
    rangs = np.empty(tout.size, dtype=float)
    i = 0
    while i < trie.size:
        j = i
        while j + 1 < trie.size and trie[j + 1] == trie[i]:
            j += 1
        rangs[ordre[i:j + 1]] = 0.5 * (i + j) + 1.0
        i = j + 1
    somme_a = float(rangs[:na].sum())
    return (somme_a - na * (na + 1) / 2.0) / (na * nb)


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
        # ⚠ Le MIROIR, et il n'est pas redondant : la première part se lit « le vide déborde-t-il
        # sur la face », la seconde « la face dépasse-t-elle le vide ». Un détecteur aveugle rend
        # 50 % aux deux ; un détecteur qui discrimine rend peu à l'une et beaucoup à l'autre.
        part_face_au_dessus_mediane_nul=float((a1 > float(np.median(b1))).mean()),
        auc_face_contre_nul=aire_sous_la_courbe(a1, b1),
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
        if not f["pic_central"]:
            # ⚠⚠ REFUSÉ, ET LE REFUS EST ÉCRIT PLUTÔT QUE SILENCIEUX. Deux inférences coûtent
            # huit minutes ; les dépenser sur une fenêtre hors feuille produirait un couple
            # face/vide inversé, dont le résultat *ressemble* à une mesure. Le dossier garde le
            # profil et la raison, donc le prochain lecteur voit pourquoi ce segment manque.
            return dict(segment=segment, zarr=zarr, top=top, left=left, taille=taille,
                        profil=profil["contraste"], profil_intensite=profil["moyenne"], **f,
                        refus="pic de contraste hors de la moitié centrale : la fenêtre ne "
                              "tombe pas sur la feuille tracée mais sur une spire voisine")
        # ⚠⚠ LES CARTES SONT GARDÉES, et c'est `--out` qui écrit un `.npy` : les valeurs
        # BRUTES, pas une image déjà normalisée. Une figure qui rendrait chaque carte à sa
        # propre échelle ferait passer le bruit du nul pour de l'encre — c'est précisément la
        # panne que ce contrôle existe pour montrer, donc l'échelle doit être commune, donc il
        # faut les valeurs.
        CARTES.mkdir(parents=True, exist_ok=True)
        face = _inference(couches, f["debut_face"], taille, CARTES / f"{segment}_face.npy")
        nul = _inference(couches, f["debut_nul"], taille, CARTES / f"{segment}_nul.npy")
    out = dict(segment=segment, zarr=zarr, top=top, left=left, taille=taille,
               profil=profil["contraste"], profil_intensite=profil["moyenne"],
               **f, face=face, nul=nul)
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


def _verifier_tous(lots: list[dict]) -> int:
    """
    @brief La batterie sur TOUS les segments mesurés, plus ce qui ne se voit qu'en les réunissant.

    ⚠⚠ Un seul segment ne peut pas dire si le résultat est une propriété du détecteur ou un
    accident de cette fenêtre-là. C'est exactement pourquoi `C2` en demande trois, et pourquoi
    la batterie doit refuser de conclure sur un.
    """
    total = 0
    for r in lots:
        print(f"\n=== {r.get('segment')} ===")
        total += _verifier(r)
    if len(lots) >= 2:
        print(f"\net sur les {len(lots)} segments réunis")
        echecs = 0

        def v(nom, ok, detail=""):
            nonlocal echecs
            print(f"  {'ok  ' if ok else 'FAIL'}  {nom}" + (f"   [{detail}]" if detail else ""))
            if not ok:
                echecs += 1

        rapports = [x["rapport_etendue"] for x in lots if x.get("rapport_etendue")]
        sauts = [x["face"]["mediane"] - x["nul"]["mediane"] for x in lots
                 if x.get("face") and x.get("nul") and not x["face"].get("echec")]
        # ⚠⚠⚠ LE RESULTAT N'EST UNE PROPRIETE DU DETECTEUR QUE S'IL TIENT SUR TOUS. Ecrit pour
        # tomber si un segment se comportait autrement -- ce serait alors une propriete de la
        # FENETRE, et il faudrait chercher laquelle.
        v("la dispersion ne s'effondre sur AUCUN segment",
          all(x > 0.8 for x in rapports),
          " · ".join(f"{x:.2f}" for x in rapports))
        v("... et le niveau se déplace sur TOUS",
          all(x > 0.5 for x in sauts), " · ".join(f"{x:+.2f}" for x in sauts))
        total += echecs
    print()
    print(f"  {'ECHEC' if total else 'ALL PASS'} ({total} failures, {len(lots)} segment(s))")
    return total


def _verifier(r: dict | None = None) -> int:
    echecs = comptees = 0

    def v(nom, ok, detail=""):
        nonlocal echecs, comptees
        comptees += 1
        print(f"  {'ok  ' if ok else 'FAIL'}  {nom}" + (f"   [{detail}]" if detail else ""))
        if not ok:
            echecs += 1

    # ⚠⚠ LE CHOIX DES FENÊTRES, testé sur un profil FABRIQUÉ dont on connaît la réponse — et
    # fabriqué ADVERSAIRE : la feuille est au milieu en intensité pendant que le contraste
    # dessine un U dont les maxima sont aux deux bords. C'est la forme RÉELLE mesurée sur
    # `w058` et `w056` à 2,4 µm, et c'est elle qui a inversé le couple face/vide. Un profil
    # gentil (une bosse dans les deux séries) aurait passé la version fausse comme la juste.
    feuille = [0.02] * 109
    for i in range(30, 81):
        feuille[i] = 1.0 - abs(i - 55) * 0.01
    u = [1.0 - min(i, 108 - i) / 54.0 for i in range(109)]
    faux = dict(moyenne=feuille, contraste=u)
    f = fenetres(faux)
    v("la fenêtre sur face suit l'INTENSITÉ, pas le U du contraste",
      f["pic"] == 55 and f["debut_face"] == 55 - SURFACE_DANS_LA_FENETRE,
      f"pic d'intensité {f['pic']} (contraste {f['pic_contraste']}), début {f['debut_face']}")
    # ⚠⚠⚠ LE CONTRÔLE QUI AURAIT ATTRAPÉ LA PANNE. Sur ce profil, le maximum de contraste est
    # au bord ; si le choix le suivait, la fenêtre face commencerait à 0 ou à 83.
    v("... et le maximum de contraste est bien AU BORD dans ce piège",
      f["pic_contraste"] in (0, 108), f"pic de contraste {f['pic_contraste']}")
    v("... et la fenêtre nulle tombe là où il y a le moins de MATIÈRE",
      f["intensite_nul"] < 0.1 * f["intensite_face"],
      f"intensité {f['intensite_nul']:.3f} contre {f['intensite_face']:.3f}")
    v("... et elle ne chevauche PAS celle de la face",
      f["debut_nul"] >= f["debut_face"] + COUCHES_LUES
      or f["debut_nul"] + COUCHES_LUES <= f["debut_face"],
      f"{f['debut_face']}..{f['debut_face'] + COUCHES_LUES} contre "
      f"{f['debut_nul']}..{f['debut_nul'] + COUCHES_LUES}")
    v("... et les deux restent dans la pile",
      f["debut_face"] >= 0 and f["debut_nul"] + COUCHES_LUES <= 109, "pile de 109")
    # ⚠⚠ LA GARDE, testée dans les DEUX sens : elle doit accepter une feuille au milieu et
    # refuser un pic de bord. Une garde qui n'accepte rien protège autant qu'un mur sans porte.
    v("la garde accepte une feuille au milieu de la pile", f["pic_central"], f"pic {f['pic']}")
    bord = dict(moyenne=[1.0 - i / 108.0 for i in range(109)], contraste=[0.5] * 109)
    v("... et refuse un pic d'intensité au bord (feuille hors fenêtre)",
      not fenetres(bord)["pic_central"], f"pic {fenetres(bord)['pic']}")
    v("... et la moitié centrale est bien ce qu'elle nomme",
      pic_sur_la_feuille(54, 109) and not pic_sur_la_feuille(20, 109)
      and not pic_sur_la_feuille(90, 109),
      "54 dedans, 20 et 90 dehors")
    # ⚠⚠ Une pile trop courte pour deux fenêtres disjointes rend {} plutôt qu'un chevauchement.
    # ⚠ Écrit d'abord avec un `or True` qui le rendait incapable d'échouer — le défaut que ce
    # dépôt attrape en boucle, commis ici dans le fichier qui existe pour un contrôle.
    plat = dict(moyenne=[0.5] * 30, contraste=[0.5] * 30)
    v("une pile trop courte ne rend AUCUNE fenêtre plutôt que deux qui se chevauchent",
      fenetres(plat) == {}, str(fenetres(plat)))
    court = fenetres(dict(moyenne=[0.5] * 40, contraste=[0.5] * 40))
    v("... et si elle en rend deux, elles restent disjointes",
      not court or court["debut_nul"] >= court["debut_face"] + COUCHES_LUES
      or court["debut_nul"] + COUCHES_LUES <= court["debut_face"], str(court))
    # ⚠⚠ L'AUC, testée sur trois cas dont on connaît la réponse exacte. Sans ça « 0,50 » ne
    # voudrait rien dire : une AUC mal écrite rend elle aussi un nombre entre 0 et 1.
    v("l'AUC vaut 1 quand les deux populations sont séparées",
      abs(aire_sous_la_courbe(np.arange(10.0, 20.0), np.arange(10.0)) - 1.0) < 1e-12)
    v("... 0 quand elles le sont dans l'autre sens",
      abs(aire_sous_la_courbe(np.arange(10.0), np.arange(10.0, 20.0))) < 1e-12)
    v("... et exactement 0,5 sur deux populations IDENTIQUES (ex æquo compris)",
      abs(aire_sous_la_courbe(np.arange(10.0), np.arange(10.0)) - 0.5) < 1e-12)

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
    p.add_argument("--chercher", action="store_true",
                   help="chercher la fenêtre la plus pleine au lieu de --top/--left")
    p.add_argument("--rederiver", action="store_true",
                   help="recalculer ce qui se déduit des cartes gardées, sans refaire l'inférence")
    p.add_argument("--tous", action="store_true",
                   help="mesurer les trois segments de SEGMENTS, l'un après l'autre")
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--json", type=Path)
    a = p.parse_args()

    if a.rederiver:
        # ⚠⚠ SANS `--json`, TOUS LES SEGMENTS. Le défaut visait un fichier qui n'existe plus
        # (renommé par segment), donc un `--rederiver` nu échouait ; et surtout, n'en toucher
        # qu'un laisserait les autres porter d'anciennes grandeurs sans que rien ne le dise —
        # la panne exacte que `--verifier` a été élargi pour éviter.
        cibles = ([a.json] if a.json
                  else sorted((RACINE / "docs" / "mesures").glob("le_nul_verso*.json")))
        for cible in cibles:
            d = json.loads(cible.read_text())
            d.update(deriver_des_cartes(d["segment"]))
            cible.write_text(json.dumps(d, indent=2, ensure_ascii=False), encoding="utf-8")
            print(f"{d['segment']}")
            print(f"  corrélation face/vide            {d.get('correlation_face_nul'):+.3f}")
            print(f"  AUC face contre vide             {d.get('auc_face_contre_nul'):.3f}")
            print(f"  part du vide au-dessus de la face {100 * d.get('part_nul_au_dessus_mediane_face', 0):5.1f} %")
            print(f"  part de la face au-dessus du vide {100 * d.get('part_face_au_dessus_mediane_nul', 0):5.1f} %")
            print(f"  écrit : {cible}")
        return 0

    if a.tous:
        _verrou = prendre_le_verrou()  # noqa: F841 — relâché à la mort du processus
        # ⚠ SÉQUENTIEL, pas en parallèle : chaque segment fait deux inférences sur le
        # processeur, et trois campagnes concurrentes se disputeraient les mêmes cœurs pour
        # finir plus tard. Ce dépôt a par ailleurs déjà payé deux écrivains simultanés.
        codes = []
        for segment in SEGMENTS:
            court = segment.split("_")[0]
            cible = RACINE / "docs" / "mesures" / f"le_nul_verso_{court}.json"
            print(f"\n########## {segment}")
            enfant = dict(__import__("os").environ, LPL_NUL_VERSO_VERROU="1")
            codes.append(subprocess.run(
                ["uv", "run", "python", __file__, "--segment", segment, "--chercher",
                 "--json", str(cible)], cwd=RACINE, env=enfant).returncode)
        # ⚠ Un refus (code 3) n'est pas une panne : c'est le contrôle qui fait son travail.
        # Les confondre ferait échouer la campagne entière sur un segment que le corpus ne
        # permet pas de mesurer, et pousserait à retirer la garde.
        pannes = [c for c in codes if c not in (0, 3)]
        print(f"\ncampagne : {codes.count(0)} mesuré(s), {codes.count(3)} refusé(s), "
              f"{len(pannes)} en panne")
        return 1 if pannes else 0

    if a.verifier and not a.json:
        # ⚠⚠ TOUS LES SEGMENTS MESURÉS, pas seulement le premier. `C2` demande **trois** segments
        # `w`, et une batterie qui n'en lirait qu'un dirait « le contrôle tient » sur un cas.
        fichiers = sorted((RACINE / "docs" / "mesures").glob("le_nul_verso*.json"))
        lots = [json.loads(f.read_text()) for f in fichiers]
        return 1 if _verifier_tous(lots) else 0

    zarr = a.zarr or (f"PHerc0139/segments/{a.segment}/surface-volumes/"
                      "2.399um-0.22m-78keV-volume-20260102150214.zarr")
    top, left = a.top, a.left
    if a.chercher:
        f = chercher_fenetre(zarr, a.taille)
        top, left = f["top"], f["left"]
        print(f"  fenêtre trouvée : top {top}, left {left} "
              f"({100 * f['part_matiere']:.0f} % de matière, cherchée au niveau "
              f"{f['niveau_cherche']})")
    _verrou = prendre_le_verrou()  # noqa: F841 — relâché à la mort du processus
    r = mesurer(a.segment, zarr, top, left, a.taille)
    print(f"{r['segment']} — pile de {r['couches']} couches, pic à {r['pic']}")
    print(f"  fenêtre face : {r['debut_face']}..{r['debut_face'] + COUCHES_LUES}"
          f"   contraste moyen {r['contraste_face']:.3f}")
    print(f"  fenêtre nulle: {r['debut_nul']}..{r['debut_nul'] + COUCHES_LUES}"
          f"   contraste moyen {r['contraste_nul']:.3f}")
    if r.get("refus"):
        # ⚠⚠ LE REFUS EST UNE SORTIE, PAS UNE EXCEPTION. Il porte le profil et sa raison, donc
        # le prochain lecteur voit pourquoi ce segment manque au lieu de trouver un trou. Le
        # code 3 est celui que ce dépôt utilise déjà pour « hors domaine » (`run_proximity.sh`).
        print(f"  REFUSÉ — {r['refus']}", file=sys.stderr)
        if a.json:
            a.json.parent.mkdir(parents=True, exist_ok=True)
            a.json.write_text(json.dumps(r, indent=2, ensure_ascii=False), encoding="utf-8")
            print(f"\nécrit : {a.json}")
        return 3
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
