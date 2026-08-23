"""Vidéo 7 — Ce que mesurer coûte, et pourquoi le coût était invisible.

⚠⚠ **Une ressource que personne ne mesure est une ressource qui décide à votre place.** Un
calcul tournait depuis deux heures, annonçait six heures de plus, et n'utilisait qu'un quart
d'un cœur sur vingt-deux. Il ne calculait pas : il attendait la mémoire. Et la cause n'était
pas dans le programme — elle était dans un réglage que personne n'avait jamais posé.

⭐ Le fil conducteur : à chaque étape, ce qui a tranché n'est pas une relecture du code mais
une MESURE — et deux relectures avaient déjà produit deux diagnostics faux.
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


class VingtDeuxCoeursQuiNeFontRien(Scene):
    """Le symptôme : beaucoup de threads, presque aucun calcul."""

    def construct(self):
        t = titre("Deux heures de calcul, et six annoncées").scale(0.78).to_edge(UP)
        self.play(Write(t))

        # ── 22 coeurs, un seul (a peine) occupe ──────────────────────────────────
        coeurs = VGroup()
        for i in range(22):
            r = Square(side_length=0.52, stroke_color=SOURD, stroke_width=2,
                       fill_color=FOND, fill_opacity=1)
            coeurs.add(r)
        coeurs.arrange_in_grid(rows=2, buff=0.16).shift(UP * 0.7)
        self.play(LaggedStart(*[FadeIn(c) for c in coeurs], lag_ratio=0.04), run_time=1.8)
        lg = legende("la machine a 22 cœurs")
        self.play(FadeIn(lg))
        self.wait(2)

        # ⚠⚠ 23,7 % d UN c ur : le premier remplit au quart, les 21 autres restent vides.
        self.play(coeurs[0].animate.set_fill(FROID, opacity=0.24), run_time=1.2)
        lg2 = legende("le programme en utilise 23,7 %… d'UN seul", 22, ROUGE)
        self.play(ReplacementTransform(lg, lg2))
        self.wait(2)

        th = phrase("et il avait 59 fils d'exécution lancés", 21, "#9A928A")
        th.to_edge(DOWN, buff=1.5)
        self.play(FadeIn(th))
        self.wait(3)

        cle = phrase("Un programme à 59 fils qui utilise un quart d'un cœur\n"
                     "ne calcule pas. Il attend.", 25, ROUGE)
        cle.to_edge(DOWN, buff=1.1)
        self.play(FadeOut(lg2), FadeOut(th), FadeIn(cle))
        self.wait(4)
        self.clear()


class IlAttendaitLaMemoire(Scene):
    """Ce qu'il attendait : de la mémoire, dont il n'y en avait plus."""

    def construct(self):
        t = titre("Il attendait la mémoire").scale(0.78).to_edge(UP)
        self.play(Write(t))

        # ── Une barre de RAM ──────────────────────────────────────────────────────
        LARG = 9.0
        cadre = Rectangle(width=LARG, height=1.1, stroke_color=CRAIE, stroke_width=3)
        cadre.shift(UP * 0.6)
        tot = phrase("32 Go de mémoire", 20, CRAIE).next_to(cadre, UP, buff=0.25)
        self.play(Create(cadre), FadeIn(tot))

        part = 28.2 / 32.0
        plein = Rectangle(width=LARG * part, height=1.1, fill_color=ROUGE,
                          fill_opacity=0.6, stroke_width=0)
        plein.align_to(cadre, LEFT).set_y(cadre.get_y())
        self.play(GrowFromEdge(plein, LEFT), run_time=2)
        e1 = phrase("28,2 Go pris par UN programme", 20, ROUGE).next_to(cadre, DOWN, buff=0.3)
        self.play(FadeIn(e1))
        self.wait(2)

        reste = phrase("il reste 274 Mo", 22, AMBRE)
        reste.next_to(cadre, DOWN, buff=1.0)
        self.play(FadeIn(reste))
        self.wait(2)

        # ⚠ Le swap : quand il n y a plus de place, le systeme ecrit sur le DISQUE, qui est
        # des milliers de fois plus lent. C est ca, « attendre la memoire ».
        sw = phrase("et 3,4 Go déplacés sur le DISQUE — des milliers de fois plus lent",
                    20, ROUGE)
        sw.to_edge(DOWN, buff=0.9)
        self.play(FadeIn(sw))
        self.wait(4)
        self.clear()


class LeReglageQuePersonneNAvaitPose(Scene):
    """La cause : un défaut de 16 Go, jamais réglé, sur 28 appels."""

    def construct(self):
        t = titre("La cause n'était pas dans le programme").scale(0.75).to_edge(UP)
        self.play(Write(t))

        ligne = phrase("--cache-gb   (défaut : 16)", 30, AMBRE)
        self.play(FadeIn(ligne))
        self.wait(2)
        self.play(ligne.animate.scale(0.8).to_edge(UP, buff=1.3))

        expl = VGroup(
            phrase("le programme réserve de la mémoire pour aller plus vite.", 22),
            phrase("Par défaut : la moitié de cette machine.", 22, ROUGE),
            phrase("Aucun des 28 endroits qui l'appellent ne réglait cette valeur.",
                   22, ROUGE),
        ).arrange(DOWN, buff=0.35)
        for x in expl:
            self.play(FadeIn(x), run_time=0.8)
            self.wait(1.6)
        self.wait(2)

        # ⭐ Pourquoi c est reste invisible : sur les petites surfaces, le cache ne se
        # remplit jamais jusqu au plafond. Le defaut n a rien coute pendant des mois.
        self.play(FadeOut(expl))
        invisible = VGroup(
            phrase("Pourquoi personne ne l'avait vu :", 23),
            phrase("sur une petite surface, cette réserve ne se remplit jamais.", 22),
            phrase("Le réglage ne coûtait rien —", 22, "#9A928A"),
            phrase("jusqu'à la première surface assez grande.", 22, AMBRE),
        ).arrange(DOWN, buff=0.32)
        self.play(FadeIn(invisible))
        self.wait(5)
        self.clear()


class LeMurQuAucunReglageNeDeplace(Scene):
    """Et derrière le réglage, un mur qui ne se règle pas : la taille du travail."""

    def construct(self):
        t = titre("Et derrière, un mur qui ne se règle pas").scale(0.75).to_edge(UP)
        self.play(Write(t))

        expl = phrase("Le programme doit garder en mémoire, en même temps,\n"
                      "toutes les images qu'il fabrique.", 23)
        self.play(FadeIn(expl))
        self.wait(3)
        self.play(expl.animate.scale(0.8).to_edge(UP, buff=1.25))

        # ── Trois barres, et la ligne de la RAM ───────────────────────────────────
        LARG = 8.4
        MAX = 42.0
        cas = [("41 images", 9.7, FROID), ("161 images", 38.2, ROUGE)]
        barres = VGroup()
        for i, (nom, go, c) in enumerate(cas):
            y = 0.4 - i * 1.3
            r = Rectangle(width=LARG * go / MAX, height=0.75, fill_color=c,
                          fill_opacity=0.6, stroke_width=0)
            r.move_to(LEFT * 4.6 + RIGHT * LARG * go / MAX / 2 + UP * y)
            n = phrase(nom, 19, CRAIE).next_to(r, LEFT, buff=0.25)
            v = phrase(f"{go} Go", 20, c).next_to(r, RIGHT, buff=0.2)
            barres.add(VGroup(r, n, v))
        for b in barres:
            self.play(GrowFromEdge(b[0], LEFT), FadeIn(b[1]), FadeIn(b[2]), run_time=1.4)
            self.wait(1)

        x_ram = LEFT * 4.6 + RIGHT * LARG * 32.0 / MAX
        mur = DashedLine(x_ram + UP * 1.3, x_ram + DOWN * 1.7, color=CRAIE,
                         stroke_width=4, dash_length=0.14)
        lab = phrase("la machine", 19, CRAIE).next_to(mur, UP, buff=0.15)
        self.play(Create(mur), FadeIn(lab))
        self.wait(3)

        cle = phrase("Ce n'était pas lent. C'était impossible.", 27, ROUGE)
        cle.to_edge(DOWN, buff=0.8)
        self.play(FadeIn(cle))
        self.wait(4)
        self.clear()


class LaPyramide(Scene):
    """La sortie : regarder moins fin, et vérifier que la réponse ne change pas."""

    def construct(self):
        t = titre("La sortie : regarder moins fin").scale(0.78).to_edge(UP)
        self.play(Write(t))

        expl = phrase("Le scan est publié à plusieurs finesses.\n"
                      "Deux fois moins fin, c'est quatre fois moins de pixels.", 23)
        self.play(FadeIn(expl))
        self.wait(3)
        self.play(expl.animate.scale(0.8).to_edge(UP, buff=1.25))

        # ── Deux grilles, fine et grossiere ───────────────────────────────────────
        def grille(centre, n, couleur):
            g = VGroup()
            pas = 2.4 / n
            for i in range(n):
                for j in range(n):
                    g.add(Square(side_length=pas * 0.86, stroke_width=1,
                                 stroke_color=couleur, fill_opacity=0)
                          .move_to(centre + np.array([(i - n / 2 + 0.5) * pas,
                                                      (j - n / 2 + 0.5) * pas, 0.0])))
            return g

        gf = grille(LEFT * 3.2 + DOWN * 0.5, 8, FROID)
        gg = grille(RIGHT * 3.2 + DOWN * 0.5, 4, AMBRE)
        ef = phrase("fin : 38,2 Go", 20, FROID).next_to(gf, DOWN, buff=0.4)
        eg = phrase("deux fois moins fin : 4,8 Go", 20, AMBRE).next_to(gg, DOWN, buff=0.4)
        self.play(FadeIn(gf), FadeIn(ef))
        self.wait(1)
        self.play(FadeIn(gg), FadeIn(eg))
        self.wait(2)

        # ⚠⚠ Et le controle, qui est la seule chose qui autorise a le faire.
        lg = legende("mais est-ce qu'on mesure encore la même chose ?", 23, CRAIE)
        self.play(FadeIn(lg))
        self.wait(3)

        self.play(FadeOut(gf), FadeOut(gg), FadeOut(ef), FadeOut(eg), FadeOut(lg),
                  FadeOut(expl))
        res = VGroup(
            phrase("On a mesuré la MÊME surface aux deux finesses :", 23),
            phrase("α = 0,91        α = 0,89", 30, AMBRE),
            phrase("écart : 0,02, pour une précision de 0,20", 22, VERT),
        ).arrange(DOWN, buff=0.4)
        self.play(FadeIn(res[0]))
        self.wait(1.5)
        self.play(FadeIn(res[1]))
        self.wait(2)
        self.play(FadeIn(res[2]))
        self.wait(3)

        self.play(FadeOut(res), FadeOut(t))
        fin = VGroup(
            phrase("Une ressource que personne ne mesure", 26, AMBRE),
            phrase("est une ressource qui décide à votre place.", 26, AMBRE),
            phrase("Ici : deux relectures du code ont donné deux diagnostics faux.", 21),
            phrase("C'est la mesure qui a tranché, à chaque fois.", 21, "#9A928A"),
        ).arrange(DOWN, buff=0.34)
        self.play(FadeIn(fin))
        self.wait(5)
