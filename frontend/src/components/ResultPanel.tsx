import { useState } from "react";

import type { AnalyzeResult, Issue, Operation } from "../types/api";

interface ResultPanelProps {
  result: AnalyzeResult | null;
  busy: Operation | null;
  networkError: string;
  structureLabel: string;
  onUseOutput: (output: string) => void;
}

const statusLabel = (status: "pass" | "warning" | "error" | "idle") =>
  ({ pass: "PASS", warning: "WARNING", error: "FAIL", idle: "—" })[status];

function StatusRow({ label, status }: { label: string; status: "pass" | "warning" | "error" | "idle" }) {
  return (
    <div className="status-row">
      <span>{label}</span>
      <span className={`status status--${status}`}>
        <span className="status-dot" aria-hidden="true" />
        {statusLabel(status)}
      </span>
    </div>
  );
}

function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  return `${(bytes / 1024).toFixed(bytes >= 10 * 1024 ? 1 : 2)} KB`;
}

function printable(value: unknown): string {
  if (typeof value === "string") return value;
  return JSON.stringify(value) ?? String(value);
}

function Finding({ issue, severity }: { issue: Issue; severity: "error" | "warning" }) {
  return (
    <li className={`finding finding--${severity}`}>
      <div className="finding-head">
        <span className={`finding-kind finding-kind--${severity}`}>{severity}</span>
        {issue.path && <code>{issue.path}</code>}
      </div>
      <p>{issue.message}</p>
      {(issue.expected !== undefined || issue.received !== undefined) && (
        <dl className="expected-grid">
          {issue.expected !== undefined && (
            <div>
              <dt>Expected</dt>
              <dd>{printable(issue.expected)}</dd>
            </div>
          )}
          {issue.received !== undefined && (
            <div>
              <dt>Received</dt>
              <dd>{printable(issue.received)}</dd>
            </div>
          )}
        </dl>
      )}
      {issue.hint && <p className="finding-hint">{issue.hint}</p>}
    </li>
  );
}

