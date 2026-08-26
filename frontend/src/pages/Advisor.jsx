import { useState } from "react";
import { Link } from "react-router-dom";
import ChatWindow from "../components/ChatWindow";
import ClientPicker from "../components/ClientPicker";

export default function Advisor() {
  const [clientId, setClientId] = useState(null);

  return (
    <div className="app-page app-page--advisor">
      <header className="app-header">
        <Link to="/" className="app-header__mark">LEDGER</Link>
        <div className="app-header__title">For clients</div>
        <div className="app-header__powered-by">RAFT, powered by Claude</div>
      </header>

      <div className="app-body app-body--split">
        <ClientPicker selectedId={clientId} onSelect={setClientId} />
        <ChatWindow
          mode="advisor"
          clientId={clientId}
          accentVar="--brass"
          placeholder="Ask about this client's readiness, drawdown, or drift&hellip;"
          disabled={!clientId}
        />
      </div>
    </div>
  );
}
