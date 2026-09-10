import { ChangeEvent, FormEvent, useState } from "react";

type NumericColumn = {
  minimum: number;
  maximum: number;
};

type AnalysisResult = {
  filename: string;
  total_records: number;
  column_count: number;
  columns: string[];
  missing_values: number;
  numeric_columns: Record<string, NumericColumn>;
};

const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

function App() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<string>("");
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  function handleFileChange(event: ChangeEvent<HTMLInputElement>) {
    setSelectedFile(event.target.files?.[0] ?? null);
    setResult(null);
    setError("");
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selectedFile) {
      setError("Choose a CSV file first.");
      return;
    }

    setIsAnalyzing(true);
    setError("");
    setResult(null);

    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      const response = await fetch(`${API_URL}/api/v1/analyze`, {
        method: "POST",
        body: formData,
      });
      const payload = await response.json();
      if (!response.ok) {
        throw new Error(payload.detail ?? "The file could not be analyzed.");
      }
      setResult(payload as AnalysisResult);
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "The request failed.");
    } finally {
      setIsAnalyzing(false);
    }
  }

  return (
    <main className="page-shell">
      <section className="intro-panel">
        <p className="eyebrow">AWS File Processing Lab · Phase 1</p>
        <h1>Make a CSV tell you something useful.</h1>
        <p className="intro-copy">
          Upload one bounded CSV and get a clear first look at its shape, missing data, and numeric ranges.
        </p>
      </section>

      <section className="workspace" aria-label="CSV analyzer">
        <form className="upload-panel" onSubmit={handleSubmit}>
          <label htmlFor="csv-file">CSV file</label>
          <input id="csv-file" type="file" accept=".csv,text/csv" onChange={handleFileChange} />
          <p className="hint">UTF-8 CSV, up to 5 MB, with a header row.</p>
          <button type="submit" disabled={isAnalyzing}>
            {isAnalyzing ? "Analyzing..." : "Analyze file"}
          </button>
          {selectedFile && <p className="selected-file">Selected: {selectedFile.name}</p>}
          {error && <p className="error-message" role="alert">{error}</p>}
        </form>

        <section className="results-panel" aria-live="polite">
          {!result && !isAnalyzing && <p className="empty-state">Your summary will appear here.</p>}
          {isAnalyzing && <p className="empty-state">Reading rows and measuring the file...</p>}
          {result && (
            <>
              <div className="results-heading">
                <div>
                  <p className="eyebrow">Analysis complete</p>
                  <h2>{result.filename}</h2>
                </div>
                <span className="status-badge">Ready</span>
              </div>
              <div className="metric-grid">
                <Metric label="Records" value={result.total_records} />
                <Metric label="Columns" value={result.column_count} />
                <Metric label="Missing values" value={result.missing_values} />
              </div>
              <div className="detail-block">
                <h3>Numeric ranges</h3>
                {Object.keys(result.numeric_columns).length === 0 ? (
                  <p className="muted">No columns contained exclusively numeric values.</p>
                ) : (
                  <ul>
                    {Object.entries(result.numeric_columns).map(([column, range]) => (
                      <li key={column}><span>{column}</span><strong>{range.minimum} – {range.maximum}</strong></li>
                    ))}
                  </ul>
                )}
              </div>
            </>
          )}
        </section>
      </section>
    </main>
  );
}

function Metric({ label, value }: { label: string; value: number }) {
  return <div className="metric"><span>{label}</span><strong>{value}</strong></div>;
}

export default App;
