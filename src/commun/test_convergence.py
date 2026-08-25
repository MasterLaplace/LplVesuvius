#!/usr/bin/env python3
"""Une trace suit-elle une feuille ? -- par la CONVERGENCE, sans seuil ni verite terrain.

⚠⚠ Ce fichier est ne de trois hypotheses refutees le 2026-08-20, et c'est la refutation qui
l'a produit. On a d'abord cru que nos traces etaient a une spire de leur feuille, puis a
deux, puis que la difference etait de FORME et non de distance. Les trois fois, la mesure
suivait la fenetre de rendu au lieu de suivre le papyrus.

⭐⭐ Le motif de l'echec EST le test. Sur une surface qui suit sa feuille, la matiere est la,
tout pres, et l'elargissement de la fenetre ne change rien a la distance mesuree. Sur une
surface posee EN TRAVERS de l'empilement, il n'y a aucun pic a trouver : le « pic » est le
plus fort de ce que la fenetre contenait, donc il s'eloigne avec elle.

Mesure appariee, meme rouleau, meme chaine, meme instrument :

    fenetre   segment officiel   notre trace
       21          —               86,4 µm
       31        17,3 µm             —
       41          —              159,8 µm
       81        17,3 µm          311,0 µm
      161          —              682,6 µm

⭐ Ce test a trois proprietes qu'aucun autre instrument de ce depot n'a toutes :
  - **aucun seuil** : on compare une mesure a elle-meme ;
  - **aucune verite terrain** : ni segment de reference, ni carte d'encre ;
  - **aucune echelle** : le rapport est sans dimension, donc il traverse les rouleaux, les
    tailles de voxel et les resolutions sans etre re-etalonne.

⚠ Ce qu'il ne dit PAS : de combien corriger. Une trace qui ne converge pas n'a pas de
distance a sa feuille -- il n'y a pas de feuille a portee. Le test separe « posee a cote »
de « posee en travers », et c'est tout, ce qui est deja ce que rien d'autre ne faisait.

⚠ Il faut au moins DEUX fenetres dans un rapport d'au moins deux. Deux mesures trop proches
rendraient un rapport proche de 1 quelle que soit la surface -- c'est-a-dire un test qui ne
peut pas echouer.

Usage :
    uv run python src/commun/test_convergence.py --serie "21:86.4,41:159.84,81:311.04" \\
        --nom "notre trace" --json docs/convergence.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
sys.path[:0] = [str(p) for p in Path(__file__).resolve().parents[1].iterdir() if p.is_dir()]

RACINE = Path(__file__).resolve().parents[2]
# Une surface qui suit sa feuille garde sa distance ; on tolere le bruit de mesure.
CONVERGE = 1.25

# ⚠⚠ LE seuil sur α, nomme et EXPORTE. Il etait un litteral `0.7` enfoui dans `analyser`,
# et `juge_a_un_rendu.py` en avait redefini un SECOND a 0,75 pour la meme notion. Le cas
# qui l'a revele est reel : la spire 04 de la chaine a pas 0,125 sort a α = +0,722 — « suit
# la fenetre » pour ce fichier, PAS condamnee pour l'autre. Le meme tour, deux verdicts
# opposes, dans le meme depot. Un seuil, un endroit.
ALPHA_TRAVERS = 0.7

# ⚠⚠ La resolution de l'instrument, ecrite dans `43` : « α sur deux fenetres ne discrimine
# pas a ±0,2 pres ». Ce n'est donc PAS un seuil de plus — c'est la largeur en dessous de
# laquelle une comparaison de verdicts ne veut rien dire. Un verdict dont l'α est a moins de
# ca du seuil est un tirage au sort, et le compter dans un tableau « 4/7 contre 6/7 » fait
# passer un tirage pour une mesure.
BRUIT_ALPHA = 0.2

# ⚠ Une constante `SUIT_LA_FENETRE = 1.6` (un rapport de CROISSANCE) vivait ici, definie et
# utilisee nulle part, portant le nom d'un verdict que α seul decide. Un lecteur pouvait
# raisonnablement croire que le verdict venait d'elle. Supprimee plutot que gardee « au cas
# ou » : une constante morte au nom trompeur est une explication fausse posee dans le code.


# ⚠⚠ α EST UNE MEDIANE, DONC IL CACHE UNE MINORITE. Mesure du 2026-08-22 : une nappe etendue
# rend α = +0,000 et un ecart median de 17,3 µm — exactement ceux du segment officiel de
# reference — alors que **9,1 % de ses fenetres ont leur pic AU BORD**, contre 0,0 % pour la
# reference. Un dixieme de la surface n'a aucune feuille a portee, et le verdict ne le dit
# pas, parce qu'une mediane est insensible a une minorite. La periphERIE se VOIT sur le rendu
# (`44`), pas dans α.
#
# ⚠⚠ ET LE COMPTE D'AUTO-INTERSECTIONS NE REMPLACE PAS CE COMPLEMENT. Contre-exemple mesure
# le 2026-08-22 : une surface a **ZERO** auto-intersection et α = **+1,806**, la pire de toute
# sa campagne. Une surface peut donc etre posee entierement en travers sans se croiser une
# seule fois — se replier et etre mal posee sont deux defauts differents.
#
# ⭐ Le complement est `au_bord_relief`, deja calcule par `depth_profile` pour chaque surface.
# Au-dela de ce seuil, le verdict porte une reserve : ce n'est pas un second verdict, c'est
# la mention qu'une part de la surface echappe a celui qui est rendu.
# Valeur posee a partir des cas mesures : 0,000 sur la reference et sur les spires radiales
# qui convergent, 0,091 sur l'extension, 0,25 a 0,31 sur celles qui cassent.
AU_BORD_RESERVE = 0.05


def analyser(serie: list[tuple[int, float]], au_bord: float | None = None,
             amplitude: float | None = None, amplitude_min: float | None = None,
             borne: str | None = None) -> dict:
    """Rendre le verdict d'une serie (couches, ecart) -- ou refuser de le rendre.

    ⚠⚠ **α = 1 a DEUX causes, et elles ne veulent pas dire la meme chose.** Un pic qui
    RECULE avec la fenetre est une mesure : il y a un pic, il est loin, sa distance suit la
    fenetre. Un profil PLAT n'en est pas une : il n'y a aucun pic, donc l'ecart rapporte est
    le bord de la fenetre par defaut -- et le rapport de deux bords de fenetre vaut le
    rapport des fenetres, donc α = 1 **par identite arithmetique**, quoi qu'il y ait dans le
    volume.

    Mesure du 2026-08-22 qui l'a impose : sur `PHercParis4`, la prediction `m7` rend
    `amplitude_mediane = 0,0` (le minimum de detection de l'instrument est 0,02),
    `au_bord = 1,0`, `au_bord_relief = nan`, et des ecarts de 48,00 et 192,00 µm qui sont
    exactement les demi-fenetres a 41 et 161 couches. Le verdict imprime etait pourtant
    « suit la fenetre — il n'y a aucune feuille a portee », affirme avec la meme assurance
    que sur une vraie mesure.

    ⭐ `amplitude` distingue les deux, et `depth_profile` la calcule deja. Sous le minimum,
    ce fichier REFUSE : « je n'ai rien mesure » n'est pas « la feuille est loin ».

    ⚠⚠ **Et le refus ci-dessus ne suffit pas, mesure du 2026-08-23.** L'amplitude passee
    ici est un MAXIMUM sur les fenetres — « si une seule fenetre a du relief, la mesure
    n'est pas vide ». Juste pour « y a-t-il quelque chose ici », faux pour « quelle est
    la pente » : α est une pente a deux appuis, et un appui qui ne mesure rien n'en est
    pas un. `borne` porte ce que `appui_de_pente` en dit — `exacte`, `majorant`,
    `minorant` ou `aucune` — et le verdict rendu porte alors le champ `appuis_portent`.
    ⭐ Ce n'est PAS un refus de plus : un appui au bord est une borne, donc α garde un
    SIGNE, et un majorant preserve exactement ce qui est sous le seuil.
    """
    serie = sorted(serie)
    if len(serie) < 2:
        return {"verdict": "indecidable", "raison": "une seule fenêtre", "serie": serie}
    (n0, e0), (n1, e1) = serie[0], serie[-1]
    if n1 / n0 < 2:
        return {"verdict": "indecidable",
                "raison": f"fenêtres trop proches ({n0} et {n1}, rapport {n1/n0:.2f})",
                "serie": serie}
    if e0 <= 0:
        return {"verdict": "indecidable", "raison": "écart nul dans la fenêtre étroite",
                "serie": serie}
    # ⚠⚠ Le refus qui compte : sans relief, les ecarts ne sont pas des mesures.
    if amplitude is not None and amplitude_min is not None and amplitude < amplitude_min:
        return {"verdict": "indecidable",
                "raison": (f"profil PLAT — amplitude {amplitude:.4f} sous le minimum de "
                           f"détection {amplitude_min:.4f} de l'instrument. Les écarts "
                           f"rapportés sont les bords de fenêtre, donc leur rapport vaut "
                           f"celui des fenêtres et α ≈ 1 par identité, quoi qu'il y ait "
                           f"dans le volume"),
                "serie": serie, "amplitude": amplitude, "amplitude_min": amplitude_min}

    croissance = e1 / e0
    fenetre = n1 / n0
    # ⚠ On normalise par l'elargissement : comparer une serie 21->81 a une serie 21->41
    # sans ca ferait passer la premiere pour « pire » alors qu'on l'a juste regardee plus
    # loin. L'exposant est celui d'une loi de puissance ecart ∝ fenetre^alpha.
    import math
    alpha = math.log(croissance) / math.log(fenetre)

    if croissance <= CONVERGE:
        verdict, sens = "converge", ("la distance ne bouge pas quand la fenêtre s'élargit — "
                                     "la matière est là, tout près")
    elif alpha >= ALPHA_TRAVERS:
        verdict, sens = "suit la fenêtre", ("le « pic » s'éloigne avec la fenêtre — il n'y a "
                                            "aucune feuille à portée, la surface est posée "
                                            "en travers de l'empilement")
    else:
        verdict, sens = "intermédiaire", ("la mesure bouge sans suivre la fenêtre — ni "
                                          "convergée ni clairement en travers")
    # ⭐ Chaque verdict porte sa propre FRAGILITE. Sans ce champ, un tableau qui compare
    # deux campagnes en comptant les verdicts ne peut pas dire lesquels de ses comptes
    # tiennent — et ce depot en a publie trois.
    marge = abs(alpha - ALPHA_TRAVERS)
    r = {"verdict": verdict, "sens": sens, "serie": serie,
         "croissance": croissance, "elargissement": fenetre, "alpha": alpha,
         "marge_au_seuil": marge, "fragile": bool(marge < BRUIT_ALPHA)}
    if amplitude is not None:
        r["amplitude"] = amplitude
    if borne is not None:
        # ⚠ « tient » ne veut pas dire « juste » : il veut dire qu'aucune valeur
        # admissible de α vrai ne fait changer le verdict de cote du seuil.
        r["borne"] = borne
        condamne = alpha >= ALPHA_TRAVERS
        r["appuis_portent"] = bool(
            borne == "exacte"
            or (borne == "minorant" and condamne)
            or (borne == "majorant" and not condamne))
        if not r["appuis_portent"]:
            r["reserve_appuis"] = (
                f"⚠⚠ les appuis ne portent pas ce verdict — la borne est "
                f"« {borne} », donc α vrai peut être de l'autre côté du seuil "
                f"{ALPHA_TRAVERS}. Voir `appui_de_pente.py`")
    if au_bord is not None:
        r["au_bord"] = au_bord
        r["reserve"] = bool(au_bord >= AU_BORD_RESERVE)
        if r["reserve"]:
            # ⚠ La formulation depend du verdict, et la premiere version ne le faisait pas :
            # elle disait « et α ne le montre pas » meme sur une surface deja condamnee, ou
            # α le montre parfaitement. La reserve n'a de valeur d'ALERTE que quand le
            # verdict est bon ; sur un verdict mauvais elle CHIFFRE l'etendue du mal.
            if verdict == "converge":
                r["sens"] += (f" — ⚠ mais {au_bord * 100:.0f} % des fenêtres ont leur pic AU "
                              f"BORD : cette part de la surface n'a aucune feuille à portée, "
                              f"et α ne le montre pas (c'est une médiane)")
            else:
                r["sens"] += (f" — et {au_bord * 100:.0f} % des fenêtres ont leur pic AU "
                              f"BORD, ce qui chiffre l'étendue du mal que α ne fait que "
                              f"signaler")
    return r


def verifier() -> int:
    """Temoin hors ligne : les deux verdicts francs, et les trois refus."""
    echecs = controles = 0

    def v(nom, cond, detail=""):
        nonlocal echecs, controles
        controles += 1
        if not cond:
            echecs += 1
            print(f"  ECHEC  {nom}" + (f"  — {detail}" if detail else ""))

    # Le cas mesure : notre trace double a chaque doublement.
    r = analyser([(21, 86.4), (41, 159.84), (81, 311.04), (161, 682.56)])
    v("une mesure qui double avec la fenêtre suit la fenêtre",
      r["verdict"] == "suit la fenêtre", r["verdict"])
    v("... avec un exposant proche de 1", abs(r["alpha"] - 1.0) < 0.15, f"{r['alpha']:.3f}")

    # Le cas mesure : le segment officiel ne bouge pas.
    v("une mesure stable converge",
      analyser([(31, 17.28), (81, 17.30)])["verdict"] == "converge")
    v("un petit bruit ne casse pas la convergence",
      analyser([(31, 17.0), (81, 20.0)])["verdict"] == "converge")

    # ⭐ Les trois refus : sans eux le test rendrait un verdict sur rien.
    v("une seule fenêtre est indécidable",
      analyser([(81, 300.0)])["verdict"] == "indecidable")
    v("deux fenêtres trop proches sont indécidables",
      analyser([(41, 100.0), (61, 150.0)])["verdict"] == "indecidable",
      analyser([(41, 100.0), (61, 150.0)])["verdict"])
    v("un écart nul est indécidable, pas convergé",
      analyser([(21, 0.0), (81, 0.0)])["verdict"] == "indecidable")

    # ⭐⭐ La FRAGILITE d'un verdict. Le cas est reel et il est la raison de ce champ : la
    # spire 04 de la chaine a pas 0,125 sort a α = +0,722, donc « suit la fenetre » — a
    # 0,022 du seuil, quand l'instrument ne discrimine pas a ±0,2 pres. La compter comme une
    # rupture dans un tableau « 4/7 contre 6/7 » fait passer un tirage au sort pour une mesure.
    r_bord = analyser([(31, 100.0), (81, 200.0)])
    v("un α juste au-dessus du seuil est bien « suit la fenêtre »",
      r_bord["verdict"] == "suit la fenêtre", f"{r_bord['alpha']:.3f} {r_bord['verdict']}")
    v("... et il est marqué FRAGILE", r_bord["fragile"],
      f"α = {r_bord['alpha']:.3f}, marge {r_bord['marge_au_seuil']:.3f}")
    v("le cas réel de la spire 04 tombe bien à 0,022 du seuil",
      abs(r_bord["marge_au_seuil"] - 0.022) < 0.005, f"{r_bord['marge_au_seuil']:.4f}")

    r_franc = analyser([(31, 100.0), (81, 355.0)])
    v("un α franchement en travers n'est PAS fragile", not r_franc["fragile"],
      f"α = {r_franc['alpha']:.3f}, marge {r_franc['marge_au_seuil']:.3f}")
    r_plat = analyser([(31, 100.0), (81, 100.0)])
    v("une convergence franche n'est PAS fragile", not r_plat["fragile"],
      f"α = {r_plat['alpha']:.3f}, marge {r_plat['marge_au_seuil']:.3f}")
    # ⚠ Temoin du temoin : si la largeur de bruit etait nulle, RIEN ne serait jamais fragile
    # et le champ ne dirait rien. Il faut donc qu'elle soit non nulle ET que le verdict le
    # plus proche du seuil du depot y tombe.
    v("la largeur de bruit est celle documentée dans `43`", BRUIT_ALPHA == 0.2,
      str(BRUIT_ALPHA))

    # ⚠⚠ Un SEUL seuil pour tout le depot. `juge_a_un_rendu.py` en avait redefini un second
    # a 0,75 en pretendant en commentaire reprendre celui d'ici. Ce controle rend un futur
    # desaccord impossible a livrer.
    import juge_a_un_rendu
    v("le juge à un rendu utilise LE seuil, pas une copie",
      juge_a_un_rendu.SEUIL_TRAVERS == ALPHA_TRAVERS,
      f"{juge_a_un_rendu.SEUIL_TRAVERS} contre {ALPHA_TRAVERS}")

    # ⭐⭐ LA RESERVE : α est une mediane, donc il cache une minorite. Le cas est reel et
    # c'est la figure qui l'a montre, pas le verdict — une extension a α = +0,000 dont 9,1 %
    # des fenetres ont leur pic au bord.
    r_ok = analyser([(31, 17.3), (81, 17.3)], au_bord=0.0)
    v("une surface sans pic au bord ne porte aucune réserve", not r_ok["reserve"])
    r_res = analyser([(31, 17.3), (81, 17.3)], au_bord=0.091)
    v("le cas mesuré (9,1 % au bord) porte une réserve", r_res["reserve"],
      f"au_bord={r_res['au_bord']}")
    v("... et le verdict reste « converge » — la réserve n'est PAS un second verdict",
      r_res["verdict"] == "converge", r_res["verdict"])
    v("... et la réserve est DITE dans le sens, pas seulement dans un champ",
      "AU BORD" in r_res["sens"])
    v("sans mesure de bord, aucun champ n'est inventé",
      "au_bord" not in analyser([(31, 17.3), (81, 17.3)]))
    # ⚠⚠ La formulation DEPEND du verdict. Premiere version : « et α ne le montre pas »
    # etait ajoute meme sur une surface deja condamnee, ou α le montre parfaitement.
    r_mauvais = analyser([(31, 100.0), (81, 355.0)], au_bord=0.557)
    v("sur un verdict mauvais, la réserve CHIFFRE au lieu de prétendre qu'α cache",
      "ne le montre pas" not in r_mauvais["sens"] and "56 %" in r_mauvais["sens"],
      r_mauvais["sens"][-90:])
    v("sur un verdict bon, elle dit bien qu'α ne le montre pas",
      "ne le montre pas" in r_res["sens"])

    # ⚠ Temoin du temoin : si le seuil etait a zero, TOUT porterait une reserve et la mention
    # ne voudrait plus rien.
    v("une surface parfaite ne porte pas de réserve à cause d'un seuil nul",
      AU_BORD_RESERVE > 0.0, str(AU_BORD_RESERVE))

    # Un cas intermediaire doit etre nomme, pas range de force.
    # ⚠⚠ LE REFUS DU PROFIL PLAT, et sa sonde. Mesure du 2026-08-22 sur `PHercParis4` : la
    # prediction `m7` rend une amplitude de 0,0 pour un minimum de detection de 0,02, et des
    # ecarts de 48,00 et 192,00 µm qui sont EXACTEMENT les demi-fenetres a 41 et 161
    # couches. Leur rapport vaut donc celui des fenetres, et α = 1,01 sort par identite
    # arithmetique -- pourtant le verdict imprime etait « suit la fenetre », affirme avec la
    # meme assurance que sur une vraie mesure.
    plat = analyser([(41, 48.0), (161, 192.0)], au_bord=1.0, amplitude=0.0,
                    amplitude_min=0.02)
    v("un profil PLAT rend le verdict indécidable", plat["verdict"] == "indecidable",
      plat.get("verdict"))
    v("... en nommant l'amplitude", "amplitude" in (plat.get("raison") or ""))
    # ⚠ Et le controle : la MEME serie avec du relief doit rester jugee, sinon le refus
    # eteindrait aussi les vraies mesures qui se trouvent avoir α = 1.
    avec = analyser([(41, 48.0), (161, 192.0)], au_bord=1.0, amplitude=0.09,
                    amplitude_min=0.02)
    v("... alors qu'avec du relief la même série est jugée",
      avec["verdict"] == "suit la fenêtre", avec.get("verdict"))
    v("... et α y vaut bien ~1", abs(avec["alpha"] - 1.0) < 0.05, f"{avec['alpha']:.3f}")
    # --- les APPUIS de la pente, 2026-08-23 ------------------------------------------
    # ⚠⚠ Le refus « profil PLAT » ci-dessus prend l'amplitude MAXIMALE des fenetres. Une
    # serie dont la fenetre etroite ne mesure rien et la large mesure passe donc au travers,
    # et c'est exactement le cas des trois candidats `ps256` publies dans `48`.
    maj = analyser([(41, 48.0), (161, 172.8)], borne="majorant")
    v("une condamnation sur un MAJORANT ne tient pas", maj["appuis_portent"] is False,
      f"α = {maj['alpha']:.3f}")
    v("... et elle le dit", "appuis ne portent pas" in (maj.get("reserve_appuis") or ""))
    v("une convergence sur un MAJORANT tient",
      analyser([(31, 100.0), (81, 104.0)], borne="majorant")["appuis_portent"] is True)
    v("une condamnation sur un MINORANT tient",
      analyser([(41, 48.0), (161, 172.8)], borne="minorant")["appuis_portent"] is True)
    v("une convergence sur un MINORANT ne tient pas",
      analyser([(31, 100.0), (81, 104.0)], borne="minorant")["appuis_portent"] is False)
    v("deux appuis francs portent tout",
      analyser([(41, 48.0), (161, 172.8)], borne="exacte")["appuis_portent"] is True
      and analyser([(31, 100.0), (81, 104.0)], borne="exacte")["appuis_portent"] is True)
    v("sans appui, rien ne porte",
      analyser([(41, 48.0), (161, 172.8)], borne="aucune")["appuis_portent"] is False)
    # ⚠ Sans borne fournie, le champ est ABSENT et non False : « on n'a pas regarde » n'est
    # pas « les appuis ne portent pas ». Confondre les deux ferait lire une absence de
    # controle comme un echec de controle -- le defaut que ce depot a paye sur l'index zero.
    v("sans borne, le champ est absent et non faux",
      "appuis_portent" not in analyser([(41, 48.0), (161, 172.8)]))

    # ⚠ Sans amplitude fournie, rien ne change : les appelants anciens gardent leur verdict.
    v("sans amplitude, le comportement est inchangé",
      analyser([(41, 48.0), (161, 192.0)])["verdict"] == "suit la fenêtre")
    v("une amplitude AU-DESSUS du minimum ne refuse pas",
      analyser([(31, 17.3), (81, 17.3)], amplitude=0.5,
               amplitude_min=0.02)["verdict"] == "converge")

    m = analyser([(21, 100.0), (81, 160.0)])
    v("une croissance lente est dite intermédiaire", m["verdict"] == "intermédiaire",
      f"{m['verdict']} alpha={m['alpha']:.2f}")

    if echecs:
        print(f"\nECHEC ({echecs} failures, {controles} checks)")
        return 1
    print(f"ALL PASS ({echecs} failures, {controles} checks)")
    return 0


def borne_des_appuis(profils: list[dict]) -> str | None:
    """Le signe que les deux appuis de la pente donnent à α, ou None si on ne sait pas.

    ⚠ Délégué à `appui_de_pente`, jamais réécrit ici : deux réponses à « cet appui
    mesure-t-il quelque chose » finiraient par se contredire, et c'est précisément le
    désaccord qu'une borne existe pour empêcher.

    ⚠ L'import est différé parce que `appui_de_pente` lit `ALPHA_TRAVERS` dans ce
    fichier-ci. Le faire au niveau du module ferait un cycle.
    """
    if len(profils) < 2:
        return None
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    sys.path[:0] = [str(p) for p in Path(__file__).resolve().parents[1].iterdir() if p.is_dir()]
    try:
        from appui_de_pente import appui, borne
        from audit_profils_plats import lire_profil            # noqa: F401
    except ImportError:                                        # pragma: no cover
        return None
    vus = []
    for d in profils:
        ct, vx = d.get("couche_tracee"), d.get("voxel_um")
        if ct is None or not vx:
            return None
        plafond = float(ct) * float(vx)
        e = float(d["ecart_trace_um_median"])
        vus.append({"couche_tracee": int(ct),
                    "au_plafond": e >= plafond * (1 - 1e-9),
                    "amplitude": d.get("amplitude_mediane"),
                    "seuil": d.get("amplitude_min") if d.get("amplitude_min") is not None
                    else 0.02})
    vus.sort(key=lambda y: y["couche_tracee"])
    if vus[0]["couche_tracee"] == vus[-1]["couche_tracee"]:
        return None
    return borne(appui(vus[0]), appui(vus[-1]))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--serie", action="append", default=[],
                    help="couches:écart,couches:écart… (répétable)")
    ap.add_argument("--nom", action="append", default=[])
    ap.add_argument("--au-bord", action="append", default=[], type=float,
                    help="part des fenêtres dont le pic tombe AU BORD (`au_bord_relief` de "
                         "depth_profile) — le complément que α, étant une médiane, ne "
                         "montre pas")
    ap.add_argument("--depuis", action="append", default=[], metavar="JSON[=nom]",
                    help="reprendre les séries d'un verdict déjà écrit (répétable) ; "
                         "« fichier.json=nom » renomme la série")
    ap.add_argument("--json")
    # ⚠⚠ `--profil` construit la serie DEPUIS les fichiers de profil, et lit au passage
    # l'amplitude et la part au bord. C'est ce qui evite de recopier a la main des ecarts
    # que le profil contient deja -- une transcription est une occasion de se tromper, et
    # c'est en la faisant que j'ai lance un verdict sur un profil plat sans le voir.
    ap.add_argument("--profil", action="append", default=[], metavar="FICHIER",
                    help="profil de depth_profile.py ; répétable, un par fenêtre")
    ap.add_argument("--verifier", action="store_true")
    a = ap.parse_args()
    if a.verifier:
        return verifier()
    # ⚠⚠ Rassembler des verdicts DÉJÀ écrits plutôt que de recopier leurs nombres à la
    # main. Une figure qui compare trois surfaces a besoin des trois séries dans un seul
    # fichier ; les retaper est le mode de panne que ce dépôt a payé plusieurs fois — un
    # chiffre juste au moment où on le lit et faux dès que la mesure bouge.
    reprises = []
    for spec in a.depuis:
        chemin, _, renomme = spec.partition("=")
        p_json = Path(chemin)
        if not p_json.is_file():
            print(f"⚠ absent, ignoré : {chemin}", file=sys.stderr)
            continue
        for brut_serie in json.loads(p_json.read_text(encoding="utf-8")).get("series", []):
            # ⚠⚠ RECALCULER au lieu de faire confiance aux champs stockes. Un verdict ecrit
            # hier a ete rendu par les seuils d'hier ; si un seuil a bouge depuis, le champ
            # `verdict` du fichier est perime et rien ne le dit. Ce depot a deja publie une
            # mesure faite sur un binaire perime, et lit desormais ses catalogues en
            # recalculant pour la meme raison. La SERIE, elle, est une donnee : elle ne
            # peut pas etre perimee.
            recalcule = analyser([tuple(x) for x in brut_serie["serie"]],
                                 brut_serie.get("au_bord"))
            avant = brut_serie.get("verdict")
            if avant and avant != recalcule["verdict"]:
                print(f"⚠ verdict PÉRIMÉ dans {p_json.name} : « {avant} » recalculé en "
                      f"« {recalcule['verdict']} »", file=sys.stderr)
                recalcule["etait"] = avant
            recalcule["nom"] = renomme or brut_serie.get("nom", p_json.stem)
            reprises.append(recalcule)

    # ⚠⚠ La serie construite DEPUIS les profils : l'ecart, la part au bord ET l'amplitude
    # viennent du meme fichier, donc ils ne peuvent pas se contredire. Le chemin `--serie`
    # reste, pour les references dont on n'a que les nombres.
    if a.profil:
        pts, bords, ampl, bruts = [], [], [], []
        for f in a.profil:
            pf = Path(f)
            if not pf.is_file():
                ap.error(f"profil absent : {f}")
            d_ = json.loads(pf.read_text(encoding="utf-8"))
            d_ = d_[0] if isinstance(d_, list) else d_
            manquant = [k for k in ("ecart_trace_um_median", "couche_tracee")
                        if k not in d_]
            if manquant:
                ap.error(f"{f} : champs absents {manquant}")
            # ⚠ Le nombre de couches se deduit de `couche_tracee`, qui est la MOITIE de la
            # fenetre par construction du rendu. Le lire dans le nom du fichier marcherait
            # aussi et dependrait d'une convention de nommage, qui n'est pas une donnee.
            pts.append((int(d_["couche_tracee"]) * 2 + 1, float(d_["ecart_trace_um_median"])))
            if d_.get("au_bord") is not None:
                bords.append(float(d_["au_bord"]))
            if d_.get("amplitude_mediane") is not None:
                ampl.append((float(d_["amplitude_mediane"]),
                             float(d_.get("amplitude_min") or 0.0)))
            bruts.append(d_)
        nom = a.nom[len(a.serie)] if len(a.nom) > len(a.serie) else "série de profils"
        # ⚠ On prend le MAXIMUM d'amplitude sur les fenetres : si une seule fenetre a du
        # relief, la mesure n'est pas vide. Prendre la mediane condamnerait une serie dont
        # une fenetre sur trois mesure quelque chose.
        amax = max((x for x, _ in ampl), default=None)
        amin = max((y for _, y in ampl), default=None)
        r = analyser(pts, max(bords) if bords else None, amax, amin,
                     borne_des_appuis(bruts))
        r["nom"] = nom
        r["profils"] = [str(f) for f in a.profil]
        reprises.append(r)

    if not a.serie and not reprises:
        ap.error("donner au moins une --serie, un --depuis ou un --profil, ou --verifier")

    sorties = list(reprises)
    for r in reprises:
        pts = "  ".join(f"{n}c→{e:.1f}" for n, e in r["serie"])
        marque = "  ⚠ FRAGILE" if r.get("fragile") else ""
        print(f"\n  {r['nom']}\n    {pts}")
        if r.get("verdict") == "indecidable":
            print(f"    ⚠⚠ INDÉCIDABLE — {r['raison']}")
        else:
            print(f"    α = {r.get('alpha', 0.0):+.2f} — {r.get('verdict', '?')}{marque}")
            if r.get("sens"):
                print(f"    {r['sens']}")
            if r.get("reserve_appuis"):
                print(f"    {r['reserve_appuis']}")
            elif r.get("borne") in ("majorant", "minorant"):
                print(f"    ⭐ appui au bord, mais α est un {r['borne']} — le "
                      f"verdict tient malgré tout")

    for i, brut in enumerate(a.serie):
        nom = a.nom[i] if i < len(a.nom) else f"série {i + 1}"
        serie = [(int(p.split(":")[0]), float(p.split(":")[1])) for p in brut.split(",")]
        r = analyser(serie, a.au_bord[i] if i < len(a.au_bord) else None)
        r["nom"] = nom
        sorties.append(r)
        pts = "  ".join(f"{n}c→{e:.1f}" for n, e in r["serie"])
        print(f"\n  {nom}\n    {pts}")
        if r["verdict"] == "indecidable":
            print(f"    ⚠ INDÉCIDABLE — {r['raison']}")
        else:
            print(f"    ×{r['croissance']:.2f} pour ×{r['elargissement']:.1f} de fenêtre "
                  f"(α = {r['alpha']:+.2f})")
            marque = {"converge": "✅", "suit la fenêtre": "⚠⚠", "intermédiaire": "⚠"}[r["verdict"]]
            print(f"    {marque} {r['verdict'].upper()} — {r['sens']}")

    # ⭐⭐ Le recensement de fragilite. Un tableau qui compare deux campagnes en COMPTANT
    # les verdicts ne dit rien de ce que ses comptes valent ; celui-ci le dit.
    juges = [r for r in sorties if "fragile" in r]
    fragiles = [r for r in juges if r["fragile"]]
    if len(juges) >= 2:
        print(f"\n  {len(fragiles)} verdict(s) sur {len(juges)} sont FRAGILES — leur α est "
              f"à moins de {BRUIT_ALPHA} du seuil de {ALPHA_TRAVERS},")
        print(f"  or l'instrument ne discrimine pas à ±{BRUIT_ALPHA} près (`43`). "
              f"Les compter comme des mesures ferait")
        print("  passer un tirage au sort pour un résultat.")
        for r in fragiles:
            print(f"    ⚠ {r['nom']} : α = {r['alpha']:+.3f}, à "
                  f"{r['marge_au_seuil']:.3f} du seuil — verdict « {r['verdict']} »")

    if a.json:
        Path(a.json).write_text(json.dumps({"series": sorties}, indent=2,
                                           ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"\n  écrit : {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
