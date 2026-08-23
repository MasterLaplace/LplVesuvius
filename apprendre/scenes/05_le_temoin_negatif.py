"""Vidéo 5 — Le témoin négatif : prouver qu'un détecteur ne prouve rien.

⚠⚠ **La question la plus difficile de tout le projet.** Un modèle regarde une surface et dit
où il voit de l'encre. Comment sait-on qu'il ne l'invente pas ? On ne peut pas le tester
contre la vérité — il n'y en a pas. Et on ne peut pas se contenter de trouver ses sorties
« plausibles » : une carte plausible est exactement ce qu'un modèle qui invente produirait.

⭐ La sortie de l'impasse est un renversement : au lieu de chercher une surface dont on sait
qu'elle est BONNE, on en fabrique une dont on sait qu'elle est FAUSSE — et α le prouve
géométriquement, sans rien supposer du modèle.
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


def carte(centre, graine, couleur=AMBRE, taille=2.2):
    """Une petite « carte d'encre » : des taches, déterministes pour une graine donnée."""
    g = np.random.default_rng(graine)
    cadre = Square(side_length=taille, stroke_color=SOURD, stroke_width=2)
    cadre.move_to(centre)
    taches = VGroup()
    for _ in range(26):
        x, y = g.uniform(-0.42, 0.42, 2) * taille
        r = float(g.uniform(0.05, 0.13)) * taille
        taches.add(Dot(centre + np.array([x, y, 0.0]), radius=r, color=couleur)
                   .set_opacity(float(g.uniform(0.4, 0.95))))
    return VGroup(cadre, taches)


class CommentSavoirSiUnModeleInvente(Scene):
    """Le problème : on ne peut pas juger une carte d'encre sur son allure."""

    def construct(self):
        t = titre("Comment savoir si un modèle invente ?").scale(0.82)
        self.play(Write(t))
        self.wait(1)
        self.play(t.animate.scale(0.7).to_edge(UP))

        surf = Rectangle(width=2.4, height=1.4, stroke_color=AMBRE, stroke_width=4,
                         fill_color=PAPYRUS, fill_opacity=0.15)
        surf.move_to(LEFT * 4.0)
        e1 = phrase("une surface", 19, AMBRE).next_to(surf, DOWN, buff=0.3)

        boite = Rectangle(width=2.4, height=1.6, stroke_color=FROID, stroke_width=4)
        nom = phrase("le modèle", 19, FROID).move_to(boite)

        c = carte(RIGHT * 4.0, 7)
        e3 = phrase("une carte d'encre", 19, AMBRE).next_to(c, DOWN, buff=0.3)

        f1 = Arrow(surf.get_right(), boite.get_left(), buff=0.25, color=SOURD,
                   stroke_width=3)
        f2 = Arrow(boite.get_right(), c.get_left(), buff=0.25, color=SOURD,
                   stroke_width=3)

        self.play(FadeIn(surf), FadeIn(e1))
        self.play(Create(boite), FadeIn(nom))
        self.play(GrowArrow(f1))
        self.play(GrowArrow(f2), FadeIn(c), FadeIn(e3))
        self.wait(2)

        lg = legende("elle a l'air crédible. Et alors ?", 24)
        self.play(FadeIn(lg))
        self.wait(3)

        # ⚠⚠ Le point qui bloque toute evaluation naive.
        lg2 = legende("une carte crédible est exactement ce qu'un modèle qui invente\n"
                      "produirait aussi", 22, ROUGE)
        self.play(ReplacementTransform(lg, lg2))
        self.wait(4)
        self.play(*[FadeOut(m) for m in (t, surf, e1, boite, nom, c, e3, f1, f2, lg2)])


class LeRenversement(Scene):
    """On ne cherche pas une bonne surface : on en fabrique une qu'on sait fausse."""

    def construct(self):
        t = titre("Le renversement").scale(0.8)
        self.play(Write(t))
        self.wait(1)
        self.play(t.animate.scale(0.72).to_edge(UP))

        a = phrase("On ne peut pas trouver une surface dont on SAIT qu'elle est bonne.",
                   24)
        self.play(FadeIn(a))
        self.wait(3)
        b = phrase("Mais on peut en fabriquer une dont on sait qu'elle est FAUSSE.",
                   25, AMBRE)
        b.next_to(a, DOWN, buff=0.6)
        self.play(FadeIn(b))
        self.wait(3)

        self.play(FadeOut(a), b.animate.scale(0.85).to_edge(UP, buff=1.3))

        # ⭐ Et c est alpha qui le prouve -- rappel de la video 2, en une image.
        NIV = [-1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5]
        feuilles = VGroup(*[
            Line(LEFT * 3.4 + UP * y, RIGHT * 0.6 + UP * y, stroke_width=4,
                 color=PAPYRUS).set_stroke(opacity=0.4) for y in NIV])
        obl = Line(LEFT * 3.4 + DOWN * 1.4, RIGHT * 0.6 + UP * 1.4,
                   stroke_width=7, color=ROUGE)
        grp = VGroup(feuilles, obl).shift(DOWN * 0.4)
        self.play(FadeIn(feuilles), Create(obl))

        preuve = VGroup(
            phrase("α = 0,91", 30, ROUGE),
            phrase("elle traverse l'empilement.", 21),
            phrase("Aucune feuille n'est à portée —", 21, "#9A928A"),
            phrase("c'est de la géométrie, pas une opinion.", 21, "#9A928A"),
        ).arrange(DOWN, buff=0.28)
        preuve.move_to(RIGHT * 3.6 + DOWN * 0.4)
        self.play(FadeIn(preuve))
        self.wait(4)

        q = legende("alors : que dit le modèle, sur CETTE surface-là ?", 24, AMBRE)
        self.play(FadeIn(q))
        self.wait(3)
        self.play(*[FadeOut(m) for m in (t, b, grp, preuve, q)])


