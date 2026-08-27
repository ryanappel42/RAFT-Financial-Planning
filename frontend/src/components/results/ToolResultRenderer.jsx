import RetirementResult from "./RetirementResult";
import WithdrawalResult from "./WithdrawalResult";
import RebalancingResult from "./RebalancingResult";

const RESULT_COMPONENTS = {
  run_retirement_monte_carlo: RetirementResult,
  run_withdrawal_sequencing: WithdrawalResult,
  run_portfolio_rebalancing: RebalancingResult,
};

export default function ToolResultRenderer({ toolCalls, accentVar }) {
  if (!toolCalls || toolCalls.length === 0) return null;

  return (
    <div className="result-card-stack">
      {toolCalls.map((call, i) => {
        const Component = RESULT_COMPONENTS[call.tool_name];
        if (!Component) return null;
        return <Component key={i} result={call.result} accentVar={accentVar} />;
      })}
    </div>
  );
}
