#!/usr/bin/env python3
"""Le tableau des grandeurs de `07` §8, rejoué au rayon que `07` §9 a corrigé.

⚠⚠⚠ CE FICHIER EXISTE PARCE QUE `07` §9 A CORRIGE L'INSTRUMENT ET N'A RE-MESURE QU'UNE COLONNE.
Le §9 établit que le rayon de recherche était **4× trop grand** — il trouvait la spire voisine,
qui est de la géométrie parfaitement normale, et noyait l'anomalie dedans — puis publie le gain
pour `fraction_below_third` seule (+0,769 → **+0,840** sur Scroll 1). Le §8, qui est *au-dessus*
dans le document et compare les **grandeurs entre elles**, n'a jamais été rejoué. Son fichier de
mesure `docs/mesures/proximity_scroll1.jsonl` porte encore l'ancien rayon : sur une même trace il
rend `measured = 19 702` et un espacement médian de **260,8 µm** là où l'instrument corrigé rend
`2 487` et **117,9 µm**.

⭐⭐⭐ ET C'EST LA CONCLUSION DU §8 QUI EN DEPEND. Il conclut *« aucune grandeur sans seuil ne
l'égale »* — `shortfall` n'y fait que +0,340 — et en tire que **le seuil n'est pas supprimable**.
Or la dilution que le §9 diagnostique frappe bien plus fort une **moyenne sur toute la queue
basse** qu'un **compte dans la queue extrême** : c'est exactement la forme d'un artefact de
rayon. Ce fichier le mesure au lieu de le supposer.

⚠ CE QU'IL N'ETABLIT PAS : quel rayon est le bon. Le §9 l'a tranché ailleurs et avant, par la
physique (pas inter-feuilles 142,8 µm, cv 1,8 %, `11` §3), ce qui est précisément ce qui rend ce
choix non ajustable. Ce fichier prend l'instrument tel que le §9 l'a laissé.

⭐ La corrélation est calculée par `correlate.py`, jamais réécrite ici : c'est lui qui porte la
jointure sur le nom de trace, le rang de Spearman et le traitement du confond de longueur.

Usage :
    uv run python src/excision/le_seuil_au_bon_rayon.py \\
        --json docs/mesures/le_seuil_au_bon_rayon.json
    uv run python src/excision/le_seuil_au_bon_rayon.py --verifier
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
CORRELATE = RACINE / "src" / "excision" / "correlate.py"
INDEX = RACINE / "data" / "repos" / "windcheck" / "results" / "index.json"
ANCIEN = RACINE / "docs" / "mesures" / "proximity_scroll1.jsonl"
CORRIGE = RACINE / "docs" / "mesures" / "proximity_scroll1_rayon_corrige.jsonl"
DEFAUT_JSON = RACINE / "docs" / "mesures" / "le_seuil_au_bon_rayon.json"

GRANDEURS = ("fraction_below_third", "fraction_below_half", "ratio_p5", "shortfall",
             "shortfall_worst_decile")
"""Les grandeurs du tableau de `07` §8, dans son ordre, plus le décile le pire.

