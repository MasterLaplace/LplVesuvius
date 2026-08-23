"""Vidéo 6 — α ≈ 1 a deux causes, et ne les distingue pas.

⚠⚠ **Une mesure doit savoir quand elle ne mesure pas.** α vaut 1 quand la surface traverse
l'empilement — c'est ce que la vidéo 2 a montré. Mais il vaut *aussi* 1 quand il n'y a
aucun pic du tout, et pour une raison purement arithmétique qui n'a rien à voir avec le
volume. Les deux condamnent la trace, donc le verdict tient — mais « en travers » et
« impossible à mesurer » ne sont pas la même phrase.
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


def legende(txt, taille=21, couleur=CRAIE):
    return phrase(txt, taille, couleur).to_edge(DOWN, buff=0.6)


def profil(centre, plat, hauteur=2.2, largeur=2.4, couleur=AMBRE):
    """Un profil de profondeur : un pic net, ou un plateau sans relief."""
    pts = []
    for y in np.linspace(-hauteur / 2, hauteur / 2, 90):
        if plat:
            x = 0.55 * largeur * (1.0 + 0.03 * float(np.sin(y * 5)))
        else:
            x = largeur * float(np.exp(-(y / (hauteur * 0.13)) ** 2)) + 0.12
        pts.append(centre + np.array([x, y, 0.0]))
    m = VMobject(stroke_width=5, stroke_color=couleur)
    m.set_points_smoothly(pts)
    return m


class LaPremiereCause(Scene):
    """Rappel : un pic qui s'éloigne quand la fenêtre grandit."""

    def construct(self):
        t = titre("Première cause : le pic recule").scale(0.78).to_edge(UP)
        self.play(Write(t))

        for i, (h, etq) in enumerate(((1.6, "petite fenêtre"), (3.2, "grande fenêtre"))):
            c = LEFT * 3.2 + RIGHT * 6.4 * i
            axe = Line(c + DOWN * h / 2, c + UP * h / 2, stroke_width=2, color=SOURD)
            cadre = Rectangle(width=3.4, height=h, stroke_color=FROID, stroke_width=2)
            cadre.move_to(c + RIGHT * 1.2)
            # ⭐ Le pic est AU BORD de la fenetre, et il y reste : il « recule » avec elle.
            pic = Dot(c + RIGHT * 2.4 + UP * (h / 2 - 0.18), radius=0.09, color=ROUGE)
            lab = phrase(f"écart : {45 if i == 0 else 158}", 19, ROUGE)
            lab.next_to(pic, RIGHT, buff=0.15)
            e = phrase(etq, 19, FROID).next_to(cadre, DOWN, buff=0.3)
            self.play(Create(axe), Create(cadre), FadeIn(e), run_time=0.9)
            self.play(GrowFromCenter(pic), FadeIn(lab), run_time=0.7)
            self.wait(1)

        lg = legende("le pic est là, mais toujours plus loin quand on regarde plus loin",
                     21, ROUGE)
        self.play(FadeIn(lg))
        self.wait(2)
        cle = phrase("α = 1, et ça veut dire quelque chose :\n"
                     "aucune feuille n'est à portée.", 24, ROUGE)
        cle.to_edge(DOWN, buff=1.4)
        self.play(FadeOut(lg), FadeIn(cle))
        self.wait(3)
        self.clear()


