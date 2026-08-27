import { formatCurrency } from "../../utils/format";

export default function WithdrawalResult({ result, accentVar }) {
  const { years_lasted, depleted, total_tax_paid, final_balance } = result;
  const color = `var(${accentVar})`;

  return (
    <div className="result-card">
      <div className="result-card__label">Withdrawal projection</div>
      <div className="result-card__body result-card__body--stats">
        <div className="stat-block">
          <div className="stat-block__value mono" style={{ color }}>
            {years_lasted}
            <span className="stat-block__unit"> yrs</span>
          </div>
          <div className="stat-block__label">
            {depleted ? "Portfolio depleted at" : "Portfolio lasts through"}
          </div>
        </div>

        <div className="stat-block">
          <div className="stat-block__value mono">{formatCurrency(total_tax_paid)}</div>
          <div className="stat-block__label">Total tax paid</div>
        </div>

        <div className="stat-block">
          <div className="stat-block__value mono">{formatCurrency(final_balance)}</div>
          <div className="stat-block__label">Ending balance</div>
        </div>
      </div>

      {depleted && (
        <div className="result-card__flag">Portfolio does not last the full horizon under these assumptions</div>
      )}
    </div>
  );
}
