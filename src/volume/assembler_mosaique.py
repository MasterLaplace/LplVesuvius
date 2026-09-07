#!/usr/bin/env python3
"""Empiler les cartes d'encre publiees d'un rouleau, une par spire, en une seule image.

⚠⚠ CE QUE CETTE IMAGE EST. Chaque bande est une spire deroulee par l'equipe du concours
et publiee telle quelle. Nous ne deroulons rien ici : nous ORDONNONS. L'image ne devient
un rouleau que parce que les spires se suivent sans trou, et c'est la seule chose que ce
fichier ajoute. Ecrit ici parce qu'une image assemblee ne porte pas son auteur.

⚠⚠ CE QU'ELLE N'EST PAS -- et c'est la limite a ne pas laisser tomber. Les bandes sont
alignees a GAUCHE, pas RECALEES. Deux spires voisines ne commencent pas au meme endroit
du rouleau : l'origine du depliage est propre a chaque segment. Donc une colonne de
l'image ne correspond PAS a une meme position sur le rouleau d'une bande a l'autre. Une
image qui aurait l'air d'un rouleau continu alors que ses colonnes ne se correspondent
pas serait exactement le genre de resultat qui trompe -- d'ou la reglette et l'ecart de
largeur imprimes, qui rendent le desalignement VISIBLE au lieu de le cacher.

⭐ A quoi ca sert, au-dela de l'image : c'est la REFERENCE. Une chaine automatique qui
pretend derouler un rouleau doit produire ceci, sans les 775 heures d'annotation. Sans
reference assemblee, « ca marche » n'avait rien a quoi se comparer.

Usage :
    uv run python src/volume/assembler_mosaique.py data/mosaique/PHerc0172/index.tsv \\
        --sortie docs/images/mosaique_PHerc0172.png --rouleau PHerc0172
    uv run python src/volume/assembler_mosaique.py --verifier
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]

# Une bande plus haute que ca coute plus qu'elle ne montre a l'echelle d'un rouleau
# entier ; en dessous, les lettres disparaissent. Mesure, pas gout : les ds8 publies
# font ~2000 px de haut, donc /2 laisse une lettre a ~10 px.
HAUTEUR_BANDE = 1000
MARGE = 6


# Interligne d'un rouleau d'Herculanum : 5 a 7 mm mesures sur le segment de `10`. On
# ouvre un peu (3 a 12 mm) pour ne pas exclure une main plus serree ou plus large.
INTERLIGNE_MM = (3.0, 12.0)


def score_de_lignes(im, lag_min: int = 4, lag_max: int | None = None) -> tuple[float, str, int]:
    """A quel point cette bande porte-t-elle des LIGNES d'ecriture ?

    ⚠⚠ Pourquoi ce score existe a cote de σ. Le contraste ne distingue pas du texte d'un
    mouchetis : une carte d'encre bruitee et une carte d'encre ecrite ont le meme ecart-type.
    Mesure, pas opinion : la spire la plus contrastee de PHerc0172 (081, σ 58,6) est
    speckle, et des spires a σ plus faible portent des lignes nettes. Trier sur σ aurait
    donc publie le morceau le moins lisible en l'appelant le meilleur.

    Ce que le score voit : une ecriture est PERIODIQUE dans la direction perpendiculaire
    aux lignes. On projette la bande sur chacun des deux axes et on cherche le pic
    d'autocorrelation du profil, hors lag 0. Un mouchetis n'a pas de periode ; du texte en a.

    ⚠ On ne connait pas l'orientation d'avance -- une bande peut avoir ses lignes dans un
    sens ou dans l'autre -- donc les deux axes sont essayes et le meilleur gagne. Choisir
    un axe a priori aurait note zero toutes les bandes tournees de 90 degres.

    ⚠⚠ LES BORNES DE LAG DOIVENT VENIR DE LA PHYSIQUE, PAS DE LA COMMODITE. Premiere
    version : lag minimum fixe a 4 px « pour eviter le grain ». Elle a elu la spire 093
    avec une periodicite de 0,987 a un interligne de 4 px -- soit 0,4 mm a cette
    resolution, dix fois trop serre pour de l'ecriture. Ce n'etait pas du texte, c'etait
    le grain du JPEG et du reechantillonnage, et le score le notait mieux que n'importe
    quelle vraie ligne. Un seuil choisi pour la commodite avait donc produit un classement
    entierement faux, sans rien qui ait l'air faux. Passer les bornes calculees depuis
    `INTERLIGNE_MM` et la resolution est ce qui rend le classement defendable.

    Retourne (score, axe gagnant, interligne en pixels).
    """
    import numpy as np

    a = np.asarray(im, dtype=np.float32)
    meilleur = (0.0, "aucun", 0)
    for axe, nom in ((1, "lignes horizontales"), (0, "lignes verticales")):
        profil = a.mean(axis=axe)
        # ⚠⚠ Lisser AVANT de correler, a l'echelle sous l'interligne cherche. Borner les
        # lags ne suffit pas : un grain de periode 3 a des harmoniques a 21, 30, 42 -- donc
        # il gagne AUSSI a l'interieur de la fenetre plausible, en s'y faisant passer pour
        # de l'ecriture. Teste : sans ce lissage, un melange grain-3 + lignes-30 borne sur
        # [20,45] elit 21 px. Un passe-bas a l'echelle du grain supprime la famille entiere
        # d'harmoniques, et la vraie ligne ressort.
        if lag_min > 4:
            k = max(2, lag_min // 3)
            noyau = np.ones(k, dtype=np.float32) / k
            profil = np.convolve(profil, noyau, mode="same")
        profil = profil - profil.mean()
        if profil.size < 64 or not np.any(profil):
            continue
        n = profil.size
        # ⚠ Les lags plausibles sont bornes : en dessous de 4 px on mesure le grain du
        # JPEG, au-dela du quart de la bande on mesure la forme du fragment, pas l'ecriture.
        ac = np.correlate(profil, profil, mode="full")[n - 1:]
        ac = ac / (ac[0] if ac[0] else 1.0)
        lo = max(2, lag_min)
        hi = min(n // 2, lag_max if lag_max else max(lo + 4, n // 4))
        if hi <= lo + 1:
            continue
        lag = int(np.argmax(ac[lo:hi])) + lo
        if ac[lag] > meilleur[0]:
            meilleur = (float(ac[lag]), nom, lag)
    return meilleur


def lire_index(chemin: Path) -> list[tuple[int, str, Path]]:
    """Lire l'index (spire, segment, fichier), trie par spire croissante."""
    lignes = []
    for ligne in chemin.read_text(encoding="utf-8").splitlines():
        if not ligne.strip() or ligne.startswith("#"):
            continue
        champs = ligne.split("\t")
        if len(champs) < 3:
            continue
        lignes.append((int(champs[0]), champs[1], resoudre(champs[2], chemin)))
    return sorted(lignes, key=lambda t: t[0])


