"""Vidéo 8 — Un nombre appartient à la fenêtre qui l'a mesuré.

⚠⚠ **Le piège le plus cher de tout le dépôt, payé CINQ fois en une nuit.** À chaque fois, un
nombre parfaitement juste a été déplacé hors de la géométrie qui l'avait produit, et à chaque
fois il est devenu faux sans cesser d'avoir l'air sensé. Aucune des cinq n'a été trouvée en
relisant du code : les cinq par une mesure qui ne collait pas.

⭐ Le fil : on construit la grandeur (le relief), on montre qu'elle dépend de la fenêtre où
on la lit, et on en tire la seule règle qui tienne — comparer un candidat à un corpus lu
DANS LA MÊME fenêtre. La vidéo se termine sur le résultat que cette règle a débloqué.
"""
from manim import *
import numpy as np

FOND, CRAIE, AMBRE = "#12100E", "#EDE8E0", "#D89A3E"
PAPYRUS, FROID, ROUGE, VERT, SOURD = "#C9B896", "#5A82A8", "#C4483C", "#5E9C6A", "#4E4640"
config.background_color = FOND

rng = np.random.default_rng(20260824)


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


class UneColonneDeProfondeur(Scene):
    """Ce qu'on regarde : une pile d'images, et une colonne qui la traverse."""

    def construct(self):
        t = titre("On regarde une colonne, pas une image").scale(0.8).to_edge(UP)
        self.play(Write(t))

        # ── la pile d images, vue de trois quarts ────────────────────────────────
        pile = VGroup()
        for i in range(9):
            r = Rectangle(width=3.4, height=2.1, stroke_color=SOURD, stroke_width=1.6,
                          fill_color=FOND, fill_opacity=0.92)
            r.shift(RIGHT * i * 0.12 + UP * i * 0.16)
            pile.add(r)
        pile.move_to(LEFT * 3.1 + UP * 0.4)
        self.play(LaggedStart(*[FadeIn(r) for r in pile], lag_ratio=0.09), run_time=1.8)
        lg = legende("le rendu d'une surface : une pile d'images, une par couche")
        self.play(FadeIn(lg))
        self.wait(2)

        # ⚠ La colonne traverse la pile : c est UN pixel (en vrai un petit carre) suivi
        # d une couche a l autre. C est l unite que tout le reste mesure.
        pts = [pile[i].get_center() + LEFT * 0.5 + DOWN * 0.2 for i in range(9)]
        col = VGroup(*[Dot(p, radius=0.062, color=AMBRE) for p in pts])
        trait = DashedLine(pts[0], pts[-1], color=AMBRE, stroke_width=2.4)
        self.play(Create(trait), LaggedStart(*[GrowFromCenter(d) for d in col],
                                             lag_ratio=0.08), run_time=1.6)
        lg2 = legende("une COLONNE : le même endroit, suivi d'une couche à l'autre", 21, AMBRE)
        self.play(ReplacementTransform(lg, lg2))
        self.wait(2)

        # ── la meme colonne, depliee en profil ───────────────────────────────────
        axes = Axes(x_range=[0, 8, 2], y_range=[0, 1.15, 1], x_length=4.6, y_length=2.5,
                    axis_config={"stroke_color": SOURD, "include_ticks": False})
        axes.move_to(RIGHT * 3.0 + UP * 0.3)
        val = np.array([0.18, 0.2, 0.24, 0.42, 0.95, 0.44, 0.23, 0.19, 0.18])
        pf = axes.plot_line_graph(list(range(9)), list(val), line_color=PAPYRUS,
                                  add_vertex_dots=False, stroke_width=4)
        self.play(Create(axes), run_time=1.0)
        self.play(*[Transform(col[i].copy(),
                              Dot(axes.c2p(i, val[i]), radius=0.05, color=PAPYRUS))
                    for i in range(9)], run_time=1.4)
        self.play(Create(pf), run_time=1.2)
        lg3 = legende("dépliée, elle donne un PROFIL — et là, il y a une bosse")
        self.play(ReplacementTransform(lg2, lg3))
        self.wait(3)


