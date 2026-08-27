import { formatCurrency, formatPercent } from "../utils/format";

const FILING_LABELS = {
  single: "Single",
  married_filing_jointly: "Married filing jointly",
  head_of_household: "Head of household",
};

const ASSET_LABELS = {
  us_stocks: "US stocks",
  intl_stocks: "Intl stocks",
  bonds: "Bonds",
};

export default function ClientDetailCard({ client }) {
  const accts = client.accounts || {};
  const totalBalance = (accts.taxable_balance || 0) + (accts.tax_deferred_balance || 0) + (accts.roth_balance || 0);
  const allocation = Object.entries(client.target_allocation || {});

  return (
    <div className="client-detail">
      <div className="client-detail__header">
        <div className="client-detail__name">{client.name}</div>
        <div className="client-detail__meta">
          Age {client.age ?? "—"} &middot; retiring at {client.target_retirement_age ?? "—"} &middot; {FILING_LABELS[client.filing_status] || client.filing_status}
        </div>
      </div>

      <div className="client-detail__balances">
        <div className="client-detail__balance">
          <div className="client-detail__balance-label">Taxable</div>
          <div className="client-detail__balance-value mono">{formatCurrency(accts.taxable_balance)}</div>
        </div>
        <div className="client-detail__balance">
          <div className="client-detail__balance-label">Tax-deferred</div>
          <div className="client-detail__balance-value mono">{formatCurrency(accts.tax_deferred_balance)}</div>
        </div>
        <div className="client-detail__balance">
          <div className="client-detail__balance-label">Roth</div>
          <div className="client-detail__balance-value mono">{formatCurrency(accts.roth_balance)}</div>
        </div>
        <div className="client-detail__balance client-detail__balance--total">
          <div className="client-detail__balance-label">Total</div>
          <div className="client-detail__balance-value mono">{formatCurrency(totalBalance)}</div>
        </div>
      </div>

      {allocation.length > 0 && (
        <div className="client-detail__allocation">
          {allocation.map(([asset, frac]) => (
            <span key={asset} className="allocation-chip">
              {ASSET_LABELS[asset] || asset}: {formatPercent(frac)}
            </span>
          ))}
        </div>
      )}

      {client.notes && <div className="client-detail__notes">{client.notes}</div>}
    </div>
  );
}