class LaSecondeCause(Scene):
    """Le profil plat : aucun pic, donc l'écart rapporté est le bord de la fenêtre."""

    def construct(self):
        t = titre("Seconde cause : il n'y a aucun pic").scale(0.78).to_edge(UP)
        self.play(Write(t))

        g = profil(LEFT * 4.2, plat=False)
        d = profil(RIGHT * 1.0, plat=True, couleur=ROUGE)
        eg = phrase("un vrai profil", 19, AMBRE).next_to(g, DOWN, buff=0.45)
        ed = phrase("un profil PLAT", 19, ROUGE).next_to(d, DOWN, buff=0.45)
        self.play(Create(g), FadeIn(eg))
        self.wait(1)
        self.play(Create(d), FadeIn(ed))
        self.wait(2)

        lg = legende("à droite, il n'y a rien à trouver : pas de pic, pas de feuille lue",
                     21, ROUGE)
        self.play(FadeIn(lg))
        self.wait(3)

        # ⚠⚠ Le mecanisme exact, et il est purement arithmetique.
        self.play(FadeOut(lg), FadeOut(g), FadeOut(eg), FadeOut(d), FadeOut(ed),
                  FadeOut(t))
        etapes = VGroup(
            phrase("Sans pic, le programme rapporte quoi ?", 24),
            phrase("le BORD de la fenêtre — il n'a rien d'autre.", 24, ROUGE),
        ).arrange(DOWN, buff=0.4)
        self.play(FadeIn(etapes[0]))
        self.wait(2)
        self.play(FadeIn(etapes[1]))
        self.wait(3)

        self.play(etapes.animate.scale(0.78).to_edge(UP, buff=1.1))
        calc = VGroup(
            phrase("petite fenêtre 40  →  écart rapporté  48", 23),
            phrase("grande fenêtre 160  →  écart rapporté  192", 23),
            phrase("192 ÷ 48 = 4        160 ÷ 40 = 4", 24, ROUGE),
            phrase("α = 1", 32, ROUGE),
        ).arrange(DOWN, buff=0.32)
        for x in calc:
            self.play(FadeIn(x), run_time=0.8)
            self.wait(1.2)
        self.wait(2)

        cle = phrase("α = 1 par pure arithmétique —\n"
                     "quoi qu'il y ait dans le volume.", 25, ROUGE)
        cle.to_edge(DOWN, buff=0.7)
        self.play(FadeIn(cle))
        self.wait(4)
        self.clear()


class CeQueCaCoute(Scene):
    """Combien de séries sont touchées, et pourquoi la conclusion tient quand même."""

    def construct(self):
        t = titre("Combien de mesures sont touchées ?").scale(0.75).to_edge(UP)
        self.play(Write(t))

        # ── 111 series, 24 indiscernables ─────────────────────────────────────────
        pts = VGroup()
        for i in range(111):
            c = ROUGE if i < 24 else FROID
            d = Dot(radius=0.07, color=c)
            pts.add(d)
        pts.arrange_in_grid(rows=8, buff=0.22)
        pts.shift(DOWN * 0.3)
        self.play(LaggedStart(*[FadeIn(p) for p in pts], lag_ratio=0.006), run_time=2.5)

        lg = phrase("24 séries sur 111 ne peuvent pas dire\n"
                    "laquelle des deux causes s'applique", 22, ROUGE)
        lg.to_edge(DOWN, buff=0.9)
        self.play(FadeIn(lg))
        self.wait(3)

        # ⭐ La moitie rassurante, et c est elle qui sauve la conclusion.
        self.play(FadeOut(lg))
        bonne = VGroup(
            phrase("Mais aucune des séries qui CONVERGENT n'est touchée.", 23, VERT),
            phrase("La plus petite α indiscernable : 0,87", 21, "#9A928A"),
            phrase("La plus grande α convergente : 0,42", 21, "#9A928A"),
            phrase("Les deux populations ne se recouvrent pas.", 22, VERT),
        ).arrange(DOWN, buff=0.28).to_edge(DOWN, buff=0.6)
        self.play(FadeIn(bonne))
        self.wait(5)

        self.play(FadeOut(bonne), FadeOut(pts), FadeOut(t))
        fin = VGroup(
            phrase("Une mesure doit savoir", 26, AMBRE),
            phrase("quand elle ne mesure pas.", 28, AMBRE),
            phrase("Le programme REFUSE désormais ces séries,", 21),
            phrase("au lieu de leur donner un α trompeur.", 21),
        ).arrange(DOWN, buff=0.32)
        self.play(FadeIn(fin))
        self.wait(5)
