import { useTranslation } from "react-i18next";

import "./pile-plan-view.css";

import { computeViewBox, toPlanPoints } from "./planGeometry";
import type { PlanInputPile } from "./planGeometry";

interface PilePlanViewProps {
  /** A single pile cap's piles — 3, 4, 6, 9, or any other count. No
   * special-casing by count or by cap_type ("straddle" or otherwise) is
   * needed here; geometry is derived entirely from what's passed in
   * (Decision D3). */
  piles: PlanInputPile[];
  /** Package.chainage_bearing, in degrees. */
  chainageBearing: number;
  onPileClick?: (pileId: string) => void;
}

/**
 * Plain-SVG schematic plan of one pile cap (Decision D2) — normalises
 * pile coordinates to the cap's own local origin and rotates them to the
 * package's chainage bearing so the drawing matches the paper working
 * drawing. Deliberately does not use Leaflet; see CorridorMap for the
 * georeferenced corridor-level view.
 */
export function PilePlanView({ piles, chainageBearing, onPileClick }: PilePlanViewProps) {
  const { t } = useTranslation();

  if (piles.length === 0) {
    return <p className="pile-plan-view-empty">{t("pilePlanView.empty")}</p>;
  }

  const points = toPlanPoints(piles, chainageBearing);
  const viewBox = computeViewBox(points);

  return (
    <svg
      className="pile-plan-view"
      viewBox={`${viewBox.minX} ${viewBox.minY} ${viewBox.width} ${viewBox.height}`}
      role="img"
      aria-label={t("pilePlanView.ariaLabel")}
    >
      {points.map((point) => (
        <g
          key={point.pileId}
          className="pile-plan-view-pile"
          role={onPileClick ? "button" : undefined}
          tabIndex={onPileClick ? 0 : undefined}
          onClick={onPileClick ? () => onPileClick(point.pileId) : undefined}
          onKeyDown={
            onPileClick
              ? (event) => {
                  if (event.key === "Enter" || event.key === " ") {
                    event.preventDefault();
                    onPileClick(point.pileId);
                  }
                }
              : undefined
          }
        >
          <circle
            cx={point.x}
            cy={point.y}
            r={point.radius}
            vectorEffect="non-scaling-stroke"
          />
          <text x={point.x} y={point.y}>
            {point.label}
          </text>
        </g>
      ))}
    </svg>
  );
}
