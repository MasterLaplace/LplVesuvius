#!/usr/bin/env python3
"""Combien de nos profils de profondeur ne mesurent RIEN, et quels verdicts en dépendent ?

⚠⚠ **Pourquoi cet audit existe.** `test_convergence.py` rend α depuis une série d'écarts.
Un écart n'est une mesure que s'il y a un pic à mesurer : quand le profil est **plat**,
l'écart rapporté est le **bord de la fenêtre** par défaut — et le rapport de deux bords de
fenêtre vaut le rapport des fenêtres, donc **α = 1 par identité arithmétique**, quoi qu'il
y ait dans le volume. Le verdict imprimé était pourtant « suit la fenêtre — il n'y a aucune
feuille à portée », affirmé avec la même assurance que sur une vraie mesure.

⭐ `depth_profile.py` calcule déjà `amplitude_mediane` et son propre seuil de détection
`amplitude_min`. L'information était là ; personne ne la lisait. Cet audit la lit sur
**tous** les profils de l'arbre et dit lesquels ne mesurent rien.

⚠⚠ **Ce que cet audit lit, et ce qu'il ne lit pas.** Il balaie les profils **présents sur
disque**, pas ceux qui ont produit les tableaux publiés. Une campagne relancée dans la même
destination écrase les siens : mesuré le 2026-08-22, `data/spires_pas025/spire03` porte des
profils de 14 h 29 alors que le verdict que [`43`](../docs/43_la_chaine_des_spires.md)
tabule date de 08 h 02 le même jour — six heures et un tirage plus tôt. Les deux sont
justes ; ils ne parlent pas du même run.

⭐ Conséquence pratique : un écart entre ce tableau et un document n'est pas forcément une
erreur du document. Vérifier les horodatages avant de conclure. Et la vraie leçon est en
amont — **une campagne qui réécrit sa propre destination détruit la preuve derrière un
tableau déjà publié**, alors que les verdicts, eux, survivent dans `docs/`.

⚠ Ce qu'il n'établit pas : qu'un verdict rendu sur un profil plat est faux. Il établit qu'il
n'est **pas soutenu par une mesure** — ce qui est différent, et suffisant pour le retirer
d'un tableau de comptes.

Usage :
    python3 analysis/src/audit_profils_plats.py --racine . --json docs/audit_profils.json
    python3 analysis/src/audit_profils_plats.py --verifier
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# ⚠ Repli utilise seulement quand un profil ne declare pas son propre seuil. Les profils
# recents portent `amplitude_min` ; les anciens non, et supposer zero les declarerait tous
# valides -- c'est-a-dire exactement l'erreur que cet audit cherche.
AMPLITUDE_MIN_DEFAUT = 0.02


def lire_profil(p: Path) -> dict | None:
    """Un profil, reduit à ce qui décide s'il mesure quelque chose."""
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    d = d[0] if isinstance(d, list) and d else d
    if not isinstance(d, dict) or "ecart_trace_um_median" not in d:
        return None
    a = d.get("amplitude_mediane")
    seuil = d.get("amplitude_min")
    # ⚠⚠ LE PLAFOND DU RENDU, calcule depuis le profil lui-meme. Une fenetre de `layers`
    # couches centree sur la surface ne peut pas voir plus loin que sa demi-fenetre, soit
    # `couche_tracee` couches, soit `couche_tracee * voxel_um` microns. Un ecart pose
    # exactement dessus n'est pas une distance mesuree, c'est le bord du regard.
    ct, vx = d.get("couche_tracee"), d.get("voxel_um")
    plafond = (float(ct) * float(vx)) if (ct is not None and vx) else None
    e = float(d["ecart_trace_um_median"])
    return {"fichier": str(p), "ecart_um": e,
            "plafond_um": plafond,
            # ⚠ L'epaisseur d'un voxel est reportee telle quelle : c'est la SEULE grandeur
            # qui rend deux niveaux de pyramide comparables, et la deduire du plafond
            # ailleurs ferait un second calcul de la meme chose.
            "voxel_um": (float(vx) if vx else None),
            # ⚠ Comparaison a une tolerance relative : les ecarts sont des medianes de
            # quantites discretisees au pas de couche, donc exiger l'egalite exacte raterait
            # un ecart pose au bord a un arrondi pres.
            "au_plafond": (plafond is not None and e >= plafond * (1 - 1e-9)),
            "amplitude": a, "seuil_declare": seuil,
            "seuil": seuil if seuil is not None else AMPLITUDE_MIN_DEFAUT,
            "seuil_est_un_repli": seuil is None,
            "au_bord": d.get("au_bord"), "couche_tracee": d.get("couche_tracee"),
            "avec_matiere": d.get("avec_matiere")}


