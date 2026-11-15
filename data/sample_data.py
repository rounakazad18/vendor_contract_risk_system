"""
Sample Company Playbook Documents and Sample Vendor Contracts (TXT, DOCX, PDF, and Unnumbered).
"""

from __future__ import annotations
import os
from typing import Dict, List, Tuple
try:
    import docx
    from docx.shared import Inches, Pt
except ImportError:
    docx = None
    Inches = Pt = None
from vector_store import PlaybookVectorStore


PLAYBOOK_DOCUMENTS: List[Tuple[str, str, str]] = [
    (
        "POL-LEGAL-2026-v4.2",
        "Enterprise Procurement & Master Services Legal Playbook",
        """## §1.1 Scope of Services & Affiliate Access [Category: Scope & SLA]
**Governing Policy Rule**: Scope of services must clearly define deliverables, service levels (minimum 99.9% uptime SLA for cloud services), and expressly permit Customer's majority-owned Affiliates to use the Services under the same contract terms without additional platform access fees.
**Mandatory Requirements**: Express Affiliate usage rights; 99.9% uptime SLA commitment; clear acceptance criteria for deliverables.
**Prohibited Terms**: "as-is without SLA"; "affiliates require separate master agreement".
**Fallback Position**: Permit named Affiliates listed in an Order Form to access Services at no extra base fee.
**Preferred Replacement Wording**: Vendor shall provide the Services and Deliverables described in each Order Form in accordance with a minimum 99.9% monthly uptime Service Level Agreement. Customer's Affiliates may access and use the Services under this Agreement to the same extent as Customer without additional base licensing fees.

## §3.2 Intellectual Property & Work Product Ownership [Category: Intellectual Property]
**Governing Policy Rule**: All custom deliverables, bespoke configurations, integrations, and work product paid for by Customer shall be owned exclusively by Customer as "Work Made for Hire" (with a present assignment of all intellectual property rights). Vendor retains ownership only of its pre-existing Background IP and grants Customer a perpetual, irrevocable, worldwide, royalty-free license to use any Background IP embedded in Deliverables.
**Mandatory Requirements**: Customer ownership of custom deliverables and derivative works; Work Made for Hire + present IP assignment; perpetual royalty-free license to embedded Vendor Background IP.
**Prohibited Terms**: "all deliverables belong exclusively to vendor"; "derivative works sole property of vendor"; "vendor shall own all right, title, and interest in custom".
**Fallback Position**: If Vendor insists on owning generic connectors, Customer must receive an exclusive license within its industry vertical for 36 months and a perpetual, irrevocable, royalty-free enterprise license thereafter.
**Preferred Replacement Wording**: All custom Deliverables, configurations, work product, and derivative works created specifically for Customer under an Order Form shall be deemed "Work Made for Hire" and owned exclusively by Customer, and Vendor hereby irrevocably assigns all right, title, and interest therein to Customer. Vendor retains ownership of its pre-existing Background IP and grants Customer a perpetual, irrevocable, worldwide, royalty-free, transferable license to use, modify, and exploit any Background IP incorporated into the Deliverables.

## §4.1 Limitation of Liability & Super-Caps [Category: Liability]
**Governing Policy Rule**: Aggregate liability must be mutual and capped at no less than twelve (12) months of gross fees paid or payable. Consequential, indirect, and special damages waivers must be strictly mutual. Data privacy/security breaches, confidentiality breaches, and third-party IP indemnification obligations must be carved out from the general cap or subject to a minimum 2x–3x (24–36 months fees) Super-Cap.
**Mandatory Requirements**: Mutual 12-month fee general liability cap; mutual consequential damages waiver; uncapped or 3x super-cap for IP indemnity, confidentiality, and data security breaches.
**Prohibited Terms**: "one (1) month"; "1 month"; "vendor shall not be liable for any indirect"; "excludes data breach from cap".
**Fallback Position**: Accept a 24-month (2x) or $5,000,000 Super-Cap (whichever is greater) for data security incidents and confidentiality breaches, provided third-party IP indemnification remains uncapped.
**Preferred Replacement Wording**: NEITHER PARTY SHALL BE LIABLE FOR INDIRECT, INCIDENTAL, OR CONSEQUENTIAL DAMAGES, AND EACH PARTY'S AGGREGATE LIABILITY SHALL NOT EXCEED THE TOTAL FEES PAID OR PAYABLE IN THE TWELVE (12) MONTHS PRECEDING THE CLAIM; PROVIDED THAT SUCH LIMITATIONS SHALL NOT APPLY TO (A) INDEMNIFICATION OBLIGATIONS, (B) BREACHES OF CONFIDENTIALITY OR DATA SECURITY OBLIGATIONS (WHICH SHALL BE SUBJECT TO A SUPER-CAP EQUAL TO THREE TIMES (3X) ANNUAL FEES OR $3,000,000, WHICHEVER IS GREATER), OR (C) GROSS NEGLIGENCE OR WILLFUL MISCONDUCT.

## §5.1 Mutual & Third-Party IP Indemnification [Category: Indemnification]
**Governing Policy Rule**: Vendor must defend, indemnify, and hold harmless Customer and its Affiliates against all third-party claims, losses, damages, and reasonable attorneys' fees arising out of (a) alleged infringement or misappropriation of third-party intellectual property rights by the Services or Deliverables, (b) Vendor's breach of data protection or confidentiality obligations, or (c) Vendor's gross negligence, willful misconduct, or violation of law.
**Mandatory Requirements**: Full Vendor IP infringement indemnity; Vendor data breach and gross negligence indemnity; remedy hierarchy (procure right, modify non-infringing, or refund).
**Prohibited Terms**: "customer shall indemnify, defend, and hold harmless vendor"; "vendor disclaims any obligation to indemnify".
**Fallback Position**: Mutual indemnification for bodily injury, property damage, gross negligence, and willful misconduct, plus one-way Vendor IP infringement indemnity.
**Preferred Replacement Wording**: Vendor shall defend, indemnify, and hold harmless Customer, its Affiliates, and their respective officers, directors, and employees from and against any and all third-party claims, damages, liabilities, penalties, and reasonable attorneys' fees arising from or relating to: (a) any allegation that the Services or Deliverables infringe or misappropriate any third-party Intellectual Property Right; (b) Vendor's breach of Confidentiality or Data Protection obligations; or (c) Vendor's gross negligence, willful misconduct, or violation of applicable law.

## §6.1 Confidentiality & Non-Disclosure Standards [Category: Confidentiality]
**Governing Policy Rule**: Confidentiality obligations must be mutual, apply a minimum reasonable degree of care, restrict use of Confidential Information solely to performing the Agreement, permit compelled legal disclosures with prompt prior written notice, and require prompt return or certified destruction of Confidential Information upon request or termination.
**Mandatory Requirements**: Mutual protection of Confidential Information; standard carve-outs (public domain, independent development, prior possession); prompt destruction/return on termination.
**Prohibited Terms**: "unrestricted disclosure to marketing partners"; "no obligation to destroy confidential data".
**Fallback Position**: Allow retention of routine encrypted archival backups subject to ongoing confidentiality obligations for 5 years (indefinitely for trade secrets).
**Preferred Replacement Wording**: Each Party (as Receiving Party) shall hold the Disclosing Party's Confidential Information in strict confidence using at least the same degree of care it uses to protect its own confidential information (and no less than reasonable care), shall use such Confidential Information solely to perform its obligations under this Agreement, and shall return or certify destruction of all Confidential Information within thirty (30) days of termination.

## §8.1 Governing Law, Venue & Dispute Resolution [Category: Governing Law & Dispute]
**Governing Policy Rule**: Contracts must be governed by the laws of the State of Delaware or the State of New York (without regard to conflict-of-law principles), with exclusive venue in the state or federal courts located in Wilmington, Delaware or New York County, New York. Offshore jurisdictions and one-way fee-shifting provisions requiring Customer to pay Vendor's legal fees are strictly prohibited.
**Mandatory Requirements**: Governing law of Delaware or New York; mutual venue in DE or NY courts (or AAA arbitration in NY/DE); each party bears its own costs or prevailing-party fee recovery.
**Prohibited Terms**: "laws of the cayman islands"; "george town"; "customer shall bear all costs and attorneys' fees".
**Fallback Position**: Neutral AAA commercial arbitration in New York, NY or San Francisco, CA before three neutral arbitrators, with prevailing party entitled to recover reasonable attorneys' fees.
**Preferred Replacement Wording**: This Agreement and any dispute arising hereunder shall be governed by and construed in accordance with the laws of the State of Delaware, without giving effect to any choice or conflict of law provision. Any legal suit, action, or proceeding shall be instituted exclusively in the federal or state courts located in New Castle County, Delaware, and the prevailing Party in any final judgment shall be entitled to recover its reasonable attorneys' fees and court costs.

## §9.1 Force Majeure & Business Continuity [Category: Force Majeure]
**Governing Policy Rule**: Force Majeure provisions must be mutual, require prompt written notice and diligent mitigation (including activation of Vendor's Business Continuity and Disaster Recovery Plan within 24 hours), and grant Customer the right to terminate without penalty and receive a pro-rata refund if a Force Majeure event prevents performance for more than fifteen (15) consecutive days.
**Mandatory Requirements**: Mutual Force Majeure relief; mandatory BC/DR plan activation; termination + pro-rata refund right after 15 days of disruption.
**Prohibited Terms**: "payment obligations excused only for vendor"; "no termination right during force majeure".
**Fallback Position**: Extend the Force Majeure termination threshold from 15 calendar days to 30 calendar days.
**Preferred Replacement Wording**: Neither Party shall be liable for delays caused by Force Majeure events beyond its reasonable control, provided the affected Party gives prompt written notice, executes its Business Continuity/Disaster Recovery plan, and uses diligent efforts to resume performance. If a Force Majeure event prevents Vendor from providing the Services for more than fifteen (15) consecutive days, Customer may terminate this Agreement immediately upon written notice and receive a pro-rata refund of all prepaid, unearned fees.
""",
    ),
    (
        "POL-SEC-2026-v3.1",
        "Global Data Privacy, AI Governance & InfoSec Addendum Playbook",
        """## §2.3 Security Incident Notification & AI Model Training Prohibition [Category: Data Privacy & AI]
**Governing Policy Rule**: Vendor must maintain AES-256 encryption at rest and TLS 1.3 in transit, notify Customer's Security Operations Center within twenty-four (24) hours of confirming or reasonably suspecting any Security Incident or Data Breach, and is strictly prohibited from using Customer Data, prompts, telemetry, or outputs to train, fine-tune, or improve any artificial intelligence or machine learning models shared with third parties.
**Mandatory Requirements**: <= 24-hour Security Incident notification; strict prohibition on AI/ML model training using Customer Data; Vendor bears breach remediation and notification costs.
**Prohibited Terms**: "ten (10) business days"; "10 business days"; "train its artificial intelligence"; "train foundation models".
**Fallback Position**: Accept a maximum 36-hour (or 48-hour outer limit) breach notification window, but the prohibition on training shared AI/ML models on Customer Data is non-negotiable.
**Preferred Replacement Wording**: Vendor shall notify Customer in writing within twenty-four (24) hours of discovering any actual or reasonably suspected Security Incident affecting Customer Data and shall promptly cooperate at Vendor's expense in investigation, mitigation, and regulatory reporting. Customer retains all right, title, and interest in Customer Data; Vendor is strictly prohibited from using Customer Data, inputs, or outputs to train, fine-tune, or validate any artificial intelligence, machine learning, or foundation model.

## §4.1 Subcontracting & Fourth-Party Subprocessors [Category: Subcontracting]
**Governing Policy Rule**: Vendor shall not subcontract material obligations or engage new third-party data subprocessors without providing Customer at least thirty (30) days' prior written notice and an opportunity to object on reasonable data security grounds. Vendor must bind all subprocessors to written data protection and confidentiality obligations no less restrictive than this Agreement and remains fully liable for all subprocessor acts and omissions.
**Mandatory Requirements**: 30-day advance written notice of new subprocessors; Customer right to object and terminate without penalty if objection is unresolved; full flow-down liability on Vendor.
**Prohibited Terms**: "engage any third-party subcontractors or subprocessors without prior notice"; "without prior notice or consent of customer".
**Fallback Position**: 15 business days' prior notice via an automated subprocessor subscription registry with a 15-day Customer objection window.
**Preferred Replacement Wording**: Vendor shall provide Customer at least thirty (30) days' prior written notice before authorizing any new Subprocessor to process Customer Data, allowing Customer to object on reasonable privacy or security grounds. Vendor shall impose written data protection and confidentiality obligations on all Subprocessors no less protective than this Agreement and shall remain fully liable for all acts and omissions of its Subprocessors.

## §5.2 SOC 2 Type II Certifications & Customer Audit Rights [Category: Audit & Compliance]
**Governing Policy Rule**: Vendor must annually provide an independent third-party SOC 2 Type II report and ISO/IEC 27001 certification, plus executive summaries of annual penetration tests. Customer (or its accredited independent auditor) shall have the right to audit Vendor's security controls and compliance records once annually upon fifteen (15) business days' notice, and immediately upon notice following any confirmed Security Incident.
**Mandatory Requirements**: Annual SOC 2 Type II and ISO 27001 report delivery; annual Customer or third-party audit right upon 15 business days' notice; immediate for-cause audit right after a breach.
**Prohibited Terms**: "once every twenty-four (24) months"; "self-attestation letter"; "prohibited from conducting any on-site or third-party security audit".
**Fallback Position**: Review of annual SOC 2 Type II report and penetration test summary satisfies the routine annual audit, preserving on-site/remote audit rights for regulatory inquiries or confirmed security incidents.
**Preferred Replacement Wording**: Vendor shall annually furnish Customer with a current independent SOC 2 Type II audit report, ISO 27001 certificate, and third-party penetration test summary. Upon fifteen (15) business days' prior written notice (or immediately following a Security Incident or regulatory directive), Customer or its independent accredited auditor may inspect and audit Vendor's security systems, facilities, and compliance documentation.
""",
    ),
    (
        "POL-FIN-2026-v2.0",
        "Commercial Terms, Renewal & Payment Governance Playbook",
        """## §1.4 Term, Renewal Notice & Termination for Convenience [Category: Term & Termination]
**Governing Policy Rule**: Initial contract terms shall not exceed twelve (12) to twenty-four (24) months. Any renewal must require affirmative mutual written agreement or allow non-renewal notice up to thirty (30) days prior to expiration (never >60 days or multi-year evergreen lock-ins). Customer must have the right to terminate for convenience upon thirty (30) days' written notice with a pro-rata refund of prepaid, unearned fees.
**Mandatory Requirements**: Maximum 12-month renewal increments; <= 30-day non-renewal notice window; Customer termination for convenience upon 30 days' notice with pro-rata refund.
**Prohibited Terms**: "automatically renew for successive thirty-six (36)"; "120 days prior written notice"; "no right to terminate for convenience".
**Fallback Position**: 12-month auto-renewal with 45 days' non-renewal notice, and termination for convenience upon 60 days' written notice.
**Preferred Replacement Wording**: Following the Initial Term, this Agreement may renew for successive twelve (12) month Renewal Terms unless either Party provides written notice of non-renewal at least thirty (30) days prior to the end of the then-current Term. Customer may terminate this Agreement or any Order Form for convenience at any time upon thirty (30) days' prior written notice and shall receive a pro-rata refund of all prepaid, unearned fees within thirty (30) days of termination.

## §2.1 Payment Terms, Disputed Invoices & Escalation Caps [Category: Commercial & Payment]
**Governing Policy Rule**: All undisputed invoices shall be payable Net Forty-Five (45) days from Customer's receipt of a valid, itemized invoice. Customer may withhold payment of any good-faith disputed invoice amounts without service suspension or late fees. Late interest on undisputed overdue balances shall not exceed 1.0% per month (or the statutory maximum, if lower). Renewal fee increases must be capped at the lesser of 3% or the Consumer Price Index (CPI-U) per annum.
**Mandatory Requirements**: Net-45 payment terms; right to withhold disputed amounts in good faith; annual price escalation cap <= 3% or CPI-U.
**Prohibited Terms**: "net 15"; "within fifteen (15) days"; "2.5% per month"; "increase fees at any time in its sole discretion".
**Fallback Position**: Net-30 payment terms and a 5% annual renewal fee increase cap after the Initial Term.
**Preferred Replacement Wording**: Customer shall pay all undisputed invoice amounts within forty-five (45) days of receiving an accurate invoice ("Net-45"). Customer may withhold any amounts disputed in good faith without penalty or suspension of Services. Late interest on undisputed past-due amounts shall not exceed 0.5% per month, and renewal fees shall not increase by more than the lesser of three percent (3%) or the twelve-month CPI-U change over the immediately preceding Term.
""",
    ),
]


