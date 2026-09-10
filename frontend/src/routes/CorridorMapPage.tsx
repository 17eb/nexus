import { useParams } from "react-router-dom";

import { CorridorMap } from "../features/corridor-map/CorridorMap";

export function CorridorMapPage() {
  const { packageId } = useParams<{ packageId: string }>();
  if (!packageId) {
    return null;
  }
  return (
    <div className="h-screen w-screen">
      <CorridorMap packageId={packageId} />
    </div>
  );
}
