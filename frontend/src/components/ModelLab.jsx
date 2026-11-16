import React, { useState } from "react";
import { BrainCircuit, AlertCircle, Sparkles, ShieldCheck } from "lucide-react";
import { api, payload } from "../api";
import { label, percent, Button } from "../lib/ui";
export default function ModelLab({ reports, onError }) {
  const [text, setText] = useState(""),
    [busy, setBusy] = useState(false),
    [result, setResult] = useState(null);
  async function test(e) {
    e.preventDefault();
    setBusy(true);
    try {
      setResult(await api("/predict", payload({ text })));
    } catch (e) {
      onError(e.message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <>
      <div className="model-grid">
        {["category", "priority"].map((task) => {
          const r = reports?.[task];
          return (
            <section className="card model-card" key={task}>
              <div className="card-heading">
                <div>
                  <span className="model-icon">
                    <BrainCircuit size={19} />
                  </span>
                  <h2>
                    {task === "category"
                      ? "Ticket classification"
                      : "Priority prediction"}
                  </h2>
                  <p>{r?.model || "TF-IDF + Logistic Regression"}</p>
                </div>
                <span
                  className={`model-status ${r?.status === "trained" ? "trained" : ""}`}
                >
                  {r?.status || "loading"}
                </span>
              </div>
              {r?.metrics ? (
                <>
                  <div className="metric-grid">
                    {[
                      ["accuracy", "Accuracy"],
                      ["precision_macro", "Precision"],
                      ["recall_macro", "Recall"],
                      ["f1_macro", "Macro F1"],
                    ].map(([key, title]) => (
                      <div key={key}>
                        <span>{title}</span>
                        <strong>{percent(r.metrics[key])}</strong>
                      </div>
                    ))}
                  </div>
                  <p className="evaluation-context">
                    {r.train_rows.toLocaleString()} training ·{" "}
                    {r.test_rows.toLocaleString()} held-out test rows
                    <br />
                    Majority baseline accuracy: {percent(r.baseline_accuracy)} ·
                    No test-set tuning
                  </p>
                  <h3 className="confusion-title">
                    Confusion matrix{" "}
                    <span>rows: actual · columns: predicted</span>
                  </h3>
                  <div className="confusion-table">
                    <table>
                      <thead>
                        <tr>
                          <th />
                          {r.classes.map((c) => (
                            <th key={c}>{c}</th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {r.confusion_matrix.map((row, i) => (
                          <tr key={i}>
                            <th>{r.classes[i]}</th>
                            {row.map((n, j) => (
                              <td
                                key={j}
                                style={{
                                  background: `rgba(48,157,147,${0.04 + (n / Math.max(1, ...r.confusion_matrix.flat())) * 0.38})`,
                                }}
                              >
                                {n}
                              </td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                  <div className="model-provenance">
                    <strong>{r.provenance.source}</strong>
                    <p>{r.provenance.domain || r.provenance.label_origin}</p>
                    <small>
                      Actual training run:{" "}
                      {new Date(r.trained_at).toLocaleString()}
                    </small>
                  </div>
                </>
              ) : (
                <div className="untrained-message">
                  <AlertCircle size={27} />
                  <h3>Model awaiting training</h3>
                  <p>
                    {task === "priority"
                      ? "A verified, real, human-labeled priority dataset has not been supplied. Prepare reviewed data and run the separate priority training pipeline."
                      : "Download and prepare BANKING77, then train the category pipeline using the commands in the README."}
                  </p>
                  <code>
                    python -m ml.train --task {task}
                    <br />
                    --data-dir data/{task}
                  </code>
                </div>
              )}
            </section>
          );
        })}
      </div>
      <section className="card model-playground">
        <div className="card-heading">
          <div>
            <h2>Take your models for a test drive</h2>
            <p>
              Inspect each component independently. Predictions are not saved as
              tickets.
            </p>
          </div>
          <span className="period">CPU inference</span>
        </div>
        <form onSubmit={test}>
          <textarea
            rows={3}
            minLength={3}
            maxLength={10000}
            required
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="e.g. I was charged twice for my last card payment. Could you help?"
          />
          <Button
            className="primary"
            loading={busy}
            disabled={busy || text.trim().length < 3}
          >
            <Sparkles size={15} />
            Run prediction
          </Button>
        </form>
        {result && (
          <div className="playground-results">
            {Object.entries(result).map(([task, r]) => (
              <div key={task}>
                <span>{label(task)}</span>
                <strong>{r.label ? label(r.label) : label(r.status)}</strong>
                <small>
                  {r.confidence != null
                    ? `${percent(r.confidence)} confidence`
                    : r.message || "Not available"}
                </small>
              </div>
            ))}
          </div>
        )}
      </section>
      <div className="model-note">
        <ShieldCheck size={19} />
        <p>
          Sentiment: <strong>{reports?.sentiment.model}</strong> ·{" "}
          {label(reports?.sentiment.status)}. Pretrained English social-media
          model; no support-domain evaluation is claimed. Confidence scores are
          not calibrated reliability estimates.
        </p>
      </div>
    </>
  );
}
