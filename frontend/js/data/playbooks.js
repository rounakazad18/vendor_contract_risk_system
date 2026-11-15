// data/playbooks.js — Fallback playbook chunks (12 policy chunks)
// Source: POL-LEGAL-2026-v4.2, POL-SEC-2026-v3.1, POL-FIN-2026-v2.0

export const FALLBACK_PLAYBOOK_CHUNKS = [
  {
    chunk_id: "POL-LEGAL-2026-v4.2_CHUNK_01",
    document_id: "POL-LEGAL-2026-v4.2",
    document_title: "Enterprise Procurement & Master Services Legal Playbook",
    section_ref: "POL-LEGAL-2026-v4.2 §1.1",
    heading: "Scope of Services & Affiliate Access",
    category: "Scope & SLA",
    policy_rule: "Scope of services must clearly define deliverables, service levels (minimum 99.9% uptime SLA for cloud services), and expressly permit Customer's majority-owned Affiliates to use the Services under the same contract terms without additional platform access fees.",
    fallback_position: "Permit named Affiliates listed in an Order Form to access Services at no extra base fee.",
    preferred_wording_template: "Vendor shall provide the Services and Deliverables described in each Order Form in accordance with a minimum 99.9% monthly uptime Service Level Agreement. Customer's Affiliates may access and use the Services under this Agreement to the same extent as Customer without additional base licensing fees.",
    keywords: ["scope", "services", "affiliates", "sla", "uptime", "99.9%", "order form", "hosting", "analytics"]
  },
  {
    chunk_id: "POL-LEGAL-2026-v4.2_CHUNK_02",
    document_id: "POL-LEGAL-2026-v4.2",
    document_title: "Enterprise Procurement & Master Services Legal Playbook",
    section_ref: "POL-LEGAL-2026-v4.2 §3.2",
    heading: "Intellectual Property & Work Product Ownership",
    category: "Intellectual Property",
    policy_rule: "All custom deliverables, bespoke configurations, integrations, and work product paid for by Customer shall be owned exclusively by Customer as 'Work Made for Hire' (with a present assignment of all intellectual property rights). Vendor retains ownership only of its pre-existing Background IP and grants Customer a perpetual, irrevocable, worldwide, royalty-free license to use any Background IP embedded in Deliverables.",
    fallback_position: "If Vendor insists on owning generic connectors, Customer must receive an exclusive license within its industry vertical for 36 months and a perpetual, irrevocable, royalty-free enterprise license thereafter.",
    preferred_wording_template: "All custom Deliverables, configurations, work product, and derivative works created specifically for Customer under an Order Form shall be deemed 'Work Made for Hire' and owned exclusively by Customer, and Vendor hereby irrevocably assigns all right, title, and interest therein to Customer. Vendor retains ownership of its pre-existing Background IP and grants Customer a perpetual, irrevocable, worldwide, royalty-free, transferable license to use, modify, and exploit any Background IP incorporated into the Deliverables.",
    keywords: ["intellectual property", "work product", "deliverables", "derivative", "custom", "ownership", "assigns", "statement of work", "license"]
  },
  {
    chunk_id: "POL-LEGAL-2026-v4.2_CHUNK_03",
    document_id: "POL-LEGAL-2026-v4.2",
    document_title: "Enterprise Procurement & Master Services Legal Playbook",
    section_ref: "POL-LEGAL-2026-v4.2 §4.1",
    heading: "Limitation of Liability & Super-Caps",
    category: "Liability",
    policy_rule: "Aggregate liability must be mutual and capped at no less than twelve (12) months of gross fees paid or payable. Consequential, indirect, and special damages waivers must be strictly mutual. Data privacy/security breaches, confidentiality breaches, and third-party IP indemnification obligations must be carved out from the general cap or subject to a minimum 2x–3x (24–36 months fees) Super-Cap.",
    fallback_position: "Accept a 24-month (2x) or $5,000,000 Super-Cap (whichever is greater) for data security incidents and confidentiality breaches, provided third-party IP indemnification remains uncapped.",
    preferred_wording_template: "NEITHER PARTY SHALL BE LIABLE FOR INDIRECT, INCIDENTAL, OR CONSEQUENTIAL DAMAGES, AND EACH PARTY'S AGGREGATE LIABILITY SHALL NOT EXCEED THE TOTAL FEES PAID OR PAYABLE IN THE TWELVE (12) MONTHS PRECEDING THE CLAIM; PROVIDED THAT SUCH LIMITATIONS SHALL NOT APPLY TO (A) INDEMNIFICATION OBLIGATIONS, (B) BREACHES OF CONFIDENTIALITY OR DATA SECURITY OBLIGATIONS (WHICH SHALL BE SUBJECT TO A SUPER-CAP EQUAL TO THREE TIMES (3X) ANNUAL FEES OR $3,000,000, WHICHEVER IS GREATER), OR (C) GROSS NEGLIGENCE OR WILLFUL MISCONDUCT.",
    keywords: ["limitation of liability", "liability", "consequential", "indirect", "punitive", "cap", "aggregate", "one (1) month", "damages"]
  },
  {
    chunk_id: "POL-LEGAL-2026-v4.2_CHUNK_04",
    document_id: "POL-LEGAL-2026-v4.2",
    document_title: "Enterprise Procurement & Master Services Legal Playbook",
    section_ref: "POL-LEGAL-2026-v4.2 §5.1",
    heading: "Mutual & Third-Party IP Indemnification",
    category: "Indemnification",
    policy_rule: "Vendor must defend, indemnify, and hold harmless Customer and its Affiliates against all third-party claims, losses, damages, and reasonable attorneys' fees arising out of (a) alleged infringement or misappropriation of third-party intellectual property rights by the Services or Deliverables, (b) Vendor's breach of data protection or confidentiality obligations, or (c) Vendor's gross negligence, willful misconduct, or violation of law.",
    fallback_position: "Mutual indemnification for bodily injury, property damage, gross negligence, and willful misconduct, plus one-way Vendor IP infringement indemnity.",
    preferred_wording_template: "Vendor shall defend, indemnify, and hold harmless Customer, its Affiliates, and their respective officers, directors, and employees from and against any and all third-party claims, damages, liabilities, penalties, and reasonable attorneys' fees arising from or relating to: (a) any allegation that the Services or Deliverables infringe or misappropriate any third-party Intellectual Property Right; (b) Vendor's breach of Confidentiality or Data Protection obligations; or (c) Vendor's gross negligence, willful misconduct, or violation of applicable law.",
    keywords: ["indemnification", "indemnify", "hold harmless", "defend", "third-party claims", "infringement", "disclaims"]
  },
  {
    chunk_id: "POL-LEGAL-2026-v4.2_CHUNK_05",
    document_id: "POL-LEGAL-2026-v4.2",
    document_title: "Enterprise Procurement & Master Services Legal Playbook",
    section_ref: "POL-LEGAL-2026-v4.2 §6.1",
    heading: "Confidentiality & Non-Disclosure Standards",
    category: "Confidentiality",
    policy_rule: "Confidentiality obligations must be mutual, apply a minimum reasonable degree of care, restrict use of Confidential Information solely to performing the Agreement, permit compelled legal disclosures with prompt prior written notice, and require prompt return or certified destruction of Confidential Information upon request or termination.",
    fallback_position: "Allow retention of routine encrypted archival backups subject to ongoing confidentiality obligations for 5 years (indefinitely for trade secrets).",
    preferred_wording_template: "Each Party (as Receiving Party) shall hold the Disclosing Party's Confidential Information in strict confidence using at least the same degree of care it uses to protect its own confidential information (and no less than reasonable care), shall use such Confidential Information solely to perform its obligations under this Agreement, and shall return or certify destruction of all Confidential Information within thirty (30) days of termination.",
    keywords: ["confidentiality", "non-disclosure", "confidential information", "strict confidence", "degree of care", "destruction"]
  },
  {
    chunk_id: "POL-LEGAL-2026-v4.2_CHUNK_06",
    document_id: "POL-LEGAL-2026-v4.2",
    document_title: "Enterprise Procurement & Master Services Legal Playbook",
    section_ref: "POL-LEGAL-2026-v4.2 §8.1",
    heading: "Governing Law, Venue & Dispute Resolution",
    category: "Governing Law & Dispute",
    policy_rule: "Contracts must be governed by the laws of the State of Delaware or the State of New York (without regard to conflict-of-law principles), with exclusive venue in the state or federal courts located in Wilmington, Delaware or New York County, New York. Offshore jurisdictions and one-way fee-shifting provisions requiring Customer to pay Vendor's legal fees are strictly prohibited.",
    fallback_position: "Neutral AAA commercial arbitration in New York, NY or San Francisco, CA before three neutral arbitrators, with prevailing party entitled to recover reasonable attorneys' fees.",
    preferred_wording_template: "This Agreement and any dispute arising hereunder shall be governed by and construed in accordance with the laws of the State of Delaware, without giving effect to any choice or conflict of law provision. Any legal suit, action, or proceeding shall be instituted exclusively in the federal or state courts located in New Castle County, Delaware, and the prevailing Party in any final judgment shall be entitled to recover its reasonable attorneys' fees and court costs.",
    keywords: ["governing law", "venue", "dispute", "arbitration", "cayman islands", "george town", "attorneys' fees", "delaware"]
  },
  {
    chunk_id: "POL-LEGAL-2026-v4.2_CHUNK_07",
    document_id: "POL-LEGAL-2026-v4.2",
    document_title: "Enterprise Procurement & Master Services Legal Playbook",
    section_ref: "POL-LEGAL-2026-v4.2 §9.1",
    heading: "Force Majeure & Business Continuity",
    category: "Force Majeure",
    policy_rule: "Force Majeure provisions must be mutual, require prompt written notice and diligent mitigation (including activation of Vendor's Business Continuity and Disaster Recovery Plan within 24 hours), and grant Customer the right to terminate without penalty and receive a pro-rata refund if a Force Majeure event prevents performance for more than fifteen (15) consecutive days.",
    fallback_position: "Extend the Force Majeure termination threshold from 15 calendar days to 30 calendar days.",
    preferred_wording_template: "Neither Party shall be liable for delays caused by Force Majeure events beyond its reasonable control, provided the affected Party gives prompt written notice, executes its Business Continuity/Disaster Recovery plan, and uses diligent efforts to resume performance. If a Force Majeure event prevents Vendor from providing the Services for more than fifteen (15) consecutive days, Customer may terminate this Agreement immediately upon written notice and receive a pro-rata refund of all prepaid, unearned fees.",
    keywords: ["force majeure", "business continuity", "disaster recovery", "beyond its reasonable control", "fifteen (15) consecutive"]
  },
  {
    chunk_id: "POL-SEC-2026-v3.1_CHUNK_01",
    document_id: "POL-SEC-2026-v3.1",
    document_title: "Global Data Privacy, AI Governance & InfoSec Addendum Playbook",
    section_ref: "POL-SEC-2026-v3.1 §2.3",
    heading: "Security Incident Notification & AI Model Training Prohibition",
    category: "Data Privacy & AI",
    policy_rule: "Vendor must maintain AES-256 encryption at rest and TLS 1.3 in transit, notify Customer's Security Operations Center within twenty-four (24) hours of confirming or reasonably suspecting any Security Incident or Data Breach, and is strictly prohibited from using Customer Data, prompts, telemetry, or outputs to train, fine-tune, or improve any artificial intelligence or machine learning models shared with third parties.",
    fallback_position: "Accept a maximum 36-hour (or 48-hour outer limit) breach notification window, but the prohibition on training shared AI/ML models on Customer Data is non-negotiable.",
    preferred_wording_template: "Vendor shall notify Customer in writing within twenty-four (24) hours of discovering any actual or reasonably suspected Security Incident affecting Customer Data and shall promptly cooperate at Vendor's expense in investigation, mitigation, and regulatory reporting. Customer retains all right, title, and interest in Customer Data; Vendor is strictly prohibited from using Customer Data, inputs, or outputs to train, fine-tune, or validate any artificial intelligence, machine learning, or foundation model.",
    keywords: ["data privacy", "data breach", "security incident", "notification", "ten (10) business days", "artificial intelligence", "machine learning", "foundation models", "train"]
  },
  {
    chunk_id: "POL-SEC-2026-v3.1_CHUNK_02",
    document_id: "POL-SEC-2026-v3.1",
    document_title: "Global Data Privacy, AI Governance & InfoSec Addendum Playbook",
    section_ref: "POL-SEC-2026-v3.1 §4.1",
    heading: "Subcontracting & Fourth-Party Subprocessors",
    category: "Subcontracting",
    policy_rule: "Vendor shall not subcontract material obligations or engage new third-party data subprocessors without providing Customer at least thirty (30) days' prior written notice and an opportunity to object on reasonable data security grounds. Vendor must bind all subprocessors to written data protection and confidentiality obligations no less restrictive than this Agreement and remains fully liable for all subprocessor acts and omissions.",
    fallback_position: "15 business days' prior notice via an automated subprocessor subscription registry with a 15-day Customer objection window.",
    preferred_wording_template: "Vendor shall provide Customer at least thirty (30) days' prior written notice before authorizing any new Subprocessor to process Customer Data, allowing Customer to object on reasonable privacy or security grounds. Vendor shall impose written data protection and confidentiality obligations on all Subprocessors no less protective than this Agreement and shall remain fully liable for all acts and omissions of its Subprocessors.",
    keywords: ["subcontracting", "subcontractors", "subprocessors", "fourth-party", "delegate", "without prior notice"]
  },
  {
    chunk_id: "POL-SEC-2026-v3.1_CHUNK_03",
    document_id: "POL-SEC-2026-v3.1",
    document_title: "Global Data Privacy, AI Governance & InfoSec Addendum Playbook",
    section_ref: "POL-SEC-2026-v3.1 §5.2",
    heading: "SOC 2 Type II Certifications & Customer Audit Rights",
    category: "Audit & Compliance",
    policy_rule: "Vendor must annually provide an independent third-party SOC 2 Type II report and ISO/IEC 27001 certification, plus executive summaries of annual penetration tests. Customer (or its accredited independent auditor) shall have the right to audit Vendor's security controls and compliance records once annually upon fifteen (15) business days' notice, and immediately upon notice following any confirmed Security Incident.",
    fallback_position: "Review of annual SOC 2 Type II report and penetration test summary satisfies the routine annual audit, preserving on-site/remote audit rights for regulatory inquiries or confirmed security incidents.",
    preferred_wording_template: "Vendor shall annually furnish Customer with a current independent SOC 2 Type II audit report, ISO 27001 certificate, and third-party penetration test summary. Upon fifteen (15) business days' prior written notice (or immediately following a Security Incident or regulatory directive), Customer or its independent accredited auditor may inspect and audit Vendor's security systems, facilities, and compliance documentation.",
    keywords: ["audit", "regulatory compliance", "soc 2", "self-attestation", "twenty-four (24) months", "security audit"]
  },
  {
    chunk_id: "POL-FIN-2026-v2.0_CHUNK_01",
    document_id: "POL-FIN-2026-v2.0",
    document_title: "Commercial Terms, Renewal & Payment Governance Playbook",
    section_ref: "POL-FIN-2026-v2.0 §1.4",
    heading: "Term, Renewal Notice & Termination for Convenience",
    category: "Term & Termination",
    policy_rule: "Initial contract terms shall not exceed twelve (12) to twenty-four (24) months. Any renewal must require affirmative mutual written agreement or allow non-renewal notice up to thirty (30) days prior to expiration (never >60 days or multi-year evergreen lock-ins). Customer must have the right to terminate for convenience upon thirty (30) days' written notice with a pro-rata refund of prepaid, unearned fees.",
    fallback_position: "12-month auto-renewal with 45 days' non-renewal notice, and termination for convenience upon 60 days' written notice.",
    preferred_wording_template: "Following the Initial Term, this Agreement may renew for successive twelve (12) month Renewal Terms unless either Party provides written notice of non-renewal at least thirty (30) days prior to the end of the then-current Term. Customer may terminate this Agreement or any Order Form for convenience at any time upon thirty (30) days' prior written notice and shall receive a pro-rata refund of all prepaid, unearned fees within thirty (30) days of termination.",
    keywords: ["term", "auto-renewal", "automatically renew", "thirty-six (36)", "120 days", "terminate for convenience", "non-cancellable"]
  },
  {
    chunk_id: "POL-FIN-2026-v2.0_CHUNK_02",
    document_id: "POL-FIN-2026-v2.0",
    document_title: "Commercial Terms, Renewal & Payment Governance Playbook",
    section_ref: "POL-FIN-2026-v2.0 §2.1",
    heading: "Payment Terms, Disputed Invoices & Escalation Caps",
    category: "Commercial & Payment",
    policy_rule: "All undisputed invoices shall be payable Net Forty-Five (45) days from Customer's receipt of a valid, itemized invoice. Customer may withhold payment of any good-faith disputed invoice amounts without service suspension or late fees. Late interest on undisputed overdue balances shall not exceed 1.0% per month. Renewal fee increases must be capped at the lesser of 3% or the Consumer Price Index (CPI-U) per annum.",
    fallback_position: "Net-30 payment terms and a 5% annual renewal fee increase cap after the Initial Term.",
    preferred_wording_template: "Customer shall pay all undisputed invoice amounts within forty-five (45) days of receiving an accurate invoice ('Net-45'). Customer may withhold any amounts disputed in good faith without penalty or suspension of Services. Late interest on undisputed past-due amounts shall not exceed 0.5% per month, and renewal fees shall not increase by more than the lesser of three percent (3%) or the twelve-month CPI-U change over the immediately preceding Term.",
    keywords: ["fees", "invoicing", "payment terms", "net 15", "fifteen (15) days", "2.5% per month", "price escalation", "increase fees"]
  }
];
