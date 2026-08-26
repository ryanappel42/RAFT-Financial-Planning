import { Link } from "react-router-dom";
import ChatWindow from "../components/ChatWindow";

export default function Consumer() {
  return (
    <div className="app-page app-page--consumer">
      <header className="app-header">
        <Link to="/" className="app-header__mark">LEDGER</Link>
        <div className="app-header__title">For yourself</div>
      </header>

      <div className="app-body app-body--single">
        <ChatWindow
          mode="consumer"
          accentVar="--emerald"
          placeholder="Ask about your retirement, withdrawals, or portfolio&hellip;"
        />
      </div>
    </div>
  );
}
