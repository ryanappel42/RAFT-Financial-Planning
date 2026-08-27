import { useState } from "react";
import ChatWindow from "../components/ChatWindow";
import IntakeForm from "../components/IntakeForm";
import IntakeSummaryBar from "../components/IntakeSummaryBar";
import SiteNav from "../components/SiteNav";

const STORAGE_KEY = "raft_intake_v1";

function loadSavedIntake() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

function saveIntake(data) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
  } catch {
    // localStorage unavailable (private browsing, etc.), form still works, just won't persist
  }
}

export default function Consumer() {
  const [intake, setIntake] = useState(loadSavedIntake);
  const [showForm, setShowForm] = useState(() => !loadSavedIntake());

  function handleSubmit(data) {
    setIntake(data);
    saveIntake(data);
    setShowForm(false);
  }

  return (
    <div className="app-page app-page--consumer">
      <SiteNav
        active="consumer"
        title="For yourself"
        right={<span>RAFT, powered by Claude</span>}
      />

      {intake && !showForm && (
        <IntakeSummaryBar intake={intake} onEdit={() => setShowForm(true)} />
      )}

      {showForm ? (
        <IntakeForm onSubmit={handleSubmit} initialValues={intake} />
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