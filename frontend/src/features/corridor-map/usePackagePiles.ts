import { useQuery } from "@tanstack/react-query";

import { apiClient } from "../../api/client";

export interface PackagePilesResponse {
  package: { crs_epsg: number; chainage_bearing: string };
  piles: Array<{
    id: string;
    pile_no: string;
    label: string;
    diameter_mm: number;
    pile_cap: { id: string; ref: string; cap_type: string };
    structure: { id: string; ref: string; kind: string };
    coordinates: { source: "design" | "as_built"; e: string; n: string };
  }>;
}

export function usePackagePiles(packageId: string) {
  return useQuery({
    queryKey: ["packages", packageId, "piles"],
    queryFn: async () => {
      const { data } = await apiClient.get<PackagePilesResponse>(
        `/packages/${packageId}/piles`,
      );
      return data;
    },
  });
}
