import { formatCurrency } from "../../utils/format";

export default function RebalancingResult({ result, accentVar }) {
  const { trades, total_capital_gains_tax, total_portfolio_value } = result;
  const color = `var(${accentVar})`;

  return (
    <div className="result-card">
      <div className="result-card__label">Rebalancing trades</div>

      <div className="result-card__body result-card__body--stats">
        <div className="stat-block">
          <div className="stat-block__value mono">{formatCurrency(total_portfolio_value)}</div>
          <div className="stat-block__label">Total portfolio</div>
        </div>
        <div className="stat-block">
          <div className="stat-block__value mono" style={{ color: total_capital_gains_tax > 0 ? "#A9823C" : color }}>
            {formatCurrency(total_capital_gains_tax)}
          </div>
          <div className="stat-block__label">Capital gains tax</div>
        </div>
      </div>

      {trades && trades.length > 0 ? (
        <table className="trades-table">
          <thead>
            <tr>
              <th>Account</th>
              <th>Asset</th>
              <th>Action</th>
              <th>Amount</th>
            </tr>
          </thead>
          <tbody>
            {trades.map((t, i) => (
              <tr key={i}>
                <td>{t.account_type.replace("_", " ")}</td>
                <td>{t.asset_class.replace("_", " ")}</td>
                <td>
                  <span className={`trade-action trade-action--${t.action}`}>{t.action}</span>
                </td>
                <td className="mono">{formatCurrency(t.amount)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : (
        <div className="result-card__flag">No trades needed, portfolio is already at target</div>
      )}
    </div>
  );
}
