import { useState } from "react";
import { useTranslation } from "react-i18next";

import { usePackagePiles } from "../corridor-map/usePackagePiles";
import { PilePlanView } from "../pile-plan/PilePlanView";
import type { PlanInputPile } from "../pile-plan/planGeometry";

interface StructureDetailProps {
  packageId: string;
  structureId: string;
}

/**
 * The landing spot for a CorridorMap marker click: one pier, one plot.
 * Fetches the same package-wide pile list CorridorMap does (shared
 * TanStack Query cache — same query key, no duplicate request) and
 * filters to this structure. All of the structure's piles go into a
 * single PilePlanView — a straddle pier's two pile-cap groups (Decision
 * D3) are two DB rows but still one pier, so they render as one wide
 * plot with a gap between the groups, not two separate plots. The
 * geometry (centroid + bounding box) already handles that with no
 * special-casing; grouping by pile cap instead of by structure was the
 * bug, not the geometry.
 */
export function StructureDetail({ packageId, structureId }: StructureDetailProps) {
  const { t } = useTranslation();
  const { data, isLoading, isError } = usePackagePiles(packageId);
  const [selectedPileId, setSelectedPileId] = useState<string | null>(null);

  if (isLoading) {
    return <p className="p-8">{t("structureDetail.loading")}</p>;
  }

  if (isError) {
    return (
      <p className="p-8" role="alert">
        {t("structureDetail.error")}
      </p>
    );
  }

  const structurePiles = data?.piles.filter((pile) => pile.structure.id === structureId) ?? [];

  if (structurePiles.length === 0) {
    return <p className="p-8">{t("structureDetail.empty")}</p>;
  }

  const chainageBearing = Number(data!.package.chainage_bearing);
  const structureRef = structurePiles[0].structure.ref;
  const planPiles: PlanInputPile[] = structurePiles.map((pile) => ({
    id: pile.id,
    label: pile.label,
    e: Number(pile.coordinates.e),
    n: Number(pile.coordinates.n),
    diameterMm: pile.diameter_mm,
  }));
  const selectedPile = structurePiles.find((pile) => pile.id === selectedPileId) ?? null;

  return (
    <div className="flex h-screen w-screen">
      <div className="flex flex-1 flex-col items-center gap-2 overflow-auto p-4">
        <h2 className="self-start text-sm font-semibold text-foreground">
          {t("structureDetail.heading", { ref: structureRef })}
        </h2>
        <div className="aspect-square w-full max-w-2xl">
          <PilePlanView
            piles={planPiles}
            chainageBearing={chainageBearing}
            onPileClick={setSelectedPileId}
          />
        </div>
      </div>
      <aside className="w-64 shrink-0 border-l border-border p-4">
        {selectedPile ? (
          <p className="text-foreground">
            {t("structureDetail.selectedPile", {
              pileNo: selectedPile.pile_no,
              label: selectedPile.label,
            })}
          </p>
        ) : (
          <p className="text-muted">{t("structureDetail.noPileSelected")}</p>
        )}
      </aside>
    </div>
  );
}
