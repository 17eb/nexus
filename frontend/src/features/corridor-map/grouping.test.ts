import { describe, expect, it } from "vitest";

import { groupPilesByCap } from "./grouping";
import { projectToWgs84 } from "./projection";
import type { PackagePilesResponse } from "./usePackagePiles";

const EPSG = 3123;

function pile(
  overrides: Partial<PackagePilesResponse["piles"][number]> = {},
): PackagePilesResponse["piles"][number] {
  return {
    id: "pile-id",
    pile_no: "P-1",
    label: "A",
    diameter_mm: 1500,
    pile_cap: { id: "cap-1", ref: "1", cap_type: "standard" },
    structure: { id: "structure-1", ref: "PR01", kind: "viaduct" },
    coordinates: { source: "design", e: "498000.000", n: "1557000.000" },
    ...overrides,
  };
}

describe("groupPilesByCap", () => {
  it("collapses piles sharing a pile_cap.id into one group at their projected centroid", () => {
    const piles = [
      pile({ id: "p1", label: "A", coordinates: { source: "design", e: "498000", n: "1557000" } }),
      pile({ id: "p2", label: "B", coordinates: { source: "design", e: "498004.5", n: "1557000" } }),
    ];

    const groups = groupPilesByCap(piles, EPSG);

    expect(groups).toHaveLength(1);
    expect(groups[0].pileCapId).toBe("cap-1");
    expect(groups[0].pileCount).toBe(2);
    // Centroid must equal the projection of the *projected-space* average,
    // not an average of independently-transformed lat/lngs.
    const expectedCentroid = projectToWgs84(EPSG, 498002.25, 1557000);
    expect(groups[0].centroid[0]).toBeCloseTo(expectedCentroid[0], 10);
    expect(groups[0].centroid[1]).toBeCloseTo(expectedCentroid[1], 10);
  });

  it("keeps piles in different pile caps as separate groups", () => {
    const piles = [
      pile({ id: "p1", pile_cap: { id: "cap-1", ref: "1", cap_type: "standard" } }),
      pile({
        id: "p2",
        pile_cap: { id: "cap-2", ref: "2", cap_type: "standard" },
        structure: { id: "structure-2", ref: "PR02", kind: "viaduct" },
      }),
    ];

    const groups = groupPilesByCap(piles, EPSG);

    expect(groups.map((g) => g.pileCapId).sort()).toEqual(["cap-1", "cap-2"]);
  });
});
