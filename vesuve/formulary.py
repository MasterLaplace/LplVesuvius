"""The formulary: every equation the program applies, with the fact that carries it and what computes it.

An equation is an ENTRY of this module, never a sentence in a document: `vesuve formulas` renders it, a
pipeline's report cites its identifier with its inputs and its value, and a test requires every equation that
carries a computation to perform it. The identifiers are those of `docs/archive/151` §5 and `213` §4 on the
`experimental` branch when they exist ([F…], [N…], [D…]); the others are named here.

⚠ A correction of an archived document, stated and not made in silence: `151` [F31] writes the Fresnel number
a²/(λD). The research (`src/encre/nombre_de_fresnel.py:142`) computes √(λD)/p, the inverse square root of the
classical form, and this is the form that gives F = 0.39 for the thirteen prize scrolls. The formulary follows
the research.
"""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from vesuve import core


@dataclass(frozen=True)
class Equation:
    id: str
    stage: str      # the pipeline stage where it serves: E2, B, E4, E5, E6, E7, N, TR, T, E8
    name: str
    latex: str
    statement: str  # what it says, in one sentence
    fact: str       # the identifier of the registry fact that carries it
    source: str     # where it was established, and its producer
    compute: Callable | None = None  # the function that computes it; None when it is a procedure rule


