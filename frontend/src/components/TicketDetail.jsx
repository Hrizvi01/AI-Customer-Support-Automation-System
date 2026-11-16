import React, { useState, useEffect } from "react";
import {
  X,
  BrainCircuit,
  Sparkles,
  ArrowRight,
  Copy,
  ShieldCheck,
  CheckCheck,
} from "lucide-react";
import { api, payload } from "../api";
import { useDialog } from "../lib/useDialog";
import {
  CATEGORIES,
  PRIORITIES,
  STATUSES,
  label,
  time,
  percent,
  Badge,
  Button,
} from "../lib/ui";
export default function TicketDetail({ ticket, onClose, onUpdate, onNotice }) {
  const [busy, setBusy] = useState(""),
    [error, setError] = useState(""),
    [events, setEvents] = useState([]),
    [instructions, setInstructions] = useState(""),
    [editing, setEditing] = useState(false),
    [text, setText] = useState({
      subject: ticket.subject,
      description: ticket.description,
    });
  const dialog = useDialog(onClose, !!busy);
  useEffect(() => {
    api(`/tickets/${ticket.id}/events`)
      .then(setEvents)
      .catch((e) => setError(e.message));
  }, [ticket.updated_at]);
  async function perform(action, path, body, method = "POST") {
    setBusy(action);
    setError("");
    try {
      onUpdate(
        await api(`/tickets/${ticket.id}${path}`, payload(body, method)),
      );
      if (action === "save") setEditing(false);
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy("");
    }
  }
  async function copy() {
    try {
      await navigator.clipboard.writeText(ticket.suggested_reply);
      onNotice("Suggested reply copied. Review it before sending.");
    } catch {
      setError(
        "Clipboard access is unavailable. Select and copy the draft text manually.",
      );
    }
  }
  return (
    <div className="drawer-backdrop">
      <aside
        ref={dialog}
        className="ticket-drawer"
        role="dialog"
        aria-modal="true"
        aria-labelledby="ticket-detail-title"
      >
        <div className="drawer-header">
          <span className="ticket-number">
            SP-{String(ticket.id).padStart(4, "0")}
          </span>
          <Badge value={ticket.status} />
          <button
            className="icon"
            aria-label="Close ticket"
            onClick={onClose}
            disabled={!!busy}
          >
            <X size={21} />
          </button>
        </div>
        <div className="drawer-body">
          <h2 id="ticket-detail-title">{ticket.subject}</h2>
          <div className="detail-customer">
            <span className="customer-avatar avatar-1">
              {ticket.customer_name[0]}
            </span>
            <div>
              <strong>{ticket.customer_name}</strong>
              <small>
                {ticket.customer_email} · {time(ticket.created_at)}
              </small>
            </div>
          </div>
          {error && (
            <div className="alert error" role="alert">
              {error}
            </div>
          )}
          <div className="detail-fields">
            {[
              ["category", CATEGORIES],
              ["priority", PRIORITIES],
              ["status", STATUSES],
            ].map(([key, values]) => (
              <label key={key}>
                {label(key)}
                <select
                  disabled={!!busy}
                  value={ticket[key] || ""}
                  onChange={(e) =>
                    perform("update", "", { [key]: e.target.value }, "PATCH")
                  }
                >
                  {!ticket[key] && <option value="">Unassigned</option>}
                  {values.map((x) => (
                    <option value={x} key={x}>
                      {label(x)}
                    </option>
                  ))}
                </select>
              </label>
            ))}
          </div>
          <section className="detail-section">
            <div className="detail-section-heading">
              <h3>Customer message</h3>
              <button
                className="text-button"
                disabled={!!busy}
                onClick={() => {
                  setText({
                    subject: ticket.subject,
                    description: ticket.description,
                  });
                  setEditing(!editing);
                }}
              >
                {editing ? "Cancel edit" : "Edit ticket"}
              </button>
            </div>
            {editing ? (
              <div className="edit-form">
                <label>
                  Subject
                  <input
                    value={text.subject}
                    maxLength={180}
                    onChange={(e) =>
                      setText((t) => ({ ...t, subject: e.target.value }))
                    }
                  />
                </label>
                <label>
                  Description
                  <textarea
                    rows={5}
                    value={text.description}
                    maxLength={10000}
                    onChange={(e) =>
                      setText((t) => ({ ...t, description: e.target.value }))
                    }
                  />
                </label>
                <Button
                  className="secondary"
                  loading={busy === "save"}
                  disabled={
                    !!busy ||
                    text.subject.trim().length < 3 ||
                    text.description.trim().length < 10
                  }
                  onClick={() => perform("save", "", text, "PATCH")}
                >
                  Save changes
                </Button>
              </div>
            ) : (
              <p className="customer-message">{ticket.description}</p>
            )}
          </section>
          <section className="detail-section ai-analysis">
            <div className="detail-section-heading">
              <h3>
                <BrainCircuit size={17} />
                AI analysis
              </h3>
              <Button
                className="secondary"
                loading={busy === "analyze"}
                disabled={!!busy}
                onClick={() => perform("analyze", "/analyze", {})}
              >
                Analyze ticket
                <Sparkles size={13} />
              </Button>
            </div>
            <p className="muted">
              Suggestions only. Apply routing changes after reviewing confidence
              and domain fit.
            </p>
            {ticket.analysis ? (
              <div className="prediction-grid">
                {["category", "priority", "sentiment"].map((task) => {
                  const result = ticket.analysis[task];
                  return (
                    <div className="prediction" key={task}>
                      <span>{label(task)}</span>
                      {result?.label ? (
                        <>
                          <strong>{label(result.label)}</strong>
                          <small>
                            {percent(result.confidence)} confidence
                            {result.needs_review ? " · review recommended" : ""}
                          </small>
                          {task !== "sentiment" && (
                            <button
                              className="text-button"
                              disabled={!!busy}
                              onClick={() =>
                                perform(
                                  "apply",
                                  "",
                                  { [task]: result.label },
                                  "PATCH",
                                )
                              }
                            >
                              Apply suggestion
                              <ArrowRight size={12} />
                            </button>
                          )}
                        </>
                      ) : (
                        <>
                          <strong className="unavailable">
                            {label(result?.status || "unavailable")}
                          </strong>
                          <small>
                            {result?.message || "No prediction available."}
                          </small>
                        </>
                      )}
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className="analysis-empty">
                <Sparkles size={19} />
                <p>
                  Run analysis to see model suggestions.
                  <br />
                  Missing models are reported without placeholder predictions.
                </p>
              </div>
            )}
          </section>
          <section className="detail-section">
            <div className="detail-section-heading">
              <h3>
                <Sparkles size={16} />
                Suggested reply
              </h3>
              <Button
                className="primary small"
                loading={busy === "reply"}
                disabled={!!busy}
                onClick={() => perform("reply", "/reply", { instructions })}
              >
                {ticket.suggested_reply ? "Regenerate" : "Generate draft"}
              </Button>
            </div>
            <input
              className="guidance"
              aria-label="Agent guidance"
              value={instructions}
              maxLength={1000}
              onChange={(e) => setInstructions(e.target.value)}
              placeholder="Optional guidance, e.g. ask for the transaction date"
            />
            {ticket.suggested_reply ? (
              <>
                <div className="reply-draft">{ticket.suggested_reply}</div>
                <div className="draft-footer">
                  <span>Draft · {ticket.reply_model} · Not sent</span>
                  <button className="text-button" onClick={copy}>
                    <Copy size={12} />
                    Copy reply
                  </button>
                </div>
              </>
            ) : (
              <p className="muted draft-empty">
                A professional first draft, generated locally with Ollama. No
                customer message is sent automatically.
              </p>
            )}
          </section>
          <section className="detail-section">
            <h3>Activity</h3>
            <div className="activity-list">
              {events.map((e) => (
                <div key={e.id}>
                  <span />
                  <p>
                    <strong>{label(e.action)}</strong>
                    <small>{e.detail}</small>
                  </p>
                  <time>{time(e.created_at)}</time>
                </div>
              ))}
            </div>
          </section>
        </div>
        <div className="drawer-footer">
          <span>
            <ShieldCheck size={13} />
            Human review, always.
          </span>
          <Button
            className="primary"
            disabled={!!busy || ticket.status === "resolved"}
            loading={busy === "resolve"}
            onClick={() =>
              perform("resolve", "", { status: "resolved" }, "PATCH")
            }
          >
            <CheckCheck size={15} />
            {ticket.status === "resolved" ? "Resolved" : "Mark resolved"}
          </Button>
        </div>
      </aside>
    </div>
  );
}
