import L from "leaflet";
import "leaflet.markercluster";
import { useEffect } from "react";
import { useMap } from "react-leaflet";

import type { PileCapGroup } from "./grouping";

function pileCapIcon(group: PileCapGroup) {
  return L.divIcon({
    className: group.hasDocuments
      ? "corridor-map-marker corridor-map-marker--has-docs"
      : "corridor-map-marker",
    iconSize: [24, 24],
  });
}

function clusterIcon(cluster: L.MarkerCluster) {
  return L.divIcon({
    html: `<span>${cluster.getChildCount()}</span>`,
    className: "corridor-map-cluster",
    iconSize: [40, 40],
  });
}

interface ClusterLayerProps {
  groups: PileCapGroup[];
  onSelect: (structureId: string) => void;
}

/**
 * react-leaflet has no first-class marker-clustering component compatible
 * with the react-leaflet@4 / React 18 pairing this repo is pinned to, so
 * leaflet.markercluster is wired in imperatively via useMap().
 */
export function ClusterLayer({ groups, onSelect }: ClusterLayerProps) {
  const map = useMap();

  useEffect(() => {
    const clusterGroup = L.markerClusterGroup({ iconCreateFunction: clusterIcon });

    for (const group of groups) {
      const marker = L.marker(group.centroid, { icon: pileCapIcon(group) });
      marker.on("click", () => onSelect(group.structureId));
      marker.bindTooltip(`${group.structureRef} / ${group.pileCapRef}`);
      clusterGroup.addLayer(marker);
    }

    map.addLayer(clusterGroup);
    return () => {
      map.removeLayer(clusterGroup);
    };
  }, [map, groups, onSelect]);

  return null;
}