_E = Equation
FORMULARY: dict[str, Equation] = {e.id: e for e in [
    _E("E2", "E2", "the half sheet", r"\delta = \mathrm{round}\!\left(\frac{s}{2\,v}\right)",
       "Half the sheet-to-sheet step, in voxels: the search range of the step and the threshold of the certificate.",
       "R4-F14", "`que_montrent_ces_deux_vues.py:60`, published step s = 173 µm at v = 2.4 µm",
       core.half_sheet_voxels),
    _E("N2", "B", "the spread of k rows", r"\sigma_k = \sqrt{\sigma_p^2 + \sigma_b^2 / k}",
       "Averaging k rows only divides their own noise, never the part they share.",
       "R4-F328", "`213` [N2], `210`", core.spread_of_k_rows),
    _E("N5", "B", "the holdable length", r"n_{\max} = \left(\frac{\delta}{\sigma}\right)^2",
       "A sheet trace whose steps spread by σ leaves its sheet after n_max seams.",
       "R4-F340", "`213` [N5], `src/nappe/le_budget_de_la_nappe.py:120`", core.holdable_length),
    _E("N7", "B", "the triangle of own noises",
       r"\sigma_{b,i}^2 = \frac{\sigma_\Delta^2(i,j) + \sigma_\Delta^2(i,k) - \sigma_\Delta^2(j,k)}{2}",
       "Three disagreements give three own noises; a negative variance would refute the model.",
       "R4-F343", "`213` [N7], `212`", core.triangle_own_noise),
    _E("D1", "B", "the error of a spread", r"\mathrm{se}(\hat\sigma) = \frac{\hat\sigma}{\sqrt{2n}}",
       "Without it, a strict inequality against a bound only passes by chance.",
       "R5-L21", "`213` [D1]", core.spread_standard_error),
    _E("D2", "B", "the decisive count", r"m = \left\lceil \frac{9\,(1-g)}{g} \right\rceil",
       "The number of replicates that puts three sampling errors within the margin of a guarantee g.",
       "R5-L21", "`213` [D2]; 171 at g = 0.05", core.decisive_count),
    _E("F4", "E4", "the step of a cut",
       r"s = -\left(\arg\max_{|k| \le \delta} \frac{\sum a_{t+k}\, b_t}{\sqrt{\sum a_{t+k}^2 \sum b_t^2}} - \delta\right)",
       "The depth shift that aligns a chunk's edge with its neighbour's, profiles centred, correlation normalised by "
       "the energy of both windows.",
       "R4-F293", "`src/nappe/la_derive_saccumule_t_elle.py:99` (`un_pas`)", core.cut_step),
    _E("F4c", "E4", "the step of a seam",
       r"\hat s = \frac{1}{n}\sum_{i=1}^{n} s_i, \qquad d = \bar s_{\mathrm{even}} - \bar s_{\mathrm{odd}}",
       "The mean of the steps of sixteen cuts, and the disagreement of its even and odd ranks, which measures chance.",
       "R4-F293", "`combien_de_rangees_faut_il_pour_lire_le_pas.py:120`", core.seam_step),
    _E("C1", "E6", "the consensus",
       r"c(s) = \mathrm{median}\{\hat s_\ell(s)\} \ \text{if}\ \#\{\ell\} \ge \lfloor k/2 \rfloor + 1",
       "At each seam, the median of the lines of a band that are present, if there is a majority of them.",
       "R4-F378", "`le_consensus_traverse_t_il_la_rangee.py:94`"),
    _E("C2", "E5", "the crossed hole", r"c(s) = 0 \quad \text{for each seam of a hole of length} \le 17",
       "A majority hole of at most seventeen seams is crossed at zero step; longer, the loop is open.",
       "R4-F389", "`quest_ce_qui_franchit_le_trou_de_majorite.py:243`, the \"mesh\" rule"),
    _E("L", "E6", "the closure of a loop",
       r"L = H(r_0; c_0 \to c_1) + V(c_1; r_0 \to r_1) - H(r_1; c_0 \to c_1) - V(c_0; r_0 \to r_1)",
       "The gap between the two paths from one corner to the other; a geometry closes it exactly.",
       "R4-F393", "`deux_chemins_arrivent_ils_sur_la_meme_spire.py:38`"),
    _E("P", "E6", "the profile of a loop", r"P_j = \sum_{i \le j} L_i, \qquad |P_j| < \delta \ \ \forall j",
       "The closure cumulated cut after cut: a loop holds if its profile stays under the half sheet everywhere.",
       "R4-F403", "`ou_laile_de_droite_se_separe.py:236`"),
    _E("S", "E6", "the reach that sees", r"p = \max_{\text{cuts off the crossing}} (y_{j+1} - y_j) - 1 = 29",
       "Two neighbouring cuts at most 29 rows apart see every crossing as the segment's own did.",
       "R4-F409", "`la_portee_voit_elle_sa_traversee.py:131`"),
    _E("B0", "E6", "the block null", r"b = \max\!\left(1, \min\!\left(\lceil n^{1/3}\rceil, n\right)\right)",
       "The length of the blocks that draw a loop's null, to decide between two lines.",
       "R4-L22", "`pourquoi_lerreur_declaree_est_trop_petite.py:375`", core.block_length),
    _E("M", "E6", "the deciding margin",
       r"\mu_n = |L_n| - \min_m |L_m| - \mathrm{median}\,|L_n^{\mathrm{null}}|",
       "The drifting line is the one the tightest of the three loops avoids, if each other loop exceeds it by more "
       "than its own noise.", "R4-F401", "`laquelle_des_deux_colonnes_derive.py:234`"),
    _E("K", "E6", "the coverage", r"\kappa = \frac{|A \wedge \bigcup_b M_b|}{|A|}",
       "The share of the present chunks surrounded by a loop that holds.", "R4-F410",
       "`une_aile_plus_etroite_tient_elle.py:163`"),
    _E("F25", "E7", "the convergence test",
       r"\alpha = \frac{\log(e_1/e_0)}{\log(n_1/n_0)}",
       "α ≈ 0: the surface converges, a sheet is within reach; α ≈ 1: the error follows the window.",
       "R3-F10", "`src/commun/test_convergence.py:145`", core.convergence_alpha),
    _E("F17", "E7", "the corrected coherence",
       r"c' = \max\!\left(0, \frac{c - 1/\sqrt n}{1 - 1/\sqrt n}\right)",
       "Zero on pure noise, one on a perfect rotation.", "R4-F100", "`151` [F17]",
       core.corrected_coherence),
    _E("NW1", "N", "the sheets along a normal",
       r"C_k = \left\{ \frac{t_a + t_{b-1}}{2} \ :\ [a, b) \text{ a maximal run of } P\!\left(\left\lfloor"
       r" \frac{x_k + t_i\, n_k}{f} \right\rfloor\right) > 0 \right\}, \quad t_i = \sigma\, i, \quad"
       r" 0 \le i \le \lfloor 3 s \rfloor",
       "Along the normal of each point of the mesh, from the surface out to three steps on side sigma, the prediction "
       "(f times coarser than the scan) marks runs of samples; the centre of each run is a sheet the next winding may "
       "land on.",
       "R4-F412", "`le_transfert_retrouve_t_il_la_spire_voisine.py:220` (`les_centres`), `247`"),
    _E("NW2", "N", "the next sheet",
       r"\tau^{(0)}_k = \frac{t_a + t_{b-1}}{2} \ \text{for the first run with } a \ge b^{\circ}"
       r" \ \text{(or } |t_a| > 12 \text{ without an own run)}, \quad \text{else } \tau^{(0)}_k = \sigma s",
       "The own sheet is the first run that starts within 12 voxels of the surface, ending at b°; the next winding "
       "starts from the first run after it, and from the fixed step where the ray sees none.",
       "R4-F412", "`le_transfert_retrouve_t_il_la_spire_voisine.py:191` (`la_feuille_suivante`), `247`"),
    _E("NW3", "N", "the vote of the neighbours",
       r"\mu_k = \operatorname{med}\{\tau_j : j \in W_k\} \ \text{if}\ \#\{j \in W_k\ \text{seen}\} \ge 5,"
       r" \ \text{else } \mu_k = \tau_k, \qquad"
       r" \tau_k \leftarrow \begin{cases} \arg\min_{c \in C_k} |c - \mu_k| & \text{if } \min_{c \in C_k} |c - \mu_k|"
       r" < \delta \\ \mu_k & \text{otherwise} \end{cases}",
       "Each point aims at the median of the three by three meshes around it, and takes the sheet its own ray sees "
       "nearest to that aim within half a sheet; repeated until fewer than one point in a thousand changes, thirty "
       "rounds at most.",
       "R4-F412", "`le_transfert_retrouve_t_il_la_spire_voisine.py:233` (`le_vote_itere`), `247`; chained on the band, "
       "`248` (`R4-F413`, `R4-F414`)"),
    _E("F4w", "TR", "the window-to-window step",
       r"s = -\left(k^\star + \frac{c_{k^\star-1} - c_{k^\star+1}}{2\,(c_{k^\star-1} - 2\,c_{k^\star} + c_{k^\star+1})}"
       r"\right), \quad c_k = \frac{\langle a_{[k]}, b_{[k]} \rangle}{\lVert a_{[k]} \rVert\, \lVert b_{[k]} \rVert},"
       r" \quad |k| \le \delta",
       "The shift that aligns two window profiles: the top of their normalised correlation over lags of up to half a "
       "sheet, refined by a parabola. The step of a seam is the sum of eight of them, from the centre of one chunk to "
       "the centre of the next, averaged over sixteen cuts.",
       "R4-F439", "`le_pas_de_fenetre_en_fenetre_voit_il_la_rampe.py:71`"),
    _E("W", "T", "the walk of a neighbourhood",
       r"\hat D = \arg\min_{D,\ \sum_c D_c = 0} \sum_{(i,j)} \left(D_j - D_i - s_{ij}\right)^2",
       "The depth of the sheet in every chunk, by least squares on the window-to-window steps of the seams, over the "
       "largest connected set of chunks; walked once on the reference and once on the produced winding.",
       "R4-F440", "`la_spire_produite_se_lit_elle_dans_le_treillis.py:328`"),
    _E("A", "T", "the anchor of a block",
       r"a = \mathrm{median}\left\{\hat D^{\,p}_c - \hat D^{\,r}_c \ :\ c \in \mathcal{N} \setminus B\right\}",
       "The level the produced winding should have, read on the neighbouring blocks only: the block itself is left "
       "out, so its own slip cannot pull its anchor.",
       "R4-F446", "`le_voisinage_dit_il_quel_niveau_est_le_bon.py:98`"),
    _E("X", "T", "the slip mixture",
       r"x \sim w_0\,\mathcal{N}(0, \sigma^2) + w_+\,\mathcal{N}(g, \sigma^2) + w_-\,\mathcal{N}(-g, \sigma^2)",
       "The departure of each chunk from its anchor is noise, or a slip of one winding above or below; weights and "
       "the shared width by EM, the slip g = 69.458 voxels read without a judge by `261`.",
       "R4-F445", "`la_marche_sait_elle_ou_ne_pas_corriger.py:79`"),
    _E("R", "T", "the correction rule",
       r"\tau_1 = \tau_0 - x \quad \text{if} \quad \max\left(w_+ e^{-\frac{(x-g)^2}{2\sigma^2}},\ "
       r"w_- e^{-\frac{(x+g)^2}{2\sigma^2}}\right) > w_0\, e^{-\frac{x^2}{2\sigma^2}}",
       "A point of the transfer is brought back by its departure when a slip explains that departure better than the "
       "noise; otherwise it is left alone. No judge takes part.",
       "R4-F456", "`la_marche_sait_elle_ou_ne_pas_corriger.py:131`"),
    _E("G", "T", "the sign test",
       r"p = \min\left(1,\ 2 \sum_{i \le \min(a, b)} \binom{a+b}{i} 2^{-(a+b)}\right)",
       "How often chance alone, one in two, would give a split at least as uneven as a misses made right against b "
       "rights made misses; exact and two-sided.",
       "R4-F471", "`les_gains_publies_se_distinguent_ils_du_hasard.py:78`"),
    _E("F31", "E8", "the Fresnel number", r"F = \frac{\sqrt{\lambda D}}{p}, \qquad \lambda = \frac{hc}{E}",
       "The width of the first fringe in pixels: 0.39 for the prize scrolls, 0.74 in production.",
       "R6-F08", "`src/encre/nombre_de_fresnel.py:142`", core.fresnel_number),
    _E("F29", "E8", "the area under the curve", r"\mathrm{AUC} = \frac{R_+ - n_+(n_+ + 1)/2}{n_+\, n_-}",
       "Mann-Whitney on mid ranks; the shuffle control must return 0.500.", "R1-F01",
       "`src/volume/evaluate_segment.py:72`", core.area_under_curve),
]}


def equation(ident: str) -> Equation:
    try:
        return FORMULARY[ident]
    except KeyError:
        raise KeyError(f"unknown equation {ident!r}; the formulary holds: {sorted(FORMULARY)}") from None
