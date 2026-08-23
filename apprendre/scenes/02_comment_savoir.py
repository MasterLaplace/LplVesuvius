"""Vidéo 2 — Comment savoir si on a suivi la BONNE feuille ?

⚠⚠ **C'est le concept central du projet, et il s'appelle α.** Cette vidéo le construit sans
rien supposer : on part du problème (il n'y a pas de vérité à laquelle comparer), on trouve
l'idée (regarder deux fois), puis on met un nombre dessus — et le nombre demande un
logarithme, donc le logarithme est expliqué AVANT d'être utilisé, à partir de la seule
question qu'il pose : « combien de fois ai-je multiplié ? ».

⭐ Règle de rédaction : **aucun symbole n'apparaît avant que la chose qu'il nomme ait été
montrée.** `d` arrive après qu'on ait vu un écart, `n` après qu'on ait vu une fenêtre, et α
seulement quand les deux rapports sont à l'écran.
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


def legende(txt, taille=21, couleur=CRAIE):
    """Une légende, toujours ancrée en bas — voir la vidéo 1 pour la raison."""
    return phrase(txt, taille, couleur).to_edge(DOWN, buff=0.6)


class LeProblemeIlNyAPasDeVerite(Scene):
    """On ne peut pas comparer à la bonne réponse : personne ne l'a."""

    def construct(self):
        t = titre("Comment savoir si on a suivi la BONNE feuille ?").scale(0.85)
        self.play(Write(t))
        self.wait(1)
        self.play(t.animate.scale(0.62).to_edge(UP))

        naif = phrase("L'idée naïve : comparer à la bonne réponse.", 26)
        self.play(FadeIn(naif))
        self.wait(2)

        barre = Line(naif.get_left() + LEFT * 0.2, naif.get_right() + RIGHT * 0.2,
                     color=ROUGE, stroke_width=5)
        self.play(Create(barre), run_time=0.8)
        # ⚠⚠ C'est LE point de départ, et il est contre-intuitif : dans ce problème il
        # n'existe aucune vérité de référence. Personne n'a jamais déroulé ce rouleau.
        pourquoi = phrase("Il n'y en a pas. Personne n'a jamais déroulé ce rouleau.",
                          24, AMBRE)
        pourquoi.next_to(naif, DOWN, buff=0.8)
        self.play(FadeIn(pourquoi))
        self.wait(3)

        self.play(FadeOut(naif), FadeOut(barre), FadeOut(pourquoi))
        q = phrase("Alors il faut une question que la trace elle-même\npeut trancher.", 26)
        self.play(FadeIn(q))
        self.wait(3)
        self.play(FadeOut(q), FadeOut(t))


