function fmt(v) {
  if (v == null) return null;
  return `$${Number(v).toLocaleString()}`;
}

export default function IntakeSummaryBar({ intake, onEdit }) {
  const totalSavings = (intake.taxable_balance || 0) + (intake.tax_deferred_balance || 0) + (intake.roth_balance || 0);

  const parts = [
    intake.age != null && intake.target_retirement_age != null
      ? `Age ${intake.age} \u2192 retiring at ${intake.target_retirement_age}`
      : null,
    totalSavings > 0 ? `${fmt(totalSavings)} saved` : null,
    intake.risk_tolerance ? `${intake.risk_tolerance} risk` : null,
  ].filter(Boolean);

  return (
    <div className="intake-summary-bar">
      <span className="intake-summary-bar__text">{parts.join(" \u00b7 ")}</span>
      <button className="intake-summary-bar__edit" onClick={onEdit}>Edit</button>
    </div>
  );
}