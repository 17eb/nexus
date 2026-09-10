import i18next from "i18next";
import { initReactI18next } from "react-i18next";

import enCommon from "./locales/en/common.json";
import enJaCommon from "./locales/en-ja/common.json";
import enKoCommon from "./locales/en-ko/common.json";
import jaCommon from "./locales/ja/common.json";
import koCommon from "./locales/ko/common.json";

export const SUPPORTED_LOCALES = ["en", "ko", "ja", "en-ko", "en-ja"] as const;
export type SupportedLocale = (typeof SUPPORTED_LOCALES)[number];

void i18next.use(initReactI18next).init({
  fallbackLng: "en",
  supportedLngs: SUPPORTED_LOCALES,
  lng: "en",
  ns: ["common"],
  defaultNS: "common",
  resources: {
    en: { common: enCommon },
    ko: { common: koCommon },
    ja: { common: jaCommon },
    "en-ko": { common: enKoCommon },
    "en-ja": { common: enJaCommon },
  },
  interpolation: {
    escapeValue: false,
  },
});

export default i18next;