def juger(x: dict) -> dict:
    """Ce profil mesure-t-il quelque chose ?

    ⚠⚠ « plat » et « inconnu » sont deux réponses différentes. Un profil qui ne rapporte
    aucune amplitude n'est pas un profil plat : c'est un profil dont on ne sait pas. Les
    confondre ferait compter une absence de donnée comme une observation — le défaut que ce
    dépôt a déjà payé sur le niveau de langue et sur l'index zéro.
    """
    if x["amplitude"] is None:
        return {**x, "etat": "inconnu"}
    return {**x, "etat": "plat" if x["amplitude"] < x["seuil"] else "mesure"}


def balayer(racine: Path) -> list[dict]:
    """Les profils de la famille `profil*`, jugés."""
    out = []
    for p in sorted(racine.rglob("profil*.json")):
        x = lire_profil(p)
        if x:
            out.append(juger(x))
    return out


def hors_portee(racine: Path) -> list[str]:
    """Les fichiers qui PORTENT un profil et que le balayage ne prend pas.

    ⚠⚠ **Mesurer ce qu'on ne couvre pas, plutôt que dire « tout ».** Le balayage sélectionne
    par NOM de fichier, et une famille nommée autrement passerait inaperçue — le défaut de
    « forme supposée » que ce dépôt a déjà payé deux fois. Mesuré le 2026-08-22 : **33**
    fichiers portent un `ecart_trace_um_median` hors de la famille `profil*`.

    ⭐ Et ils ne sont pas simplement oubliés : `data/second_axe/*.json` a une structure
    **différente** — un fichier par trace, pas un par fenêtre — donc le regroupement par
    dossier en ferait une seule série de seize au lieu de seize traces. C'est
    `analysis/src/derive_avec_profondeur.py` qui les analyse, avec la bonne notion de série.
    Forcer un outil à couvrir les deux structures serait pire que deux outils qui disent
    chacun sa portée.

    ⚠ Le compte est publié pour qu'il ne grandisse pas en silence : une troisième famille
    apparaîtrait ici avant d'apparaître dans une conclusion.
    """
    out = []
    for p in sorted(racine.rglob("*.json")):
        if p.name.startswith("profil") or ".git" in p.parts:
            continue
        x = lire_profil(p)
        if x:
            out.append(str(p))
    return out


def alpha(serie: list[tuple[float, float]]) -> float | None:
    """L'exposant d'une serie (couches, ecart) — la meme formule que `test_convergence`."""
    import math
    if len(serie) < 2:
        return None
    (n0, e0), (n1, e1) = min(serie), max(serie)
    if n0 <= 0 or e0 <= 0 or n1 <= n0:
        return None
    return math.log(e1 / e0) / math.log(n1 / n0)


def alpha_discriminant(xs: list[dict], resolution: float) -> dict | None:
    """α distingue-t-il cette série d'une qui n'aurait RIEN mesuré ?

    ⚠⚠ **La question que α seul ne peut pas poser.** Si toutes les lectures étaient le bord
    de la fenêtre, α vaudrait le rapport des bords sur le rapport des fenêtres — c'est-à-dire
    ~1, par identité. Une série dont l'α **mesuré** est à moins d'une résolution de cet α
    **de plafond** ne peut donc pas séparer « le pic recule » de « il n'y avait pas de pic ».

    ⭐ La résolution n'est pas choisie ici : c'est celle que `test_convergence` déclare pour
    son propre α. Deux seuils pour une même grandeur finiraient par se contredire.
    """
    pts = [(x["couche_tracee"] * 2 + 1, x["ecart_um"]) for x in xs
           if x.get("couche_tracee") and x.get("ecart_um")]
    pla = [(x["couche_tracee"] * 2 + 1, x["plafond_um"]) for x in xs
           if x.get("couche_tracee") and x.get("plafond_um")]
    a_mes, a_pla = alpha(pts), alpha(pla)
    if a_mes is None or a_pla is None:
        return None
    ecart = abs(a_mes - a_pla)
    return {"alpha_mesure": a_mes, "alpha_si_tout_au_plafond": a_pla,
            "ecart": ecart, "resolution": resolution,
            "discriminant": ecart >= resolution}