class RegarderAutourDeLaSurface(Scene):
    """Le profil de profondeur : où est la matière, autour de la surface tracée ?"""

    def construct(self):
        t = titre("L'idée : regarder AUTOUR de la surface").scale(0.72).to_edge(UP)
        self.play(Write(t))

        # ── Le décor : des feuilles empilées, vues de côté ────────────────────────
        NIVEAUX = [-2.1, -1.4, -0.7, 0.0, 0.7, 1.4, 2.1]
        feuilles = VGroup(*[
            Line(LEFT * 5 + UP * y, RIGHT * 1.2 + UP * y, stroke_width=5, color=PAPYRUS)
            .set_stroke(opacity=0.45)
            for y in NIVEAUX
        ])
        self.play(LaggedStart(*[Create(f) for f in feuilles], lag_ratio=0.1),
                  run_time=2)
        lg = legende("le rouleau vu de CÔTÉ : des feuilles, empilées")
        self.play(FadeIn(lg))
        self.wait(2)

        # ── Cas A : la trace est POSÉE sur une feuille ────────────────────────────
        trace = Line(LEFT * 5 + UP * 0.0, RIGHT * 1.2 + UP * 0.0,
                     stroke_width=8, color=AMBRE)
        self.play(Create(trace), run_time=1.2)
        lg2 = legende("une trace, posée sur l'une d'elles", 21, AMBRE)
        self.play(ReplacementTransform(lg, lg2))
        self.wait(2)

        # ── La fenêtre : on regarde à N couches de part et d'autre ────────────────
        fen = Rectangle(width=6.2, height=1.5, stroke_color=FROID, stroke_width=3)
        fen.move_to(trace.get_center())
        self.play(Create(fen))
        lgf = legende("on regarde dans une FENÊTRE, au-dessus et en dessous", 21, FROID)
        self.play(ReplacementTransform(lg2, lgf))
        self.wait(2)

        # ── Le profil : combien de matière à chaque profondeur ────────────────────
        axe = Line(RIGHT * 2.2 + DOWN * 2.4, RIGHT * 2.2 + UP * 2.4,
                   stroke_width=2, color=SOURD)
        self.play(Create(axe))
        prof = phrase("profondeur", 16, SOURD).rotate(PI / 2)
        prof.next_to(axe, LEFT, buff=0.12)
        mat = phrase("matière trouvée →", 16, SOURD)
        mat.next_to(axe, DOWN, buff=0.25).shift(RIGHT * 0.8)
        self.play(FadeIn(prof), FadeIn(mat))

        # ⭐ Le pic est AU CENTRE : la feuille est là où la trace est posée.
        courbe = VMobject(stroke_color=AMBRE, stroke_width=5)
        pts = []
        for y in np.linspace(-2.3, 2.3, 90):
            x = 2.25 + 2.6 * float(np.exp(-(y / 0.42) ** 2))
            pts.append(np.array([x, y, 0.0]))
        courbe.set_points_smoothly(pts)
        self.play(Create(courbe), run_time=2)

        pic = Dot(np.array([4.85, 0.0, 0.0]), color=AMBRE, radius=0.09)
        etq = phrase("le PIC : la feuille est ici", 19, AMBRE)
        etq.next_to(pic, RIGHT, buff=0.2)
        self.play(GrowFromCenter(pic), FadeIn(etq))
        lgp = legende("la trace est SUR une feuille : le pic est juste là, au centre",
                      21, AMBRE)
        self.play(ReplacementTransform(lgf, lgp))
        self.wait(3)

        self.play(*[FadeOut(m) for m in (t, feuilles, trace, fen, axe, prof, mat,
                                         courbe, pic, etq, lgp)])


class QuandLaTraceEstEnTravers(Scene):
    """Le cas fautif : la surface coupe la pile au lieu de la suivre."""

    def construct(self):
        t = titre("Et quand la trace coupe la pile ?").scale(0.72).to_edge(UP)
        self.play(Write(t))

        NIVEAUX = [-2.1, -1.4, -0.7, 0.0, 0.7, 1.4, 2.1]
        feuilles = VGroup(*[
            Line(LEFT * 5 + UP * y, RIGHT * 1.2 + UP * y, stroke_width=5, color=PAPYRUS)
            .set_stroke(opacity=0.45)
            for y in NIVEAUX
        ])
        self.play(LaggedStart(*[Create(f) for f in feuilles], lag_ratio=0.06),
                  run_time=1.4)

        # ⚠⚠ La trace OBLIQUE : elle traverse les feuilles au lieu d'en suivre une. C'est
        # la panne que tout le projet cherche à détecter, et elle est invisible sur l'image
        # rendue — d'où le besoin d'une mesure.
        oblique = Line(LEFT * 5 + DOWN * 2.0, RIGHT * 1.2 + UP * 2.0,
                       stroke_width=8, color=ROUGE)
        self.play(Create(oblique), run_time=1.5)
        lg = legende("elle traverse l'empilement — c'est LA panne qu'on cherche", 21, ROUGE)
        self.play(FadeIn(lg))
        self.wait(3)

        lg2 = legende("sur l'image rendue, ça ne se voit pas : le rendu est joli quand même",
                      20)
        self.play(ReplacementTransform(lg, lg2))
        self.wait(3)
        self.play(*[FadeOut(m) for m in (t, feuilles, oblique, lg2)])


