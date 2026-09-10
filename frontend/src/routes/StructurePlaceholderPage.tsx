import { useTranslation } from "react-i18next";
import { useParams } from "react-router-dom";

/**
 * Stub landing spot for CorridorMap marker clicks. The real structure
 * detail page is out of scope for this task (same as PilePlanView).
 */
export function StructurePlaceholderPage() {
  const { t } = useTranslation();
  const { structureId } = useParams<{ structureId: string }>();
  return <p className="p-8">{t("structure.placeholder", { structureId })}</p>;
}
