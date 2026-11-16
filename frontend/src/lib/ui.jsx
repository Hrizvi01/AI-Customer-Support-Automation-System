import React from "react";
import { LoaderCircle } from "lucide-react";
const CATEGORIES = ["billing", "technical", "account", "general"],
  PRIORITIES = ["low", "medium", "high"],
  STATUSES = ["open", "in_progress", "resolved"];
const COLORS = {
  billing: "#6986ee",
  technical: "#46b8b3",
  account: "#b493dd",
  general: "#f1be69",
  positive: "#39b89f",
  negative: "#e38b94",
  neutral: "#a3b1c9",
  unassigned: "#d4dce7",
};
const label = (value) => (value || "unassigned").replaceAll("_", " ");
const date = (value) =>
  new Date(
    value.endsWith("Z") || /[+-]\d\d:\d\d$/.test(value) ? value : value + "Z",
  );
const time = (value) =>
  date(value).toLocaleDateString(undefined, { month: "short", day: "numeric" });
const percent = (value) => `${(value * 100).toFixed(1)}%`;
function Badge({ value, type = "" }) {
  return (
    <span className={`badge ${value || "unassigned"} ${type}`}>
      <i />
      {label(value)}
    </span>
  );
}
function Button({ children, loading, ...props }) {
  return (
    <button {...props} disabled={props.disabled || loading}>
      {loading ? <LoaderCircle size={15} className="spin" /> : null}
      {children}
    </button>
  );
}

export {
  CATEGORIES,
  PRIORITIES,
  STATUSES,
  COLORS,
  label,
  time,
  percent,
  Badge,
  Button,
};