class RegarderDeuxFois(Scene):
    """L'idée qui tranche : mesurer avec DEUX tailles de fenêtre."""

    def construct(self):
        t = titre("L'idée : regarder DEUX fois").scale(0.78).to_edge(UP)
        self.play(Write(t))

        gauche, droite = LEFT * 3.4, RIGHT * 3.4

        def scene_locale(centre, oblique, couleur):
            g = VGroup()
            for y in (-1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5):
                g.add(Line(centre + LEFT * 2.4 + UP * y, centre + RIGHT * 2.4 + UP * y,
                           stroke_width=3, color=PAPYRUS).set_stroke(opacity=0.35))
            if oblique:
                g.add(Line(centre + LEFT * 2.4 + DOWN * 1.4,
                           centre + RIGHT * 2.4 + UP * 1.4,
                           stroke_width=6, color=couleur))
            else:
                g.add(Line(centre + LEFT * 2.4, centre + RIGHT * 2.4,
                           stroke_width=6, color=couleur))
            return g

        sur = scene_locale(gauche, False, AMBRE)
        trav = scene_locale(droite, True, ROUGE)
        eg = phrase("SUR une feuille", 20, AMBRE).next_to(sur, UP, buff=0.3)
        ed = phrase("EN TRAVERS", 20, ROUGE).next_to(trav, UP, buff=0.3)
        self.play(FadeIn(sur), FadeIn(trav), FadeIn(eg), FadeIn(ed))
        self.wait(1)

        # ── Petite fenêtre ────────────────────────────────────────────────────────
        pf_g = Rectangle(width=5.0, height=0.9, stroke_color=FROID, stroke_width=3)
        pf_g.move_to(gauche)
        pf_d = Rectangle(width=5.0, height=0.9, stroke_color=FROID, stroke_width=3)
        pf_d.move_to(droite)
        self.play(Create(pf_g), Create(pf_d))
        lg = legende("d'abord une PETITE fenêtre", 21, FROID)
        self.play(FadeIn(lg))

        rg = phrase("écart trouvé : petit", 19, AMBRE).next_to(sur, DOWN, buff=0.5)
        rd = phrase("écart trouvé : petit", 19, ROUGE).next_to(trav, DOWN, buff=0.5)
        self.play(FadeIn(rg), FadeIn(rd))
        self.wait(2)

        sur_prise = phrase("les deux se ressemblent !", 22, CRAIE).to_edge(DOWN, buff=1.6)
        self.play(FadeIn(sur_prise))
        self.wait(2)
        self.play(FadeOut(sur_prise))

        # ── Grande fenêtre : c'est là que tout se sépare ──────────────────────────
        gf_g = Rectangle(width=5.0, height=2.6, stroke_color=FROID, stroke_width=3)
        gf_g.move_to(gauche)
        gf_d = Rectangle(width=5.0, height=2.6, stroke_color=FROID, stroke_width=3)
        gf_d.move_to(droite)
        lg2 = legende("puis une GRANDE fenêtre — et là, tout se sépare", 21, FROID)
        self.play(ReplacementTransform(pf_g, gf_g), ReplacementTransform(pf_d, gf_d),
                  ReplacementTransform(lg, lg2), run_time=1.6)

        rg2 = phrase("écart : LE MÊME", 20, AMBRE).next_to(sur, DOWN, buff=0.5)
        rd2 = phrase("écart : PLUS GRAND", 20, ROUGE).next_to(trav, DOWN, buff=0.5)
        self.play(ReplacementTransform(rg, rg2), ReplacementTransform(rd, rd2))
        self.wait(3)

        # ⭐ La phrase à retenir de toute la vidéo.
        cle = phrase("La feuille ne bouge pas. Le vide, lui, suit la fenêtre.", 25, CRAIE)
        cle.to_edge(DOWN, buff=1.5)
        self.play(FadeOut(lg2), FadeIn(cle))
        self.wait(4)
        self.play(*[FadeOut(m) for m in (t, sur, trav, eg, ed, gf_g, gf_d,
                                         rg2, rd2, cle)])