class LeReliefEnTroisMorceaux(Scene):
    """La formule, décortiquée : (max − min) / moyenne."""

    def construct(self):
        t = titre("Mettre un nombre sur « il y a une bosse »").scale(0.78).to_edge(UP)
        self.play(Write(t))

        axes = Axes(x_range=[0, 8, 2], y_range=[0, 1.15, 1], x_length=6.4, y_length=3.0,
                    axis_config={"stroke_color": SOURD, "include_ticks": False})
        axes.shift(UP * 0.5)
        val = np.array([0.18, 0.2, 0.24, 0.42, 0.95, 0.44, 0.23, 0.19, 0.18])
        pf = axes.plot_line_graph(list(range(9)), list(val), line_color=PAPYRUS,
                                  add_vertex_dots=False, stroke_width=4)
        self.play(Create(axes), Create(pf), run_time=1.4)

        # ── le max ──────────────────────────────────────────────────────────────
        hmax = DashedLine(axes.c2p(0, val.max()), axes.c2p(8, val.max()),
                          color=VERT, stroke_width=2.4)
        emax = phrase("le plus haut", 19, VERT).next_to(hmax, RIGHT, buff=0.14)
        self.play(Create(hmax), FadeIn(emax))
        lg = legende("on prend le point le plus HAUT du profil", 21, VERT)
        self.play(FadeIn(lg))
        self.wait(2)

        # ── le min ──────────────────────────────────────────────────────────────
        hmin = DashedLine(axes.c2p(0, val.min()), axes.c2p(8, val.min()),
                          color=FROID, stroke_width=2.4)
        emin = phrase("le plus bas", 19, FROID).next_to(hmin, RIGHT, buff=0.14)
        self.play(Create(hmin), FadeIn(emin))
        lg2 = legende("…et le plus BAS. Leur écart, c'est la hauteur de la bosse", 21, FROID)
        self.play(ReplacementTransform(lg, lg2))
        self.wait(2)

        fleche = DoubleArrow(axes.c2p(3.0, val.min()), axes.c2p(3.0, val.max()),
                             color=CRAIE, stroke_width=3, buff=0, tip_length=0.16)
        self.play(GrowFromCenter(fleche))
        self.wait(1.5)

        # ⚠⚠ LA DIVISION PAR LA MOYENNE : sans elle on mesure la LAMPE, pas le papyrus.
        hmoy = DashedLine(axes.c2p(0, val.mean()), axes.c2p(8, val.mean()),
                          color=AMBRE, stroke_width=2.4)
        emoy = phrase("la moyenne", 19, AMBRE).next_to(hmoy, RIGHT, buff=0.14)
        self.play(Create(hmoy), FadeIn(emoy))
        lg3 = legende("on divise par la MOYENNE — sinon on mesure la lampe, pas le papyrus",
                      21, AMBRE)
        self.play(ReplacementTransform(lg2, lg3))
        self.wait(3)

        self.play(FadeOut(VGroup(axes, pf, hmax, hmin, hmoy, emax, emin, emoy, fleche)))

        # ⚠ La fraction est bâtie en Text + Line, comme la vidéo 2 : cet environnement n'a
        # pas de LaTeX, et `MathTex` y meurt sur un `FileNotFoundError: latex`. Une formule
        # dessinée à la main se lit exactement pareil et se rend partout.
        f_haut = VGroup(phrase("le plus haut", 26, VERT), phrase("−", 26, CRAIE),
                        phrase("le plus bas", 26, FROID)).arrange(RIGHT, buff=0.22)
        barre = Line(LEFT * 2.1, RIGHT * 2.1, stroke_width=3, color=CRAIE)
        f_bas = phrase("la moyenne", 26, AMBRE)
        gauche = phrase("relief  =", 30, CRAIE)
        frac = VGroup(f_haut, barre, f_bas).arrange(DOWN, buff=0.26)
        f = VGroup(gauche, frac).arrange(RIGHT, buff=0.42).shift(UP * 0.3)
        self.play(FadeIn(gauche))
        self.play(FadeIn(f_haut, shift=DOWN * 0.2))
        self.play(Create(barre))
        self.play(FadeIn(f_bas, shift=UP * 0.2), run_time=0.9)
        lg4 = legende("un profil plat donne zéro ; une bosse franche donne beaucoup")
        self.play(ReplacementTransform(lg3, lg4))
        self.wait(3.5)