def resumer(profils: list[dict]) -> dict:
    """Le compte par état, et les dossiers dont TOUS les profils sont plats.

    ⭐ Le second est ce qui compte : un verdict de convergence se rend sur une SÉRIE. Une
    série dont une fenêtre mesure quelque chose reste jugeable ; une série dont aucune ne
    mesure rien ne l'est pas. Compter les profils un par un dirait moins.
    """
    par_dossier: dict[str, list[dict]] = {}
    for x in profils:
        par_dossier.setdefault(str(Path(x["fichier"]).parent), []).append(x)
    series_mortes = sorted(d for d, xs in par_dossier.items()
                           if xs and all(y["etat"] == "plat" for y in xs))
    series_partielles = sorted(d for d, xs in par_dossier.items()
                               if any(y["etat"] == "plat" for y in xs)
                               and any(y["etat"] == "mesure" for y in xs))
    # ⚠ La resolution vient de `test_convergence`, jamais recopiee.
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    try:
        from test_convergence import BRUIT_ALPHA as RESOLUTION
    except ImportError:      # pragma: no cover
        RESOLUTION = 0.2
    indiscernables, juges = {}, {}
    for dossier, xs in sorted(par_dossier.items()):
        j = alpha_discriminant(xs, RESOLUTION)
        if not j:
            continue
        juges[dossier] = j
        if not j["discriminant"]:
            indiscernables[dossier] = j
    # ⭐⭐ LA MOITIE RASSURANTE, MESUREE ET NON SUPPOSEE. L'α de plafond vaut toujours ~1,
    # donc une serie qui CONVERGE (α ~ 0) en est loin par construction et reste
    # discriminante. Ce qui perd son pouvoir de discrimination est exactement le verdict
    # « suit la fenetre » -- et ses deux causes possibles, « le pic recule » et « il n'y
    # avait pas de pic », condamnent la trace toutes les deux. La conclusion pratique tient
    # donc ; c'est la FORMULATION qui sur-affirme.
    #
    # ⚠ Ce constat est publie comme une mesure : le plus petit α parmi les non
    # discriminants, et le plus grand parmi ceux qui convergent. Si un jour une serie
    # convergente devenait non discriminante, ces deux nombres se croiseraient.
    # ⚠⚠ LES SERIES OU UN CRITERE RELATIF SERAIT CONSTRUCTIBLE. `47` propose de lire un
    # critere a DEUX profondeurs, comme l'exposant α, pour qu'il cesse d'avoir besoin d'une
    # reference -- et note que ca demande des traces NON CENSUREES aux deux bouts, en
    # affirmant que le depot en a deux. C'est verifiable ici : une serie est utilisable
    # quand aucun de ses profils n'a son ecart pose sur le bord de sa fenetre.
    #
    # ⭐ Le compte est publie parce que c'est lui qui dit si le lot suivant est faisable, et
    # il grandira avec les campagnes -- donc le deviner une fois ne suffirait pas.
    utilisables = sorted(d for d, xs in par_dossier.items()
                         if len(xs) >= 2 and not any(y.get("au_plafond") for y in xs)
                         and all(y["etat"] == "mesure" for y in xs))
    alphas_ind = [j["alpha_mesure"] for j in indiscernables.values()]
    convergents = [j["alpha_mesure"] for j in juges.values() if j["alpha_mesure"] < 0.5]
    return {"profils": len(profils),
            "resolution_alpha": RESOLUTION,
            "series_indiscernables_du_plafond": indiscernables,
            "series_utilisables_pour_un_critere_relatif": utilisables,
            # ⚠⚠ TOUTES les series jugees, et pas seulement celles qui echouent. Ne garder
            # que les 20 non discriminantes serait publier un echantillon filtre : un
            # lecteur ne pourrait pas voir que les 87 autres sont loin de leur plafond, et
            # c'est justement ce qui rend le constat supportable.
            "jugees": juges,
            "series_jugees": len(juges),
            "alpha_min_indiscernable": min(alphas_ind) if alphas_ind else None,
            "alpha_max_convergent": max(convergents) if convergents else None,
            "convergents_indiscernables": sorted(
                d for d, j in indiscernables.items() if j["alpha_mesure"] < 0.5),
            "au_plafond": sum(1 for x in profils if x.get("au_plafond")),
            "plats": sum(1 for x in profils if x["etat"] == "plat"),
            "mesures": sum(1 for x in profils if x["etat"] == "mesure"),
            "inconnus": sum(1 for x in profils if x["etat"] == "inconnu"),
            "sans_seuil_declare": sum(1 for x in profils if x["seuil_est_un_repli"]),
            "series": len(par_dossier),
            "series_entierement_plates": series_mortes,
            "series_partiellement_plates": series_partielles}