export function ResultPanel({ result, busy, networkError, structureLabel, onUseOutput }: ResultPanelProps) {
  const [copyState, setCopyState] = useState<"idle" | "copied" | "failed">("idle");

  if (busy) {
    return (
      <div className="result-state" role="status">
        <span className="activity-mark" aria-hidden="true" />
        <strong>Examining payload</strong>
        <p>Running {busy.replace("_", " ")} in Lambda…</p>
      </div>
    );
  }

  if (networkError) {
    return (
      <div className="result-state result-state--error" role="alert">
        <strong>Analysis service unavailable</strong>
        <p>{networkError}</p>
        <span>Check the API URL and CORS origin, then try again.</span>
      </div>
    );
  }

  if (!result) {
    return (
      <div className="result-state" role="status">
        <div className="empty-scan" aria-hidden="true">
          <i />
          <i />
          <i />
        </div>
        <strong>Ready for inspection</strong>
        <p>Run Diagnose to check syntax, structure, and payload health.</p>
        <kbd>⌘ / Ctrl + Enter</kbd>
      </div>
    );
  }

  if (!result.success && result.error) {
    const title =
      result.error.code === "INVALID_JSON"
        ? "Invalid JSON"
        : result.error.code === "INVALID_SCHEMA_JSON"
          ? "Invalid JSON Schema"
          : result.error.code === "PAYLOAD_TOO_LARGE" || result.error.code === "SCHEMA_TOO_LARGE"
            ? "Request too large"
            : result.error.code === "INTERNAL_ERROR"
              ? "Unable to analyze payload"
              : "Request rejected";
    return (
      <div className="report" aria-live="assertive">
        <section className="syntax-error" role="alert" aria-labelledby="request-error-title">
          <div className="section-heading">
            <h2 id="request-error-title">{title}</h2>
            {result.error.line && <span>Line {result.error.line}, column {result.error.column}</span>}
          </div>
          <p>{result.error.reason ?? result.error.message}</p>
          {result.error.excerpt && <pre>{result.error.excerpt}</pre>}
        </section>
      </div>
    );
  }

  const errors = result.errors ?? [];
  const warnings = result.warnings ?? [];
  const operationChecksStructure = ["diagnose", "repair", "schema_validate"].includes(result.operation ?? "");
  const structureStatus = !operationChecksStructure
    ? "idle"
    : result.structureValid
      ? warnings.length
        ? "warning"
        : "pass"
      : "error";
  const issueCount = errors.length + warnings.length;
  const structureName = result.operation === "schema_validate" ? "JSON Schema" : structureLabel;
  const findingSummary =
    result.operation === "repair" && !result.repaired && !result.jsonValid
      ? "Repair refused"
      : issueCount
        ? `${issueCount} finding${issueCount === 1 ? "" : "s"}`
        : "No findings";

  const copyOutput = async () => {
    if (!result.output) return;
    try {
      await navigator.clipboard.writeText(result.output);
      setCopyState("copied");
    } catch {
      setCopyState("failed");
    }
    window.setTimeout(() => setCopyState("idle"), 1600);
  };

  return (
    <div className="report" aria-live="polite">
      <section className="health" aria-labelledby="health-title">
        <div className="section-heading">
          <h2 id="health-title">Payload health</h2>
          <span>{findingSummary}</span>
        </div>
        <div className="health-grid">
          <div className="health-statuses">
            <StatusRow label="JSON syntax" status={result.jsonValid ? "pass" : "error"} />
            <StatusRow label={structureName} status={structureStatus} />
          </div>
          {result.metrics && (
            <dl className="metrics">
              <div>
                <dt>Size</dt>
                <dd>{formatBytes(result.metrics.bytes)}</dd>
              </div>
              <div>
                <dt>Depth</dt>
                <dd>{result.metrics.depth}</dd>
              </div>
              <div>
                <dt>Keys</dt>
                <dd>{result.metrics.keys}</dd>
              </div>
              <div>
                <dt>Arrays</dt>
                <dd>{result.metrics.arrays}</dd>
              </div>
              <div>
                <dt>Errors</dt>
                <dd>{errors.length}</dd>
              </div>
              <div>
                <dt>Warnings</dt>
                <dd>{warnings.length}</dd>
              </div>
            </dl>
          )}
        </div>
      </section>

      {result.message && (
        <p className={`operation-message ${result.repaired === false ? "operation-message--neutral" : ""}`}>
          {result.message}
        </p>
      )}

      {result.sizes && (
        <dl className="size-strip">
          <div>
            <dt>Original</dt>
            <dd>{formatBytes(result.sizes.originalBytes)}</dd>
          </div>
          {result.sizes.formattedBytes !== undefined && (
            <div>
              <dt>Formatted</dt>
              <dd>{formatBytes(result.sizes.formattedBytes)}</dd>
            </div>
          )}
          {result.sizes.minifiedBytes !== undefined && (
            <div>
              <dt>Minified</dt>
              <dd>{formatBytes(result.sizes.minifiedBytes)}</dd>
            </div>
          )}
          {result.sizes.bytesSaved !== undefined && (
            <div>
              <dt>Saved</dt>
              <dd>
                {formatBytes(result.sizes.bytesSaved)} · {result.sizes.percentageReduction}%
              </dd>
            </div>
          )}
        </dl>
      )}

      {issueCount > 0 && (
        <section className="findings" aria-labelledby="findings-title">
          <div className="section-heading">
            <h2 id="findings-title">Findings</h2>
            <span>Errors before warnings</span>
          </div>
          <ol>
            {errors.map((issue, index) => (
              <Finding key={`error-${issue.path ?? index}-${index}`} issue={issue} severity="error" />
            ))}
            {warnings.map((issue, index) => (
              <Finding key={`warning-${issue.path ?? index}-${index}`} issue={issue} severity="warning" />
            ))}
          </ol>
        </section>
      )}

      {!!result.changes?.length && (
        <section className="changes" aria-labelledby="changes-title">
          <div className="section-heading">
            <h2 id="changes-title">Repairs applied</h2>
            <span>{result.changes.length} safe edits</span>
          </div>
          <ol>
            {result.changes.map((change, index) => (
              <li key={`${change.type}-${change.line}-${index}`}>
                <span>Line {change.line}</span>
                <p>{change.message}</p>
              </li>
            ))}
          </ol>
        </section>
      )}

      {result.output && (
        <section className="output" aria-labelledby="output-title">
          <div className="section-heading output-heading">
            <h2 id="output-title">Output</h2>
            <div>
              <button type="button" className="text-button" onClick={() => onUseOutput(result.output!)}>
                Use as input
              </button>
              <button type="button" className="copy-button" onClick={copyOutput}>
                {copyState === "copied" ? "Copied" : copyState === "failed" ? "Copy failed" : "Copy output"}
              </button>
            </div>
          </div>
          <pre tabIndex={0}>{result.output}</pre>
        </section>
      )}
    </div>
  );
}
