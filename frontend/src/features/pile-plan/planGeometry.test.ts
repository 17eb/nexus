import { describe, expect, it } from "vitest";

import { computeLocalOrigin, computeViewBox, toPlanPoints } from "./planGeometry";
import type { PlanInputPile } from "./planGeometry";

function pile(overrides: Partial<PlanInputPile> = {}): PlanInputPile {
  return {
    id: "pile-id",
    label: "A",
    e: 498000,
    n: 1557000,
    diameterMm: 1500,
    ...overrides,
  };
}

describe("computeLocalOrigin", () => {
  it("is the centroid of the pile positions", () => {
    const piles = [
      pile({ e: 498000, n: 1557000 }),
      pile({ e: 498004, n: 1557000 }),
      pile({ e: 498000, n: 1557004 }),
      pile({ e: 498004, n: 1557004 }),
    ];

    expect(computeLocalOrigin(piles)).toEqual({ e0: 498002, n0: 1557002 });
  });

  it("doesn't care whether the piles form one cluster or two (straddle caps)", () => {
    // Two 4.5m-square groups 16m apart, e.g. a straddle cap's two sides.
    const groupA = [
      pile({ id: "a1", e: 498000, n: 1557000 }),
      pile({ id: "a2", e: 498004.5, n: 1557000 }),
      pile({ id: "a3", e: 498000, n: 1557004.5 }),
      pile({ id: "a4", e: 498004.5, n: 1557004.5 }),
    ];
    const groupB = groupA.map((p, i) => ({ ...p, id: `b${i + 1}`, e: p.e + 16 }));

    // No special-casing required: the same centroid formula applies to
    // the combined straddle-cap pile list as to a single cluster above.
    const origin = computeLocalOrigin([...groupA, ...groupB]);
    expect(origin.e0).toBeCloseTo(498010.25, 6);
    expect(origin.n0).toBeCloseTo(1557002.25, 6);
  });
});

describe("toPlanPoints", () => {
  it("returns an empty array for an empty pile list", () => {
    expect(toPlanPoints([], 180)).toEqual([]);
  });

  it("places a pile south of centroid near the top of the SVG when bearing is 180 (southbound)", () => {
    // SCRP 4/5/6's real chainage_bearing (docs/domain.md: increasing
    // chainage is southbound). A pile due south of centroid (smaller n)
    // sits in the direction of increasing chainage, which must render
    // toward the top of the SVG (smaller y), not the bottom.
    const piles = [
      pile({ id: "north", e: 498000, n: 1557004 }),
      pile({ id: "south", e: 498000, n: 1557000 }),
    ];
    const centroid_n = 1557002;
    void centroid_n;

    const points = toPlanPoints(piles, 180);
    const north = points.find((p) => p.pileId === "north")!;
    const south = points.find((p) => p.pileId === "south")!;

    expect(south.y).toBeLessThan(north.y);
  });

  it("places an east pile to the right when bearing is 0 (north-up)", () => {
    const piles = [
      pile({ id: "west", e: 498000, n: 1557000 }),
      pile({ id: "east", e: 498004, n: 1557000 }),
    ];

    const points = toPlanPoints(piles, 0);
    const west = points.find((p) => p.pileId === "west")!;
    const east = points.find((p) => p.pileId === "east")!;

    expect(east.x).toBeGreaterThan(west.x);
    // North-up: no north/south offset here, so y should be identical.
    expect(east.y).toBeCloseTo(west.y, 10);
  });

  it("rotates rather than mirrors, preserving an asymmetric cap's chirality", () => {
    // An L-shaped arrangement: east pile and north pile, both offset from
    // a shared corner. A reflection would swap which side the east pile
    // ends up on relative to the north pile; a proper rotation preserves
    // their relative handedness for any bearing.
    const piles = [
      pile({ id: "corner", e: 498000, n: 1557000 }),
      pile({ id: "east", e: 498004, n: 1557000 }),
      pile({ id: "north", e: 498000, n: 1557004 }),
    ];

    for (const bearing of [0, 45, 90, 180, 270]) {
      const points = toPlanPoints(piles, bearing);
      const corner = points.find((p) => p.pileId === "corner")!;
      const east = points.find((p) => p.pileId === "east")!;
      const north = points.find((p) => p.pileId === "north")!;

      // Cross product of (east - corner) and (north - corner) in SVG
      // space must keep a consistent sign across all bearings — a proper
      // rotation preserves orientation, a mirror would flip it.
      const cross =
        (east.x - corner.x) * (north.y - corner.y) -
        (east.y - corner.y) * (north.x - corner.x);
      expect(cross).toBeLessThan(0);
    }
  });

  it("scales radius from diameter_mm", () => {
    const points = toPlanPoints([pile({ diameterMm: 1500 })], 0);
    expect(points[0].radius).toBeCloseTo(0.75, 10);
  });
});

describe("computeViewBox", () => {
  it("returns a fixed small box for an empty point list", () => {
    expect(computeViewBox([], 1)).toEqual({ minX: -1, minY: -1, width: 2, height: 2 });
  });

  it("bounds the box by point position plus radius plus padding", () => {
    const points = [
      { pileId: "a", label: "A", x: -2, y: -1, radius: 0.75 },
      { pileId: "b", label: "B", x: 2, y: 1, radius: 0.75 },
    ];

    const box = computeViewBox(points, 1);

    expect(box.minX).toBeCloseTo(-2 - 0.75 - 1, 10);
    expect(box.minY).toBeCloseTo(-1 - 0.75 - 1, 10);
    expect(box.width).toBeCloseTo((2 + 0.75 + 1) - (-2 - 0.75 - 1), 10);
    expect(box.height).toBeCloseTo((1 + 0.75 + 1) - (-1 - 0.75 - 1), 10);
  });

  it("handles a straddle cap's wide, non-square footprint with no special-casing", () => {
    // Two 4-pile clusters 16m apart — the box must simply be wide, there
    // is no branch anywhere for "this is a straddle cap".
    const points = [
      { pileId: "a1", label: "A", x: -8, y: -1, radius: 0.75 },
      { pileId: "a2", label: "B", x: -4, y: 1, radius: 0.75 },
      { pileId: "b1", label: "C", x: 4, y: -1, radius: 0.75 },
      { pileId: "b2", label: "D", x: 8, y: 1, radius: 0.75 },
    ];

    const box = computeViewBox(points, 1);

    expect(box.width).toBeGreaterThan(box.height * 3);
  });
});
