"""Vidéo 1 — Un rouleau, c'est une feuille enroulée. Le problème, en images.

⚠⚠ **Public : quelqu'un qui n'a AUCUN prérequis.** Aucune formule, aucun symbole, aucun mot
technique introduit sans être montré d'abord. Chaque terme du projet — feuille, spire,
coupe, pile, segmenter, graine, trace — apparaît ici pour la première fois, attaché à une
image concrète, et sera réutilisé tel quel dans les vidéos suivantes.

⭐ La règle de rédaction : **on ne dit jamais « comme vous le savez »**, et on ne saute
jamais d'une image à la suivante sans avoir dit ce qui a changé.
"""
from manim import *
import numpy as np

# Palette du dépôt : fond sombre, texte cassé, ambre pour ce qui compte.
FOND = "#12100E"
CRAIE = "#EDE8E0"
AMBRE = "#D89A3E"
PAPYRUS = "#C9B896"
ENCRE = "#2A2622"
BRAISE = "#8C4A32"
FROID = "#5A82A8"

config.background_color = FOND


def titre(txt, taille=34):
    return Text(txt, font_size=taille, color=CRAIE, weight=BOLD)


def phrase(txt, taille=24, couleur=CRAIE):
    return Text(txt, font_size=taille, color=couleur)


def legende(txt, taille=22, couleur=CRAIE):
    """Une légende, TOUJOURS posée en bas du cadre.

    ⚠⚠ `ReplacementTransform` déplace l'ancien objet vers la position du NOUVEAU. Une
    légende de remplacement créée sans position naît donc au centre, et la phrase vient se
    poser par-dessus la figure — ce qui s'est produit une fois et ne se voit qu'en
    REGARDANT le rendu, jamais en relisant le code. Cette fonction rend la position
    impossible à oublier.
    """
    return phrase(txt, taille, couleur).to_edge(DOWN, buff=0.7)


class UnRouleauEstUneFeuilleEnroulee(Scene):
    """La feuille, l'enroulement, la carbonisation."""

    def construct(self):
        t = titre("Un rouleau, c'est une feuille enroulée")
        self.play(Write(t))
        self.wait(1)
        self.play(t.animate.scale(0.55).to_edge(UP))

        # ── 1. Une feuille plate, avec du texte dessus ────────────────────────────
        feuille = Rectangle(width=10, height=1.6, fill_color=PAPYRUS,
                            fill_opacity=1, stroke_width=0)
        lignes = VGroup(*[
            Line(feuille.get_left() + RIGHT * 0.4 + UP * y,
                 feuille.get_right() + LEFT * 0.4 + UP * y,
                 stroke_width=2, color=ENCRE)
            for y in (0.42, 0.14, -0.14, -0.42)
        ])
        # ⚠ Les lignes sont hachurées pour évoquer du texte SANS écrire de faux grec :
        # une écriture inventée dans une vidéo pédagogique se fait toujours prendre
        # pour de la donnée par quelqu'un.
        for l in lignes:
            l.set_stroke(opacity=0.55)
        rouleau_plat = VGroup(feuille, lignes)

        self.play(FadeIn(rouleau_plat, shift=UP * 0.3))
        lg = legende("une feuille de papyrus — deux mille ans, du texte dessus")
        self.play(FadeIn(lg))
        self.wait(2)

        # ── 2. On l'enroule ───────────────────────────────────────────────────────
        self.play(FadeOut(lg))
        lg2 = legende("on l'enroule")
        self.play(FadeIn(lg2))

        TOURS = 5.0

        def spirale(t):
            # t va de 0 (centre) à 1 (extérieur)
            r = 0.35 + 1.55 * t
            a = TOURS * TAU * t
            return np.array([r * np.cos(a), r * np.sin(a), 0.0])

        enroule = ParametricFunction(spirale, t_range=[0.0, 1.0, 0.004],
                                     stroke_width=7, color=PAPYRUS)
        enroule.move_to(ORIGIN)
        self.play(ReplacementTransform(rouleau_plat, enroule), run_time=2.5)
        self.wait(1)

        # ── 3. Le Vésuve ──────────────────────────────────────────────────────────
        self.play(FadeOut(lg2))
        lg3 = legende("puis le Vésuve : il ne brûle pas, il CARBONISE", 24, AMBRE)
        self.play(FadeIn(lg3))
        self.play(enroule.animate.set_color(BRAISE), run_time=1.5)
        self.play(enroule.animate.set_color("#3A3330"), run_time=1.5)
        self.wait(1)

        lg4 = legende("le texte est toujours là — mais le dérouler le briserait")
        self.play(ReplacementTransform(lg3, lg4))
        self.wait(2)
        self.play(FadeOut(lg4), FadeOut(t))
        self.spirale_finale = enroule


