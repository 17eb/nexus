import axios from "axios";
import { describe, expect, it, vi } from "vitest";

import { apiClient } from "../../api/client";
import { uploadDocument } from "./useUploadDocument";

vi.mock("../../api/client", () => ({
  apiClient: { post: vi.fn() },
}));

vi.mock("axios", () => ({
  default: { put: vi.fn() },
}));

describe("uploadDocument", () => {
  it("requests an upload URL, PUTs the file bytes directly to it, then confirms", async () => {
    const file = new File(["hello"], "drawing.pdf", { type: "application/pdf" });
    vi.mocked(apiClient.post)
      .mockResolvedValueOnce({
        data: { storage_key: "documents/1/a.pdf", upload_url: "/api/v1/documents/local-storage/tok/" },
      } as never)
      .mockResolvedValueOnce({ data: { id: "doc-1", title: "drawing.pdf" } } as never);
    vi.mocked(axios.put).mockResolvedValueOnce({ status: 204 } as never);

    const result = await uploadDocument("pile-1", {
      docTypeCode: "WORKING_DRAWINGS",
      title: "drawing.pdf",
      file,
    });

    expect(apiClient.post).toHaveBeenNthCalledWith(1, "/documents/upload-requests/", {
      pile_id: "pile-1",
      doc_type_code: "WORKING_DRAWINGS",
      filename: "drawing.pdf",
    });
    // Never through apiClient (would double up the "/api/v1" prefix
    // locally, and would be flatly wrong for a real cross-origin S3 URL).
    expect(axios.put).toHaveBeenCalledWith("/api/v1/documents/local-storage/tok/", file, {
      headers: { "Content-Type": "application/pdf" },
    });
    expect(apiClient.post).toHaveBeenNthCalledWith(2, "/documents/", {
      pile_id: "pile-1",
      doc_type_code: "WORKING_DRAWINGS",
      title: "drawing.pdf",
      storage_key: "documents/1/a.pdf",
      content_type: "application/pdf",
      supersedes: undefined,
    });
    expect(result).toEqual({ id: "doc-1", title: "drawing.pdf" });
  });

  it("defaults content type to application/octet-stream when the File has none", async () => {
    const file = new File(["hello"], "notes.bin", { type: "" });
    vi.mocked(apiClient.post)
      .mockResolvedValueOnce({ data: { storage_key: "documents/1/b.bin", upload_url: "/x/" } } as never)
      .mockResolvedValueOnce({ data: { id: "doc-2" } } as never);
    vi.mocked(axios.put).mockResolvedValueOnce({ status: 204 } as never);

    await uploadDocument("pile-1", { docTypeCode: "WORKING_DRAWINGS", title: "notes.bin", file });

    expect(axios.put).toHaveBeenCalledWith("/x/", file, {
      headers: { "Content-Type": "application/octet-stream" },
    });
  });

  it("passes supersedes through to the confirm call when provided", async () => {
    const file = new File(["hello"], "rev-b.pdf", { type: "application/pdf" });
    vi.mocked(apiClient.post)
      .mockResolvedValueOnce({
        data: { storage_key: "documents/1/c.pdf", upload_url: "/x/" },
      } as never)
      .mockResolvedValueOnce({ data: { id: "doc-3" } } as never);
    vi.mocked(axios.put).mockResolvedValueOnce({ status: 204 } as never);

    await uploadDocument("pile-1", {
      docTypeCode: "WORKING_DRAWINGS",
      title: "rev-b.pdf",
      file,
      supersedes: "doc-old",
    });

    expect(apiClient.post).toHaveBeenNthCalledWith(
      2,
      "/documents/",
      expect.objectContaining({ supersedes: "doc-old" }),
    );
  });
});
