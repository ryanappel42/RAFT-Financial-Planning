import { useState } from "react";
import { Link } from "react-router-dom";
import ChatWindow from "../components/ChatWindow";
import IntakeForm from "../components/IntakeForm";
import IntakeSummaryBar from "../components/IntakeSummaryBar";

export default function Consumer() {
  const [intake, setIntake] = useState(null);

  return (
    <div className="app-page app-page--consumer">
      <header className="app-header">
        <Link to="/" className="app-header__mark">LEDGER</Link>
        <div className="app-header__title">For yourself</div>
        <div className="app-header__powered-by">RAFT, powered by Claude</div>
      </header>

      {intake && <IntakeSummaryBar intake={intake} onEdit={() => setIntake(null)} />}

      {!intake ? (
        <IntakeForm onSubmit={setIntake} />
      ) : (
        <div className="app-body app-body--single">
          <ChatWindow
            mode="consumer"
            intake={intake}
            accentVar="--emerald"
            placeholder="Ask about your retirement, withdrawals, or portfolio&hellip;"
          />
        </div>
      )}
    </div>
  );
}