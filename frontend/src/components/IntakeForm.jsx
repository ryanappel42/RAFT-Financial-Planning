import { useState } from "react";

const RISK_OPTIONS = [
  { value: "conservative", label: "Conservative" },
  { value: "moderate", label: "Moderate" },
  { value: "aggressive", label: "Aggressive" },
];

const FILING_OPTIONS = [
  { value: "single", label: "Single" },
  { value: "married_filing_jointly", label: "Married filing jointly" },
  { value: "head_of_household", label: "Head of household" },
];

const initialForm = {
  age: "",
  target_retirement_age: "",
  taxable_balance: "",
  tax_deferred_balance: "",
  roth_balance: "",
  annual_contribution: "",
  risk_tolerance: "",
  filing_status: "",
  target_balance: "",
};

const REQUIRED_FIELDS = ["age", "target_retirement_age", "annual_contribution", "risk_tolerance", "filing_status"];

export default function IntakeForm({ onSubmit }) {
  const [form, setForm] = useState(initialForm);

  const isValid = REQUIRED_FIELDS.every((f) => form[f] !== "");

  function update(field, value) {
    setForm((prev) => ({ ...prev, [field]: value }));
  }

  function handleSubmit(e) {
    e.preventDefault();
    if (!isValid) return;

    const numeric = (v) => (v === "" ? null : Number(v));

    onSubmit({
      age: numeric(form.age),
      target_retirement_age: numeric(form.target_retirement_age),
      taxable_balance: numeric(form.taxable_balance) ?? 0,
      tax_deferred_balance: numeric(form.tax_deferred_balance) ?? 0,
      roth_balance: numeric(form.roth_balance) ?? 0,
      annual_contribution: numeric(form.annual_contribution),
      risk_tolerance: form.risk_tolerance,
      filing_status: form.filing_status,
      target_balance: numeric(form.target_balance),
    });
  }

  return (
    <div className="intake-wrap">
      <form className="intake-form" onSubmit={handleSubmit}>
        <div className="intake-form__header">
          <div className="intake-form__eyebrow">Before we begin</div>
          <h2 className="intake-form__title">Tell us about your plan</h2>
          <p className="intake-form__sub">
            This lets RAFT skip the back and forth and get straight to the numbers.
            Anything you don't know, leave blank and it'll ask.
          </p>
        </div>

        <div className="intake-form__grid">
          <label className="intake-field">
            <span className="intake-field__label">Your age *</span>
            <input type="number" min="0" value={form.age} onChange={(e) => update("age", e.target.value)} />
          </label>

          <label className="intake-field">
            <span className="intake-field__label">Target retirement age *</span>
            <input type="number" min="0" value={form.target_retirement_age} onChange={(e) => update("target_retirement_age", e.target.value)} />
          </label>

          <label className="intake-field">
            <span className="intake-field__label">Taxable brokerage balance</span>
            <input type="number" min="0" placeholder="0" value={form.taxable_balance} onChange={(e) => update("taxable_balance", e.target.value)} />
          </label>

          <label className="intake-field">
            <span className="intake-field__label">401(k) / traditional IRA balance</span>
            <input type="number" min="0" placeholder="0" value={form.tax_deferred_balance} onChange={(e) => update("tax_deferred_balance", e.target.value)} />
          </label>

          <label className="intake-field">
            <span className="intake-field__label">Roth balance</span>
            <input type="number" min="0" placeholder="0" value={form.roth_balance} onChange={(e) => update("roth_balance", e.target.value)} />
          </label>

          <label className="intake-field">
            <span className="intake-field__label">Annual contribution *</span>
            <input type="number" min="0" value={form.annual_contribution} onChange={(e) => update("annual_contribution", e.target.value)} />
          </label>

          <label className="intake-field">
            <span className="intake-field__label">Risk tolerance *</span>
            <select value={form.risk_tolerance} onChange={(e) => update("risk_tolerance", e.target.value)}>
              <option value="" disabled>Select one</option>
              {RISK_OPTIONS.map((o) => (
                <option key={o.value} value={o.value}>{o.label}</option>
              ))}
            </select>
          </label>

          <label className="intake-field">
            <span className="intake-field__label">Filing status *</span>
            <select value={form.filing_status} onChange={(e) => update("filing_status", e.target.value)}>
              <option value="" disabled>Select one</option>
              {FILING_OPTIONS.map((o) => (
                <option key={o.value} value={o.value}>{o.label}</option>
              ))}
            </select>
          </label>

          <label className="intake-field">
            <span className="intake-field__label">Target retirement balance (optional)</span>
            <input type="number" min="0" placeholder="No target in mind" value={form.target_balance} onChange={(e) => update("target_balance", e.target.value)} />
          </label>
        </div>

        <button type="submit" className="intake-form__submit" disabled={!isValid}>
          Start planning
        </button>
      </form>
    </div>
  );
}