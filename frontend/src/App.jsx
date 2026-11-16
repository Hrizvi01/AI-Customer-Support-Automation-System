import React, { useEffect, useRef, useState } from "react";
import {
  ArrowRight,
  ArrowUpRight,
  BookOpen,
  BrainCircuit,
  Check,
  CheckCheck,
  ChevronDown,
  ChevronLeft,
  ChevronRight,
  Clock3,
  ExternalLink,
  Filter,
  Headphones,
  LayoutDashboard,
  LoaderCircle,
  MessageSquare,
  MoreHorizontal,
  Plus,
  Search,
  Settings2,
  ShieldCheck,
  Sparkles,
  Ticket,
  TrendingUp,
  X,
  Zap,
  Menu,
  RefreshCw,
  AlertCircle,
  ChartNoAxesCombined,
} from "lucide-react";
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  BarChart,
  Bar,
  Legend,
} from "recharts";
import { api } from "./api";

import { CATEGORIES, PRIORITIES, COLORS, label, time, Badge } from "./lib/ui";
import NewTicket from "./components/NewTicket";
import TicketDetail from "./components/TicketDetail";
import ModelLab from "./components/ModelLab";
export default function App() {
  const [view, setView] = useState("overview"),
    [tickets, setTickets] = useState({ items: [], total: 0 }),
    [analytics, setAnalytics] = useState(null),
    [health, setHealth] = useState(null),
    [reports, setReports] = useState(null);
  const [q, setQ] = useState(""),
    [filters, setFilters] = useState({
      status: "",
      priority: "",
      category: "",
    }),
    [page, setPage] = useState(1),
    [loading, setLoading] = useState(true),
    [error, setError] = useState(""),
    [tick, setTick] = useState(0);
  const [newTicket, setNewTicket] = useState(false),
    [detail, setDetail] = useState(null),
    [notice, setNotice] = useState(""),
    [mobile, setMobile] = useState(false);
  const sequence = useRef(0);
  const refresh = () => setTick((t) => t + 1);
  useEffect(() => {
    let active = true;
    Promise.allSettled([
      api("/analytics"),
      api("/health"),
      api("/models"),
    ]).then((results) => {
      if (!active) return;
      const setters = [setAnalytics, setHealth, setReports];
      results.forEach((result, index) => {
        if (result.status === "fulfilled") setters[index](result.value);
        else setError(result.reason.message);
      });
    });
    return () => {
      active = false;
    };
  }, [tick]);
  useEffect(() => {
    const seq = ++sequence.current;
    setLoading(true);
    const timer = setTimeout(() => {
      const params = new URLSearchParams({
        q,
        page: String(page),
        page_size: "8",
        ...Object.fromEntries(Object.entries(filters).filter(([, v]) => v)),
      });
      api(`/tickets?${params}`)
        .then((data) => {
          if (seq === sequence.current) setTickets(data);
        })
        .catch((e) => {
          if (seq === sequence.current) setError(e.message);
        })
        .finally(() => {
          if (seq === sequence.current) setLoading(false);
        });
    }, 200);
    return () => clearTimeout(timer);
  }, [q, filters, page, tick]);
  useEffect(() => {
    if (!notice) return;
    const timer = setTimeout(() => setNotice(""), 5000);
    return () => clearTimeout(timer);
  }, [notice]);
  const navigate = (v) => {
    setView(v);
    setMobile(false);
  };
  const filter = (key, value) => {
    setFilters((f) => ({ ...f, [key]: value }));
    setPage(1);
  };
  async function openTicket(id) {
    setError("");
    try {
      setDetail(await api(`/tickets/${id}`));
    } catch (e) {
      setError(e.message);
    }
  }
  const updated = (t) => {
    setDetail(t);
    refresh();
  };
  const categoryData = CATEGORIES.map((name) => ({
    name: label(name),
    value: analytics?.categories[name] || 0,
    color: COLORS[name],
  }));
  return (
    <div className="shell">
      <aside className={`sidebar ${mobile ? "visible" : ""}`}>
        <a
          className="brand"
          href="#"
          onClick={(e) => {
            e.preventDefault();
            navigate("overview");
          }}
        >
          <span className="brand-mark">
            <Headphones size={22} />
          </span>
          support<span>pilot</span>
          <span className="brand-point" />
        </a>
        <div className="workspace-picker">
          <span className="workspace-avatar">S</span>
          <div>
            <strong>Support workspace</strong>
            <small>Personal portfolio</small>
          </div>
          <ChevronDown size={14} />
        </div>
        <div className="nav-heading">WORKSPACE</div>
        <nav>
          {[
            ["overview", LayoutDashboard, "Overview"],
            ["tickets", Ticket, "All tickets"],
            ["analytics", ChartNoAxesCombined, "Analytics"],
            ["models", BrainCircuit, "AI & models"],
          ].map(([key, Icon, title]) => (
            <button
              className={view === key ? "active" : ""}
              key={key}
              onClick={() => navigate(key)}
            >
              <Icon size={18} />
              {title}
              {key === "tickets" && (
                <span className="nav-count">{analytics?.total ?? "—"}</span>
              )}
              {key === "models" && <span className="nav-ai">AI</span>}
            </button>
          ))}
        </nav>
        <div className="nav-heading tools-label">RESOURCES</div>
        <nav>
          <button
            onClick={() => navigate("guide")}
            className={view === "guide" ? "active" : ""}
          >
            <BookOpen size={18} />
            Getting started
          </button>
          <a href="http://127.0.0.1:8001/docs" target="_blank" rel="noreferrer">
            <Settings2 size={18} />
            API documentation
            <ExternalLink size={12} />
          </a>
        </nav>
        <div className="sidebar-bottom">
          <div className="local-box">
            <div>
              <span className="local-orb">
                <Zap size={15} />
              </span>
              <strong>Local intelligence</strong>
              <span className="local-pill">FREE</span>
            </div>
            <p>
              Your workflow. Your models.
              <br />
              No paid API keys required.
            </p>
            <button onClick={() => navigate("models")}>
              Explore your AI stack
              <ArrowRight size={13} />
            </button>
          </div>
          <div className="account">
            <span className="account-avatar">YO</span>
            <div>
              <strong>Your workspace</strong>
              <small>Local administrator</small>
            </div>
            <ShieldCheck size={16} />
          </div>
        </div>
      </aside>
      <main>
        <header>
          <div className="breadcrumb">
            <button
              className="icon mobile-menu"
              aria-label="Toggle navigation"
              onClick={() => setMobile(!mobile)}
            >
              <Menu size={19} />
            </button>
            <span>Workspace</span>
            <ChevronRight size={12} />
            <strong>
              {
                {
                  overview: "Overview",
                  tickets: "All tickets",
                  analytics: "Analytics",
                  models: "AI & models",
                  guide: "Getting started",
                }[view]
              }
            </strong>
          </div>
          <div className="header-right">
            <span className="connection">
              <i className={health?.database === "ready" ? "connected" : ""} />
              {health?.database === "ready"
                ? "Workspace connected"
                : "Connecting to backend"}
            </span>
            <span className="header-divider" />
            <button
              className="icon"
              aria-label="Refresh dashboard"
              onClick={refresh}
            >
              <RefreshCw size={16} />
            </button>
            <span className="header-avatar">Y</span>
          </div>
        </header>
        <div className="content">
          {error && (
            <div className="alert error" role="alert">
              <AlertCircle size={16} />
              <span>{error}</span>
              <button
                className="icon"
                onClick={() => setError("")}
                aria-label="Dismiss error"
              >
                <X size={15} />
              </button>
            </div>
          )}
          {notice && (
            <div className="alert success" role="status">
              <Check size={16} />
              {notice}
            </div>
          )}
          {health?.database_type === "sqlite_demo" && (
            <div className="demo-note">
              <span>LOCAL DEMO</span>SQLite workspace · Use Docker Compose for
              PostgreSQL. Demo tickets are fictional; analytics reflect stored
              records.
            </div>
          )}
          <div className="page-heading">
            <div>
              <div className="eyebrow">YOUR SUPPORT, A LITTLE SMARTER</div>
              <h1>
                {
                  {
                    overview: "A clear view of every conversation.",
                    tickets: "Every ticket. One workspace.",
                    analytics: "Turn conversations into insight.",
                    models: "Intelligence you can inspect.",
                    guide: "Your next great support workflow.",
                  }[view]
                }
              </h1>
              <p>
                {
                  {
                    overview:
                      "Less busywork. More meaningful support. Here’s where things stand.",
                    tickets:
                      "Find, prioritize, and resolve the conversations that matter.",
                    analytics:
                      "Real workspace data, with the context behind every number.",
                    models:
                      "Transparent predictions, reproducible evaluation, and local inference.",
                    guide:
                      "Start small, verify the evidence, and keep a human in the loop.",
                  }[view]
                }
              </p>
            </div>
            <button className="primary" onClick={() => setNewTicket(true)}>
              <Plus size={16} />
              New ticket
            </button>
          </div>
          {(view === "overview" || view === "analytics") && (
            <>
              <div className="stats-grid">
                {[
                  [
                    Ticket,
                    "Total tickets",
                    analytics?.total,
                    "Every conversation in this workspace",
                    "blue",
                  ],
                  [
                    Clock3,
                    "Awaiting resolution",
                    analytics ? analytics.open + analytics.in_progress : null,
                    "Open and in-progress tickets",
                    "amber",
                  ],
                  [
                    CheckCheck,
                    "Resolved tickets",
                    analytics?.resolved,
                    analytics
                      ? `${analytics.resolution_rate}% of all tickets`
                      : "Resolution rate",
                    "green",
                  ],
                  [
                    Zap,
                    "High priority",
                    analytics?.high_priority,
                    "Unresolved tickets needing attention",
                    "purple",
                  ],
                ].map(([Icon, title, value, sub, color]) => (
                  <article className="stat-card" key={title}>
                    <div>
                      <span>{title}</span>
                      <span className={`stat-icon ${color}`}>
                        <Icon size={17} />
                      </span>
                    </div>
                    <strong>{value ?? "—"}</strong>
                    <small>
                      {title === "Resolved tickets" ? (
                        <TrendingUp size={12} />
                      ) : (
                        <span className={`tiny-dot ${color}`} />
                      )}{" "}
                      {sub}
                    </small>
                  </article>
                ))}
              </div>
              <div className="charts-row">
                <section className="card volume-chart">
                  <div className="card-heading">
                    <div>
                      <h2>Ticket activity</h2>
                      <p>A little perspective on your support volume</p>
                    </div>
                    <span className="period">
                      <Clock3 size={12} />
                      Last 14 days
                    </span>
                  </div>
                  <div className="chart-key">
                    <span />
                    <span>Tickets created</span>
                  </div>
                  <div className="chart">
                    <ResponsiveContainer width="100%" height="100%">
                      <AreaChart
                        data={analytics?.trend || []}
                        margin={{ top: 10, right: 12, bottom: 0, left: -25 }}
                      >
                        <defs>
                          <linearGradient
                            id="ticketFill"
                            x1="0"
                            y1="0"
                            x2="0"
                            y2="1"
                          >
                            <stop
                              offset="0%"
                              stopColor="#4fb7b2"
                              stopOpacity={0.2}
                            />
                            <stop
                              offset="100%"
                              stopColor="#4fb7b2"
                              stopOpacity={0}
                            />
                          </linearGradient>
                        </defs>
                        <CartesianGrid
                          stroke="#edf1f5"
                          vertical={false}
                          strokeDasharray="3 4"
                        />
                        <XAxis
                          dataKey="date"
                          axisLine={false}
                          tickLine={false}
                          tick={{ fontSize: 9, fill: "#98a4b4" }}
                          tickFormatter={(v) =>
                            new Date(v + "T00:00:00").toLocaleDateString(
                              undefined,
                              { month: "short", day: "numeric" },
                            )
                          }
                          minTickGap={28}
                        />
                        <YAxis
                          axisLine={false}
                          tickLine={false}
                          allowDecimals={false}
                          tick={{ fontSize: 9, fill: "#a1adbb" }}
                        />
                        <Tooltip
                          contentStyle={{
                            border: "1px solid #e5ebf0",
                            borderRadius: 8,
                            fontSize: 11,
                          }}
                        />
                        <Area
                          type="monotone"
                          dataKey="tickets"
                          stroke="#44aaa6"
                          strokeWidth={2.5}
                          fill="url(#ticketFill)"
                        />
                      </AreaChart>
                    </ResponsiveContainer>
                  </div>
                </section>
                <section className="card category-chart">
                  <div className="card-heading">
                    <div>
                      <h2>Conversations by category</h2>
                      <p>Where your customers need a hand</p>
                    </div>
                    <span className="icon-static">
                      <MoreHorizontal size={18} />
                    </span>
                  </div>
                  <div className="category-total">
                    <strong>{analytics?.total ?? "—"}</strong>
                    <span>total tickets</span>
                  </div>
                  <div className="category-stack">
                    {[
                      ...categoryData,
                      {
                        name: "unassigned",
                        value: analytics?.categories.unassigned || 0,
                        color: COLORS.unassigned,
                      },
                    ]
                      .filter((x) => x.value > 0)
                      .map((d) => (
                        <span
                          key={d.name}
                          style={{
                            width: `${(d.value / (analytics?.total || 1)) * 100}%`,
                            background: d.color,
                          }}
                          title={`${d.name}: ${d.value}`}
                        />
                      ))}
                  </div>
                  <div className="category-list">
                    {categoryData.map((d) => (
                      <div key={d.name}>
                        <span>
                          <i style={{ background: d.color }} />
                          {d.name}
                        </span>
                        <strong>
                          {d.value}
                          <small>
                            {analytics?.total
                              ? Math.round((d.value / analytics.total) * 100)
                              : 0}
                            %
                          </small>
                        </strong>
                      </div>
                    ))}
                    {analytics?.categories.unassigned > 0 && (
                      <div>
                        <span>
                          <i style={{ background: COLORS.unassigned }} />
                          Unassigned
                        </span>
                        <strong>{analytics.categories.unassigned}</strong>
                      </div>
                    )}
                  </div>
                </section>
              </div>
            </>
          )}
          {(view === "overview" || view === "tickets") && (
            <section className="card tickets-card">
              <div className="card-heading">
                <div className="ticket-title">
                  <h2>
                    {view === "overview"
                      ? "Recent conversations"
                      : "Ticket inbox"}
                  </h2>
                  <span className="total-pill">{tickets.total}</span>
                </div>
                {view === "overview" ? (
                  <button
                    className="text-button"
                    onClick={() => navigate("tickets")}
                  >
                    View all tickets
                    <ArrowUpRight size={14} />
                  </button>
                ) : (
                  <span className="period">Page {page}</span>
                )}
              </div>
              <div className="table-toolbar">
                <div className="tabs">
                  {[
                    ["", "All tickets"],
                    ["open", "Open"],
                    ["in_progress", "In progress"],
                    ["resolved", "Resolved"],
                  ].map(([value, title]) => (
                    <button
                      className={filters.status === value ? "selected" : ""}
                      key={value}
                      onClick={() => filter("status", value)}
                    >
                      {title}
                      {value === "" && <span>{analytics?.total ?? 0}</span>}
                    </button>
                  ))}
                </div>
                <label className="search-box">
                  <Search size={14} />
                  <input
                    aria-label="Search tickets"
                    placeholder="Search conversations…"
                    value={q}
                    onChange={(e) => {
                      setQ(e.target.value);
                      setPage(1);
                    }}
                  />
                </label>
                <label className="select-filter">
                  <Filter size={13} />
                  <select
                    aria-label="Filter priority"
                    value={filters.priority}
                    onChange={(e) => filter("priority", e.target.value)}
                  >
                    <option value="">All priorities</option>
                    {PRIORITIES.map((p) => (
                      <option key={p} value={p}>
                        {label(p)}
                      </option>
                    ))}
                  </select>
                </label>
                {view === "tickets" && (
                  <label className="select-filter">
                    <select
                      aria-label="Filter category"
                      value={filters.category}
                      onChange={(e) => filter("category", e.target.value)}
                    >
                      <option value="">All categories</option>
                      {CATEGORIES.map((p) => (
                        <option key={p} value={p}>
                          {label(p)}
                        </option>
                      ))}
                    </select>
                  </label>
                )}
              </div>
              <div className="table-scroll">
                <table>
                  <thead>
                    <tr>
                      <th>CONVERSATION</th>
                      <th>CUSTOMER</th>
                      <th>PRIORITY</th>
                      <th>STATUS</th>
                      <th>SENTIMENT</th>
                      <th>CREATED</th>
                      <th />
                    </tr>
                  </thead>
                  <tbody>
                    {loading ? (
                      <tr>
                        <td colSpan="7" className="table-state">
                          <LoaderCircle size={19} className="spin" />
                          Loading conversations…
                        </td>
                      </tr>
                    ) : tickets.items.length ? (
                      tickets.items.map((t) => (
                        <tr key={t.id} onClick={() => openTicket(t.id)}>
                          <td>
                            <button
                              className="ticket-link"
                              onClick={(e) => {
                                e.stopPropagation();
                                openTicket(t.id);
                              }}
                            >
                              <span className="ticket-number">
                                SP-{String(t.id).padStart(4, "0")}
                              </span>
                              <strong>{t.subject}</strong>
                              <small>
                                <span
                                  className="category-dot"
                                  style={{
                                    background:
                                      COLORS[t.category] || COLORS.unassigned,
                                  }}
                                />
                                {label(t.category)}
                              </small>
                            </button>
                          </td>
                          <td>
                            <div className="customer-cell">
                              <span
                                className={`customer-avatar avatar-${t.id % 4}`}
                              >
                                {t.customer_name
                                  .split(" ")
                                  .map((n) => n[0])
                                  .slice(0, 2)
                                  .join("")}
                              </span>
                              <div>
                                <strong>{t.customer_name}</strong>
                                <small>{t.customer_email}</small>
                              </div>
                            </div>
                          </td>
                          <td>
                            <Badge value={t.priority} type="priority" />
                          </td>
                          <td>
                            <Badge value={t.status} />
                          </td>
                          <td>
                            {t.sentiment ? (
                              <span className={`sentiment ${t.sentiment}`}>
                                <span>
                                  {t.sentiment === "positive"
                                    ? "☺"
                                    : t.sentiment === "negative"
                                      ? "☹"
                                      : "◉"}
                                </span>
                                {label(t.sentiment)}
                              </span>
                            ) : (
                              <span className="not-analyzed">Not analyzed</span>
                            )}
                          </td>
                          <td className="date-cell">{time(t.created_at)}</td>
                          <td>
                            <ChevronRight size={14} color="#b4bdc9" />
                          </td>
                        </tr>
                      ))
                    ) : (
                      <tr>
                        <td colSpan="7">
                          <div className="empty">
                            <MessageSquare size={29} />
                            <h3>
                              {q || Object.values(filters).some(Boolean)
                                ? "No matching conversations"
                                : "Your support story starts here"}
                            </h3>
                            <p>
                              {q || Object.values(filters).some(Boolean)
                                ? "Try a different search or filter."
                                : "Create a ticket or load the fictional demo tickets using the setup guide."}
                            </p>
                            <button
                              className="primary"
                              onClick={() => setNewTicket(true)}
                            >
                              <Plus size={14} />
                              Create a ticket
                            </button>
                          </div>
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
              <div className="table-footer">
                <span>
                  {tickets.total
                    ? `${(page - 1) * 8 + 1}–${Math.min(page * 8, tickets.total)} of ${tickets.total} conversations`
                    : "No conversations to show"}
                </span>
                <div>
                  <button
                    className="icon"
                    aria-label="Previous page"
                    disabled={page === 1}
                    onClick={() => setPage((p) => p - 1)}
                  >
                    <ChevronLeft size={15} />
                  </button>
                  <span>{page}</span>
                  <button
                    className="icon"
                    aria-label="Next page"
                    disabled={page * 8 >= tickets.total}
                    onClick={() => setPage((p) => p + 1)}
                  >
                    <ChevronRight size={15} />
                  </button>
                </div>
              </div>
            </section>
          )}
          {view === "analytics" && (
            <div className="charts-row">
              <section className="card">
                <div className="card-heading">
                  <div>
                    <h2>Sentiment over time</h2>
                    <p>
                      Analyzed tickets grouped by creation date · unknown
                      excluded
                    </p>
                  </div>
                </div>
                <div className="chart sentiment-chart">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={analytics?.trend || []}>
                      <CartesianGrid vertical={false} stroke="#edf1f5" />
                      <XAxis
                        dataKey="date"
                        tickFormatter={(v) => v.slice(5)}
                        tick={{ fontSize: 9 }}
                        axisLine={false}
                        tickLine={false}
                      />
                      <YAxis
                        allowDecimals={false}
                        tick={{ fontSize: 9 }}
                        axisLine={false}
                        tickLine={false}
                      />
                      <Tooltip />
                      <Legend wrapperStyle={{ fontSize: 10 }} />
                      {["positive", "neutral", "negative"].map((s) => (
                        <Bar
                          key={s}
                          dataKey={s}
                          stackId="sentiment"
                          fill={COLORS[s]}
                          maxBarSize={26}
                        />
                      ))}
                    </BarChart>
                  </ResponsiveContainer>
                </div>
                {!Object.keys(analytics?.sentiments || {}).some(
                  (k) => k !== "unassigned",
                ) && (
                  <p className="chart-note">
                    No sentiment inference yet. Analyze a ticket to populate
                    this chart.
                  </p>
                )}
              </section>
              <section className="card">
                <div className="card-heading">
                  <div>
                    <h2>Priority distribution</h2>
                    <p>Agent-selected priorities across all tickets</p>
                  </div>
                </div>
                <div className="priority-breakdown">
                  {[...PRIORITIES, "unassigned"].map((p) => (
                    <div key={p}>
                      <Badge value={p} type="priority" />
                      <div className="meter">
                        <span
                          style={{
                            width: `${((analytics?.priorities[p] || 0) / (analytics?.total || 1)) * 100}%`,
                            background:
                              p === "high"
                                ? "#e39794"
                                : p === "medium"
                                  ? "#edc178"
                                  : "#72b9ac",
                          }}
                        />
                      </div>
                      <strong>{analytics?.priorities[p] || 0}</strong>
                    </div>
                  ))}
                </div>
                <p className="chart-note">
                  Priority labels are not model predictions unless an agent
                  explicitly applies a suggestion.
                </p>
              </section>
            </div>
          )}
          {view === "models" && (
            <ModelLab reports={reports} onError={setError} />
          )}
          {view === "guide" && (
            <section className="card guide">
              <h2>From first ticket to a thoughtful reply.</h2>
              {[
                [
                  "01",
                  "Create a conversation",
                  "Add a customer, subject, and description. Category and priority can stay unassigned until an agent reviews them.",
                ],
                [
                  "02",
                  "Analyze with local models",
                  "Open a ticket and run AI analysis. Category uses a trained TF-IDF classifier; sentiment uses pretrained PyTorch RoBERTa when downloaded. Unavailable components stay explicit.",
                ],
                [
                  "03",
                  "Review the evidence",
                  "Check confidence, apply suggestions deliberately, and inspect held-out evaluation in AI & models. BANKING77 results are domain-specific.",
                ],
                [
                  "04",
                  "Draft, review, resolve",
                  "Generate a reply with Ollama. Edit or copy the suggestion for review. This app never sends customer messages. Mark a ticket resolved when the work is complete.",
                ],
              ].map(([n, title, text]) => (
                <article key={n}>
                  <span>{n}</span>
                  <div>
                    <h3>{title}</h3>
                    <p>{text}</p>
                  </div>
                </article>
              ))}
              <div className="guide-warning">
                <ShieldCheck size={20} />
                <div>
                  <strong>Built for a local interview demonstration</strong>
                  <p>
                    No authentication or customer email delivery is configured.
                    Use fictional tickets and loopback networking. PostgreSQL
                    and Docker instructions are in the README.
                  </p>
                </div>
              </div>
            </section>
          )}
          {view === "overview" && (
            <div className="insight-strip">
              <span className="insight-icon">
                <Sparkles size={17} />
              </span>
              <div>
                <strong>A helpful copilot. You’re still in control.</strong>
                <p>
                  AI can classify, read sentiment, and draft replies. Your team
                  makes the final call.
                </p>
              </div>
              <button onClick={() => navigate("models")}>
                Meet your AI stack
                <ArrowRight size={14} />
              </button>
            </div>
          )}
          <footer>
            <span>
              <ShieldCheck size={12} />
              Local-first support intelligence
            </span>
            <span>FastAPI · Scikit-learn · PyTorch · Ollama</span>
          </footer>
        </div>
      </main>
      {newTicket && (
        <NewTicket
          onClose={() => setNewTicket(false)}
          onCreated={(t) => {
            setNewTicket(false);
            setDetail(t);
            refresh();
            setNotice("Ticket created. Ready for a thoughtful response.");
          }}
        />
      )}
      {detail && (
        <TicketDetail
          key={detail.id}
          ticket={detail}
          onClose={() => setDetail(null)}
          onUpdate={updated}
          onNotice={setNotice}
        />
      )}
    </div>
  );
}
