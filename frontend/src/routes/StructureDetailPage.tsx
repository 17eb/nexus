import { useParams } from "react-router-dom";

import { StructureDetail } from "../features/structure-detail/StructureDetail";

export function StructureDetailPage() {
  const { packageId, structureId } = useParams<{ packageId: string; structureId: string }>();
  if (!packageId || !structureId) {
    return null;
  }
  return <StructureDetail packageId={packageId} structureId={structureId} />;
}
