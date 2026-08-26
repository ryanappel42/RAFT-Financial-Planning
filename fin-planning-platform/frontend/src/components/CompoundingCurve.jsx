export default function CompoundingCurve({ stroke = "var(--emerald)", className = "" }) {
  // A hand-drawn-feeling exponential curve, low points early, steep late,
  // echoing compound growth. Animates in via stroke-dashoffset on mount.
  return (
    <svg
      className={`compounding-curve ${className}`}
      viewBox="0 0 600 200"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden="true"
    >
      <path
        d="M 10 180 C 120 175, 220 165, 300 140 C 380 115, 430 70, 480 40 C 520 18, 555 8, 590 4"
        stroke={stroke}
        strokeWidth="2.5"
        strokeLinecap="round"
        className="compounding-curve__path"
      />
      {[
        [10, 180], [150, 172], [300, 140], [420, 90], [590, 4],
      ].map(([x, y], i) => (
        <circle key={i} cx={x} cy={y} r="3" fill={stroke} className="compounding-curve__dot" style={{ animationDelay: `${0.9 + i * 0.15}s` }} />
      ))}
    </svg>
  );
}
