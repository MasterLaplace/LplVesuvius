#!/usr/bin/env python3
"""Une chaîne tangentielle s'emballe, et son PAS le dit avant sa boîte.

⚠⚠ CE QUE LA FIGURE DOIT RENDRE ÉVIDENT : ce n'est pas « enchaîner est mauvais », c'est que
l'emballement dépend du **pas**. À 95 µm par maillon, trois maillons ne bougent pas ; à 238 µm,
cinq maillons partent en vrille. Deux panneaux à la **même** échelle verticale, sinon les deux
courbes se ressemblent et le résultat disparaît.

⭐ Les deux grandeurs tracées ne sont pas redondantes, et leur ORDRE est le résultat :

  - **×pas** — la distance réellement couverte par un maillon, rapportée au premier. `--pas`
    est un pas de **grille**, donc la distance vaut `pas × longueur de tangente` : un maillage
    qui cisaille allonge ses tangentes, donc la même commande couvre plus de terrain. Une
    chaîne dont le pas dérive **ne va plus là où on l'a envoyée**.
  - **×boîte** — le volume englobant à nombre de points constant. Un maillage qui ne se
    déplace pas mais s'étale.

Le pas **précède** la boîte : au quatrième maillon il est déjà à +47 % quand la boîte n'est
qu'à +22 %. C'est donc lui l'instrument d'alerte, et c'est ce que la figure doit montrer.

⚠ Aucun rendu n'entre ici. Les deux grandeurs se lisent dans les `meta.json`, ce qui est la
raison pour laquelle ce diagnostic est utilisable à chaque maillon plutôt qu'à la fin.

⚠⚠ Et la limite est portée par la figure : ces chaînes projettent **purement**, sans
réoptimisation sur la matière. C'est le plancher d'une chaîne tangentielle, pas son plafond.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw

FOND = (250, 249, 246)
ENCRE = (28, 30, 34)
GRIS = (140, 143, 148)
TRAIT = (215, 213, 208)
PAS = (196, 72, 60)
BOITE = (74, 132, 96)
REPERE = (176, 174, 168)

ANGLAIS = {
    "une chaîne tangentielle s'emballe, et son pas le dit avant sa boîte":
        "a tangential chain runs away, and its step says so before its box",
    "⚠ projection PURE, sans réoptimisation : c'est le plancher d'une chaîne, pas son plafond":
        "⚠ PURE projection, no re-optimisation: this is a chain's floor, not its ceiling",
    "pas réellement parcouru (×premier maillon)": "step actually covered (×first link)",
    "volume englobant (×premier maillon)": "bounding box (×first link)",
    "maillons de": "links of",
    "bond direct": "direct jump",
    "maillon": "link",
    "un pas tenu": "a step held",
    "échelle verticale logarithmique": "logarithmic vertical scale",
}


def _police():
    from PIL import ImageFont
    for c in ("DejaVuSans.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
        try:
            return (ImageFont.truetype(c, 14), ImageFont.truetype(c, 12),
                    ImageFont.truetype(c, 11))
        except OSError:
            continue
    d = ImageFont.load_default()
    return d, d, d


def _pixels(im):
    f = getattr(im, "get_flattened_data", None) or im.getdata
    return set(f())


def emballement(valeurs: list[float], seuil: float = 1.10) -> int | None:
    """Le rang du premier maillon qui dépasse `seuil`, ou `None`.

    ⚠⚠ C'est l'énoncé que la figure prétend montrer, donc il est **calculé** et non affirmé.
    Une figure qui écrirait « s'emballe » sous une courbe plate mentirait, et personne ne
    recompte cinq nombres. Le rang est **1-basé** : c'est un numéro de maillon, pas un indice.
    """
    for i, v in enumerate(valeurs):
        if v > seuil:
            return i + 1
    return None


def lire_chaine(json_croissance: Path) -> dict:
    """Une chaîne, telle que `projeter_tangentiel.py --croissance` l'a écrite.

    ⚠ La **source** et le **bond direct** ne sont pas des maillons : l'une n'a pas été
    projetée, l'autre n'est pas dans la chaîne. Les tracer parmi les maillons ferait lire un
    témoin comme une étape, ce qui est exactement l'erreur que le témoin existe pour éviter.
    """
    rangs = json.loads(json_croissance.read_text(encoding="utf-8"))
    maillons = [r for r in rangs if r["maillage"].startswith("maillon")]
    direct = next((r for r in rangs if r["maillage"] == "direct"), None)
    if not maillons:
        raise ValueError(f"{json_croissance} : aucun maillon — rien à tracer")
    return {"maillons": maillons, "direct": direct}


TITRE_DEFAUT = "une chaîne tangentielle s'emballe, et son pas le dit avant sa boîte"


def dessiner(chaines: list[dict], sortie: Path, anglais: bool = False,
             log: bool = False, titre: str | None = None) -> dict:
    """Un panneau par chaîne, à échelle verticale PARTAGÉE.

    ⚠⚠ `log` n'est PAS un réglage de goût. Une chaîne qui survit six maillons puis multiplie
    son pas par deux mille ne tient pas sur un axe linéaire : les six maillons qui portent le
    résultat s'écrasent sur la ligne du bas et la figure ne montre plus que l'explosion, qu'on
    connaît déjà. L'axe est **étiqueté** en conséquence, sinon un lecteur lirait des écarts
    verticaux comme des différences additives.
    """
    if len(chaines) < 1:
        raise ValueError("aucune chaîne — il faut au moins un panneau")
    g1, g2, g3 = _police()
    intraduits, inchanges = [], []

    def T(txt: str) -> str:
        if not anglais:
            return txt
        out = txt
        for fr, en in sorted(ANGLAIS.items(), key=lambda kv: -len(kv[0])):
            out = out.replace(fr, en)
        if out == txt and any(c.isalpha() for c in txt):
            inchanges.append(txt)
        if any(c in out for c in "éèêàùôîçâû"):
            intraduits.append(out)
        return out

    largeur, hauteur = 720, 392
    im = Image.new("RGB", (largeur, hauteur), FOND)
    d = ImageDraw.Draw(im)
    # ⚠⚠ Le titre est une AFFIRMATION, et le défaut cesse d'être vrai dès qu'un panneau
    # montre une chaîne à pas fixe — qui, elle, ne s'emballe pas. Une figure dont le titre est
    # faux pour la moitié de ce qu'elle montre est pire qu'une figure sans titre.
    d.text((24, 16), T(titre or TITRE_DEFAUT), font=g1, fill=ENCRE)

    # ⚠⚠ UNE SEULE ÉCHELLE VERTICALE pour tous les panneaux. Donner à chaque chaîne la sienne
    # ferait paraître identiques une chaîne plate et une chaîne qui quadruple : c'est le piège
    # le plus commun d'un graphe à plusieurs panneaux, et c'est précisément le résultat ici.
    toutes = [v for c in chaines for m in c["maillons"]
              for v in (m.get("rapport_pas") or 1.0, m.get("rapport") or 1.0)]
    haut = max(1.15, max(toutes) * 1.06)
    import math
    lhaut = math.log10(haut)

    gy, gh = 92, hauteur - 92 - 94
    marge, entre = 62, 40
    pw = (largeur - marge - 24 - entre * (len(chaines) - 1)) // len(chaines)

    # La légende, en haut, à place connue d'avance — jamais au bout d'une courbe.
    lx = 24
    for couleur, nom in ((PAS, "pas réellement parcouru (×premier maillon)"),
                         (BOITE, "volume englobant (×premier maillon)")):
        d.rectangle([lx, 44, lx + 12, 52], fill=couleur)
        t = T(nom)
        d.text((lx + 17, 41), t, font=g3, fill=couleur)
        lx += 17 + int(d.textlength(t, font=g3)) + 24
    depassement = max(0, lx - (largeur - 24))

    emballements = []
    for pi, c in enumerate(chaines):
        gx = marge + pi * (pw + entre)
        maillons = c["maillons"]
        n = len(maillons)
        d.text((gx, gy - 22), T(c.get("titre", "")), font=g2, fill=ENCRE)

        for k in range(5):
            y = gy + gh * k / 4
            d.line([(gx, y), (gx + pw, y)], fill=TRAIT, width=1)
            if pi == 0:
                if log:
                    val = 10.0 ** (lhaut * (1.0 - k / 4))
                    t = f"×{val:,.0f}".replace(",", " ") if val >= 10 else \
                        f"×{val:.2f}".replace(".", ",")
                else:
                    val = 1.0 + (haut - 1.0) * (1.0 - k / 4)
                    t = f"×{val:.2f}".replace(".", ",")
                d.text((gx - 48, y - 7), t, font=g3, fill=GRIS)
        d.line([(gx, gy + gh), (gx + pw, gy + gh)], fill=GRIS, width=1)

        def Y(v):
            w = max(1.0, min(haut, v))
            if log:
                return gy + gh * (1.0 - (math.log10(w) / lhaut if lhaut > 0 else 0.0))
            return gy + gh * (1.0 - (w - 1.0) / (haut - 1.0))

        def X(i):
            return gx + (pw * (i + 1) / (n + 1) if n > 1 else pw / 2)

        # ⭐ Le repère « un pas tenu » : la ligne que la chaîne devrait suivre. Sans elle,
        # une courbe à 1,06 et une courbe à 4,05 se lisent toutes deux comme « ça monte ».
        d.line([(gx, Y(1.0)), (gx + pw, Y(1.0))], fill=REPERE, width=1)
        if pi == 0:
            d.text((gx + 4, Y(1.0) - 14), T("un pas tenu"), font=g3, fill=REPERE)

        for cle, couleur in (("rapport", BOITE), ("rapport_pas", PAS)):
            pts = [(X(i), Y(m.get(cle) or 1.0)) for i, m in enumerate(maillons)]
            if len(pts) > 1:
                d.line(pts, fill=couleur, width=2)
            for i, (x, y) in enumerate(pts):
                d.ellipse([x - 4, y - 4, x + 4, y + 4], fill=couleur)
            # La dernière valeur de chaque série, écrite : c'est celle qui porte le verdict.
            der = maillons[-1].get(cle) or 1.0
            t = (f"{der:,.0f}".replace(",", " ") if log and der >= 10
                 else f"{der:.2f}".replace(".", ","))
            w = d.textlength(t, font=g3)
            x, y = pts[-1]
            d.text((min(x + 7, gx + pw - w), y - 15 if cle == "rapport_pas" else y + 5),
                   t, font=g3, fill=couleur)

        for i, m in enumerate(maillons):
            x = X(i)
            d.line([(x, gy + gh), (x, gy + gh + 5)], fill=GRIS, width=1)
            t = str(i + 1)
            d.text((x - d.textlength(t, font=g3) / 2, gy + gh + 8), t, font=g3, fill=GRIS)
        d.text((gx, gy + gh + 26), T("maillon"), font=g3, fill=GRIS)

        # ⭐ Le témoin, écrit en toutes lettres sous son panneau : le bond direct de MÊME
        # longueur totale. Une chaîne qui tient ne prouve rien sans lui.
        if c.get("direct"):
            dr = c["direct"]
            d.text((gx, gy + gh + 42),
                   T("bond direct") + f" : ×{dr.get('rapport') or 1.0:.2f}".replace(".", ","),
                   font=g3, fill=GRIS)
        emballements.append(emballement([m.get("rapport_pas") or 1.0 for m in maillons]))

    d.line([(24, hauteur - 30), (largeur - 24, hauteur - 30)], fill=TRAIT, width=1)
    bas = T("⚠ projection PURE, sans réoptimisation : c'est le plancher d'une chaîne, "
            "pas son plafond")
    if log:
        # ⚠ L'axe DIT qu'il est logarithmique. Sans ça, un lecteur lit les écarts verticaux
        # comme des différences additives, et cette figure couvre trois ordres de grandeur.
        bas = T("échelle verticale logarithmique") + "   ·   " + bas
    d.text((24, hauteur - 24), bas, font=g3, fill=GRIS)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    im.save(sortie)
    # ⚠ Deux repères que la sonde peut lire : où tombe le plancher (×1) et où tombe une
    # valeur d'essai (×5). C'est ce qui rend « le log décolle les petites valeurs » vérifiable
    # au lieu d'être une affirmation sur une image.
    def _y(v):
        w = max(1.0, min(haut, v))
        if log:
            return gy + gh * (1.0 - (math.log10(w) / lhaut if lhaut > 0 else 0.0))
        return gy + gh * (1.0 - (w - 1.0) / (haut - 1.0))

    return {"panneaux": len(chaines), "largeur": largeur, "hauteur": hauteur,
            "haut_axe": haut, "depassement": int(depassement), "log": log,
            "y_plancher": int(_y(1.0)), "y_essai": int(_y(5.0)),
            "emballements": emballements,
            "intraduits": intraduits, "inchanges": inchanges}


def _verifier() -> int:
    import tempfile

    ech = []

    def v(nom, cond, det=""):
        ech.append((nom, bool(cond), det))

    # ⚠⚠ L'énoncé de la figure, sondé dans les deux sens : une chaîne plate ne s'emballe pas,
    # une chaîne qui dérive s'emballe, et le rang rendu est un NUMÉRO DE MAILLON.
    v("une chaîne plate ne s'emballe pas", emballement([1.0, 1.0, 1.0]) is None)
    v("une chaîne qui dérive s'emballe", emballement([1.0, 1.01, 1.06, 1.47]) == 4)
    v("... au premier maillon qui dépasse", emballement([1.0, 1.5, 4.0]) == 2)
    v("le rang est 1-basé, pas un indice", emballement([2.0]) == 1)
    v("le seuil est réglable", emballement([1.0, 1.05], seuil=1.02) == 2)
    v("... et il ne se déclenche pas sous le seuil", emballement([1.0, 1.05]) is None)

    courte = {"titre": "3 maillons de 95 µm", "direct": {"rapport": 1.01},
              "maillons": [{"maillage": f"maillon_{i}", "rapport": 1.0 + 0.005 * i,
                            "rapport_pas": 1.0 + 0.002 * i} for i in range(1, 4)]}
    longue = {"titre": "5 maillons de 238 µm", "direct": {"rapport": 1.10},
              "maillons": [{"maillage": "maillon_1", "rapport": 1.01, "rapport_pas": 1.00},
                           {"maillage": "maillon_2", "rapport": 1.02, "rapport_pas": 1.01},
                           {"maillage": "maillon_3", "rapport": 1.04, "rapport_pas": 1.06},
                           {"maillage": "maillon_4", "rapport": 1.22, "rapport_pas": 1.47},
                           {"maillage": "maillon_5", "rapport": 2.38, "rapport_pas": 4.05}]}

    with tempfile.TemporaryDirectory() as td:
        f = Path(td) / "a.png"
        r = dessiner([courte, longue], f)
        v("l'image est écrite", f.is_file() and f.stat().st_size > 0)
        v("les deux panneaux sont tracés", r["panneaux"] == 2)
        # ⚠⚠ LE CONTRÔLE QUI PORTE LA FIGURE : une SEULE échelle verticale. Deux panneaux à
        # leur propre échelle feraient paraître identiques une chaîne plate et une chaîne qui
        # quadruple — c'est-à-dire effaceraient le résultat.
        v("l'échelle couvre la plus grande valeur", r["haut_axe"] >= 4.05,
          str(r["haut_axe"]))
        v("... et elle laisse de la marge au-dessus", r["haut_axe"] > 4.05)
        seule = dessiner([longue], Path(td) / "seule.png")
        v("la même chaîne seule garde la même échelle",
          abs(seule["haut_axe"] - r["haut_axe"]) < 1e-9, str(seule["haut_axe"]))
        v("la chaîne courte est vue calme", r["emballements"][0] is None)
        v("la chaîne longue est vue s'emballer", r["emballements"][1] == 4,
          str(r["emballements"][1]))
        px = _pixels(Image.open(f).convert("RGB"))
        v("la série du pas est tracée", PAS in px)
        v("celle de la boîte aussi", BOITE in px)
        v("le repère « un pas tenu » est tracé", REPERE in px)
        v("aucun libellé ne déborde du canevas", r["depassement"] == 0,
          f"{r['depassement']} px")

        # ⚠ Une chaîne PLATE ne doit pas écraser l'axe : sans plancher, `haut` vaudrait 1,0 et
        # toute division par `haut - 1` exploserait. Le plancher est donc sondé.
        plate = {"titre": "plate", "maillons": [{"maillage": "maillon_1", "rapport": 1.0,
                                                 "rapport_pas": 1.0}] * 3}
        rp = dessiner([plate], Path(td) / "plate.png")
        v("une chaîne plate garde un axe utilisable", rp["haut_axe"] > 1.0,
          str(rp["haut_axe"]))

        # ⚠⚠ L'AXE LOG. Une chaîne qui multiplie son pas par 2 692 écrase ses six premiers
        # maillons sur la ligne du bas en linéaire — donc la figure ne montrerait plus que
        # l'explosion, qu'on connaît déjà, et pas l'horizon, qui est le résultat.
        folle = {"titre": "20 maillons", "maillons": [
            {"maillage": f"maillon_{i}", "rapport": 1.0 + i ** 4, "rapport_pas": 1.0 + i ** 4}
            for i in range(1, 21)]}
        rl = dessiner([folle], Path(td) / "log.png", log=True)
        rlin = dessiner([folle], Path(td) / "lin.png", log=False)
        v("les deux échelles couvrent la même valeur",
          abs(rl["haut_axe"] - rlin["haut_axe"]) < 1e-9)
        # ⭐ Ce qui distingue les deux : en log, un maillon à ×5 est VISIBLEMENT au-dessus du
        # plancher ; en linéaire il est à moins d'un millième de la hauteur, donc dessus.
        v("en log, un petit maillon décolle du plancher",
          rl["y_essai"] < rl["y_plancher"] - 20, f"{rl['y_essai']} vs {rl['y_plancher']}")
        v("en linéaire, il reste collé au plancher",
          rlin["y_plancher"] - rlin["y_essai"] < 3,
          f"{rlin['y_essai']} vs {rlin['y_plancher']}")
        v("l'axe log le DIT dans son bandeau", rl["log"] and not rlin["log"])
        # ⚠⚠ Le titre par défaut AFFIRME un emballement ; il cesse d'être vrai dès qu'un
        # panneau montre une chaîne à pas fixe. Un titre faux pour la moitié de ce qu'on
        # montre est pire que pas de titre.
        px_def = _pixels(Image.open(f).convert("RGB"))
        rt = dessiner([courte, longue], Path(td) / "titre.png",
                      titre="un titre entièrement différent")
        px_t = _pixels(Image.open(Path(td) / "titre.png").convert("RGB"))
        v("le titre est remplaçable", px_def != px_t)
        v("... et le défaut reste celui d'origine",
          TITRE_DEFAUT.startswith("une chaîne tangentielle s'emballe"))
        v("... sans rien faire déborder", rl["depassement"] == 0)

        try:
            dessiner([], Path(td) / "vide.png")
            v("aucune chaîne est refusée", False)
        except ValueError:
            v("aucune chaîne est refusée", True)

        # La lecture d'une chaîne écrite par la campagne.
        j = Path(td) / "c.json"
        j.write_text(json.dumps([
            {"maillage": "morceau_00", "rapport": 1.0, "rapport_pas": None},
            {"maillage": "maillon_1", "rapport": 1.01, "rapport_pas": 1.0},
            {"maillage": "direct", "rapport": 1.10, "rapport_pas": 5.0}]), encoding="utf-8")
        c = lire_chaine(j)
        # ⚠⚠ Ni la source ni le témoin ne sont des maillons. Les tracer parmi eux ferait lire
        # le bond direct comme une étape de la chaîne — l'erreur exacte que le témoin évite.
        v("la source n'est pas un maillon", len(c["maillons"]) == 1)
        v("le bond direct non plus", c["maillons"][0]["maillage"] == "maillon_1")
        v("... mais il est gardé comme témoin", c["direct"]["rapport"] == 1.10)
        vide = Path(td) / "v.json"
        vide.write_text(json.dumps([{"maillage": "morceau_00", "rapport": 1.0}]),
                        encoding="utf-8")
        try:
            lire_chaine(vide)
            v("une chaîne sans maillon est refusée", False)
        except ValueError:
            v("une chaîne sans maillon est refusée", True)

        ra = dessiner([courte, longue], Path(td) / "en.png", anglais=True)
        v("la version anglaise ne laisse pas d'accent", not ra["intraduits"],
          ", ".join(ra["intraduits"][:2]))
        v("... et ne laisse pas de libellé intraduit", not ra["inchanges"],
          ", ".join(ra["inchanges"][:2]))
        v("... sans rien faire déborder", ra["depassement"] == 0, f"{ra['depassement']} px")

    for nom, ok, det in ech:
        if not ok:
            print(f"  ECHEC  {nom}" + (f"  --- {det}" if det else ""))
    n = len(ech)
    e = sum(1 for _, ok, _ in ech if not ok)
    print(f"{'ALL PASS' if e == 0 else 'FAILURES'} ({e} failures, {n} checks)")
    return 1 if e else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("chaines", nargs="*", type=Path,
                   help="les JSON écrits par projeter_tangentiel.py --croissance")
    p.add_argument("--titres", nargs="*", default=[],
                   help="un titre par panneau, dans le même ordre")
    p.add_argument("--sortie", type=Path, default=Path("docs/images/44_emballement.png"))
    p.add_argument("--titre", help="l'affirmation que porte la figure — le défaut ne vaut "
                                   "que pour des chaînes à pas de grille")
    p.add_argument("--log", action="store_true",
                   help="axe vertical logarithmique — nécessaire au-delà d'un ordre de grandeur")
    p.add_argument("--anglais", action="store_true")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args()

    if a.verifier:
        return _verifier()
    if not a.chaines:
        p.error("au moins une chaîne est requise")

    chaines = []
    for i, j in enumerate(a.chaines):
        c = lire_chaine(j)
        c["titre"] = a.titres[i] if i < len(a.titres) else j.stem
        chaines.append(c)
    r = dessiner(chaines, a.sortie, anglais=a.anglais, log=a.log, titre=a.titre)
    print(f"écrit : {a.sortie}  ({r['panneaux']} panneaux, axe jusqu'à ×{r['haut_axe']:.2f})")
    for i, e in enumerate(r["emballements"]):
        print(f"  {chaines[i]['titre']} : "
              + (f"⚠ s'emballe au maillon {e}" if e else "⭐ pas tenu sur toute la chaîne"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