class MettreUnNombreDessus(Scene):
    """Du constat au chiffre : le RAPPORT, expliqué avant d'être écrit."""

    def construct(self):
        t = titre("Mettre un nombre dessus").scale(0.78).to_edge(UP)
        self.play(Write(t))

        # ⚠⚠ On part de ce qui a été VU, pas d'une définition. Les quatre nombres
        # ci-dessous sont ceux de la vidéo précédente, rendus explicites.
        intro = phrase("« le même » et « plus grand », ce ne sont pas des mesures.", 24)
        self.play(FadeIn(intro))
        self.wait(2)
        self.play(intro.animate.scale(0.8).to_edge(UP, buff=1.4))

        tab = VGroup(
            phrase("fenêtre", 20, FROID),
            phrase("écart, SUR la feuille", 20, AMBRE),
            phrase("écart, EN TRAVERS", 20, ROUGE),
            phrase("petite : 40 couches", 21),
            phrase("45", 24, AMBRE),
            phrase("45", 24, ROUGE),
            phrase("grande : 160 couches", 21),
            phrase("45", 24, AMBRE),
            phrase("158", 24, ROUGE),
        ).arrange_in_grid(rows=3, cols=3, buff=(0.9, 0.55))
        tab.shift(DOWN * 0.3)
        self.play(FadeIn(tab, shift=UP * 0.2), run_time=1.6)
        self.wait(3)

        # ── Le rapport, mot avant symbole ─────────────────────────────────────────
        q = phrase("La question : quand la fenêtre est multipliée par 4,\n"
                   "l'écart est multiplié par combien ?", 24, CRAIE)
        q.to_edge(DOWN, buff=0.7)
        self.play(FadeIn(q))
        self.wait(3)

        r1 = phrase("45 → 45   :  multiplié par 1", 23, AMBRE)
        r2 = phrase("45 → 158  :  multiplié par 3,5", 23, ROUGE)
        rs = VGroup(r1, r2).arrange(DOWN, buff=0.35).to_edge(DOWN, buff=0.7)
        self.play(FadeOut(q), FadeIn(rs))
        self.wait(3)

        # ⭐ Le mot « rapport » est introduit ici, en montrant qu'on vient de le calculer.
        mot = phrase("ce « multiplié par » s'appelle un RAPPORT :\n"
                     "on divise l'arrivée par le départ.", 22, CRAIE)
        mot.to_edge(DOWN, buff=0.55)
        self.play(FadeOut(rs), FadeIn(mot))
        self.wait(3)
        self.play(*[FadeOut(m) for m in (t, intro, tab, mot)])


class LeLogarithmeEnUneQuestion(Scene):
    """Le logarithme, expliqué par la seule question qu'il pose."""

    def construct(self):
        t = titre("Le logarithme, en une question").scale(0.78).to_edge(UP)
        self.play(Write(t))

        # ⚠⚠ Aucune définition formelle. Un logarithme répond à UNE question, et c'est
        # celle-là : « combien de fois ai-je multiplié ? ». Tout le reste en découle, et
        # commencer par « l'inverse de l'exponentielle » perdrait immédiatement le lecteur
        # qui n'a pas l'exponentielle.
        q = phrase("« Combien de fois ai-je multiplié ? »", 30, AMBRE)
        self.play(FadeIn(q))
        self.wait(2)
        self.play(q.animate.scale(0.72).to_edge(UP, buff=1.3))

        # ── Un escalier de doublements ────────────────────────────────────────────
        base = LEFT * 5.2 + DOWN * 1.6
        marches = VGroup()
        etiq = VGroup()
        valeurs = [1, 2, 4, 8, 16]
        for i, v in enumerate(valeurs):
            h = 0.42 * i + 0.35
            r = Rectangle(width=1.5, height=h, fill_color=FROID, fill_opacity=0.55,
                          stroke_width=0)
            r.move_to(base + RIGHT * (2.0 * i) + UP * h / 2)
            marches.add(r)
            e = phrase(f"{v}", 22, CRAIE).next_to(r, UP, buff=0.15)
            etiq.add(e)
        self.play(LaggedStart(*[GrowFromEdge(m, DOWN) for m in marches], lag_ratio=0.25),
                  LaggedStart(*[FadeIn(e) for e in etiq], lag_ratio=0.25), run_time=3)

        fleches = VGroup()
        for i in range(4):
            a = Arrow(marches[i].get_top() + UP * 0.55 + RIGHT * 0.2,
                      marches[i + 1].get_top() + UP * 0.55 + LEFT * 0.2,
                      buff=0.1, color=AMBRE, stroke_width=3, max_tip_length_to_length_ratio=0.2)
            lab = phrase("×2", 17, AMBRE).next_to(a, UP, buff=0.06)
            fleches.add(VGroup(a, lab))
        self.play(LaggedStart(*[FadeIn(f) for f in fleches], lag_ratio=0.25), run_time=2)
        self.wait(2)

        lg = legende("de 1 à 16, j'ai multiplié par 2 quatre fois", 22)
        self.play(FadeIn(lg))
        self.wait(2)

        # ⭐ Le SEUL énoncé formel de la vidéo, et il arrive après quatre flèches dessinées.
        enonce = phrase("« logarithme en base 2 de 16 » = 4", 26, AMBRE)
        enonce.to_edge(DOWN, buff=1.6)
        self.play(FadeIn(enonce))
        self.wait(3)

        # ⚠⚠ La propriété dont on a réellement besoin, et une seule.
        self.play(FadeOut(lg), FadeOut(enonce), FadeOut(fleches))
        prop = VGroup(
            phrase("Ce qu'on retiendra, et c'est tout :", 24),
            phrase("multiplier par 1  →  logarithme = 0", 24, AMBRE),
            phrase("« je n'ai pas multiplié du tout »", 19, "#9A928A"),
        ).arrange(DOWN, buff=0.3).to_edge(DOWN, buff=0.9)
        self.play(FadeIn(prop))
        self.wait(4)
        self.play(*[FadeOut(m) for m in (t, q, marches, etiq, prop)])


