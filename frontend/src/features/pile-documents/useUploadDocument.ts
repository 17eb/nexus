import { useMutation, useQueryClient } from "@tanstack/react-query";
import axios from "axios";

import { apiClient } from "../../api/client";
import type { PileDocument } from "./usePileDocuments";

interface UploadRequestResponse {
  storage_key: string;
  upload_url: string;
}

export interface UploadDocumentInput {
  docTypeCode: string;
  title: string;
  file: File;
  supersedes?: string;
}

/**
 * The two-step upload flow itself (docs/data-model.md): request a
 * storage_key + upload_url, PUT the file bytes directly to it, then
 * confirm. Extracted as a plain function, separate from the
 * useMutation wrapper below, so it's testable without rendering a React
 * hook — this repo has no jsdom/testing-library and nothing else has
 * needed one yet.
 *
 * The PUT deliberately bypasses `apiClient` — upload_url is already a
 * full path locally, and would be a fully-qualified cross-origin URL
 * once a real S3-compatible backend is wired up, so routing it through
 * apiClient's "/api/v1" baseURL would be wrong either way.
 */
export async function uploadDocument(
  pileId: string,
  { docTypeCode, title, file, supersedes }: UploadDocumentInput,
): Promise<PileDocument> {
  const contentType = file.type || "application/octet-stream";

  const { data: uploadRequest } = await apiClient.post<UploadRequestResponse>(
    "/documents/upload-requests/",
    { pile_id: pileId, doc_type_code: docTypeCode, filename: file.name },
  );

  await axios.put(uploadRequest.upload_url, file, {
    headers: { "Content-Type": contentType },
  });

  const { data: document } = await apiClient.post<PileDocument>("/documents/", {
    pile_id: pileId,
    doc_type_code: docTypeCode,
    title,
    storage_key: uploadRequest.storage_key,
    content_type: contentType,
    supersedes,
  });
  return document;
}

export function useUploadDocument(pileId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (input: UploadDocumentInput) => uploadDocument(pileId, input),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["piles", pileId, "documents"] });
    },
  });
}
