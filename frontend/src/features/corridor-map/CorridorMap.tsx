import "leaflet/dist/leaflet.css";
import "leaflet.markercluster/dist/MarkerCluster.css";
import "leaflet.markercluster/dist/MarkerCluster.Default.css";
import "./corridor-map.css";

import { MapContainer, TileLayer } from "react-leaflet";
import { useTranslation } from "react-i18next";
import { useNavigate } from "react-router-dom";

import { ClusterLayer } from "./ClusterLayer";
import { groupPilesByCap } from "./grouping";
import { usePackagePiles } from "./usePackagePiles";

const ESRI_WORLD_IMAGERY_URL =
  "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}";
const ESRI_ATTRIBUTION =
  "Tiles &copy; Esri &mdash; Source: Esri, Maxar, Earthstar Geographics, and the GIS User Community";

const DEFAULT_ZOOM = 13;

interface CorridorMapProps {
  packageId: string;
}

/**
 * The corridor map (Decision D1: the map is the primary navigation
 * surface, not a feature). Renders one clustered marker per pile cap,
 * positioned at the centroid of that cap's piles — see D2 for why this
 * is pile-cap level, not per-pile (a pile is sub-pixel at corridor zoom).
 */
export function CorridorMap({ packageId }: CorridorMapProps) {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { data, isLoading, isError } = usePackagePiles(packageId);

  if (isLoading) {
    return <p>{t("corridorMap.loading")}</p>;
  }

  if (isError) {
    return <p role="alert">{t("corridorMap.error")}</p>;
  }

  if (!data || data.piles.length === 0) {
    return <p>{t("corridorMap.empty")}</p>;
  }

  const groups = groupPilesByCap(data.piles, data.package.crs_epsg);

  return (
    <MapContainer center={groups[0].centroid} zoom={DEFAULT_ZOOM} className="h-full w-full">
      <TileLayer url={ESRI_WORLD_IMAGERY_URL} attribution={ESRI_ATTRIBUTION} />
      <ClusterLayer
        groups={groups}
        onSelect={(structureId) => navigate(`/structures/${structureId}`)}
      />
    </MapContainer>
  );
}
