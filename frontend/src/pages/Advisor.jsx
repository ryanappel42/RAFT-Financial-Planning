import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import ChatWindow from "../components/ChatWindow";
import ClientPicker from "../components/ClientPicker";
import AddClientForm from "../components/AddClientForm";
import ClientDetailCard from "../components/ClientDetailCard";
import { fetchClients } from "../api";

export default function Advisor() {
  const [clients, setClients] = useState({});
  const [selectedId, setSelectedId] = useState(null);
  const [showAddForm, setShowAddForm] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchClients()
      .then((data) => {
        const withIds = Object.fromEntries(
          Object.entries(data).map(([id, c]) => [id, { ...c, id }])
        );
        setClients(withIds);
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  function handleAddClient(newClientData) {
    const id = `local-${Date.now()}`;
    const newClient = { ...newClientData, id };
    setClients((prev) => ({ ...prev, [id]: newClient }));
    setSelectedId(id);
    setShowAddForm(false);
  }

  const selectedClient = selectedId ? clients[selectedId] : null;

  return (
    <div className="app-page app-page--advisor">
      <header className="app-header">
        <Link to="/" className="app-header__mark">LEDGER</Link>
        <div className="app-header__title">For clients</div>
        <div className="app-header__powered-by">RAFT, powered by Claude</div>
      </header>

      <div className="app-body app-body--split">
        <ClientPicker
          clients={clients}
          selectedId={selectedId}
          onSelect={(id) => { setSelectedId(id); setShowAddForm(false); }}
          onAddClick={() => setShowAddForm(true)}
          loading={loading}
          error={error}
        />

        {showAddForm ? (
          <AddClientForm onSubmit={handleAddClient} onCancel={() => setShowAddForm(false)} />
        ) : selectedClient ? (
          <div className="advisor-main">
            <ClientDetailCard client={selectedClient} />
            <ChatWindow
              mode="advisor"
              client={selectedClient}
              accentVar="--brass"
              placeholder="Ask about this client's readiness, drawdown, or drift&hellip;"
            />
          </div>
        ) : (
          <div className="advisor-empty">
            <p>Select a client, or add a new one, to get started.</p>
          </div>
        )}
      </div>
    </div>
  );
}