import { describe, expect, it } from "vitest";

import { UnknownEpsgError, projectToWgs84 } from "./projection";

describe("projectToWgs84", () => {
  it("projects an EPSG:3123 easting/northing onto the SCRP corridor", () => {
    const [lat, lng] = projectToWgs84(3123, 498000, 1557000);

    // Cabuyao, Laguna sits at roughly 14.1-14.3°N, 121.0-121.2°E
    // (docs/domain.md "Coordinates"). A gross mis-projection (e.g. using
    // the wrong zone) would land far outside this range.
    expect(lat).toBeGreaterThan(13.5);
    expect(lat).toBeLessThan(14.5);
    expect(lng).toBeGreaterThan(120.5);
    expect(lng).toBeLessThan(121.5);
  });

  it("throws UnknownEpsgError for an unregistered EPSG code", () => {
    expect(() => projectToWgs84(3121, 498000, 1557000)).toThrow(UnknownEpsgError);
  });
});