class LaFormuleAssemblee(Scene):
    """α, construit morceau par morceau, chaque symbole après la chose qu'il nomme."""

    def construct(self):
        t = titre("La formule, morceau par morceau").scale(0.78).to_edge(UP)
        self.play(Write(t))

        # ── Les noms, chacun après son objet ──────────────────────────────────────
        noms = VGroup(
            phrase("n₀ , n₁   les deux tailles de fenêtre       40 et 160", 24),
            phrase("d₀ , d₁   les deux écarts mesurés          45 et 158", 24),
        ).arrange(DOWN, buff=0.45)
        noms[0][:5].set_color(FROID)
        noms[1][:5].set_color(AMBRE)
        self.play(FadeIn(noms[0], shift=RIGHT * 0.3))
        self.wait(2)
        self.play(FadeIn(noms[1], shift=RIGHT * 0.3))
        self.wait(2)
        self.play(noms.animate.scale(0.78).to_edge(UP, buff=1.25))

        # ── Étape 1 : les deux rapports ───────────────────────────────────────────
        e1 = phrase("1.  de combien la FENÊTRE a-t-elle grandi ?     160 ÷ 40 = 4",
                    23, FROID)
        e2 = phrase("2.  de combien l'ÉCART a-t-il grandi ?          158 ÷ 45 = 3,5",
                    23, AMBRE)
        etapes = VGroup(e1, e2).arrange(DOWN, buff=0.4, aligned_edge=LEFT)
        etapes.shift(DOWN * 0.2)
        self.play(FadeIn(e1))
        self.wait(2)
        self.play(FadeIn(e2))
        self.wait(2)

        # ── Étape 3 : comparer les deux, en logarithmes ───────────────────────────
        e3 = phrase("3.  l'écart a-t-il suivi la fenêtre ?", 23, CRAIE)
        e3.next_to(etapes, DOWN, buff=0.55, aligned_edge=LEFT)
        self.play(FadeIn(e3))
        self.wait(2)

        # ⚠⚠ Pourquoi le logarithme et pas une simple division de 3,5 par 4 : parce que le
        # « suivi parfait » ne veut pas dire « même rapport », il veut dire « même
        # PUISSANCE ». Doubler la fenêtre deux fois doit compter deux fois, et c'est
        # exactement ce que le logarithme mesure.
        pourquoi = phrase("on les compare en « combien de fois multiplié »,\n"
                          "donc en logarithmes", 21, "#9A928A")
        pourquoi.next_to(e3, DOWN, buff=0.35, aligned_edge=LEFT)
        self.play(FadeIn(pourquoi))
        self.wait(3)

        self.play(FadeOut(etapes), FadeOut(e3), FadeOut(pourquoi), FadeOut(noms))

        # ── La formule ────────────────────────────────────────────────────────────
        f_haut = phrase("log ( d₁ ÷ d₀ )", 30, AMBRE)
        barre = Line(LEFT * 1.9, RIGHT * 1.9, stroke_width=3, color=CRAIE)
        f_bas = phrase("log ( n₁ ÷ n₀ )", 30, FROID)
        alpha = phrase("α  =", 34, CRAIE)
        frac = VGroup(f_haut, barre, f_bas).arrange(DOWN, buff=0.28)
        tout = VGroup(alpha, frac).arrange(RIGHT, buff=0.45)
        self.play(FadeIn(alpha))
        self.play(FadeIn(f_haut, shift=DOWN * 0.2))
        self.play(Create(barre))
        self.play(FadeIn(f_bas, shift=UP * 0.2))
        self.wait(3)

        lect = phrase("« de combien l'écart a grandi »,  divisé par\n"
                      "« de combien la fenêtre a grandi »", 22)
        lect.to_edge(DOWN, buff=0.9)
        self.play(FadeIn(lect))
        self.wait(4)
        self.play(FadeOut(lect), tout.animate.scale(0.7).to_edge(UP, buff=1.2),
                  FadeOut(t))

        # ── Les deux cas, chiffrés ────────────────────────────────────────────────
        cas1 = VGroup(
            phrase("SUR une feuille", 22, AMBRE),
            phrase("l'écart n'a pas bougé : 45 ÷ 45 = 1", 20),
            phrase("et le logarithme de 1 vaut 0", 20, "#9A928A"),
            phrase("α = 0", 30, AMBRE),
        ).arrange(DOWN, buff=0.26)
        # ⚠⚠ Le chiffre est le VRAI, pas un arrondi commode : 158 ÷ 45 = 3,51 et non 4,
        # donc α vaut 0,91 et non 1. Écrire « α = 1 » serait plus joli et FAUX — et un
        # lecteur qui referait le calcul trouverait autre chose que la vidéo, ce qui est
        # la façon la plus rapide de perdre sa confiance. ⭐ En prime, 0,91 est exactement
        # ce que le dépôt a mesuré sur PHercParis4 : l'exemple EST la donnée.
        cas2 = VGroup(
            phrase("EN TRAVERS", 22, ROUGE),
            phrase("l'écart a suivi : 158 ÷ 45 = 3,51", 20),
            phrase("la fenêtre, elle : 160 ÷ 40 = 4", 20, "#9A928A"),
            phrase("α = 0,91", 30, ROUGE),
        ).arrange(DOWN, buff=0.26)
        duo = VGroup(cas1, cas2).arrange(RIGHT, buff=1.6).shift(DOWN * 0.6)
        self.play(FadeIn(cas1, shift=RIGHT * 0.3))
        self.wait(3)
        self.play(FadeIn(cas2, shift=LEFT * 0.3))
        self.wait(4)

        # ⭐ Et la phrase qui rend la mesure utilisable sans rien calculer.
        self.play(FadeOut(duo))
        fin = VGroup(
            phrase("α proche de 0  →  la trace suit une feuille", 25, AMBRE),
            phrase("α proche de 1  →  elle coupe l'empilement", 25, ROUGE),
        ).arrange(DOWN, buff=0.5)
        self.play(FadeIn(fin))
        self.wait(3)

        # ⚠⚠ « Proche de », et pas « égal à ». Un seuil est indispensable, et il n'est pas
        # arbitraire : la mesure elle-même a une précision d'environ ±0,2, mesurée en
        # rejouant la même trace. En dessous de 0,7 on ne condamne pas, au-dessus on
        # condamne — parce qu'entre les deux, la réponse serait un tirage à pile ou face.
        self.play(fin.animate.scale(0.8).to_edge(UP, buff=1.3))
        seuil = VGroup(
            phrase("« proche », parce que la mesure a une précision : ± 0,2", 22),
            phrase("mesurée en rejouant la même trace, pas décidée", 19, "#9A928A"),
            phrase("au-delà de 0,7 on condamne — en dessous, on ne dit rien", 22, CRAIE),
        ).arrange(DOWN, buff=0.35)
        self.play(FadeIn(seuil))
        self.wait(4)

        self.play(FadeOut(seuil), FadeOut(fin))
        vrai = VGroup(
            phrase("Et ce 0,91 n'est pas un exemple inventé :", 24),
            phrase("c'est la mesure réelle du rouleau PHercParis4.", 26, ROUGE),
            phrase("La trace qu'on avait ne suivait aucune feuille.", 22, "#9A928A"),
        ).arrange(DOWN, buff=0.4)
        self.play(FadeIn(vrai))
        self.wait(5)
