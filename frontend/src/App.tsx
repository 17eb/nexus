import { useTranslation } from "react-i18next";

import { SUPPORTED_LOCALES } from "./i18n";
import { useTheme } from "./useTheme";

/**
 * Scaffolding proof-of-wiring only — not a product screen. Confirms
 * i18next, the Tailwind theme tokens and the dark/light class strategy
 * are all connected end to end.
 */
function App() {
  const { t, i18n } = useTranslation();
  const { theme, toggleTheme } = useTheme();

  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-4 bg-background p-8 text-foreground">
      <h1 className="text-2xl font-semibold">{t("app.title")}</h1>

      <div className="flex items-center gap-3">
        <label className="text-sm text-muted" htmlFor="locale">
          Locale
        </label>
        <select
          id="locale"
          className="rounded border border-border bg-surface px-2 py-1 text-sm"
          value={i18n.language}
          onChange={(event) => void i18n.changeLanguage(event.target.value)}
        >
          {SUPPORTED_LOCALES.map((locale) => (
            <option key={locale} value={locale}>
              {locale}
            </option>
          ))}
        </select>
      </div>

      <button
        type="button"
        onClick={toggleTheme}
        className="rounded bg-primary px-4 py-2 text-sm font-medium text-primary-foreground"
      >
        Switch to {theme === "dark" ? "light" : "dark"} theme
      </button>
    </main>
  );
}

export default App;
