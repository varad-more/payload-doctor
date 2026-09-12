import { useMemo, useRef, useState } from "react";

import { Editor } from "./components/Editor";
import { ResultPanel } from "./components/ResultPanel";
import { EXAMPLES } from "./examples/payloads";
import { analyzePayload } from "./services/api";
import type { AnalyzeResult, Operation, PayloadType } from "./types/api";

const PAYLOAD_LIMIT = 1024 * 1024;
const SCHEMA_LIMIT = 256 * 1024;

const PAYLOAD_TYPES: { value: PayloadType; label: string; structure: string }[] = [
  { value: "generic", label: "Generic JSON", structure: "JSON structure" },
  { value: "api_gateway", label: "API Gateway REST proxy event (v1)", structure: "API Gateway v1 structure" },
  { value: "sqs", label: "Amazon SQS event", structure: "SQS structure" },
  { value: "sns", label: "Amazon SNS event", structure: "SNS structure" },
  { value: "eventbridge", label: "Amazon EventBridge event", structure: "EventBridge structure" },
];

const OPERATIONS: { value: Operation; label: string }[] = [
  { value: "diagnose", label: "Diagnose" },
  { value: "format", label: "Format" },
  { value: "minify", label: "Minify" },
  { value: "repair", label: "Repair" },
];

function BrandMark() {
  return (
    <svg viewBox="0 0 36 36" aria-hidden="true">
      <path d="M11 7H7v8M25 7h4v8M11 29H7v-8M25 29h4v-8" />
      <path d="M18 11v14M11 18h14" />
      <circle cx="18" cy="18" r="14.5" />
    </svg>
  );
}

