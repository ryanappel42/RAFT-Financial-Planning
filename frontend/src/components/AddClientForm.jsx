import { useState } from "react";

const FILING_OPTIONS = [
  { value: "single", label: "Single" },
  { value: "married_filing_jointly", label: "Married filing jointly" },
  { value: "head_of_household", label: "Head of household" },
];

const initialForm = {
  name: "",
  age: "",
  target_retirement_age: "",
  filing_status: "",
  taxable_balance: "",
  taxable_cost_basis: "",
  tax_deferred_balance: "",
  roth_balance: "",
  us_stocks_pct: "",
  intl_stocks_pct: "",
  bonds_pct: "",
  notes: "",
};

const REQUIRED_FIELDS = ["name", "age", "target_retirement_age", "filing_status"];

export default function AddClientForm({ onSubmit, onCancel }) {
  const [form, setForm] = useState(initialForm);

  const isValid = REQUIRED_FIELDS.every((f) => form[f] !== "");
  const allocationTotal =
    (Number(form.us_stocks_pct) || 0) + (Number(form.intl_stocks_pct) || 0) + (Number(form.bonds_pct) || 0);

  function update(field, value) {
    setForm((prev) => ({ ...prev, [field]: value }));
  }

  function handleSubmit(e) {
    e.preventDefault();
    if (!isValid) return;

    const num = (v, fallback = 0) => (v === "" ? fallback : Number(v));

    const target_allocation = {};
    if (form.us_stocks_pct !== "") target_allocation.us_stocks = num(form.us_stocks_pct) / 100;
    if (form.intl_stocks_pct !== "") target_allocation.intl_stocks = num(form.intl_stocks_pct) / 100;
    if (form.bonds_pct !== "") target_allocation.bonds = num(form.bonds_pct) / 100;

    onSubmit({
      name: form.name,
      age: num(form.age, null),
      target_retirement_age: num(form.target_retirement_age, null),
      filing_status: form.filing_status,
      accounts: {
        taxable_balance: num(form.taxable_balance),
        taxable_cost_basis: num(form.taxable_cost_basis),
        tax_deferred_balance: num(form.tax_deferred_balance),
        roth_balance: num(form.roth_balance),
      },
      target_allocation,
      notes: form.notes,
    });
  }

  return (
    <div className="intake-wrap">
      <form className="intake-form" onSubmit={handleSubmit}>
        <div className="intake-form__header">
          <div className="intake-form__eyebrow" style={{ color: "var(--brass)" }}>New client</div>
          <h2 className="intake-form__title">Add a client</h2>
          <p className="intake-form__sub">
            This client is available for the rest of your session. It isn't saved anywhere,
            so it'll be gone after a page refresh.
          </p>
        </div>

        <div className="intake-form__grid">
          <label className="intake-field">
            <span className="intake-field__label">Client name *</span>
            <input type="text" value={form.name} onChange={(e) => update("name", e.target.value)} />
          </label>

          <label className="intake-field">
            <span className="intake-field__label">Age *</span>
            <input type="number" min="0" value={form.age} onChange={(e) => update("age", e.target.value)} />
          </label>

          <label className="intake-field">
            <span className="intake-field__label">Target retirement age *</span>
            <input type="number" min="0" value={form.target_retirement_age} onChange={(e) => update("target_retirement_age", e.target.value)} />
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
            <span className="intake-field__label">Taxable brokerage balance</span>
            <input type="number" min="0" placeholder="0" value={form.taxable_balance} onChange={(e) => update("taxable_balance", e.target.value)} />
          </label>

          <label className="intake-field">
            <span className="intake-field__label">Taxable cost basis</span>
            <input type="number" min="0" placeholder="0" value={form.taxable_cost_basis} onChange={(e) => update("taxable_cost_basis", e.target.value)} />
          </label>

          <label className="intake-field">
            <span className="intake-field__label">Tax-deferred balance</span>
            <input type="number" min="0" placeholder="0" value={form.tax_deferred_balance} onChange={(e) => update("tax_deferred_balance", e.target.value)} />
          </label>

          <label className="intake-field">
            <span className="intake-field__label">Roth balance</span>
            <input type="number" min="0" placeholder="0" value={form.roth_balance} onChange={(e) => update("roth_balance", e.target.value)} />
          </label>

          <label className="intake-field">
            <span className="intake-field__label">Target: US stocks %</span>
            <input type="number" min="0" max="100" placeholder="0" value={form.us_stocks_pct} onChange={(e) => update("us_stocks_pct", e.target.value)} />
          </label>

          <label className="intake-field">
            <span className="intake-field__label">Target: Intl stocks %</span>
            <input type="number" min="0" max="100" placeholder="0" value={form.intl_stocks_pct} onChange={(e) => update("intl_stocks_pct", e.target.value)} />
          </label>

          <label className="intake-field">
            <span className="intake-field__label">Target: Bonds %</span>
            <input type="number" min="0" max="100" placeholder="0" value={form.bonds_pct} onChange={(e) => update("bonds_pct", e.target.value)} />
          </label>

          <div className="intake-field">
            <span className="intake-field__label">Allocation total</span>
            <span className={`allocation-total ${allocationTotal !== 100 && allocationTotal !== 0 ? "allocation-total--warn" : ""}`}>
              {allocationTotal}%
            </span>
          </div>
        </div>

        <label className="intake-field intake-field--full">
          <span className="intake-field__label">Notes</span>
          <textarea rows={2} value={form.notes} onChange={(e) => update("notes", e.target.value)} />
        </label>

        <div className="intake-form__actions">
          <button type="submit" className="intake-form__submit" style={{ background: "var(--brass)" }} disabled={!isValid}>
            Add client
          </button>
          <button type="button" className="intake-form__cancel" onClick={onCancel}>
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
}