class LaMemeSurfaceDeuxFenetres(Scene):
    """Le piège : la fenêtre de lecture change le nombre."""

    def construct(self):
        t = titre("La même surface, lue deux fois").scale(0.8).to_edge(UP)
        self.play(Write(t))

        # ── un champ de papyrus, avec du grain ──────────────────────────────────
        champ = VGroup()
        for i in range(16):
            for j in range(16):
                v = 0.30 + 0.45 * abs(np.sin(i * 0.9) * np.cos(j * 0.7)) \
                    + 0.14 * rng.random()
                champ.add(Square(side_length=0.26, stroke_width=0,
                                 fill_color=PAPYRUS, fill_opacity=min(v, 1.0)))
        champ.arrange_in_grid(rows=16, buff=0).scale(1.02).shift(LEFT * 3.1 + UP * 0.35)
        self.play(FadeIn(champ), run_time=1.2)
        lg = legende("on ne lit jamais un pixel seul : on MOYENNE un carré de pixels")
        self.play(FadeIn(lg))
        self.wait(2.5)

        # ── grande fenetre ──────────────────────────────────────────────────────
        # ⚠ La grande fenêtre doit rester VISIBLEMENT à l'intérieur du champ : posée sur son
        # bord, elle se confond avec le cadre de l'image et on ne voit plus la comparaison
        # qui est tout le sujet. C'est la vignette du premier rendu qui l'a dit.
        grande = Square(side_length=2.9, stroke_color=FROID, stroke_width=5)
        grande.move_to(champ.get_center() + LEFT * 0.25 + UP * 0.2)
        self.play(Create(grande))
        b1 = VGroup(phrase("grande fenêtre", 22, FROID),
                    phrase("relief 0,046", 30, FROID)).arrange(DOWN, buff=0.2)
        b1.shift(RIGHT * 3.2 + UP * 1.1)
        self.play(FadeIn(b1))
        lg2 = legende("une GRANDE fenêtre moyenne beaucoup — elle écrase les extrêmes",
                      21, FROID)
        self.play(ReplacementTransform(lg, lg2))
        self.wait(3)

        # ── petite fenetre ──────────────────────────────────────────────────────
        # ⚠⚠ La légende CHANGE en même temps que la petite fenêtre apparaît. Au premier
        # rendu elle changeait après, donc une vignette montrait la petite fenêtre sous la
        # légende de la grande — un lecteur qui met pause pile là lit l'inverse du propos.
        petite = Square(side_length=0.78, stroke_color=ROUGE, stroke_width=5)
        petite.move_to(grande.get_center() + LEFT * 0.55 + UP * 0.45)
        lg3 = legende("une PETITE fenêtre garde les extrêmes — le nombre TRIPLE", 21, ROUGE)
        self.play(ReplacementTransform(grande.copy(), petite),
                  ReplacementTransform(lg2, lg3), run_time=1.4)
        b2 = VGroup(phrase("petite fenêtre", 22, ROUGE),
                    phrase("relief 0,146", 30, ROUGE)).arrange(DOWN, buff=0.2)
        b2.shift(RIGHT * 3.2 + DOWN * 0.9)
        self.play(FadeIn(b2))
        self.wait(3)

        # ⚠⚠ Le point qui doit rester : la surface n a pas bouge d un pixel.
        cadre = SurroundingRectangle(champ, color=AMBRE, stroke_width=3, buff=0.08)
        self.play(Create(cadre))
        lg4 = legende("et la surface n'a pas bougé d'un seul pixel", 23, AMBRE)
        self.play(ReplacementTransform(lg3, lg4))
        self.wait(3.5)


