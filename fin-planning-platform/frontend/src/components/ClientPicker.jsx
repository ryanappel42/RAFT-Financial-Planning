import { useEffect, useState } from "react";
import { fetchClients } from "../api";

export default function ClientPicker({ selectedId, onSelect }) {
  const [clients, setClients] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchClients().then(setClients).catch((err) => setError(err.message));
  }, []);

  return (
    <div className="client-picker">
      <div className="client-picker__label">Clients</div>
      <div className="client-picker__rule" />

      {error && <div className="client-picker__error">{error}</div>}

      {!clients && !error && <div className="client-picker__loading">Loading&hellip;</div>}

      {clients &&
        Object.entries(clients).map(([id, name]) => (
          <button
            key={id}
            className={`client-picker__item ${id === selectedId ? "client-picker__item--active" : ""}`}
            onClick={() => onSelect(id)}
          >
            {name}
          </button>
        ))}
    </div>
  );
}