class OnLeScanne(Scene):
    """Le scanner produit une PILE d'images. Une spire, vue en coupe, est une ligne."""

    def construct(self):
        t = titre("On ne le déroule pas — on le scanne").scale(0.75).to_edge(UP)
        self.play(Write(t))

        TOURS = 5.0

        def spirale(s):
            r = 0.35 + 1.35 * s
            a = TOURS * TAU * s
            return np.array([r * np.cos(a), r * np.sin(a), 0.0])

        coupe = ParametricFunction(spirale, t_range=[0, 1, 0.004],
                                   stroke_width=5, color="#6E635C")
        coupe.move_to(LEFT * 3.4)
        cadre = Square(side_length=3.6, stroke_color="#4A423C",
                       stroke_width=2).move_to(coupe)
        self.play(Create(cadre), Create(coupe), run_time=2)

        lg = legende("UNE coupe : le scanner traverse le rouleau à une hauteur", 21)
        self.play(FadeIn(lg))
        self.wait(2)

        # ⭐ Le mot « spire » est introduit ICI, en montrant l'objet, jamais avant.
        fleche = Arrow(coupe.get_center() + UP * 2.6 + RIGHT * 1.4,
                       coupe.get_center() + UP * 0.95 + RIGHT * 0.15,
                       buff=0, color=AMBRE, stroke_width=4)
        mot = phrase("une SPIRE : un tour de la feuille", 20, AMBRE)
        mot.next_to(fleche.get_start(), UP, buff=0.15)
        self.play(GrowArrow(fleche), FadeIn(mot))
        self.wait(2)
        self.play(FadeOut(fleche), FadeOut(mot))

        # ── La pile ───────────────────────────────────────────────────────────────
        lg2 = legende("le scanner en fait des MILLIERS, empilées", 21)
        self.play(ReplacementTransform(lg, lg2))

        pile = VGroup()
        for i in range(9):
            c = Square(side_length=2.2, stroke_color="#4A423C", stroke_width=2,
                       fill_color=FOND, fill_opacity=0.92)
            c.move_to(RIGHT * 2.6 + RIGHT * 0.15 * i + UP * 0.20 * i)
            petit = ParametricFunction(spirale, t_range=[0, 1, 0.01],
                                       stroke_width=2.2, color="#6E635C")
            petit.scale(0.6).move_to(c)
            pile.add(VGroup(c, petit))
        self.play(LaggedStart(*[FadeIn(p, shift=DOWN * 0.3) for p in pile],
                              lag_ratio=0.14), run_time=3)
        self.wait(1)

        etiq = phrase("une PILE de coupes", 20, "#9A928A")
        etiq.move_to(RIGHT * 3.2 + DOWN * 2.2)
        self.play(FadeIn(etiq))
        self.wait(2)
        self.play(FadeOut(lg2), FadeOut(etiq), FadeOut(t), FadeOut(cadre),
                  FadeOut(coupe), FadeOut(pile))