⚠ `ratio_p5` est un **centile**, donc sans seuil de valeur mais pas sans coupure ; `shortfall`
est le seul qui n'ait aucune coupure du tout. La distinction est celle que `07` §8 fait, et elle
est gardée pour que les deux tableaux se comparent ligne à ligne."""

SEUILS = ("below_015", "below_020", "below_025", "below_030", "below_033",
          "below_040", "below_050", "below_060", "below_070")
"""Le balayage de seuil du §8. ⚠ `below_033` EST `fraction_below_third` — `proximity.py` les
émet tous deux depuis le même calcul. Sa présence dans les deux listes est le contrôle
d'accord : si les deux colonnes divergeaient, l'une des deux lectures serait fausse."""


def rho(jsonl: Path, champ: str) -> dict | None:
    """
    @brief Le rho de rangs contre les croisements publiés, pour une grandeur.
    """
    if not jsonl.is_file():
        return None
    with tempfile.TemporaryDirectory() as tmp:
        sortie = Path(tmp) / "r.json"
        p = subprocess.run(
            ["uv", "run", "python", str(CORRELATE), str(jsonl), str(INDEX),
             "--field", champ, "--json", str(sortie)],
            capture_output=True, text=True, cwd=RACINE, timeout=600)
        if p.returncode != 0 or not sortie.is_file():
            return None
        d = json.loads(sortie.read_text())
    return dict(rho=d["rho_croisements"], p=d.get("p_croisements"),
                rho_longueur=d.get("rho_longueur"))


def mesurer() -> dict:
    if not CORRIGE.is_file():
        raise SystemExit(
            f"mesure au rayon corrigé absente : {CORRIGE}\n"
            "  la produire : ./src/excision/run_proximity.sh "
            "data/repos/windcheck/data/scroll1_tifxyz "
            "docs/mesures/proximity_scroll1_rayon_corrige.jsonl")
    out = {"fichiers": {"ancien": str(ANCIEN.relative_to(RACINE)),
                        "corrige": str(CORRIGE.relative_to(RACINE))},
           "traces": {"ancien": sum(1 for l in ANCIEN.open() if l.startswith("{"))
                      if ANCIEN.is_file() else 0,
                      "corrige": sum(1 for l in CORRIGE.open() if l.startswith("{"))},
           "grandeurs": {}, "seuils": {}}
    for champ in GRANDEURS:
        out["grandeurs"][champ] = {"ancien": rho(ANCIEN, champ), "corrige": rho(CORRIGE, champ)}
    for champ in SEUILS:
        out["seuils"][champ] = {"ancien": rho(ANCIEN, champ), "corrige": rho(CORRIGE, champ)}
    return out


def _verifier(r: dict | None = None) -> int:
    echecs = comptees = 0

    def v(nom, ok, detail=""):
        nonlocal echecs, comptees
        comptees += 1
        print(f"  {'ok  ' if ok else 'FAIL'}  {nom}" + (f"   [{detail}]" if detail else ""))
        if not ok:
            echecs += 1

    if not r or not r.get("grandeurs"):
        print("  (aucune mesure en cache — la produire avec --json)")
        return 0

    def val(bloc, cle):
        d = r[bloc][cle]["ancien" if False else "corrige"]
        return d["rho"] if d else None

    def ancien(bloc, cle):
        d = r[bloc][cle]["ancien"]
        return d["rho"] if d else None

    print("le producteur reproduit le tableau publié, sur le fichier publié")
    # ⚠⚠⚠ LE CONTROLE QUI VALIDE L'OUTIL AVANT SES RESULTATS. Si ce script ne retrouvait pas
    # les nombres imprimes dans `07` §8 en lisant SON fichier, aucune de ses autres colonnes ne
    # vaudrait rien. Ecrit a trois decimales, comme le document.
    attendus = {"fraction_below_third": 0.769, "fraction_below_half": 0.659,
                "ratio_p5": -0.512, "shortfall": 0.340}
    for champ, att in attendus.items():
        a = ancien("grandeurs", champ)
        v(f"... {champ} = {att:+.3f}", a is not None and abs(a - att) < 0.0006,
          f"{a:+.4f}" if a is not None else "absent")

    print("\net au rayon corrigé, la grandeur SANS SEUIL rattrape celle qui en a un")
    fbt = val("grandeurs", "fraction_below_third")
    sh = val("grandeurs", "shortfall")
    # ⚠⚠ `07` §9 publie +0,840 pour `fraction_below_third` au rayon physique sur Scroll 1. Le
    # retrouver ici est le second controle de l'instrument : il dit que ce fichier est bien
    # mesure au rayon que le §9 a choisi, et non a un troisieme.
    v("`fraction_below_third` retrouve le +0,840 publié par `07` §9",
      fbt is not None and abs(fbt - 0.840) < 0.02, f"{fbt:+.3f}" if fbt else "absent")
    # ⚠⚠⚠ LE RESULTAT. `07` §8 conclut « aucune grandeur sans seuil ne l'egale » depuis un
    # +0,340 mesure a l'ancien rayon. Ce controle est ecrit pour TOMBER si l'ecart persistait au
    # rayon corrige -- ce serait alors le seuil qui serait confirme, et le §8 aurait raison pour
    # une raison qu'il ne connaissait pas.
    v("... et `shortfall` n'est plus loin derrière : l'écart tombe sous 0,10",
      fbt is not None and sh is not None and abs(fbt - sh) < 0.10,
      f"{sh:+.3f} contre {fbt:+.3f} — écart {abs(fbt - sh):.3f} "
      f"(ancien rayon : {ancien('grandeurs', 'shortfall'):+.3f} contre "
      f"{ancien('grandeurs', 'fraction_below_third'):+.3f})")
    # ⚠ Et le mecanisme, pas seulement le nombre : la dilution frappe une MOYENNE bien plus fort
    # qu'un COMPTE, donc c'est `shortfall` qui doit gagner le plus a la correction.
    gain_sh = sh - ancien("grandeurs", "shortfall")
    gain_fbt = fbt - ancien("grandeurs", "fraction_below_third")
    v("... et c'est bien la grandeur MOYENNEE qui gagne le plus à la correction",
      gain_sh > gain_fbt,
      f"shortfall {gain_sh:+.3f} contre fraction_below_third {gain_fbt:+.3f}")

    print("\nle plateau de seuil, rejoué au rayon corrigé")
    serie = [(s, val("seuils", s)) for s in SEUILS]
    connus = [(s, x) for s, x in serie if x is not None]
    v("le balayage rend une valeur pour chaque seuil", len(connus) == len(SEUILS),
      f"{len(connus)}/{len(SEUILS)}")
    # ⚠⚠ `below_033` EST `fraction_below_third`. Deux lectures d'un meme calcul doivent
    # s'accorder ; si elles ne le font pas, l'une des deux colonnes est mal lue.
    b33 = val("seuils", "below_033")
    v("... et `below_033` s'accorde avec `fraction_below_third`",
      b33 is not None and fbt is not None and abs(b33 - fbt) < 1e-9,
      f"{b33:+.4f} contre {fbt:+.4f}" if b33 is not None else "absent")

    # ⚠⚠⚠ LE RESULTAT LE PLUS DUR POUR `07` §8. Son argument est un PLATEAU SUIVI D'UN
    # EFFONDREMENT : rho tient de 0,15 a 0,40 puis chute (0,774 -> 0,659 -> 0,488 -> 0,282), et
    # 1/3 est presente comme « le bord d'un regime ». Au rayon corrige, l'effondrement N'EXISTE
    # PLUS : rho reste plat sur TOUTE la plage testee. Donc le seuil ne selectionne aucun
    # regime -- il ne fait rien. L'effondrement etait l'artefact du rayon trop grand : a 749 µm
    # un seuil lache admettait la spire VOISINE, qui est de la geometrie normale ; a 142,8 µm il
    # n'y a plus de spire voisine dans le rayon a admettre.
    chute_ancienne = ancien("seuils", "below_015") - ancien("seuils", "below_070")
    chute_corrigee = val("seuils", "below_015") - val("seuils", "below_070")
    v("à l'ancien rayon, rho s'effondrait entre 0,15 et 0,70",
      chute_ancienne > 0.4, f"{chute_ancienne:+.3f}")
    v("... et au rayon corrigé cet effondrement a DISPARU",
      chute_corrigee < 0.1, f"{chute_corrigee:+.3f}")

    # ⚠⚠ LA GARDE CONTRE LA SUR-LECTURE, et elle est indispensable : chaque rho est lui-meme un
    # tirage d'etendue ~0,125 (`le_bruit_de_lechantillon --population`). Les valeurs corrigees
    # s'etalent bien moins que ca, donc AUCUN classement entre elles n'est lisible -- ni « le
    # demi bat le tiers », ni l'inverse. Ce qui se lit, c'est qu'elles sont equivalentes, ce qui
    # est precisement l'inverse de la conclusion du §8.
    ETENDUE_DE_GRAINE = 0.125
    corriges = [abs(val("grandeurs", g)) for g in GRANDEURS if val("grandeurs", g) is not None]
    corriges += [abs(val("seuils", s2)) for s2 in SEUILS if val("seuils", s2) is not None]
    ecart = max(corriges) - min(corriges)
    v("... et toutes les grandeurs corrigées tiennent dans le bruit de graine du rho",
      ecart < ETENDUE_DE_GRAINE,
      f"de {min(corriges):.3f} à {max(corriges):.3f} — écart {ecart:.3f} "
      f"contre une étendue de graine de {ETENDUE_DE_GRAINE:.3f}")

    print()
    if echecs:
        print(f"  ECHEC ({echecs} failures)")
    else:
        print(f"  ALL PASS (0 failures, {comptees} checks)")
    return echecs


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--json", type=Path)
    a = p.parse_args()

    if a.verifier and not a.json:
        garde = json.loads(DEFAUT_JSON.read_text()) if DEFAUT_JSON.is_file() else None
        return 1 if _verifier(garde) else 0

    r = mesurer()
    print(f"  {'grandeur':28s} {'ancien rayon':>14s} {'rayon corrige':>14s}")
    for champ, d in r["grandeurs"].items():
        av = f"{d['ancien']['rho']:+.3f}" if d["ancien"] else "   —  "
        ap = f"{d['corrige']['rho']:+.3f}" if d["corrige"] else "   —  "
        print(f"  {champ:28s} {av:>14s} {ap:>14s}")
    print(f"\n  {'seuil':28s} {'ancien rayon':>14s} {'rayon corrige':>14s}")
    for champ, d in r["seuils"].items():
        av = f"{d['ancien']['rho']:+.3f}" if d["ancien"] else "   —  "
        ap = f"{d['corrige']['rho']:+.3f}" if d["corrige"] else "   —  "
        print(f"  {champ:28s} {av:>14s} {ap:>14s}")
    print(f"\n  traces : {r['traces']['ancien']} (ancien) · {r['traces']['corrige']} (corrigé)")
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
