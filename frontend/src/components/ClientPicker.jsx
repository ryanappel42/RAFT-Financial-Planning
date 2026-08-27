export default function ClientPicker({ clients, selectedId, onSelect, onAddClick, loading, error }) {
  const entries = Object.entries(clients || {});

  return (
    <div className="client-picker">
      <div className="client-picker__label">Clients</div>
      <div className="client-picker__rule" />

      <button className="client-picker__add" onClick={onAddClick}>+ Add client</button>

      {error && <div className="client-picker__error">{error}</div>}
      {loading && !error && <div className="client-picker__loading">Loading&hellip;</div>}
      {!loading && !error && entries.length === 0 && (
        <div className="client-picker__loading">No clients yet</div>
      )}

      {entries.map(([id, c]) => (
        <button
          key={id}
          className={`client-picker__item ${id === selectedId ? "client-picker__item--active" : ""}`}
          onClick={() => onSelect(id)}
        >
          {c.name}
        </button>
      ))}
    </div>
  );
}