class SegmenterCEstSuivreUneFeuille(Scene):
    """Segmenter : choisir UNE spire et la suivre à travers toute la pile."""

    def construct(self):
        t = titre("« Segmenter » : suivre UNE feuille").scale(0.75).to_edge(UP)
        self.play(Write(t))

        TOURS = 4.0

        def spirale(s):
            r = 0.4 + 1.5 * s
            a = TOURS * TAU * s
            return np.array([r * np.cos(a), r * np.sin(a), 0.0])

        fond = ParametricFunction(spirale, t_range=[0, 1, 0.004],
                                  stroke_width=5, color="#4E4640")
        fond.move_to(LEFT * 3.6 + DOWN * 0.3)
        self.play(Create(fond), run_time=1.5)

        # ⭐ Une seule spire, mise en avant : c'est CE qu'on cherche à suivre.
        cible = ParametricFunction(spirale, t_range=[0.52, 0.78, 0.002],
                                   stroke_width=7, color=AMBRE)
        cible.move_to(fond.get_center() + (fond.get_center() * 0))
        cible.shift(fond.get_center() - ORIGIN)
        self.play(Create(cible), run_time=1.5)
        lg = legende("on en choisit UNE", 22, AMBRE)
        self.play(FadeIn(lg))
        self.wait(2)

        # ── Elle se prolonge dans la pile : c'est une SURFACE ─────────────────────
        lg2 = legende("elle continue dans toutes les coupes du dessus et du dessous", 21)
        self.play(ReplacementTransform(lg, lg2))

        nappes = VGroup()
        for i in range(7):
            arc = ParametricFunction(spirale, t_range=[0.52, 0.78, 0.004],
                                     stroke_width=4, color=AMBRE)
            arc.scale(0.85).move_to(RIGHT * 2.9 + UP * (i - 3) * 0.42
                                    + RIGHT * (i - 3) * 0.12)
            arc.set_stroke(opacity=0.35 + 0.09 * i)
            nappes.add(arc)
        self.play(LaggedStart(*[FadeIn(n) for n in nappes], lag_ratio=0.15),
                  run_time=2.5)

        mot = phrase("empilées, elles forment une SURFACE", 21, AMBRE)
        mot.move_to(RIGHT * 2.9 + DOWN * 2.1)
        self.play(FadeIn(mot))
        self.wait(2)

        # ── Le vocabulaire du projet, posé une fois pour toutes ───────────────────
        self.play(FadeOut(lg2), FadeOut(mot), FadeOut(nappes),
                  FadeOut(fond), FadeOut(cible), FadeOut(t))

        # ⚠⚠ Chaque mot reçoit son IMAGE. Une définition écrite est une phrase de plus à
        # retenir ; une définition MONTRÉE est un souvenir. Les trois images réutilisent la
        # même spirale, donc le lecteur voit que les trois mots parlent du même objet à
        # trois moments — ce qu'une liste de trois lignes ne dit pas.
        def petite_spirale(centre, couleur="#4E4640", ep=3.5):
            f = ParametricFunction(spirale, t_range=[0, 1, 0.006],
                                   stroke_width=ep, color=couleur)
            f.scale(0.62).move_to(centre)
            return f

        POSTES = [LEFT * 4.3, ORIGIN, RIGHT * 4.3]

        # ── GRAINE : un point pose sur une spire ──────────────────────────────────
        sp1 = petite_spirale(POSTES[0])
        pt = Dot(radius=0.09, color=AMBRE)
        pt.move_to(sp1.point_from_proportion(0.62))
        n1 = phrase("GRAINE", 22, AMBRE)
        n1.next_to(sp1, UP, buff=0.3)
        d1 = phrase("un point de départ,\nque l'on donne au programme", 17)
        d1.next_to(sp1, DOWN, buff=0.35)

        self.play(Create(sp1), run_time=1.2)
        self.play(FadeIn(n1), GrowFromCenter(pt))
        self.play(FadeIn(d1))
        self.wait(2)

        # ── TRACE : la surface qui pousse a partir du point ───────────────────────
        sp2 = petite_spirale(POSTES[1])
        pousse = ParametricFunction(spirale, t_range=[0.62, 0.63, 0.002],
                                    stroke_width=7, color=AMBRE)
        pousse.scale(0.62).move_to(sp2.point_from_proportion(0.62))
        n2 = phrase("TRACE", 22, AMBRE)
        n2.next_to(sp2, UP, buff=0.3)
        d2 = phrase("la surface qu'il fait pousser\nà partir de là", 17)
        d2.next_to(sp2, DOWN, buff=0.35)

        self.play(Create(sp2), run_time=1.0)
        self.play(FadeIn(n2))
        grande = ParametricFunction(spirale, t_range=[0.42, 0.82, 0.003],
                                    stroke_width=7, color=AMBRE)
        grande.scale(0.62).move_to(sp2)
        # ⚠ La croissance est ANIMEE : « pousser » est un verbe, et le montrer comme un
        # objet deja fini perdrait justement ce que le mot veut dire.
        self.play(ReplacementTransform(pousse, grande), run_time=2.2)
        self.play(FadeIn(d2))
        self.wait(2)

        # ── RENDU : la surface depliee, a plat ────────────────────────────────────
        sp3 = petite_spirale(POSTES[2])
        arc = ParametricFunction(spirale, t_range=[0.42, 0.82, 0.003],
                                 stroke_width=7, color=AMBRE)
        arc.scale(0.62).move_to(sp3)
        n3 = phrase("RENDU", 22, AMBRE)
        n3.next_to(sp3, UP, buff=0.3)
        d3 = phrase("l'image obtenue\nen la dépliant à plat", 17)
        d3.next_to(sp3, DOWN, buff=0.35)

        self.play(Create(sp3), FadeIn(n3), run_time=1.0)
        self.play(Create(arc), run_time=0.8)
        plat = Rectangle(width=2.3, height=1.15, stroke_color=AMBRE, stroke_width=4,
                         fill_color=PAPYRUS, fill_opacity=0.18)
        plat.move_to(sp3)
        traits = VGroup(*[
            Line(plat.get_left() + RIGHT * 0.2 + UP * y,
                 plat.get_right() + LEFT * 0.2 + UP * y,
                 stroke_width=1.6, color=PAPYRUS).set_stroke(opacity=0.5)
            for y in (0.3, 0.1, -0.1, -0.3)
        ])
        self.play(ReplacementTransform(arc, plat), run_time=1.8)
        self.play(FadeIn(traits))
        self.play(FadeIn(d3))
        self.wait(3)

        tout = VGroup(sp1, pt, n1, d1, sp2, grande, n2, d2,
                      sp3, plat, traits, n3, d3)
        self.play(FadeOut(tout), run_time=1)

        fin = phrase("Tout le projet tient dans une question :", 24)
        q = titre("« a-t-on suivi une vraie feuille ? »", 30)
        q.set_color(AMBRE)
        grp = VGroup(fin, q).arrange(DOWN, buff=0.45)
        # ⚠ Le groupe des définitions a déjà été retiré juste au-dessus ; le refaire ici
        # lèverait une erreur de nom, ce qui est arrivé.
        self.wait(0.4)
        self.play(FadeIn(fin))
        self.play(Write(q))
        self.wait(3)
