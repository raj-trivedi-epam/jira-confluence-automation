import { useState } from "react";

interface GeneratedReport {
  id: string;
  generatedAt: string;
  canonicalPath: string;
  content: string;
}

interface RunRecord {
  id: string;
  status: "success" | "failed";
  startedAt: string;
  endedAt: string;
  reportId?: string;
  reportPath?: string;
}

type GenerationResponse =
  | { data: { run: RunRecord; report: GeneratedReport } }
  | { error: { code: string; message: string } };

export default function App() {
  const [isGenerating, setIsGenerating] = useState(false);
  const [report, setReport] = useState<GeneratedReport | null>(null);
  const [error, setError] = useState<string | null>(null);

  const generateReport = async () => {
    setIsGenerating(true);
    setError(null);
    setReport(null);

    try {
      const response = await fetch("http://127.0.0.1:3001/api/runs", {
        method: "POST",
      });
      const payload: GenerationResponse = await response.json();

      if (!response.ok || !("data" in payload)) {
        throw new Error(
          "error" in payload
            ? payload.error.message
            : `Report generation failed (${response.status}).`,
        );
      }

      setReport(payload.data.report);
    } catch (generationError) {
      setError(
        generationError instanceof Error
          ? generationError.message
          : "An unexpected error prevented report generation.",
      );
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <main
      style={{
        minHeight: "100vh",
        display: "grid",
        placeItems: "center",
        fontFamily: "system-ui, sans-serif",
        background: "#f6f7f9",
        color: "#172b4d",
      }}
    >
      <section
        style={{
          width: "min(680px, calc(100vw - 48px))",
          padding: "32px",
          border: "1px solid #dfe1e6",
          borderRadius: "12px",
          background: "#fff",
          boxShadow: "0 8px 24px rgba(9, 30, 66, 0.08)",
        }}
      >
        <p style={{ margin: 0, color: "#505f79", fontWeight: 600 }}>
          Prototype
        </p>
        <h1 style={{ marginBottom: "8px" }}>Jira/Confluence Automation</h1>
        <p style={{ color: "#505f79" }}>
          Demo mode only — no live Jira data is connected. Generated demo
          reports are not factual project updates and must not be shared.
        </p>
        <button
          type="button"
          onClick={generateReport}
          disabled={isGenerating}
          style={{
            border: 0,
            borderRadius: "6px",
            padding: "10px 14px",
            background: isGenerating ? "#f1f2f4" : "#dfe1e6",
            color: "#172b4d",
            fontWeight: 600,
            cursor: isGenerating ? "wait" : "pointer",
          }}
        >
          {isGenerating ? "Generating…" : "Generate report"}
        </button>
        {error && (
          <p role="alert" style={{ color: "#ae2e24" }}>
            {error}
          </p>
        )}
        {report && (
          <section aria-labelledby="generated-report-title">
            <p role="status" style={{ color: "#216e4e", fontWeight: 600 }}>
              Demo report generated successfully.
            </p>
            <h2 id="generated-report-title">Generated report</h2>
            <p>
              Saved to <code>{report.canonicalPath}</code>
            </p>
            <pre
              style={{
                padding: "16px",
                borderRadius: "6px",
                background: "#f6f7f9",
                whiteSpace: "pre-wrap",
              }}
            >
              {report.content}
            </pre>
          </section>
        )}
      </section>
    </main>
  );
}