class IlRendLaMemeCarte(Scene):
    """Le résultat : deux entrées différentes, la même sortie."""

    def construct(self):
        t = titre("Il rend la même carte").scale(0.78).to_edge(UP)
        self.play(Write(t))

        # ── Deux entrees, franchement differentes ────────────────────────────────
        e_bonne = Rectangle(width=2.0, height=1.3, stroke_color=AMBRE, stroke_width=3,
                            fill_color=PAPYRUS, fill_opacity=0.18).move_to(LEFT * 4.4
                                                                           + UP * 1.5)
        e_fausse = Rectangle(width=2.0, height=1.3, stroke_color=ROUGE, stroke_width=3,
                             fill_color=PAPYRUS, fill_opacity=0.18).move_to(LEFT * 4.4
                                                                            + DOWN * 1.6)
        l1 = phrase("surface qui suit\nune feuille", 17, AMBRE).next_to(e_bonne, UP, buff=0.2)
        l2 = phrase("surface en travers", 17, ROUGE).next_to(e_fausse, DOWN, buff=0.2)
        self.play(FadeIn(e_bonne), FadeIn(l1), FadeIn(e_fausse), FadeIn(l2))

        # ⚠ Placé SOUS le titre plutôt qu'au bord gauche : la version précédente
        # débordait du cadre et se lisait « 1 % » — un chiffre faux, obtenu par troncature
        # graphique. Invisible dans le code, évident sur une vignette.
        diff = phrase("11 % de différence entre les deux entrées", 19, CRAIE)
        diff.move_to(LEFT * 2.6 + UP * 3.05)
        self.play(FadeIn(diff))
        self.wait(2)

        # ── Deux sorties, la MEME carte ──────────────────────────────────────────
        # ⚠ Les deux cartes sont dessinees avec la MEME graine : c est litteralement le
        # resultat mesure, pas une licence graphique.
        c1 = carte(RIGHT * 1.4 + UP * 1.5, 11, AMBRE, 2.0)
        c2 = carte(RIGHT * 1.4 + DOWN * 1.6, 11, ROUGE, 2.0)
        f1 = Arrow(e_bonne.get_right(), c1.get_left(), buff=0.3, color=SOURD, stroke_width=3)
        f2 = Arrow(e_fausse.get_right(), c2.get_left(), buff=0.3, color=SOURD, stroke_width=3)
        self.play(GrowArrow(f1), FadeIn(c1))
        self.play(GrowArrow(f2), FadeIn(c2))
        self.wait(2)

        res = VGroup(
            phrase("les sorties se ressemblent", 20),
            phrase("à 2,9 %", 30, ROUGE),
            phrase("alors que deux cartes sans rapport", 18, "#9A928A"),
            phrase("seraient à 95,4 %", 18, "#9A928A"),
        ).arrange(DOWN, buff=0.24).move_to(RIGHT * 4.9)
        self.play(FadeIn(res))
        self.wait(4)

        cle = phrase("Sa sortie ne dépend pas de la présence d'une feuille.", 25, ROUGE)
        cle.to_edge(DOWN, buff=0.55)
        self.play(FadeIn(cle))
        self.wait(4)
        self.play(*[FadeOut(m) for m in (t, e_bonne, e_fausse, l1, l2, diff,
                                         c1, c2, f1, f2, res, cle)])


class CeQueCaProuveEtCeQueCaNeProuvePas(Scene):
    """La portée exacte du résultat — ni plus, ni moins."""

    def construct(self):
        t = titre("Ce que ça prouve, et ce que ça ne prouve pas").scale(0.72).to_edge(UP)
        self.play(Write(t))

        oui = VGroup(
            phrase("✓  établi", 22, VERT),
            phrase("sa sortie ne dépend pas", 21),
            phrase("d'une feuille présente", 21),
        ).arrange(DOWN, buff=0.24)
        non = VGroup(
            phrase("✗  NON établi", 22, ROUGE),
            phrase("qu'il signale de l'encre", 21),
            phrase("là où il n'y en a pas", 21),
        ).arrange(DOWN, buff=0.24)
        duo = VGroup(oui, non).arrange(RIGHT, buff=2.0)
        self.play(FadeIn(oui, shift=RIGHT * 0.3))
        self.wait(3)
        self.play(FadeIn(non, shift=LEFT * 0.3))
        self.wait(3)

        # ⚠⚠ La raison de la moitie manquante, et elle est honnete : sur ce rouleau, le
        # modele ne signale d encre NULLE PART. On ne peut donc pas tester la these forte.
        pourquoi = phrase("parce que sur ce rouleau, il n'en signale nulle part —\n"
                          "il n'y a rien à prendre en défaut", 21, "#9A928A")
        pourquoi.next_to(duo, DOWN, buff=0.8)
        self.play(FadeIn(pourquoi))
        self.wait(4)

        self.play(FadeOut(duo), FadeOut(pourquoi))
        fin = VGroup(
            phrase("Un résultat qui dit exactement sa portée", 25, AMBRE),
            phrase("vaut mieux qu'un résultat qui en promet plus.", 25, AMBRE),
        ).arrange(DOWN, buff=0.35)
        self.play(FadeIn(fin))
        self.wait(4)
