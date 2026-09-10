import { useState } from "react";
import { useTranslation } from "react-i18next";

import "./pile-record.css";

import { usePileDocuments } from "./usePileDocuments";
import { useUploadDocument } from "./useUploadDocument";

interface PileRecordProps {
  pileId: string;
}

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

/**
 * The nine (or however many) document sections for one pile
 * (docs/domain.md), each with an empty state, a file upload control,
 * and a download link per current document.
 */
export function PileRecord({ pileId }: PileRecordProps) {
  const { t } = useTranslation();
  const { data, isLoading, isError } = usePileDocuments(pileId);
  const uploadDocument = useUploadDocument(pileId);
  const [uploadingDocTypeCode, setUploadingDocTypeCode] = useState<string | null>(null);
  const [uploadError, setUploadError] = useState<string | null>(null);

  if (isLoading) {
    return <p className="p-8">{t("pileRecord.loading")}</p>;
  }

  if (isError) {
    return (
      <p className="p-8" role="alert">
        {t("pileRecord.error")}
      </p>
    );
  }

  if (!data) {
    return null;
  }

  async function handleFileSelected(docTypeCode: string, file: File) {
    setUploadingDocTypeCode(docTypeCode);
    setUploadError(null);
    try {
      await uploadDocument.mutateAsync({ docTypeCode, title: file.name, file });
    } catch {
      setUploadError(t("pileRecord.uploadError"));
    } finally {
      setUploadingDocTypeCode(null);
    }
  }

  return (
    <div className="p-8">
      <h1 className="mb-6 text-lg font-semibold text-foreground">{t("pileRecord.heading")}</h1>
      {uploadError && (
        <p role="alert" className="mb-4 text-danger">
          {uploadError}
        </p>
      )}
      <div className="flex flex-col gap-4">
        {data.sections.map((section) => {
          const isUploading = uploadingDocTypeCode === section.doc_type.code;
          return (
            <section key={section.doc_type.code} className="pile-record-section">
              <h2 className="text-sm font-semibold text-foreground">{section.doc_type.name}</h2>
              {section.documents.length === 0 ? (
                <p className="text-muted">{t("pileRecord.empty")}</p>
              ) : (
                <ul className="flex flex-col gap-1">
                  {section.documents.map((document) => (
                    <li key={document.id} className="flex items-center justify-between gap-2">
                      <span className="text-foreground">
                        {document.title}{" "}
                        <span className="text-muted">({formatSize(document.size_bytes)})</span>
                      </span>
                      <a
                        className="text-primary underline"
                        href={`/api/v1/documents/${document.id}/download/`}
                      >
                        {t("pileRecord.download")}
                      </a>
                    </li>
                  ))}
                </ul>
              )}
              <label className="pile-record-upload-label" aria-disabled={isUploading}>
                <input
                  type="file"
                  className="pile-record-upload-input"
                  disabled={isUploading}
                  onChange={(event) => {
                    const file = event.target.files?.[0];
                    event.target.value = "";
                    if (file) {
                      void handleFileSelected(section.doc_type.code, file);
                    }
                  }}
                />
                {isUploading ? t("pileRecord.uploading") : t("pileRecord.upload")}
              </label>
            </section>
          );
        })}
      </div>
    </div>
  );
}
