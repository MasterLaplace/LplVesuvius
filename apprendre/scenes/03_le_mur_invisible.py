"""Vidéo 3 — Le mur invisible : quand la stabilité n'est qu'un réglage.

⚠⚠ **C'est le résultat le plus frappant du dépôt, et le plus transférable.** Six exécutions
d'un même calcul rendaient des résultats identiques à 0,3 % près. Ça ressemble à de la
robustesse. C'était une troncature : toutes butaient sur le même mur.

⭐ La leçon dépasse ce projet : **quand des exécutions indépendantes s'accordent au-delà de
ce que leur bruit permet, ce n'est pas une bonne nouvelle** — c'est un réglage partagé qui
parle à leur place. Et sa cohérence est précisément ce qui le rend invisible.
"""
from manim import *
import numpy as np

FOND = "#12100E"
CRAIE = "#EDE8E0"
AMBRE = "#D89A3E"
PAPYRUS = "#C9B896"
FROID = "#5A82A8"
ROUGE = "#C4483C"
VERT = "#5E9C6A"
SOURD = "#4E4640"

config.background_color = FOND


def titre(txt, taille=32):
    return Text(txt, font_size=taille, color=CRAIE, weight=BOLD)


def phrase(txt, taille=23, couleur=CRAIE):
    return Text(txt, font_size=taille, color=couleur)


def legende(txt, taille=21, couleur=CRAIE, rang=0):
    """La légende, ancrée en bas — `rang` 1 la pose au-dessus de la ligne principale.

    ⚠⚠ Le `rang` existe parce que deux scènes posaient une seconde ligne À LA MAIN, avec un
    `buff` choisi au jugé. La sonde n'en voyait qu'une des deux : elle vise l'appel en UNE
    ligne, et la seconde était écrite sur deux. Une sonde qui attrape une ORTHOGRAPHE et pas
    la règle laisse passer exactement ce qu'elle surveille.

    ⚠ Et le motif n'est PAS cité en clair ici : l'écrire faisait matcher la sonde sur cette
    docstring même — neuvième fois que ce dépôt paie l'auto-match.
    """
    return phrase(txt, taille, couleur).to_edge(DOWN, buff=0.6 + rang * 0.9)


class SixFoisLeMemeResultat(Scene):
    """Six exécutions, six résultats identiques. Ça a l'air excellent."""

    def construct(self):
        t = titre("Six fois le même calcul").scale(0.8)
        self.play(Write(t))
        self.wait(1)
        self.play(t.animate.scale(0.72).to_edge(UP))

        intro = legende("on relance six fois, sans rien changer")
        self.play(FadeIn(intro))

        # ── Six barres d'aire, toutes égales ──────────────────────────────────────
        base = DOWN * 1.9
        barres = VGroup()
        vals = VGroup()
        for i in range(6):
            h = 2.6
            r = Rectangle(width=0.85, height=h, fill_color=FROID, fill_opacity=0.6,
                          stroke_width=0)
            r.move_to(base + RIGHT * (i - 2.5) * 1.35 + UP * h / 2)
            barres.add(r)
            v = phrase("19,83", 18, CRAIE).next_to(r, UP, buff=0.12)
            vals.add(v)
        self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in barres], lag_ratio=0.18),
                  run_time=2.4)
        self.play(LaggedStart(*[FadeIn(v) for v in vals], lag_ratio=0.15), run_time=1.6)

        unite = phrase("aire de la surface obtenue, en cm²", 18, SOURD)
        unite.next_to(barres, DOWN, buff=0.35)
        self.play(FadeIn(unite))
        self.wait(2)

        # ⭐ La lecture spontanée, celle qu'on a faite pendant des semaines.
        lecture = phrase("dispersion : 0,3 %", 28, VERT)
        lecture.to_edge(DOWN, buff=1.5)
        self.play(FadeOut(intro), FadeIn(lecture))
        self.wait(2)
        bravo = phrase("« excellent — ce calcul est très reproductible »", 24, VERT)
        bravo.next_to(lecture, DOWN, buff=0.35)
        self.play(FadeIn(bravo))
        self.wait(3)

        self.play(*[FadeOut(m) for m in (t, barres, vals, unite, lecture, bravo)])


