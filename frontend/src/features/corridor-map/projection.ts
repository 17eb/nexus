import proj4 from "proj4";

/**
 * proj4 definitions keyed by EPSG code. Package.crs_epsg (docs/domain.md
 * "Coordinates") is per-package and must never be assumed — this table
 * is looked up by whatever code the API returns, never defaulted.
 */
const PROJ4_DEFS: Record<number, string> = {
  // PRS92 / Philippines zone 3 — central meridian 121°E. Not the same
  // as EPSG:3121 (zone 1, central meridian 117°E), which is the wrong
  // zone for the SCRP corridor despite the similar code.
  3123:
    "+proj=tmerc +lat_0=0 +lon_0=121 +k=0.99995 +x_0=500000 +y_0=0 " +
    "+ellps=clrk66 +towgs84=-127.62,-67.24,-47.04,3.068,-4.903,-1.578,-1.06 " +
    "+units=m +no_defs",
};

export class UnknownEpsgError extends Error {
  constructor(epsg: number) {
    super(`No proj4 definition registered for EPSG:${epsg}`);
    this.name = "UnknownEpsgError";
  }
}

function ensureRegistered(epsg: number): string {
  const def = PROJ4_DEFS[epsg];
  if (!def) {
    throw new UnknownEpsgError(epsg);
  }
  const name = `EPSG:${epsg}`;
  if (!proj4.defs(name)) {
    proj4.defs(name, def);
  }
  return name;
}

/** Projects a single easting/northing pair (metres, package CRS) to WGS84 [lat, lng]. */
export function projectToWgs84(epsg: number, e: number, n: number): [number, number] {
  const name = ensureRegistered(epsg);
  const [lng, lat] = proj4(name, "WGS84", [e, n]);
  return [lat, lng];
}
