import SiteNav from "../components/SiteNav";

export default function About() {
  return (
    <div className="app-page">
      <SiteNav active="about" />

      <div className="about-page">
        <div className="about-content">
          <section className="about-section">
            <div className="about-section__eyebrow">The platform</div>
            <h2>What is Ledger?</h2>
            <p>
              Ledger is a full financial planning platform built as a portfolio project.
              Underneath the chat interface sits a real calculation engine, not an LLM
              guessing at numbers: deterministic and Monte Carlo retirement projections,
              tax-aware withdrawal sequencing across taxable, tax-deferred, and Roth
              accounts using real 2026 IRS tax brackets, and tax-aware portfolio
              rebalancing, all written in Python and verified against hand-calculated
              cases.
            </p>
            <p>
              RAFT, the assistant built on Claude, sits on top as the conversational
              layer. It never estimates results itself, it calls the real engine and
              explains what comes back. Two modes cover two audiences: <strong>For
              yourself</strong>, for individuals exploring their own retirement plan,
              and <strong>For clients</strong>, for financial advisors reviewing and
              prepping for client conversations.
            </p>
          </section>

          <hr className="about-rule" />

          <section className="about-section">
            <div className="about-section__eyebrow">The creator</div>
            <h2>Ryan Appel</h2>
            <p>
              Ryan is a student at Virginia Tech's Pamplin College of Business, studying
              Financial Planning and Wealth Management with a minor in FinTech and
              Artificial Intelligence. He's currently a Service Data Analyst intern at
              LPL Financial, holds VP roles in Delta Sigma Pi (Professional Activities)
              and Phi Delta Theta, and sits on the Pamplin Dean's Advisory Board of
              Students.
            </p>
            <p>
              He built Ledger to explore the intersection of financial planning, AI,
              and technical finance, the space he wants to build a career around.
            </p>
            <div className="about-links">
              <a href="https://www.linkedin.com/in/ryanappel06/" target="_blank" rel="noreferrer">LinkedIn</a>
              <a href="https://github.com/ryanappel42" target="_blank" rel="noreferrer">GitHub</a>
              <a href="mailto:ryanca312@gmail.com">Email</a>
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}