class UnSeuilNeVoyagePas(Scene):
    """La conséquence : un repère déplacé devient faux sans cesser d'avoir l'air juste."""

    def construct(self):
        t = titre("Un seuil ne voyage pas").scale(0.82).to_edge(UP)
        self.play(Write(t))

        # ── l axe, en echelle log ───────────────────────────────────────────────
        axe = NumberLine(x_range=[-2, 0.2, 1], length=9.2, color=SOURD,
                         include_numbers=False)
        axe.shift(UP * 0.6)
        self.play(Create(axe))

        def x(v):
            return axe.n2p(np.log10(v))

        plancher = Line(x(0.02) + DOWN * 0.42, x(0.02) + UP * 0.42,
                        color=ROUGE, stroke_width=4)
        lp = phrase("plancher : en dessous, c'est du bruit", 19, ROUGE)
        lp.next_to(plancher, UP, buff=0.2)
        self.play(Create(plancher), FadeIn(lp))
        self.wait(2)

        # ── le repere pris dans une grande fenetre ──────────────────────────────
        rep = Triangle(color=AMBRE, fill_color=AMBRE, fill_opacity=1).scale(0.16)
        rep.rotate(PI).next_to(x(0.045), DOWN, buff=0.12)
        lr = phrase("un repère mesuré ICI", 19, AMBRE).next_to(rep, DOWN, buff=0.16)
        self.play(FadeIn(rep), FadeIn(lr))
        lg = legende("« en dessous de ce repère, la surface ne vaut rien » — mesuré à 1024 px",
                     20, AMBRE)
        self.play(FadeIn(lg))
        self.wait(3)

        # ── on change d instrument : tout le monde se decale, sauf le repere ────
        # ⚠ Les points sont EMPILÉS : en échelle log, un corpus serré à droite se superpose
        # et huit segments se lisent comme une tache. C'est la vignette du premier rendu qui
        # l'a montré — dans le code, huit `Dot` distincts avaient l'air de suffire.
        corpus = VGroup()
        occupe = {}
        for v in (0.52, 0.62, 0.68, 0.74, 0.79, 0.83, 0.88, 0.93):
            colonne = int(x(v)[0] * 7)
            r = occupe.get(colonne, 0)
            occupe[colonne] = r + 1
            corpus.add(Dot(x(v) + UP * (0.16 + 0.19 * r), radius=0.075, color=VERT))
        self.play(LaggedStart(*[GrowFromCenter(d) for d in corpus], lag_ratio=0.07),
                  run_time=1.6)
        lg2 = legende("mais on lit AILLEURS, à 128 px — et tout le monde se décale", 21, VERT)
        self.play(ReplacementTransform(lg, lg2))
        self.wait(3)

        # ⚠⚠ Le repere reste ou il est, donc il ne separe plus rien.
        self.play(Indicate(rep, color=ROUGE, scale_factor=1.5), run_time=1.2)
        lg3 = legende("le repère, lui, n'a pas bougé : il ne sépare plus rien", 22, ROUGE)
        self.play(ReplacementTransform(lg2, lg3))
        self.wait(3)

        barre = Cross(scale_factor=0.34, stroke_color=ROUGE, stroke_width=6)
        barre.move_to(rep.get_center() + DOWN * 0.02)
        self.play(Create(barre))
        lg4 = legende("on l'a retiré. La règle : calibrer là où on lit", 23, CRAIE)
        self.play(ReplacementTransform(lg3, lg4))
        self.wait(3.5)


