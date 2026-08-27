import { RadialBarChart, RadialBar, PolarAngleAxis } from "recharts";

export default function ScoreGauge({ value, label, color = "var(--emerald)" }) {
  // value is a 0-1 fraction
  const pct = Math.round(value * 100);
  const data = [{ value: pct, fill: color }];

  return (
    <div className="score-gauge">
      <RadialBarChart
        width={140}
        height={140}
        cx={70}
        cy={70}
        innerRadius={52}
        outerRadius={68}
        barSize={12}
        data={data}
        startAngle={90}
        endAngle={-270}
      >
        <PolarAngleAxis type="number" domain={[0, 100]} angleAxisId={0} tick={false} />
        <RadialBar background={{ fill: "var(--bone-dim)" }} dataKey="value" cornerRadius={6} />
      </RadialBarChart>
      <div className="score-gauge__center">
        <div className="score-gauge__value mono">{pct}%</div>
        {label && <div className="score-gauge__label">{label}</div>}
      </div>
    </div>
  );
}