SAMPLE_VENDOR_CONTRACT_TXT = """MASTER SAAS AND CLOUD SERVICES AGREEMENT
Contract Reference: APEX-MSA-2026-089
Between: ApexCloud Infrastructure Inc. ("Vendor") and Enterprise Customer Corp. ("Customer")

1. Scope of Services and Affiliates.
1.1 Vendor shall provide the cloud hosting, analytics platform, and support services described in each mutually executed Order Form in accordance with a 99.95% monthly uptime Service Level Agreement.
1.2 Customer's majority-owned Affiliates are expressly authorized to access and use the Services under the terms of this Agreement without additional platform access fees.

2. Term, Auto-Renewal and Termination Rights.
2.1 This Agreement shall commence on the Effective Date and continue for an Initial Term of twenty-four (24) months. Thereafter, this Agreement shall automatically renew for successive thirty-six (36) month periods unless Customer provides written notice of non-renewal at least 120 days prior to the expiration of the then-current term.
2.2 All Order Forms are strictly non-cancellable, all fees are non-refundable, and Customer shall have no right to terminate for convenience under any circumstances.

3. Fees, Invoicing, Payment Terms and Price Escalation.
3.1 All fees are due and payable Net 15 (within fifteen (15) days of invoice date) without right of set-off or deduction. Overdue balances shall accrue compound interest at the rate of 2.5% per month (30% per annum), and Vendor may immediately suspend Services if any invoice remains unpaid for five (5) days.
3.2 Vendor reserves the right to increase fees at any time in its sole discretion upon fifteen (15) days' notice, and renewal terms shall be subject to uncapped annual price adjustments.

4. Intellectual Property and Work Product Ownership.
4.1 Notwithstanding anything to the contrary, all deliverables, custom configurations, software integrations, and work product funded by Customer under any Statement of Work shall belong exclusively to Vendor.
4.2 Customer hereby assigns to Vendor all rights in deliverables and acknowledges that all derivative works shall remain the sole property of Vendor, subject only to a revocable, non-exclusive license during the active Term.

5. Indemnification Obligations.
5.1 Customer shall indemnify, defend, and hold harmless Vendor, its officers, directors, and affiliates solely at Customer's expense against any and all third-party claims, liabilities, and expenses arising out of or relating to this Agreement or Customer's use of the Services.
5.2 Vendor disclaims any obligation to indemnify Customer for third-party intellectual property infringement, data security incidents, or regulatory penalties.

6. Limitation of Liability and Consequential Damages.
6.1 IN NO EVENT SHALL VENDOR BE LIABLE FOR ANY INDIRECT, INCIDENTAL, SPECIAL, PUNITIVE, OR CONSEQUENTIAL DAMAGES. Customer waives all claims for consequential damages while Customer's liability to Vendor remains uncapped.
6.2 Vendor's maximum aggregate liability for all claims arising under or related to this Agreement (including data breaches and IP claims) shall in no event exceed the fees paid in the one (1) month immediately preceding the event giving rise to liability, and explicitly excludes data breach from cap carve-outs.

7. Confidentiality and Non-Disclosure.
7.1 Each Party agrees to hold the other Party's Confidential Information in strict confidence using at least the same degree of care it uses to protect its own confidential information of like importance, and in no event less than a reasonable standard of care.
7.2 Upon termination or expiration of this Agreement, each Receiving Party shall promptly return or certify the destruction of all Disclosing Party Confidential Information within thirty (30) days.

8. Data Privacy, Security Incident Notification and AI Training.
8.1 In the event of a confirmed data breach involving Customer Personal Data, Vendor shall notify Customer within ten (10) business days after confirming the root cause of the incident in its sole discretion.
8.2 Customer hereby grants Vendor a perpetual, irrevocable, worldwide, royalty-free license to use Customer Data, user prompts, and platform outputs to train its artificial intelligence and machine learning foundation models for commercial distribution to third parties.

9. Audit Rights and Regulatory Compliance.
9.1 Customer's sole and exclusive right to verify Vendor's security posture shall be limited to receiving a one-page internal self-attestation letter from Vendor once every twenty-four (24) months.
9.2 Customer and its regulators are strictly prohibited from conducting any on-site or third-party security audit or requesting SOC 2 Type II reports.

10. Subcontracting and Fourth-Party Affiliates.
10.1 Vendor may freely delegate its obligations and engage any third-party subcontractors or subprocessors to process Customer Confidential Data without prior notice or consent of Customer, and Vendor shall not be liable for independent subprocessor failures.

11. Governing Law, Venue and Dispute Resolution.
11.1 This Agreement shall be governed by and construed in accordance with the laws of the Cayman Islands. Any dispute shall be resolved exclusively by binding arbitration in George Town, Grand Cayman before a single arbitrator appointed by Vendor.
11.2 Customer shall bear all costs and attorneys' fees incurred by both parties in connection with any dispute or arbitration proceeding, regardless of outcome.

12. Force Majeure and Business Continuity.
12.1 Neither Party shall be liable for failure or delay in performance caused by a Force Majeure event beyond its reasonable control, provided the affected Party provides prompt written notice and activates its Business Continuity and Disaster Recovery Plan within 24 hours.
12.2 If a Force Majeure event prevents Vendor from performing for more than fifteen (15) consecutive calendar days, Customer may terminate the affected Order Form immediately upon written notice and receive a full pro-rata refund of prepaid unearned fees.
"""


