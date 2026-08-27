export function formatCurrency(value) {
  if (value == null) return "—";
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(value);
}

export function formatPercent(value) {
  if (value == null) return "—";
  return `${Math.round(value * 100)}%`;
}