class SituerDansSonPropreCorpus(Scene):
    """Le remède, et ce qu'il a montré."""

    def construct(self):
        t = titre("Se comparer à son propre rouleau").scale(0.82).to_edge(UP)
        self.play(Write(t))

        axe = NumberLine(x_range=[-2, 0.2, 1], length=9.2, color=SOURD,
                         include_numbers=False)
        axe.shift(UP * 0.9)
        self.play(Create(axe))

        def x(v):
            return axe.n2p(np.log10(max(v, 0.011)))

        plancher = Line(x(0.02) + DOWN * 0.36, x(0.02) + UP * 0.36,
                        color=ROUGE, stroke_width=4)
        self.play(Create(plancher))

        # ── les 80 segments publies du meme rouleau ─────────────────────────────
        vals = list(np.clip(rng.normal(0.74, 0.12, 79), 0.30, 0.98)) + [0.040]
        nuage = VGroup()
        occupe = {}
        for v in sorted(vals):
            c = int(x(v)[0] * 12)
            r = occupe.get(c, 0)
            occupe[c] = r + 1
            nuage.add(Dot(x(v) + UP * (0.14 + 0.13 * r), radius=0.055, color=VERT))
        self.play(LaggedStart(*[GrowFromCenter(d) for d in nuage], lag_ratio=0.012),
                  run_time=2.4)
        lg = legende("les 80 surfaces PUBLIÉES du même rouleau, lues dans la même fenêtre",
                     21, VERT)
        self.play(FadeIn(lg))
        self.wait(3)

        # ── nos traces ──────────────────────────────────────────────────────────
        nous = VGroup(*[Dot(x(v) + DOWN * 0.34, radius=0.075, color=AMBRE)
                        for v in (0.1635, 0.1686, 0.1978)])
        self.play(LaggedStart(*[GrowFromCenter(d) for d in nous], lag_ratio=0.15),
                  run_time=1.2)
        l1 = phrase("nos 3 meilleures traces", 20, AMBRE)
        l1.next_to(nous, DOWN, buff=0.22)
        self.play(FadeIn(l1))
        lg2 = legende("elles lisent bien quelque chose — dix fois le plancher", 21, AMBRE)
        self.play(ReplacementTransform(lg, lg2))
        self.wait(2.5)

        lg3 = legende("mais elles sont dernières de leur propre rouleau", 22, AMBRE)
        self.play(ReplacementTransform(lg2, lg3))
        self.wait(2.5)

        # ── et les cinq autres, a zero ──────────────────────────────────────────
        zero = VGroup(*[Dot(axe.get_left() + DOWN * 0.34 + RIGHT * 0.1 * i, radius=0.075,
                            color=ROUGE) for i in range(5)])
        self.play(LaggedStart(*[GrowFromCenter(d) for d in zero], lag_ratio=0.12),
                  run_time=1.0)
        l2 = phrase("nos 5 autres : zéro", 20, ROUGE).next_to(zero, DOWN, buff=0.22)
        self.play(FadeIn(l2))
        lg4 = legende("zéro à TOUTES les fenêtres essayées — celles-là sont vraiment vides",
                      21, ROUGE)
        self.play(ReplacementTransform(lg3, lg4))
        self.wait(3.5)

        self.play(FadeOut(VGroup(axe, plancher, nuage, nous, zero, l1, l2, lg4, t)))
        fin = VGroup(
            phrase("Un nombre appartient à la fenêtre qui l'a mesuré.", 27, CRAIE),
            phrase("Le déplacer ne le rend pas faux : ça le rend", 22, "#9A928A"),
            phrase("faux ET crédible.", 26, ROUGE),
        ).arrange(DOWN, buff=0.4)
        self.play(Write(fin[0]), run_time=1.6)
        self.wait(1.2)
        self.play(FadeIn(fin[1]), FadeIn(fin[2]))
        self.wait(4)