export default function App() {
  const [payloadType, setPayloadType] = useState<PayloadType>("generic");
  const [content, setContent] = useState(EXAMPLES.generic.valid);
  const [schema, setSchema] = useState("");
  const [result, setResult] = useState<AnalyzeResult | null>(null);
  const [busy, setBusy] = useState<Operation | null>(null);
  const [networkError, setNetworkError] = useState("");
  const editorRef = useRef<HTMLTextAreaElement>(null);

  const payloadBytes = useMemo(() => new TextEncoder().encode(content).length, [content]);
  const schemaBytes = useMemo(() => new TextEncoder().encode(schema).length, [schema]);
  const tooLarge = payloadBytes > PAYLOAD_LIMIT;
  const selectedType = PAYLOAD_TYPES.find((type) => type.value === payloadType)!;
  const githubUrl = import.meta.env.VITE_GITHUB_URL as string | undefined;

  async function run(operation: Operation) {
    if (busy || !content || tooLarge || (operation === "schema_validate" && (!schema || schemaBytes > SCHEMA_LIMIT))) return;
    setBusy(operation);
    setResult(null);
    setNetworkError("");
    try {
      setResult(
        await analyzePayload({
          operation,
          payloadType,
          content,
          schema: operation === "schema_validate" ? schema : null,
        }),
      );
    } catch (error) {
      setNetworkError(error instanceof Error ? error.message : "Unable to reach the analysis service.");
    } finally {
      setBusy(null);
    }
  }

  function loadExample(kind: "valid" | "broken") {
    setContent(EXAMPLES[payloadType][kind]);
    setResult(null);
    setNetworkError("");
    requestAnimationFrame(() => editorRef.current?.focus());
  }

  function updateContent(next: string) {
    setContent(next);
    if (result) setResult(null);
    if (networkError) setNetworkError("");
  }

  return (
    <div className="app-shell">
      <header className="site-header">
        <a className="brand" href="#top" aria-label="Payload Doctor home">
          <BrandMark />
          <span>Payload Doctor</span>
        </a>
        <nav aria-label="Primary navigation">
          {githubUrl ? (
            <a href={githubUrl} target="_blank" rel="noreferrer">
              GitHub
            </a>
          ) : (
            <span className="nav-disabled" title="Set VITE_GITHUB_URL to link the repository">
              GitHub
            </span>
          )}
          <a href="#about">About</a>
        </nav>
      </header>

      <main id="top">
        <section className="intro" aria-labelledby="page-title">
          <div>
            <h1 id="page-title">Payload Doctor</h1>
            <p className="tagline">Debug JSON and AWS event payloads instantly.</p>
            <p className="supporting-copy">
              Validate syntax, inspect AWS event structures, repair common JSON mistakes, and diagnose payload issues
              with a serverless AWS backend.
            </p>
          </div>
          <button
            type="button"
            className="hero-action"
            disabled={!!busy || !content || tooLarge}
            onClick={() => {
              document.getElementById("workbench")?.scrollIntoView();
              void run("diagnose");
            }}
          >
            Diagnose payload
            <svg viewBox="0 0 20 20" aria-hidden="true">
              <path d="M5 5h10v10M15 5 5 15" />
            </svg>
          </button>
        </section>

        <section id="workbench" className="workbench" aria-label="Payload analysis workbench">
          <div className="tool-strip">
            <label>
              <span>Payload type</span>
              <select
                value={payloadType}
                onChange={(event) => {
                  setPayloadType(event.target.value as PayloadType);
                  setResult(null);
                }}
              >
                {PAYLOAD_TYPES.map((type) => (
                  <option value={type.value} key={type.value}>
                    {type.label}
                  </option>
                ))}
              </select>
            </label>
            <div className="example-control" aria-label="Load example payload">
              <span>Load example</span>
              <div>
                <button type="button" onClick={() => loadExample("valid")}>Valid</button>
                <button type="button" onClick={() => loadExample("broken")}>Broken</button>
              </div>
            </div>
            <div className="strip-actions">
              <button
                type="button"
                className="clear-button"
                onClick={() => {
                  updateContent("");
                  requestAnimationFrame(() => editorRef.current?.focus());
                }}
              >
                Clear input
              </button>
              <button
                type="button"
                className="quick-diagnose"
                disabled={!!busy || !content || tooLarge}
                onClick={() => run("diagnose")}
              >
                {busy === "diagnose" ? "Working…" : "Diagnose"}
              </button>
            </div>
          </div>

          <div className="work-grid">
            <section className="pane input-pane" aria-labelledby="input-title">
              <div className="pane-head">
                <div>
                  <span className="pane-index">A</span>
                  <h2 id="input-title">Input</h2>
                </div>
                <span className={tooLarge ? "limit limit--error" : "limit"}>{payloadBytes.toLocaleString()} / 1,048,576 bytes</span>
              </div>
              <Editor ref={editorRef} value={content} onChange={updateContent} onSubmit={() => run("diagnose")} />
              <p id="input-help" className="pane-note">
                UTF-8 · Payload contents are processed transiently and are not intentionally stored by Payload Doctor.
              </p>
              {tooLarge && <p className="limit-warning" role="alert">Payload exceeds the 1 MiB service limit.</p>}
            </section>

            <section className="pane result-pane" aria-labelledby="result-title">
              <div className="pane-head">
                <div>
                  <span className="pane-index">B</span>
                  <h2 id="result-title">Output / diagnosis</h2>
                </div>
                <span>Lambda analysis</span>
              </div>
              <div className="result-scroll">
                <ResultPanel
                  result={result}
                  busy={busy}
                  networkError={networkError}
                  structureLabel={selectedType.structure}
                  onUseOutput={(output) => {
                    updateContent(output);
                    requestAnimationFrame(() => editorRef.current?.focus());
                  }}
                />
              </div>
            </section>
          </div>

          <div className="action-bar" aria-label="Payload operations">
            <div>
              {OPERATIONS.map((operation) => (
                <button
                  key={operation.value}
                  type="button"
                  className={operation.value === "diagnose" ? "primary-operation" : ""}
                  disabled={!!busy || !content || tooLarge}
                  onClick={() => run(operation.value)}
                >
                  {busy === operation.value ? "Working…" : operation.label}
                </button>
              ))}
            </div>
            <span>⌘ / Ctrl + Enter</span>
          </div>
        </section>

        <details className="schema-panel">
          <summary>
            <span>Validate against JSON Schema</span>
            <small>Optional · draft selected from $schema</small>
          </summary>
          <div className="schema-body">
            <label htmlFor="schema-content">JSON Schema</label>
            <textarea
              id="schema-content"
              value={schema}
              onChange={(event) => setSchema(event.target.value)}
              placeholder={'{\n  "type": "object",\n  "required": ["id"]\n}'}
              spellCheck={false}
            />
            <div>
              <span className={schemaBytes > SCHEMA_LIMIT ? "limit limit--error" : "limit"}>
                {schemaBytes.toLocaleString()} / 262,144 bytes
              </span>
              <button
                type="button"
                disabled={!!busy || !content || tooLarge || !schema || schemaBytes > SCHEMA_LIMIT}
                onClick={() => run("schema_validate")}
              >
                Validate schema
              </button>
            </div>
          </div>
        </details>

        <section id="about" className="about" aria-labelledby="about-title">
          <div>
            <h2 id="about-title">Built on AWS</h2>
            <p>
              Payload Doctor uses a serverless architecture. The frontend is hosted with AWS Amplify, requests are
              routed through Amazon API Gateway, analysis runs in AWS Lambda, and operational telemetry is captured in
              Amazon CloudWatch.
            </p>
          </div>
          <ul aria-label="AWS services used">
            <li>AWS Amplify</li>
            <li>Amazon API Gateway</li>
            <li>AWS Lambda</li>
            <li>Amazon CloudWatch</li>
          </ul>
        </section>
      </main>

      <footer>
        <span>Payload Doctor</span>
        <span>No payload history. No account required.</span>
      </footer>
    </div>
  );
}