UNNUMBERED_POORLY_FORMATTED_CONTRACT_TXT = """VENDOR SERVICES AGREEMENT DRAFT (UNNUMBERED)

Payment Terms: All invoices must be paid within fifteen (15) days (Net 15) and late balances carry 2.5% per month interest. Vendor may increase fees at any time in its sole discretion without cap.

Data & AI Policy: Vendor will report security incidents within ten (10) business days after internal review and may use Customer Data to train its artificial intelligence and machine learning models.

Liability Limitation: In no event shall Vendor be liable for any indirect damages, and Vendor's total liability shall not exceed one (1) month of fees paid prior to the claim.
"""


def _write_text_pdf(pdf_path: str, text: str) -> None:
    lines: List[str] = []
    for raw_line in text.splitlines():
        if not raw_line.strip():
            lines.append("")
            continue
        words = raw_line.split(" ")
        cur = ""
        for w in words:
            if len(cur) + len(w) + 1 <= 95:
                cur = f"{cur} {w}".strip()
            else:
                lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)

    pages_lines = [lines[i : i + 48] for i in range(0, len(lines), 48)] or [[""]]
    objects: List[bytes] = []

    def add_obj(body: bytes) -> int:
        objects.append(body)
        return len(objects)

    font_obj_id = add_obj(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    page_obj_ids: List[int] = []
    content_obj_ids: List[int] = []

    for p_lines in pages_lines:
        stream_cmds = [b"BT /F1 10 Tf 50 750 Td 14 TL"]
        for ln in p_lines:
            esc = (
                ln.replace("\\", "\\\\")
                .replace("(", "\\(")
                .replace(")", "\\)")
                .encode("latin-1", errors="replace")
            )
            stream_cmds.append(b"(" + esc + b") Tj T*")
        stream_cmds.append(b"ET")
        stream_bytes = b"\n".join(stream_cmds)
        c_id = add_obj(
            f"<< /Length {len(stream_bytes)} >>\nstream\n".encode("ascii")
            + stream_bytes
            + b"\nendstream"
        )
        content_obj_ids.append(c_id)

    pages_tree_id = len(objects) + len(content_obj_ids) + 1
    for c_id in content_obj_ids:
        p_id = add_obj(
            f"<< /Type /Page /Parent {pages_tree_id} 0 R /MediaBox [0 0 612 792] "
            f"/Resources << /Font << /F1 {font_obj_id} 0 R >> >> /Contents {c_id} 0 R >>".encode(
                "ascii"
            )
        )
        page_obj_ids.append(p_id)

    kids_str = " ".join(f"{pid} 0 R" for pid in page_obj_ids)
    actual_pages_id = add_obj(
        f"<< /Type /Pages /Kids [{kids_str}] /Count {len(page_obj_ids)} >>".encode("ascii")
    )
    assert actual_pages_id == pages_tree_id
    catalog_id = add_obj(f"<< /Type /Catalog /Pages {pages_tree_id} 0 R >>".encode("ascii"))

    out = bytearray(b"%PDF-1.4\n")
    offsets: List[int] = []
    for idx, obj_bytes in enumerate(objects, start=1):
        offsets.append(len(out))
        out.extend(f"{idx} 0 obj\n".encode("ascii"))
        out.extend(obj_bytes)
        out.extend(b"\nendobj\n")

    xref_pos = len(out)
    out.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    out.extend(b"0000000000 65535 f \n")
    for off in offsets:
        out.extend(f"{off:010d} 00000 n \n".encode("ascii"))
    out.extend(
        f"trailer\n<< /Size {len(objects) + 1} /Root {catalog_id} 0 R >>\nstartxref\n{xref_pos}\n%%EOF\n".encode(
            "ascii"
        )
    )
    with open(pdf_path, "wb") as f:
        f.write(out)


def populate_default_vector_store() -> PlaybookVectorStore:
    store = PlaybookVectorStore()
    for doc_id, title, md_text in PLAYBOOK_DOCUMENTS:
        store.parse_and_index_markdown_playbook(doc_id, title, md_text)
    return store


def generate_sample_contract_files(output_dir: str) -> Dict[str, str]:
    os.makedirs(output_dir, exist_ok=True)
    txt_path = os.path.join(output_dir, "ApexCloud_Enterprise_MSA_2026.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(SAMPLE_VENDOR_CONTRACT_TXT)

    unnumbered_path = os.path.join(output_dir, "Unnumbered_Vendor_Draft.txt")
    with open(unnumbered_path, "w", encoding="utf-8") as f:
        f.write(UNNUMBERED_POORLY_FORMATTED_CONTRACT_TXT)

    docx_path = os.path.join(output_dir, "ApexCloud_Enterprise_MSA_2026.docx")
    if docx is not None:
        doc = docx.Document()
        for section in doc.sections:
            section.top_margin = Inches(1.0)
            section.bottom_margin = Inches(1.0)
            section.left_margin = Inches(1.0)
            section.right_margin = Inches(1.0)
        style_normal = doc.styles["Normal"]
        style_normal.font.name = "Calibri"
        style_normal.font.size = Pt(11)

        for block in SAMPLE_VENDOR_CONTRACT_TXT.strip().split("\n\n"):
            p = doc.add_paragraph(block.strip())
            p.paragraph_format.space_after = Pt(8)
            p.paragraph_format.line_spacing = 1.15
        doc.save(docx_path)
    else:
        with open(docx_path, "wb") as f:
            f.write(b"")

    pdf_path = os.path.join(output_dir, "ApexCloud_Enterprise_MSA_2026.pdf")
    _write_text_pdf(pdf_path, SAMPLE_VENDOR_CONTRACT_TXT)

    playbooks_dir = os.path.join(output_dir, "playbooks")
    os.makedirs(playbooks_dir, exist_ok=True)
    for doc_id, title, md_text in PLAYBOOK_DOCUMENTS:
        pb_path = os.path.join(playbooks_dir, f"{doc_id}.md")
        with open(pb_path, "w", encoding="utf-8") as f:
            f.write(f"# {doc_id}: {title}\n\n{md_text}")

    return {
        "txt": txt_path,
        "docx": docx_path,
        "pdf": pdf_path,
        "unnumbered_txt": unnumbered_path,
        "playbooks_dir": playbooks_dir,
    }
