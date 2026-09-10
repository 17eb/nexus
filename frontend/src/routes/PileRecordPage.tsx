import { useParams } from "react-router-dom";

import { PileRecord } from "../features/pile-documents/PileRecord";

export function PileRecordPage() {
  const { pileId } = useParams<{ packageId: string; pileId: string }>();
  if (!pileId) {
    return null;
  }
  return <PileRecord pileId={pileId} />;
}
