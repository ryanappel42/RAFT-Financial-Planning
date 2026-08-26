import { useState, useRef, useEffect } from "react";
import { sendMessage } from "../api";

export default function ChatWindow({ mode, clientId, accentVar, placeholder, disabled }) {
  const [messages, setMessages] = useState([]); // { role, text }
  const [input, setInput] = useState("");
  const [sessionId, setSessionId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const scrollRef = useRef(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, loading]);

  // Reset conversation when the advisor switches clients
  useEffect(() => {
    setMessages([]);
    setSessionId(null);
    setError(null);
  }, [clientId]);

  async function handleSend() {
    const text = input.trim();
    if (!text || loading || disabled) return;

    setMessages((prev) => [...prev, { role: "user", text }]);
    setInput("");
    setLoading(true);
    setError(null);

    try {
      const result = await sendMessage({ sessionId, message: text, mode, clientId });
      setSessionId(result.session_id);
      setMessages((prev) => [...prev, { role: "RAFT", text: result.reply }]);
    } catch (err) {
      setError(err.message || "Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  function handleKeyDown(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  return (
    <div className="chat-window">
      <div className="chat-scroll" ref={scrollRef}>
        {messages.length === 0 && (
          <div className="chat-empty">
            <p>No entries yet.</p>
          </div>
        )}

        {messages.map((m, i) => (
          <div key={i} className={`chat-entry chat-entry--${m.role}`}>
            <div className="chat-entry__label" style={{ color: `var(${accentVar})` }}>
              {m.role === "user" ? "You" : "RAFT"}
            </div>
            <div className="chat-entry__text">{m.text}</div>
          </div>
        ))}

        {loading && (
          <div className="chat-entry chat-entry--assistant">
            <div className="chat-entry__label" style={{ color: `var(${accentVar})` }}>RAFT</div>
            <div className="chat-entry__text chat-entry__text--pending">Working it out&hellip;</div>
          </div>
        )}

        {error && <div className="chat-error">{error}</div>}
      </div>

      <div className="chat-input-row">
        <textarea
          className="chat-input"
          rows={1}
          placeholder={disabled ? "Select a client to begin" : placeholder}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={disabled}
        />
        <button
          className="chat-send"
          style={{ background: `var(${accentVar})` }}
          onClick={handleSend}
          disabled={disabled || loading || !input.trim()}
        >
          Send
        </button>
      </div>
    </div>
  );
}