class LeMur(Scene):
    """Elles n'étaient pas d'accord : elles s'arrêtaient au même endroit."""

    def construct(self):
        t = titre("Elles n'étaient pas d'accord").scale(0.78).to_edge(UP)
        self.play(Write(t))

        # ── Six traces qui poussent, et un mur ────────────────────────────────────
        mur_x = 1.6
        mur = DashedLine(UP * 2.4 + RIGHT * mur_x, DOWN * 2.4 + RIGHT * mur_x,
                         color=ROUGE, stroke_width=5, dash_length=0.16)
        etiq_mur = phrase("le budget : « arrête-toi ici »", 19, ROUGE)
        etiq_mur.next_to(mur, UP, buff=0.15)

        lignes = VGroup()
        for i in range(6):
            y = (i - 2.5) * 0.72
            l = Line(LEFT * 5.4 + UP * y, LEFT * 5.4 + UP * y,
                     stroke_width=6, color=FROID)
            lignes.add(l)
        self.play(FadeIn(lignes))

        lg = legende("chaque trace pousse, à sa vitesse", 21, FROID)
        self.play(FadeIn(lg))

        # ⚠⚠ Elles poussent a des vitesses DIFFERENTES -- c est le fait que le mur cache.
        cibles = [mur_x] * 6
        self.play(*[l.animate.put_start_and_end_on(l.get_start(),
                                                   np.array([c, l.get_start()[1], 0]))
                    for l, c in zip(lignes, cibles)],
                  run_time=3, rate_func=rate_functions.ease_out_cubic)
        self.play(Create(mur), FadeIn(etiq_mur))
        self.wait(2)

        # ⭐ Le point : elles s arretent toutes la, donc elles ont toutes la meme longueur.
        lg2 = legende("elles s'arrêtent TOUTES là — donc elles ont toutes la même taille",
                      21, ROUGE)
        self.play(ReplacementTransform(lg, lg2))
        self.wait(3)

        cle = phrase("Ce n'était pas de la reproductibilité.\nC'était le mur.", 27, ROUGE)
        cle.to_edge(DOWN, buff=1.4)
        self.play(FadeOut(lg2), FadeIn(cle))
        self.wait(3)

        # ── On enlève le mur ──────────────────────────────────────────────────────
        self.play(FadeOut(cle))
        lg3 = legende("on recule le mur, on ne change rien d'autre", 21)
        self.play(FadeIn(lg3), FadeOut(mur), FadeOut(etiq_mur))

        # ⚠⚠ Les longueurs libres doivent TOUTES depasser celle du mur. Ma premiere
        # version en avait de plus courtes -- donc a l ecran, retirer le plafond faisait
        # RETRECIR des traces, ce qui est impossible et se lit comme une erreur de fond.
        # Invisible a la relecture du code, evident sur une vignette.
        DEPART = -5.4
        longueur_au_mur = mur_x - DEPART
        libres = [7.6, 10.9, 8.4, 12.1, 9.2, 11.3]
        assert all(v > longueur_au_mur for v in libres), (
            "retirer un plafond ne peut pas raccourcir une trace")
        # ⚠ Et l ecart doit etre GRAND : c est la revendication de la scene. Une dispersion
        # de quelques pour cent ne montrerait rien.
        assert (max(libres) - min(libres)) / max(libres) > 0.3, (
            "la dispersion doit sauter aux yeux, sinon la scene ne prouve rien")
        self.play(*[l.animate.put_start_and_end_on(
                        l.get_start(), np.array([DEPART + c, l.get_start()[1], 0]))
                    for l, c in zip(lignes, libres)],
                  run_time=3.5, rate_func=rate_functions.ease_out_cubic)
        self.wait(2)

        chiffre = phrase("dispersion : 0,3 %   →   115 %", 28, ROUGE)
        chiffre.to_edge(DOWN, buff=1.4)
        self.play(FadeOut(lg3), FadeIn(chiffre))
        self.wait(4)
        self.play(*[FadeOut(m) for m in (t, lignes, chiffre)])


