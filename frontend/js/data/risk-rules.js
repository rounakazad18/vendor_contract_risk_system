// data/risk-rules.js — Pattern-based risk detection rules (11 rules)

export const RISK_RULES = [
  {
    pattern: /one\s*\(1\)\s*month|1\s*month|three\s*\(3\)\s*months/i,
    weight: 48,
    violation: "Vendor liability cap is severely below the mandatory 12-month fees floor (2x/24-month super-cap for data/IP).",
    unfavorable: "Caps Vendor aggregate liability at 1 month of fees while exposing Customer to disproportionate loss.",
    missing: "Mutual 12-month fee general liability cap and 3x super-cap for data security and IP indemnification."
  },
  {
    pattern: /in\s+no\s+event\s+shall\s+vendor\s+be\s+liable\s+for\s+any\s+indirect|excludes\s+data\s+breach\s+from\s+cap/i,
    weight: 47,
    violation: "One-sided consequential damages waiver and exclusion of super-cap carve-outs (data breach, confidentiality, IP indemnity).",
    unfavorable: "Customer waives consequential damages while Customer's liability to Vendor remains uncapped.",
    missing: "Mutual consequential damages waiver and mandatory super-cap carve-outs."
  },
  {
    pattern: /ten\s*\(10\)\s*business\s+days|10\s+business\s+days/i,
    weight: 49,
    violation: "Security incident notification window (10 business days) violates the strict 24-hour playbook mandate.",
    unfavorable: "Delays breach reporting up to 240 hours, jeopardizing GDPR/CCPA/CERT-In regulatory reporting deadlines.",
    missing: "Mandatory 24-hour Security Incident notification commitment."
  },
  {
    pattern: /train\s+its\s+artificial\s+intelligence|foundation\s+models|machine\s+learning\s+models/i,
    weight: 47,
    violation: "Express violation of Company AI Governance Policy prohibiting Vendor from training AI/ML models on Customer Data.",
    unfavorable: "Grants Vendor a perpetual, royalty-free license to train commercial foundation models on Customer Confidential Data.",
    missing: "Explicit prohibition against using Customer Data, prompts, or outputs to train shared or third-party AI/ML models."
  },
  {
    pattern: /belong\s+exclusively\s+to\s+vendor|derivative\s+works.*sole\s+property\s+of\s+vendor/i,
    weight: 88,
    violation: "Assigns ownership of paid custom deliverables and derivative works to Vendor instead of Customer ('Work Made for Hire' violation).",
    unfavorable: "Customer funds custom development under Statements of Work but receives only a revocable license.",
    missing: "Full 'Work Made for Hire' ownership assignment of custom deliverables and derivative works to Customer."
  },
  {
    pattern: /customer\s+shall\s+indemnify,\s+defend,\s+and\s+hold\s+harmless\s+vendor|vendor\s+disclaims\s+any\s+obligation\s+to\s+indemnify/i,
    weight: 78,
    violation: "One-way indemnification requiring Customer to indemnify Vendor while disclaiming Vendor IP and data breach indemnity.",
    unfavorable: "Shifts all third-party litigation defense costs onto Customer without reciprocal protection.",
    missing: "Uncapped Vendor indemnification for third-party IP infringement, data breaches, and gross negligence."
  },
  {
    pattern: /automatically\s+renew\s+for\s+successive\s+thirty-six\s*\(36\)|120\s+days\s+prior|no\s+right\s+to\s+terminate\s+for\s+convenience/i,
    weight: 74,
    violation: "Multi-year (36-month) evergreen auto-renewal with excessive 120-day notice window and ban on termination for convenience.",
    unfavorable: "Locks Customer into a 3-year non-cancellable renewal cycle without early exit.",
    missing: "Right to terminate for convenience upon 30 days' prior written notice with pro-rata refund of unearned fees."
  },
  {
    pattern: /net\s*15|within\s+fifteen\s*\(15\)\s*days|2\.5%\s+per\s+month|increase\s+fees\s+at\s+any\s+time\s+in\s+its\s+sole\s+discretion/i,
    weight: 72,
    violation: "Violates Net-45 minimum payment standard, imposes punitive 2.5%/month late fees, and allows uncapped unilateral price hikes.",
    unfavorable: "Short 15-day invoice payment cycle coupled with 30% annualized late interest and uncapped fee escalation.",
    missing: "Net-45 payment window, right to withhold disputed invoices in good faith, and annual price cap (lesser of CPI or 3%)."
  },
  {
    pattern: /laws\s+of\s+the\s+cayman\s+islands|george\s+town|customer\s+shall\s+bear\s+all\s+costs\s+and\s+attorneys'\s+fees/i,
    weight: 52,
    violation: "Designates unapproved offshore jurisdiction (Cayman Islands) and one-way fee shifting requiring Customer to pay Vendor's legal costs.",
    unfavorable: "Forces arbitration before a Vendor-appointed sole arbitrator in Grand Cayman at Customer's sole expense.",
    missing: "Approved governing law (Delaware or New York) and prevailing-party or mutual fee allocation."
  },
  {
    pattern: /once\s+every\s+twenty-four\s*\(24\)\s*months|self-attestation\s+letter|prohibited\s+from\s+conducting\s+any\s+on-site/i,
    weight: 46,
    violation: "Replaces annual SOC 2 Type II / ISO 27001 certification delivery and customer audit rights with a biennial self-attestation.",
    unfavorable: "Bars Customer and regulators from conducting third-party security audits or requesting SOC 2 reports.",
    missing: "Annual SOC 2 Type II report delivery and right to audit upon 15 business days' notice (or immediately after a breach)."
  },
  {
    pattern: /engage\s+any\s+third-party\s+subcontractors\s+or\s+subprocessors\s+without\s+prior\s+notice/i,
    weight: 28,
    violation: "Permits unrestricted onboarding of fourth-party data subprocessors without prior written notice or Customer right to object.",
    unfavorable: "Vendor disclaims liability for independent subprocessor security failures.",
    missing: "30-day advance written notice of new subprocessors, Customer objection window, and full flow-down liability."
  }
];
