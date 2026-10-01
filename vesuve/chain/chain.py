"""The chain of windings: each jump keeps its winding if the criterion holds it, grows it again by one mesh and keeps that
if the criterion holds it too, and relaunches from a point only if it does not; the next jump starts from what was kept
(`R4-F543`, `R4-F551`, `R4-F552`).

Ported from `une_chaine_qui_garde_la_spire_tenue_va_t_elle_plus_loin_sur_pherc0358.py` (slice `356`, `la_chaine_mixte`) and
`une_chaine_relancee_a_chaque_tour_descend_elle_plus_loin.py` (`331`, `la_graine_de_la_relance`) on the `experimental`
branch, with the regrowth of `365`. What varies is injected: the jump, the relaunch, the regrowth and the count are
callables, so that a chain is run on the surfaces of a scroll or on fabricated ones, and the order of its decisions is what
is tested here.
"""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

import numpy as np

from vesuve.chain import criterion, growth
from vesuve.chain.surface import ReadValues, Surface
from vesuve.transfer.surfaces import normals

JUMPS = 8
MARGIN = 1                    # cells: the regrowth is one mesh (`R4-F551`); two meshes bring the offset back (`R4-F550`)
FROM_THE_WINDING = "the winding"
FROM_THE_REGROWTH = "the regrowth"
FROM_A_RELAUNCH = "a relaunch"
LATERAL_IN_STEPS = criterion.LATERAL_PHERCPARIS4 / growth.PHERCPARIS4.step


@dataclass(frozen=True)
class Link:
    """One jump of the chain, and what it kept."""
    jump: growth.Jump
    departure: Surface
    origin: str | None             # where the kept surface comes from; None where the chain stopped
    winding_count: dict            # the count of the winding the jump gave, against the departure
    count: dict                    # the count of the surface kept
    points: int                    # points laid of the surface kept
    kept: Surface | None

    @property
    def holds(self) -> bool:
        """The surface kept is held by the criterion."""
        return self.origin is not None and criterion.holds(self.count)


@dataclass(frozen=True)
class Operations:
    """What a chain does at each jump, for one side of one seed."""
    jump: Callable[[Surface], growth.Jump]
    relaunch: Callable[[np.ndarray, np.ndarray], growth.Grown]
    regrow: Callable[[Surface, np.ndarray, np.ndarray], growth.Grown] | None
    count: Callable[[Surface, Surface | None], dict]


def relaunch_seed(winding: Surface) -> tuple[np.ndarray, np.ndarray] | None:
    """The point laid of the winding, with a known normal, nearest the barycentre of its laid points, and its normal; None if
    there is none."""
    point_normals, has_normal = normals(winding.points, winding.valid)
    laid = winding.valid & has_normal
    if not laid.any():
        return None
    points = winding.points[laid]
    k = int(np.argmin(np.linalg.norm(points - points.mean(axis=0), axis=1)))
    return points[k], point_normals[laid][k]


def grow_chain(start: Surface, operations: Operations, jumps: int = JUMPS) -> list[Link]:
    """Up to `jumps` jumps from `start`. Each takes the winding the jump gives; if the criterion holds it against the surface the
    jump leaves, it is kept, grown again if a regrowth is given, and the regrowth kept in its place if it is held too;
    otherwise the surface is relaunched from the winding's seed and that is kept, held or not. A winding with nothing laid, or
    a relaunch with nothing laid, ends the chain."""
    surface = start
    chain: list[Link] = []
    for _ in range(jumps):
        jump = operations.jump(surface)
        departure = surface
        winding = jump.surface
        winding_count = operations.count(departure, winding)
        if winding.valid.any() and criterion.holds(winding_count):
            kept, count, origin = winding, winding_count, FROM_THE_WINDING
            seed = relaunch_seed(winding) if operations.regrow is not None else None
            if seed is not None:
                regrown = operations.regrow(winding, *seed).surface
                regrown_count = operations.count(departure, regrown)
                if regrown.valid.any() and criterion.holds(regrown_count):
                    kept, count, origin = regrown, regrown_count, FROM_THE_REGROWTH
            chain.append(Link(jump, departure, origin, winding_count, count, int(kept.valid.sum()), kept))
            surface = kept
            continue
        seed = relaunch_seed(winding) if winding.valid.any() else None
        if seed is None:
            chain.append(Link(jump, departure, None, winding_count, criterion.summarise(None), 0, None))
            break
        relaunched = operations.relaunch(*seed).surface
        count = operations.count(departure, relaunched)
        chain.append(Link(jump, departure, FROM_A_RELAUNCH, winding_count, count, int(relaunched.valid.sum()), relaunched))
        if not relaunched.valid.any():
            break
        surface = relaunched
    return chain


def held_in_a_row(chain: list[Link]) -> int:
    """How many jumps in a row, from the first, are held."""
    held = 0
    for link in chain:
        if not link.holds:
            break
        held += 1
    return held


def operations_for(read_values: ReadValues, scale: growth.Scale, side: float, regrowth: bool = True,
                   margin: int | None = MARGIN, lateral: float | None = None) -> Operations:
    """The operations of a chain on the prediction `read_values` at `scale`, on `side` (+1 or -1) of the surface: the jump
    and the relaunch as `growth` gives them, the regrowth bounded to `margin` cells (none given: unbounded; `regrowth=False`:
    no regrowth, the mixed chain of `357`), the count at the step of the scale."""
    if lateral is None:
        lateral = criterion.LATERAL_PHERCPARIS4 if scale == growth.PHERCPARIS4 else LATERAL_IN_STEPS * scale.step
    return Operations(
        jump=lambda surface: growth.jump(surface, side, read_values, scale),
        relaunch=lambda point, normal: growth.grow_from_seed(point, normal, read_values, scale),
        regrow=(lambda winding, point, normal: growth.regrow(winding, point, normal, read_values, scale, margin))
        if regrowth else None,
        count=lambda departure, arrival: criterion.count_and_summarise(departure, arrival, read_values, scale.step, lateral))