class EllesEtaientPropresParcequellesEtaientCourtes(Scene):
    """Le second effet, que l'expérience n'avait pas prévu."""

    def construct(self):
        t = titre("Et un second effet, non prévu").scale(0.78).to_edge(UP)
        self.play(Write(t))

        intro = phrase("On mesure aussi si une surface se replie sur elle-même —\n"
                       "un défaut clair, qui rend la trace inutilisable.", 23)
        self.play(FadeIn(intro))
        self.wait(3)
        self.play(intro.animate.scale(0.8).to_edge(UP, buff=1.3))

        # ── Une surface courte : lisse. Une longue : elle se replie ───────────────
        def ruban(centre, replie):
            pts = []
            for u in np.linspace(0, 1, 120):
                x = -2.0 + 4.0 * u
                if replie and u > 0.55:
                    y = 0.55 * np.sin((u - 0.55) * 26) * (u - 0.55) * 5
                else:
                    y = 0.16 * np.sin(u * 5)
                pts.append(np.array([x, y, 0.0]))
            m = VMobject(stroke_width=6,
                         stroke_color=ROUGE if replie else VERT)
            m.set_points_smoothly(pts)
            m.move_to(centre)
            return m

        court = ruban(LEFT * 3.2 + DOWN * 0.3, False)
        long_ = ruban(RIGHT * 3.2 + DOWN * 0.3, True)
        eg = phrase("trace courte", 21, VERT).next_to(court, UP, buff=0.5)
        ed = phrase("la même, laissée pousser", 21, ROUGE).next_to(long_, UP, buff=0.5)

        self.play(Create(court), FadeIn(eg), run_time=1.6)
        self.wait(1)
        self.play(Create(long_), FadeIn(ed), run_time=2.2)
        self.wait(2)

        chiffres = VGroup(
            phrase("traces qui se replient :", 22),
            phrase("1 sur 12      →      9 sur 12", 26, ROUGE),
        ).arrange(DOWN, buff=0.3).to_edge(DOWN, buff=0.9)
        self.play(FadeIn(chiffres))
        self.wait(3)

        cle = phrase("Elles étaient propres parce qu'elles étaient courtes.", 26, ROUGE)
        cle.to_edge(DOWN, buff=1.0)
        self.play(FadeOut(chiffres), FadeIn(cle))
        self.wait(4)
        self.play(*[FadeOut(m) for m in (t, intro, court, long_, eg, ed, cle)])


class LaLeconGenerale(Scene):
    """Ce que ce piège apprend, au-delà de ce projet."""

    def construct(self):
        t = titre("Ce que ce piège apprend").scale(0.8)
        self.play(Write(t))
        self.wait(1)
        self.play(t.animate.scale(0.72).to_edge(UP))

        # ⭐ La formulation generale, celle qui sert ailleurs.
        regle = phrase("Quand des mesures indépendantes s'accordent\n"
                       "AU-DELÀ de ce que leur bruit permet,", 26, CRAIE)
        suite = phrase("ce n'est pas une bonne nouvelle.", 28, ROUGE)
        g = VGroup(regle, suite).arrange(DOWN, buff=0.45)
        self.play(FadeIn(regle))
        self.wait(2)
        self.play(FadeIn(suite))
        self.wait(3)

        self.play(FadeOut(g))
        pourquoi = VGroup(
            phrase("C'est un réglage partagé qui parle à leur place.", 25, AMBRE),
            phrase("Et sa cohérence est exactement ce qui le rend invisible :", 22),
            phrase("six résultats d'accord à la décimale", 22, "#9A928A"),
            phrase("ressemblent à une mesure solide.", 22, "#9A928A"),
        ).arrange(DOWN, buff=0.38)
        self.play(FadeIn(pourquoi))
        self.wait(5)

        # ⚠⚠ Et l aveu : ce depot s est refait prendre par le MEME piege, plus tard.
        self.play(FadeOut(pourquoi))
        aveu = VGroup(
            phrase("Post-scriptum, et il n'est pas flatteur :", 23),
            phrase("ce piège a été publié dans l'article…", 24, CRAIE),
            phrase("puis repayé quatre mois plus tard, sur un autre rouleau.", 24, ROUGE),
            phrase("Huit traces, aires d'accord à 0,06 %, toutes au même budget.",
                   21, "#9A928A"),
        ).arrange(DOWN, buff=0.36)
        self.play(FadeIn(aveu))
        self.wait(5)

        self.play(FadeOut(aveu), FadeOut(t))
        fin = phrase("Connaître un piège ne suffit pas à l'éviter.\n"
                     "Il faut un instrument qui le cherche.", 26, AMBRE)
        self.play(FadeIn(fin))
        self.wait(4)
