"""Vidéo 4 — Le traceur n'est pas une fonction.

⚠⚠ **Le fait le plus déstabilisant du projet, et le plus facile à oublier.** On appelle le
même programme, avec la même graine et les mêmes réglages, et il rend un résultat
*différent* à chaque fois. Tant qu'on ne l'a pas intégré, chaque mesure isolée qu'on lit est
un tirage qu'on prend pour une valeur.

⭐ La conséquence pratique tient en une phrase : **un écart plus petit que le bruit du
tireur ne veut rien dire**, quelle que soit la conviction avec laquelle on le lit.
"""
from manim import *
import numpy as np

FOND, CRAIE, AMBRE = "#12100E", "#EDE8E0", "#D89A3E"
PAPYRUS, FROID, ROUGE, VERT, SOURD = "#C9B896", "#5A82A8", "#C4483C", "#5E9C6A", "#4E4640"
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


class UneFonctionRendToujoursPareil(Scene):
    """D'abord ce qu'est une fonction — pour pouvoir dire que ce n'en est pas une."""

    def construct(self):
        t = titre("Une machine qui rend toujours pareil").scale(0.8)
        self.play(Write(t))
        self.wait(1)
        self.play(t.animate.scale(0.72).to_edge(UP))

        boite = Rectangle(width=2.6, height=1.8, stroke_color=FROID, stroke_width=4)
        nom = phrase("machine", 20, FROID).move_to(boite)
        self.play(Create(boite), FadeIn(nom))

        # ⚠ Trois passages identiques : c est la DEFINITION d une fonction, montree plutot
        # qu enoncee. « Meme entree, meme sortie » n a pas besoin d un mot savant.
        for i in range(3):
            e = phrase("3", 26, AMBRE).move_to(LEFT * 4.2 + DOWN * 0.1)
            s = phrase("9", 26, VERT).move_to(RIGHT * 4.2 + DOWN * 0.1)
            self.play(FadeIn(e), run_time=0.4)
            self.play(e.animate.move_to(boite.get_center()), run_time=0.7)
            self.play(FadeOut(e), FadeIn(s), run_time=0.5)
            if i < 2:
                self.play(FadeOut(s), run_time=0.3)
        self.wait(1)

        lg = legende("même entrée, même sortie — à chaque fois", 22, VERT)
        self.play(FadeIn(lg))
        self.wait(2)
        mot = phrase("c'est ce qu'on appelle une FONCTION", 22, VERT)
        mot.to_edge(DOWN, buff=1.5)
        self.play(FadeIn(mot))
        self.wait(3)
        self.play(*[FadeOut(m) for m in (t, boite, nom, s, lg, mot)])


class LeTraceurNonPlus(Scene):
    """Le traceur, lui, rend six résultats pour un seul appel répété six fois."""

    def construct(self):
        t = titre("Le traceur, lui, ne fait pas ça").scale(0.78).to_edge(UP)
        self.play(Write(t))

        boite = Rectangle(width=3.0, height=1.7, stroke_color=ROUGE, stroke_width=4)
        boite.move_to(LEFT * 3.6)
        nom = phrase("le traceur", 19, ROUGE).move_to(boite)
        graine = phrase("la MÊME graine", 19, AMBRE).next_to(boite, UP, buff=0.35)
        self.play(Create(boite), FadeIn(nom), FadeIn(graine))

        lg = legende("on l'appelle six fois, sans rien changer")
        self.play(FadeIn(lg))

        # ⚠⚠ Six sorties DIFFERENTES. Les valeurs sont celles d une vraie campagne : meme
        # graine, memes reglages, six executions.
        vals = [17.4, 19.8, 12.1, 21.6, 15.9, 19.8]
        sorties = VGroup()
        for i, v in enumerate(vals):
            y = (i - 2.5) * 0.72
            fl = Arrow(boite.get_right() + RIGHT * 0.1,
                       RIGHT * 1.4 + UP * y, buff=0.05, color=SOURD, stroke_width=2,
                       max_tip_length_to_length_ratio=0.08)
            e = phrase(f"{v} cm²", 20, ROUGE).next_to(fl, RIGHT, buff=0.2)
            sorties.add(VGroup(fl, e))
        self.play(LaggedStart(*[FadeIn(s) for s in sorties], lag_ratio=0.3), run_time=3.2)
        self.wait(2)

        lg2 = legende("six résultats différents — et c'est normal, pas un bug", 22, ROUGE)
        self.play(ReplacementTransform(lg, lg2))
        self.wait(3)

        # ⭐ Le chiffre de la campagne reelle.
        camp = phrase("mesuré sur 78 exécutions, 13 rouleaux", 20, "#9A928A")
        camp.to_edge(DOWN, buff=1.5)
        self.play(FadeIn(camp))
        self.wait(3)
        self.play(*[FadeOut(m) for m in (t, boite, nom, graine, sorties, lg2, camp)])


