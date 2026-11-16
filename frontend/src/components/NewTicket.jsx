import React, { useState } from "react";
import { X, ArrowRight } from "lucide-react";
import { api, payload } from "../api";
import { useDialog } from "../lib/useDialog";
import { CATEGORIES, PRIORITIES, label, Button } from "../lib/ui";
export default function NewTicket({ onClose, onCreated }) {
  const [form, setForm] = useState({
      subject: "",
      description: "",
      customer_name: "",
      customer_email: "",
      category: "",
      priority: "",
    }),
    [busy, setBusy] = useState(false),
    [error, setError] = useState("");
  const dialog = useDialog(onClose, busy);
  const field = (key, value) => setForm((f) => ({ ...f, [key]: value }));
  async function submit(e) {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      const body = {
        ...form,
        category: form.category || null,
        priority: form.priority || null,
      };
      onCreated(await api("/tickets", payload(body)));
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <div className="modal-backdrop">
      <section
        ref={dialog}
        className="modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="new-ticket-title"
      >
        <div className="modal-heading">
          <div>
            <span className="eyebrow">START A CONVERSATION</span>
            <h2 id="new-ticket-title">Create a support ticket</h2>
          </div>
          <button
            className="icon"
            aria-label="Close new ticket"
            onClick={onClose}
            disabled={busy}
          >
            <X size={19} />
          </button>
        </div>
        <form onSubmit={submit}>
          {error && (
            <div className="alert error" role="alert">
              {error}
            </div>
          )}
          <div className="form-row">
            <label>
              Customer name
              <input
                required
                maxLength={100}
                value={form.customer_name}
                onChange={(e) => field("customer_name", e.target.value)}
                placeholder="e.g. Alex Morgan"
              />
            </label>
            <label>
              Email address
              <input
                required
                type="email"
                maxLength={254}
                value={form.customer_email}
                onChange={(e) => field("customer_email", e.target.value)}
                placeholder="alex@example.test"
              />
            </label>
          </div>
          <label>
            Subject
            <input
              required
              minLength={3}
              maxLength={180}
              value={form.subject}
              onChange={(e) => field("subject", e.target.value)}
              placeholder="A short summary of the issue"
            />
          </label>
          <label>
            Description
            <textarea
              required
              minLength={10}
              maxLength={10000}
              rows={5}
              value={form.description}
              onChange={(e) => field("description", e.target.value)}
              placeholder="What happened? What has the customer already tried?"
            />
          </label>
          <div className="form-row">
            <label>
              Category
              <select
                value={form.category}
                onChange={(e) => field("category", e.target.value)}
              >
                <option value="">Unassigned</option>
                {CATEGORIES.map((x) => (
                  <option key={x} value={x}>
                    {label(x)}
                  </option>
                ))}
              </select>
            </label>
            <label>
              Priority
              <select
                value={form.priority}
                onChange={(e) => field("priority", e.target.value)}
              >
                <option value="">Unassigned</option>
                {PRIORITIES.map((x) => (
                  <option key={x} value={x}>
                    {label(x)}
                  </option>
                ))}
              </select>
            </label>
          </div>
          <p className="form-note">
            Routing fields are agent-selected. AI suggestions can be reviewed
            after creation.
          </p>
          <div className="modal-actions">
            <button
              type="button"
              className="secondary"
              disabled={busy}
              onClick={onClose}
            >
              Cancel
            </button>
            <Button className="primary" loading={busy}>
              Create ticket
              <ArrowRight size={15} />
            </Button>
          </div>
        </form>
      </section>
    </div>
  );
}