def verifier() -> int:
    echecs = controles = 0

    def v(nom, cond, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not cond:
            echecs += 1
            print(f"  ECHEC  {nom}" + (f"  — {detail}" if detail else ""))

    plat = juger({"amplitude": 0.0, "seuil": 0.02, "seuil_est_un_repli": False})
    v("une amplitude nulle est PLATE", plat["etat"] == "plat")
    v("une amplitude au-dessus du seuil MESURE",
      juger({"amplitude": 0.09, "seuil": 0.02, "seuil_est_un_repli": False})["etat"]
      == "mesure")
    # ⚠ Le bord exact : sous le seuil est plat, AU seuil ne l'est pas. Un profil pile au
    # seuil de detection de l'instrument est, par definition de ce seuil, detecte.
    v("pile au seuil, le profil mesure",
      juger({"amplitude": 0.02, "seuil": 0.02, "seuil_est_un_repli": False})["etat"]
      == "mesure")
    v("juste sous le seuil, il est plat",
      juger({"amplitude": 0.0199, "seuil": 0.02, "seuil_est_un_repli": False})["etat"]
      == "plat")
    # ⚠⚠ « inconnu » n'est pas « plat » : une absence de donnee n'est pas une observation.
    v("une amplitude absente est INCONNUE, pas plate",
      juger({"amplitude": None, "seuil": 0.02, "seuil_est_un_repli": False})["etat"]
      == "inconnu")

    faux = [{"fichier": "a/p1.json", "etat": "plat"}, {"fichier": "a/p2.json", "etat": "plat"},
            {"fichier": "b/p1.json", "etat": "plat"}, {"fichier": "b/p2.json", "etat": "mesure"},
            {"fichier": "c/p1.json", "etat": "mesure"}]
    for x in faux:
        x.setdefault("seuil_est_un_repli", False)
    r = resumer(faux)
    v("une série entièrement plate est nommée", r["series_entierement_plates"] == ["a"])
    v("... et une série partiellement plate séparément",
      r["series_partiellement_plates"] == ["b"])
    # ⚠⚠ LA distinction qui porte l'audit : une serie dont UNE fenetre mesure reste
    # jugeable. Les mettre dans le meme sac condamnerait des verdicts valides.
    v("... et une série entièrement mesurée n'est dans aucune des deux",
      "c" not in r["series_entierement_plates"] + r["series_partiellement_plates"])
    # ⚠⚠ LE cœur de l'audit : une serie dont toutes les lectures sont le bord de la fenetre
    # a un α mesure EGAL a son α de plafond, donc un ecart nul, donc non discriminant.
    tout_au_bord = [{"couche_tracee": 20, "ecart_um": 48.0, "plafond_um": 48.0},
                    {"couche_tracee": 80, "ecart_um": 192.0, "plafond_um": 192.0}]
    j = alpha_discriminant(tout_au_bord, 0.2)
    v("une série entièrement au plafond n'est pas discriminante",
      j["discriminant"] is False, str(j))
    v("... et son écart à l'α de plafond est nul", abs(j["ecart"]) < 1e-12)
    # ⚠ Et le controle : une serie qui converge est TRES loin de son α de plafond, donc
    # discriminante -- sinon l'audit condamnerait aussi les bonnes surfaces.
    converge = [{"couche_tracee": 15, "ecart_um": 17.3, "plafond_um": 129.6},
                {"couche_tracee": 40, "ecart_um": 17.3, "plafond_um": 345.6}]
    jc = alpha_discriminant(converge, 0.2)
    v("une série qui converge est discriminante", jc["discriminant"] is True,
      f"{jc['ecart']:.3f}")
    v("... parce que son α mesuré est nul", abs(jc["alpha_mesure"]) < 1e-9)
    # ⚠⚠ La propriete qui rend l'audit rassurant plutot qu'alarmant, epinglee : l'α de
    # plafond vaut toujours ~1, donc une serie convergente en est loin par construction.
    # Si un jour ce n'etait plus vrai, ce temoin tomberait.
    v("une série convergente est TRÈS loin de son α de plafond",
      alpha_discriminant(converge, 0.2)["ecart"] > 0.9,
      f"{alpha_discriminant(converge, 0.2)['ecart']:.3f}")
    v("... alors qu'une série en travers en est proche",
      alpha_discriminant([{"couche_tracee": 20, "ecart_um": 44.0, "plafond_um": 48.0},
                          {"couche_tracee": 80, "ecart_um": 180.0, "plafond_um": 192.0}],
                         0.2)["ecart"] < 0.2)
    # ⚠ Une serie « utilisable » exige DEUX fenetres au moins et AUCUN profil au bord : une
    # seule fenetre ne fait pas un rapport, et un seul bord suffit a fausser l'exposant.
    dossier = {"a/p1.json": {"au_plafond": False, "etat": "mesure"},
               "a/p2.json": {"au_plafond": False, "etat": "mesure"}}
    v("deux profils libres du bord font une série utilisable",
      all(not x["au_plafond"] for x in dossier.values()) and len(dossier) >= 2)
    v("... et un seul profil au bord la disqualifie",
      any(x["au_plafond"] for x in {**dossier, "a/p3.json": {"au_plafond": True,
                                                             "etat": "mesure"}}.values()))

    v("une série d'un seul point ne rend pas de jugement",
      alpha_discriminant([tout_au_bord[0]], 0.2) is None)

    # ⚠⚠ La portee, mesuree et non affirmee : un fichier qui porte un profil sans s'appeler
    # `profil*` doit etre COMPTE comme hors portee, pas ignore en silence.
    import tempfile, os
    with tempfile.TemporaryDirectory() as t:
        d0 = Path(t)
        (d0 / "profil_41c.json").write_text(json.dumps(
            {"ecart_trace_um_median": 10.0, "couche_tracee": 20, "voxel_um": 2.4,
             "amplitude_mediane": 0.5, "amplitude_min": 0.02}), encoding="utf-8")
        (d0 / "autre_nom.json").write_text(json.dumps(
            {"ecart_trace_um_median": 10.0, "couche_tracee": 20, "voxel_um": 2.4,
             "amplitude_mediane": 0.5, "amplitude_min": 0.02}), encoding="utf-8")
        (d0 / "sans_profil.json").write_text(json.dumps({"x": 1}), encoding="utf-8")
        v("le balayage prend la famille nommée", len(balayer(d0)) == 1)
        v("... et compte hors portée celui qui ne l'est pas",
          hors_portee(d0) == [str(d0 / "autre_nom.json")], str(hors_portee(d0)))
        v("... sans compter un fichier qui ne porte pas de profil",
          all("sans_profil" not in x for x in hors_portee(d0)))

    v("les comptes s'additionnent",
      r["plats"] + r["mesures"] + r["inconnus"] == r["profils"])

    if echecs:
        print(f"\nECHEC ({echecs} failures, {controles} checks)")
        return 1
    print(f"ALL PASS ({echecs} failures, {controles} checks)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--racine", type=Path, default=Path("."))
    ap.add_argument("--json", type=Path)
    ap.add_argument("--verifier", action="store_true")
    a = ap.parse_args()
    if a.verifier:
        return verifier()

    profils = balayer(a.racine)
    dehors = hors_portee(a.racine)
    if not profils:
        print(f"aucun profil sous {a.racine}", file=sys.stderr)
        return 1
    r = resumer(profils)

    r["fichiers_hors_portee"] = dehors
    print(f"\n  {r['profils']} profils dans {r['series']} série(s)")
    if dehors:
        print(f"  ⚠ {len(dehors)} fichier(s) portent un profil HORS de la famille "
              f"« profil* » et ne sont pas ici — structure différente, analysés par "
              f"`derive_avec_profondeur.py`")
    print(f"    mesurent quelque chose : {r['mesures']}")
    print(f"    PLATS (rien à mesurer)  : {r['plats']}")
    print(f"    amplitude non rapportée : {r['inconnus']}")
    if r["sans_seuil_declare"]:
        print(f"    ⚠ {r['sans_seuil_declare']} profil(s) ne déclarent pas leur seuil — "
              f"repli à {AMPLITUDE_MIN_DEFAUT}")

    if r["series_entierement_plates"]:
        print(f"\n  ⚠⚠ {len(r['series_entierement_plates'])} série(s) dont AUCUNE fenêtre ne "
              f"mesure rien — un α calculé dessus est le rapport de deux bords de fenêtre :")
        for d in r["series_entierement_plates"]:
            print(f"      {d}")
    else:
        print("\n  ⭐ aucune série n'est entièrement plate : tout α publié depuis ces "
              "profils repose sur au moins une fenêtre qui mesure quelque chose")
    if r["series_partiellement_plates"]:
        print(f"\n  ⚠ {len(r['series_partiellement_plates'])} série(s) ont une fenêtre plate "
              f"et une qui mesure — jugeables, mais leur α porte sur moins de points qu'il "
              f"n'y paraît :")
        for d in r["series_partiellement_plates"]:
            print(f"      {d}")

    ind = r["series_indiscernables_du_plafond"]
    print(f"\n  profils dont l'écart EST le bord de la fenêtre : {r['au_plafond']}"
          f"/{r['profils']}")
    if ind:
        print(f"\n  ⚠⚠ {len(ind)} série(s) dont α ne peut PAS séparer « le pic recule » de "
              f"« il n'y avait pas de pic » — leur α mesuré est à moins d'une résolution "
              f"({r['resolution_alpha']}) de celui qu'on obtiendrait si toutes les lectures "
              f"étaient le bord de la fenêtre :")
        for d, j in sorted(ind.items()):
            print(f"      {d:<42} α mesuré {j['alpha_mesure']:+.4f}  "
                  f"α de plafond {j['alpha_si_tout_au_plafond']:+.4f}  "
                  f"écart {j['ecart']:.4f}")
    else:
        print("\n  ⭐ tout α publié se sépare de son α de plafond d'au moins une résolution")
    u = r["series_utilisables_pour_un_critere_relatif"]
    print(f"\n  séries où AUCUN profil n'est au bord de sa fenêtre — celles sur lesquelles "
          f"un critère relatif serait constructible : {len(u)}")
    for x in u[:8]:
        print(f"      {x}")
    if len(u) > 8:
        print(f"      … et {len(u) - 8} autre(s)")

    if r["alpha_min_indiscernable"] is not None:
        print(f"\n  ⭐⭐ et ce qui perd sa discrimination est EXACTEMENT le verdict "
              f"« suit la fenêtre » : le plus petit α non discriminant vaut "
              f"{r['alpha_min_indiscernable']:+.4f}")
        if r["alpha_max_convergent"] is not None:
            print(f"      contre {r['alpha_max_convergent']:+.4f} pour le plus grand α "
                  f"convergent — aucune série qui converge n'est concernée "
                  f"({len(r['convergents_indiscernables'])} sur {r['series_jugees']})")
        print("      Les deux causes possibles d'un α ~ 1 — le pic recule, ou il n'y a pas")
        print("      de pic — condamnent la trace toutes les deux. La conclusion pratique")
        print("      tient ; c'est la FORMULATION « le pic s'éloigne » qui sur-affirme.")

    if a.json:
        a.json.write_text(json.dumps({**r, "detail": profils}, indent=2,
                                     ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"\n  écrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
