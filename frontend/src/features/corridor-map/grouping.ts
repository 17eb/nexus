import { projectToWgs84 } from "./projection";
import type { PackagePilesResponse } from "./usePackagePiles";

export interface PileCapGroup {
  pileCapId: string;
  pileCapRef: string;
  structureId: string;
  structureRef: string;
  structureKind: string;
  centroid: [number, number];
  pileCount: number;
}

/**
 * Groups piles by pile cap and locates each cap at the centroid of its
 * piles. The average is taken in the package's projected metric CRS
 * (easting/northing) before transforming — averaging already-transformed
 * lat/lngs would be wrong, since degrees-per-metre isn't constant.
 */
export function groupPilesByCap(
  piles: PackagePilesResponse["piles"],
  epsg: number,
): PileCapGroup[] {
  const byCapId = new Map<string, PackagePilesResponse["piles"]>();
  for (const pile of piles) {
    const key = pile.pile_cap.id;
    const bucket = byCapId.get(key);
    if (bucket) {
      bucket.push(pile);
    } else {
      byCapId.set(key, [pile]);
    }
  }

  return [...byCapId.entries()].map(([pileCapId, group]) => {
    const avgE = group.reduce((sum, p) => sum + Number(p.coordinates.e), 0) / group.length;
    const avgN = group.reduce((sum, p) => sum + Number(p.coordinates.n), 0) / group.length;
    const first = group[0];
    return {
      pileCapId,
      pileCapRef: first.pile_cap.ref,
      structureId: first.structure.id,
      structureRef: first.structure.ref,
      structureKind: first.structure.kind,
      centroid: projectToWgs84(epsg, avgE, avgN),
      pileCount: group.length,
    };
  });
}
