import { Link } from "react-router-dom";

export default function SiteNav({ dark = false, active, title, right }) {
  return (
    <header className={`site-nav ${dark ? "site-nav--dark" : ""}`}>
      <div className="site-nav__left">
        <Link to="/" className="site-nav__mark">LEDGER</Link>
        {title && <span className="site-nav__title">{title}</span>}
      </div>

      <nav className="site-nav__links">
        <Link to="/consumer" className={active === "consumer" ? "site-nav__link--active" : ""}>For yourself</Link>
        <Link to="/advisor" className={active === "advisor" ? "site-nav__link--active" : ""}>For clients</Link>
        <Link to="/about" className={active === "about" ? "site-nav__link--active" : ""}>About</Link>
      </nav>

      {right && <div className="site-nav__right">{right}</div>}
    </header>
  );
}