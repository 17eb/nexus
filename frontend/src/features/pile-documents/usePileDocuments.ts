import { useQuery } from "@tanstack/react-query";

import { apiClient } from "../../api/client";

export interface PileDocument {
  id: string;
  title: string;
  content_type: string;
  size_bytes: number;
  uploaded_at: string;
}

export interface PileDocumentsSection {
  doc_type: { code: string; name: string; sort_order: number; requires_revision: boolean };
  documents: PileDocument[];
}

export interface PileDocumentsResponse {
  pile_id: string;
  sections: PileDocumentsSection[];
}

export function usePileDocuments(pileId: string) {
  return useQuery({
    queryKey: ["piles", pileId, "documents"],
    queryFn: async () => {
      const { data } = await apiClient.get<PileDocumentsResponse>(`/piles/${pileId}/documents/`);
      return data;
    },
  });
}
