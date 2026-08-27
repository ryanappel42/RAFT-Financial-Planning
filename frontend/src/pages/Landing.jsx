import { Link } from "react-router-dom";
import CompoundingCurve from "../components/CompoundingCurve";
import SiteNav from "../components/SiteNav";

export default function Landing() {
  return (
    <div className="landing">
      <SiteNav dark active="home" />

      <div className="landing__content-wrap">
        <div className="landing__inner">
          <h1 className="landing__headline">
            A financial plan<br />you can actually<br />interrogate.
          </h1>

          <p className="landing__sub">
            Real retirement, withdrawal, and tax math underneath.
            Claude explains it, never guesses it.
          </p>

          <CompoundingCurve className="landing__curve" />

          <div className="landing__entries">
            <Link to="/consumer" className="entry-card entry-card--consumer">
              <div className="entry-card__eyebrow">01</div>
              <div className="entry-card__title">For yourself</div>
              <div className="entry-card__desc">
                Talk through your own retirement readiness, withdrawal plan, or portfolio.
              </div>
            </Link>

            <Link to="/advisor" className="entry-card entry-card--advisor">
              <div className="entry-card__eyebrow">02</div>
              <div className="entry-card__title">For clients</div>
              <div className="entry-card__desc">
                Pull up a client, review their numbers, and prep tax-aware recommendations.
              </div>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}