class CeQueCaChangePourAlpha(Scene):
    """Et sur α : la même graine rend cinq valeurs. Donc un écart doit les dépasser."""

    def construct(self):
        t = titre("Ce que ça change pour α").scale(0.78).to_edge(UP)
        self.play(Write(t))

        intro = phrase("La même graine, tracée cinq fois, mesurée cinq fois :", 24)
        self.play(FadeIn(intro))
        self.wait(2)
        self.play(intro.animate.scale(0.82).to_edge(UP, buff=1.25))

        # ── Un axe d'α, et cinq points ────────────────────────────────────────────
        A0, A1 = 0.6, 1.3
        axe = Line(LEFT * 5.2, RIGHT * 5.2, stroke_width=3, color=SOURD)
        axe.shift(DOWN * 0.2)

        def X(a):
            return LEFT * 5.2 + RIGHT * ((a - A0) / (A1 - A0)) * 10.4 + DOWN * 0.2

        self.play(Create(axe))
        for a in (0.7, 0.9, 1.1, 1.3):
            tick = Line(X(a) + UP * 0.12, X(a) + DOWN * 0.12, color=SOURD, stroke_width=2)
            lab = phrase(f"{a}", 17, SOURD).next_to(tick, DOWN, buff=0.14)
            self.play(Create(tick), FadeIn(lab), run_time=0.25)

        mesures = [0.89, 0.94, 1.01, 1.09, 1.12]
        pts = VGroup()
        for a in mesures:
            d = Dot(X(a) + UP * 0.42, radius=0.1, color=ROUGE)
            e = phrase(f"{a}", 17, ROUGE).next_to(d, UP, buff=0.12)
            pts.add(VGroup(d, e))
        self.play(LaggedStart(*[GrowFromCenter(p) for p in pts], lag_ratio=0.3),
                  run_time=2.6)
        self.wait(2)

        # ⭐ L etendue : c est ELLE le nombre a retenir.
        etendue = DoubleArrow(X(0.89) + UP * 1.15, X(1.12) + UP * 1.15,
                              buff=0, color=AMBRE, stroke_width=3,
                              max_tip_length_to_length_ratio=0.05)
        lab = phrase("0,23", 24, AMBRE).next_to(etendue, UP, buff=0.1)
        self.play(GrowFromCenter(etendue), FadeIn(lab))
        self.wait(2)

        regle = phrase("Tout écart plus petit que 0,23 peut n'être que du hasard.", 24,
                       AMBRE)
        regle.to_edge(DOWN, buff=1.2)
        self.play(FadeIn(regle))
        self.wait(4)

        self.play(FadeOut(regle))
        # ⚠⚠ Et le remede, qui est la raison d etre de la moitie des scripts du depot.
        remede = VGroup(
            phrase("D'où la règle appliquée partout dans ce dépôt :", 23),
            phrase("répéter chaque condition,", 25, CRAIE),
            phrase("et comparer l'écart ENTRE conditions", 23, CRAIE),
            phrase("à l'étendue DANS une seule.", 23, CRAIE),
        ).arrange(DOWN, buff=0.3).to_edge(DOWN, buff=0.6)
        self.play(FadeIn(remede))
        self.wait(5)
