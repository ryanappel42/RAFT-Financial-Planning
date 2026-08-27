import ScoreGauge from "./ScoreGauge";
import { formatCurrency } from "../../utils/format";

export default function RetirementResult({ result, accentVar }) {
  const { median_balance, percentile_10, percentile_90, probability_of_success } = result;
  const color = `var(${accentVar})`;

  // Position markers along a 0 -> percentile_90 scale for the range bar
  const max = percentile_90 || 1;
  const pct10 = Math.min(100, (percentile_10 / max) * 100);
  const pctMedian = Math.min(100, (median_balance / max) * 100);

  return (
    <div className="result-card">
      <div className="result-card__label">Retirement projection</div>
      <div className="result-card__body result-card__body--gauge">
        {probability_of_success != null && (
          <ScoreGauge value={probability_of_success} label="Success" color={color} />
        )}

        <div className="result-range">
          <div className="result-range__track">
            <div className="result-range__fill" style={{ width: `${pctMedian}%`, background: color }} />
            <div className="result-range__marker" style={{ left: `${pct10}%` }} title="10th percentile" />
            <div className="result-range__marker result-range__marker--median" style={{ left: `${pctMedian}%`, background: color }} title="Median" />
          </div>
          <div className="result-range__labels">
            <div className="result-range__stat">
              <div className="result-range__stat-label">10th percentile</div>
              <div className="result-range__stat-value mono">{formatCurrency(percentile_10)}</div>
            </div>
            <div className="result-range__stat">
              <div className="result-range__stat-label">Median</div>
              <div className="result-range__stat-value mono">{formatCurrency(median_balance)}</div>
            </div>
            <div className="result-range__stat">
              <div className="result-range__stat-label">90th percentile</div>
              <div className="result-range__stat-value mono">{formatCurrency(percentile_90)}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
