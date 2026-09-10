export interface PlanInputPile {
  id: string;
  label: string;
  e: number;
  n: number;
  diameterMm: number;
}

export interface PlanPoint {
  pileId: string;
  label: string;
  x: number;
  y: number;
  radius: number;
}

export interface ViewBox {
  minX: number;
  minY: number;
  width: number;
  height: number;
}

/**
 * Local drawing origin: the centroid of the cap's pile positions. Works
 * identically whether the piles form one cluster or a straddle cap's two —
 * a centroid doesn't care how its inputs are distributed, so nothing here
 * needs to know about straddle caps at all (Decision D3).
 */
export function computeLocalOrigin(piles: PlanInputPile[]): { e0: number; n0: number } {
  const e0 = piles.reduce((sum, p) => sum + p.e, 0) / piles.length;
  const n0 = piles.reduce((sum, p) => sum + p.n, 0) / piles.length;
  return { e0, n0 };
}

/**
 * Translates each pile to the local origin and rotates so the package's
 * chainage_bearing direction points toward the top of the SVG — a
 * "north-up" map convention pointed at the alignment instead of true
 * north. (docs/domain.md's chainage section says the drawing must match
 * the paper working drawing's orientation but doesn't fix a screen
 * direction on its own; this was confirmed with the project team.)
 *
 * chainage_bearing is a compass bearing in degrees (0 = north/+n axis,
 * clockwise positive), so its direction vector in (e, n) space is
 * (sin θ, cos θ). Rotating by θ itself carries that vector onto the
 * local +y (north-like) axis — this is a proper rotation, not a mirror,
 * which matters: reflecting the plan would flip the chirality of an
 * asymmetric cap relative to the paper drawing. SVG y grows downward, so
 * the final flip to screen space negates y after rotating.
 */
export function toPlanPoints(piles: PlanInputPile[], chainageBearingDeg: number): PlanPoint[] {
  if (piles.length === 0) {
    return [];
  }

  const { e0, n0 } = computeLocalOrigin(piles);
  const theta = (chainageBearingDeg * Math.PI) / 180;
  const cos = Math.cos(theta);
  const sin = Math.sin(theta);

  return piles.map((pile) => {
    const dx = pile.e - e0;
    const dy = pile.n - n0;
    const rx = dx * cos - dy * sin;
    const ry = dx * sin + dy * cos;
    return {
      pileId: pile.id,
      label: pile.label,
      x: rx,
      y: -ry,
      radius: pile.diameterMm / 2000,
    };
  });
}

/**
 * Bounding box over the rotated points (each padded by its own radius),
 * plus a fixed margin so labels aren't clipped at the edge. Computed from
 * whatever points actually came in, so a straddle cap's wider footprint
 * just produces a wider box — no branch needed for cap shape or count.
 */
export function computeViewBox(points: PlanPoint[], paddingM = 1): ViewBox {
  if (points.length === 0) {
    return { minX: -paddingM, minY: -paddingM, width: paddingM * 2, height: paddingM * 2 };
  }

  const minX = Math.min(...points.map((p) => p.x - p.radius)) - paddingM;
  const maxX = Math.max(...points.map((p) => p.x + p.radius)) + paddingM;
  const minY = Math.min(...points.map((p) => p.y - p.radius)) - paddingM;
  const maxY = Math.max(...points.map((p) => p.y + p.radius)) + paddingM;

  return { minX, minY, width: maxX - minX, height: maxY - minY };
}