def resoudre(brut: str, index: Path) -> Path:
    """Resoudre un chemin d'index : tel quel, sinon a cote de l'index, sinon depuis la racine.

    ⚠ Un index ecrit par un script du depot porte des chemins RELATIFS A LA RACINE, mais
    ce fichier tourne depuis `inference/` (le seul environnement qui a Pillow). Sans cette
    resolution, l'assemblage echoue en disant « fichier introuvable » sur un fichier qui
    est bel et bien la -- panne qui se lit comme un telechargement rate.
    """
    c = Path(brut)
    if c.exists():
        return c
    for base in (index.resolve().parent, RACINE):
        if (base / brut).exists():
            return base / brut
    return c


def trous(spires: list[int]) -> list[int]:
    """Les numeros de spire manquants entre la premiere et la derniere.

    ⚠ Un trou n'invalide pas l'image, mais il doit etre DIT : un empilement sans trou
    est un rouleau, un empilement troue est une collection de morceaux, et rien dans
    l'image ne distingue les deux.
    """
    if not spires:
        return []
    return [s for s in range(min(spires), max(spires) + 1) if s not in set(spires)]


LEGENDE_DEFAUT = ("cartes d'encre publiees par le concours, empilees par numero de spire, "
                  "NON recalees")


def assembler(entrees, sortie: Path, rouleau: str, hauteur_bande: int = HAUTEUR_BANDE,
              colonnes: int = 1, um_par_px: float | None = None,
              legende: str = LEGENDE_DEFAUT):
    from PIL import Image, ImageDraw

    bandes = []
    for spire, seg, chemin in entrees:
        im = Image.open(chemin).convert("L")
        # ⚠ On reduit par un facteur ENTIER de la hauteur voulue plutot que de forcer
        # une hauteur commune : deux spires n'ont aucune raison d'avoir la meme etendue
        # le long de l'axe du rouleau, et les etirer a la meme taille inventerait une
        # correspondance qui n'existe pas.
        ech = hauteur_bande / im.height if im.height > hauteur_bande else 1.0
        if ech < 1.0:
            im = im.resize((max(1, int(im.width * ech)), int(im.height * ech)),
                           Image.LANCZOS)
        bandes.append((spire, seg, im, ech))

    # ⚠ Le CONTRASTE de chaque bande est mesure, pas juge a l'oeil. Une spire dont la
    # carte d'encre est plate ne porte pas « peu de texte » : elle ne porte aucun signal,
    # et les deux se ressemblent sur une vignette. C'est aussi ce qui choisit la spire du
    # detail -- sinon on publierait le morceau qu'on a trouve joli.
    contraste = []
    for spire, _seg, im, ech in bandes:
        h = im.histogram()
        n = sum(h) or 1
        moy = sum(i * c for i, c in enumerate(h)) / n
        var = sum((i - moy) ** 2 * c for i, c in enumerate(h)) / n
        # ⚠ La resolution effective de la bande est celle du fichier MULTIPLIEE par la
        # reduction qu'on vient d'appliquer : mesurer sur l'image reduite avec les bornes
        # du fichier plein chercherait la periode au mauvais endroit.
        if um_par_px:
            eff = um_par_px / ech
            lo = max(2, int(INTERLIGNE_MM[0] * 1000 / eff))
            hi = max(lo + 4, int(INTERLIGNE_MM[1] * 1000 / eff))
        else:
            lo, hi = 4, None
        sc, axe, interligne = score_de_lignes(im, lo, hi)
        contraste.append({"spire": spire, "moyenne": round(moy, 2),
                          "sigma": round(var ** 0.5, 2),
                          "score_lignes": round(sc, 3), "axe": axe,
                          "interligne_px": interligne})

    # ⚠ Un empilement d'une seule colonne est FIDELE (une spire suit la precedente) mais
    # illisible des qu'il y a quarante bandes : l'image fait 1:32 et s'affiche en filet.
    # Les colonnes se lisent de haut en bas PUIS de gauche a droite, comme les colonnes
    # d'un rouleau reel -- et l'ordre reste celui des spires, donc rien n'est reordonne.
    colonnes = max(1, min(colonnes, len(bandes)))
    par_col = -(-len(bandes) // colonnes)
    paquets = [bandes[i * par_col:(i + 1) * par_col] for i in range(colonnes)]
    paquets = [p for p in paquets if p]

    larg_col = [max(im.width for _, _, im, _e in p) + 2 * MARGE for p in paquets]
    haut_col = [sum(im.height + MARGE for _, _, im, _e in p) + MARGE for p in paquets]
    largeur = sum(larg_col)
    hauteur = max(haut_col) + 28
    toile = Image.new("L", (largeur, hauteur), 18)
    d = ImageDraw.Draw(toile)

    x0 = 0
    for ic, paquet in enumerate(paquets):
        y = 24
        for spire, _seg, im, _e in paquet:
            toile.paste(im, (x0 + MARGE, y))
            # La largeur de chaque bande est VISIBLE : une bande courte se voit finir
            # avant les autres, ce qui rappelle que les colonnes ne se correspondent pas.
            d.line([(x0 + MARGE + im.width, y), (x0 + MARGE + im.width, y + im.height)],
                   fill=90)
            d.text((x0 + 2, y + 2), f"{spire:03d}", fill=200)
            y += im.height + MARGE
        x0 += larg_col[ic]

    # ⚠⚠ LA LEGENDE EST UN PARAMETRE, et ca a ete paye. Elle etait ecrite en dur — « cartes
    # d'encre publiees par le concours » — et le meme assembleur a servi a empiler NOS
    # rendus de spires : la figure annoncait donc une provenance fausse, en gros, en haut de
    # l'image. Une legende fausse sur une image est pire qu'une legende absente.
    d.text((MARGE, 6), f"{rouleau} — bandes {bandes[0][0]:03d} a {bandes[-1][0]:03d} "
                       f"({len(bandes)}) — {legende}", fill=210)
    sortie.parent.mkdir(parents=True, exist_ok=True)
    toile.save(sortie, optimize=True)
    return {
        "rouleau": rouleau,
        "bandes": len(bandes),
        "spire_min": bandes[0][0],
        "spire_max": bandes[-1][0],
        "trous": trous([b[0] for b in bandes]),
        "largeur_px": largeur,
        "hauteur_px": hauteur,
        "largeur_min_bande": min(im.width for _, _, im, _e in bandes),
        "largeur_max_bande": max(im.width for _, _, im, _e in bandes),
        "colonnes": len(paquets),
        "contraste": contraste,
        "spire_plus_contrastee": max(contraste, key=lambda c: c["sigma"])["spire"],
        "spire_moins_contrastee": min(contraste, key=lambda c: c["sigma"])["spire"],
        "spire_plus_ecrite": max(contraste, key=lambda c: c["score_lignes"])["spire"],
        "sortie": str(sortie),
    }


def verifier() -> int:
    from PIL import Image
    import tempfile

    echecs = controles = 0

    def ok(cond, quoi):
        # ⚠ Le compte des CONTROLES est tenu a cote de celui des echecs : `temoins.sh` lit le
        # nombre de controles dans le verdict, et une batterie qui n'en publierait pas serait
        # comptee pour zero — donc invisible dans le total du depot.
        nonlocal echecs, controles
        controles += 1
        print(("  ✅ " if cond else "  ❌ ") + quoi)
        if not cond:
            echecs += 1

    print("Témoins de assembler_mosaique")

    ok(trous([1, 2, 3]) == [], "une suite sans trou n'en rapporte aucun")
    ok(trous([1, 3, 5]) == [2, 4], "les trous sont nommés, pas seulement comptés")
    ok(trous([]) == [], "une liste vide ne casse pas la détection de trous")
    # ⚠ Sonde : si `trous` bornait la recherche a la longueur au lieu des extremes,
    # un trou final passerait inapercu.
    ok(trous([10, 11, 20]) == list(range(12, 20)),
       "un trou large est détecté sur toute sa longueur (sonde du bornage)")

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        idx = tmp / "index.tsv"
        lignes = []
        for i, (spire, w, h) in enumerate([(5, 40, 30), (7, 90, 60), (6, 60, 45)]):
            p = tmp / f"s{spire}.jpg"
            Image.new("L", (w, h), 100 + i * 40).save(p)
            lignes.append(f"{spire}\tseg{spire}\t{p}")
        idx.write_text("\n".join(lignes) + "\n", encoding="utf-8")

        entrees = lire_index(idx)
        ok([e[0] for e in entrees] == [5, 6, 7],
           "l'index est relu dans l'ordre des spires, pas celui du fichier")

        r = assembler(entrees, tmp / "m.png", "TEST", hauteur_bande=1000)
        # ⚠ Sonde du decoupage en colonnes : l'ORDRE des spires ne doit pas changer, et
        # aucune bande ne doit disparaitre. Un decoupage qui perd la derniere bande
        # produit une image d'apparence parfaite -- personne ne compte 44 bandes a l'oeil.
        r2 = assembler(entrees, tmp / "m2.png", "TEST", hauteur_bande=1000, colonnes=2)
        ok(r2["bandes"] == 3 and r2["colonnes"] == 2,
           "un découpage en 2 colonnes garde les 3 bandes")
        r3 = assembler(entrees, tmp / "m3.png", "TEST", hauteur_bande=1000, colonnes=9)
        ok(r3["bandes"] == 3 and r3["colonnes"] == 3,
           "plus de colonnes que de bandes ne fabrique pas de colonne vide")
        im2, im3 = Image.open(tmp / "m2.png"), Image.open(tmp / "m3.png")
        ok(im3.width > im2.width and im3.height < im2.height,
           "élargir en colonnes élargit l'image et la raccourcit")
        ok(r["bandes"] == 3 and r["spire_min"] == 5 and r["spire_max"] == 7,
           "l'assemblage rapporte ses bornes")
        ok(r["trous"] == [], "trois spires consécutives : aucun trou rapporté")
        ok(r["largeur_min_bande"] == 40 and r["largeur_max_bande"] == 90,
           "l'écart de largeur entre bandes est rapporté (le désalignement reste visible)")
        im = Image.open(tmp / "m.png")
        ok(im.width >= 90 and im.height >= 135,
           "l'image contient bien les trois bandes")
        # ⚠ Sonde : une bande plus PETITE que la hauteur cible ne doit pas etre agrandie
        # -- agrandir inventerait de la resolution qu'aucune mesure ne porte.
        ok(im.height < 400, "les petites bandes ne sont pas agrandies pour remplir")

    # ⚠⚠ Le score de lignes doit SÉPARER, sinon il ne sert à rien. Deux images
    # fabriquées : du bruit sans période, et des lignes régulières. Un score qui les
    # note pareil est un score qui note tout pareil.
    import numpy as np
    rng = np.random.default_rng(7)
    bruit = Image.fromarray((rng.random((300, 300)) * 255).astype("uint8"))
    lignes = np.zeros((300, 300), dtype="uint8")
    lignes[::12, :] = 255
    texte = Image.fromarray(lignes)
    s_bruit, _, _ = score_de_lignes(bruit)
    s_texte, axe_t, pas = score_de_lignes(texte)
    ok(s_texte > 0.5, f"des lignes régulières sont vues comme périodiques ({s_texte:.2f})")
    ok(s_bruit < 0.25, f"du bruit blanc ne l'est pas ({s_bruit:.2f})")
    ok(s_texte > 3 * s_bruit, "le score sépare le texte du mouchetis d'un facteur 3")
    ok(pas == 12, f"l'interligne mesuré est le vrai pas ({pas} px pour 12)")
    ok(axe_t == "lignes horizontales", "l'axe des lignes est identifié")
    # ⚠ Sonde de l'orientation : la même image tournée doit être vue, pas ratée.
    s_rot, axe_r, pas_r = score_de_lignes(texte.transpose(Image.ROTATE_90))
    ok(s_rot > 0.5 and pas_r == 12 and axe_r == "lignes verticales",
       "l'image tournée de 90° est vue tout aussi bien (sonde de l'axe a priori)")

    # ⚠⚠ LE témoin de la panne réellement rencontrée : une image qui porte À LA FOIS un
    # grain fin (période 3, le JPEG et le rééchantillonnage) et de vraies lignes
    # (période 30). Sans borne basse, le grain gagne — c'est ce qui avait élu la spire
    # 093 avec un « interligne » de 4 px, dix fois trop serré pour de l'écriture.
    melange = np.zeros((300, 300), dtype="float32")
    melange[::3, :] = 200.0
    melange[::30, :] = 255.0
    mel = Image.fromarray(melange.astype("uint8"))
    _, _, pas_libre = score_de_lignes(mel, lag_min=2)
    _, _, pas_borne = score_de_lignes(mel, lag_min=20, lag_max=45)
    ok(pas_libre < 10, f"sans borne, le grain fin l'emporte ({pas_libre} px) — la panne")
    ok(pas_borne == 30, f"borné sur l'interligne plausible, la vraie ligne est trouvée "
                        f"({pas_borne} px)")

    # ⚠⚠⚠ LE VERDICT EST ECRIT DANS LE FORMAT DU DEPOT, et ce n'est pas cosmetique :
    # `temoins.sh` ne compte une batterie que s'il lit « ALL PASS », donc une batterie qui
    # passe sans le dire ainsi est une batterie qu'aucun run complet ne peut compter — et
    # c'est exactement pourquoi ce fichier n'y etait pas enregistre.
    print(f"\n{'ALL PASS' if not echecs else 'FAILURES'} ({echecs} failures, "
          f"{controles} checks)")
    return 1 if echecs else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("index", nargs="?", type=Path)
    ap.add_argument("--sortie", type=Path)
    ap.add_argument("--rouleau", default="?")
    ap.add_argument("--hauteur-bande", type=int, default=HAUTEUR_BANDE)
    ap.add_argument("--legende", default=LEGENDE_DEFAUT,
                    help="ce que les bandes SONT — une légende fausse est pire qu'absente")
    ap.add_argument("--um-par-px", type=float, default=None,
                    help="résolution des images ; sans elle le score de lignes n'est PAS calibré")
    ap.add_argument("--colonnes", type=int, default=1,
                    help="colonnes lues de haut en bas puis de gauche à droite")
    ap.add_argument("--json")
    ap.add_argument("--verifier", action="store_true")
    a = ap.parse_args()
    if a.verifier:
        return verifier()
    if not a.index or not a.sortie:
        ap.error("donner un index et --sortie, ou --verifier")

    entrees = lire_index(a.index)
    if not entrees:
        print("index vide — rien à assembler", file=sys.stderr)
        return 3
    r = assembler(entrees, a.sortie, a.rouleau, a.hauteur_bande, a.colonnes,
                  a.um_par_px, a.legende)

    print(f"{r['rouleau']} : {r['bandes']} spires, {r['spire_min']:03d} → {r['spire_max']:03d}")
    if r["trous"]:
        print(f"  ⚠ {len(r['trous'])} spire(s) manquante(s) : "
              f"{', '.join(f'{t:03d}' for t in r['trous'])}")
        print("    → l'image est une COLLECTION de morceaux, pas un rouleau continu")
    else:
        print("  ✅ aucune spire manquante entre la première et la dernière")
    print(f"  largeur des bandes : {r['largeur_min_bande']} → {r['largeur_max_bande']} px "
          f"({100 * (1 - r['largeur_min_bande'] / r['largeur_max_bande']):.0f} % d'écart)")
    print(f"  image : {r['largeur_px']} × {r['hauteur_px']} px → {r['sortie']}")
    sig = [c["sigma"] for c in r["contraste"]]
    print(f"  contraste des bandes : σ de {min(sig):.1f} à {max(sig):.1f} — "
          f"la plus forte est la spire {r['spire_plus_contrastee']:03d}, "
          f"la plus faible la {r['spire_moins_contrastee']:03d}")
    e = max(r["contraste"], key=lambda c: c["score_lignes"])
    print(f"  ⭐ la plus ÉCRITE est la spire {e['spire']:03d} "
          f"(périodicité {e['score_lignes']:.3f}, {e['axe']}, interligne {e['interligne_px']} px)")
    if r["spire_plus_ecrite"] != r["spire_plus_contrastee"]:
        print("     ⚠ ce n'est PAS la plus contrastée : σ ne distingue pas du texte "
              "d'un mouchetis, la périodicité si")
    if a.json:
        Path(a.json).write_text(json.dumps(r, indent=2, ensure_ascii=False) + "\n",
                                encoding="utf-8")
        print(f"  écrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
