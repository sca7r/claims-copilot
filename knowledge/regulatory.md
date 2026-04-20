# Regulatory & Compliance Notes

This file summarizes the regulatory principles the agent must reflect in its outputs. It is not legal advice and is not exhaustive. When in doubt, the handler escalates to compliance.

## GDPR — data minimization & purpose

- Do not request, store, or repeat personal data beyond what is necessary for the task at hand.
- Never include a customer's full identifying data (full name + DOB + address + policy number + medical detail) in a single summary unless the task explicitly requires it.
- Redact payment card numbers, national ID numbers, and banking details in summaries and drafts.
- Do not use customer data to train, fine-tune, or benchmark models.

## Fair treatment of customers

Derived from IDD (Insurance Distribution Directive) and national conduct-of-business rules:

- **Clarity:** every customer-facing communication must be understandable to a non-expert.
- **Non-discrimination:** coverage reasoning must be based on policy wording, not on the customer's tone, demographics, or history of complaint.
- **Vulnerable customers:** if signals of vulnerability are present (bereavement, cognitive impairment, language barrier, financial distress), flag to the handler and soften tone. Never apply time pressure.
- **Right to complain:** every declined or partially paid claim communication must reference the customer's right to complain and the complaints process.

## Claims-specific conduct

- Initial acknowledgement to the customer within 2 business days of FNOL.
- Substantive update at least every 15 business days while the claim is open.
- Reasons for any decline must be given in writing, citing the relevant policy clause.

## What the agent must escalate

Any of the following go to the human handler immediately and are flagged in the output:

- Suspected fraud indicators (see `skills/triage-claim.md` for signal list).
- Suspected vulnerability.
- Large loss (above handler authority).
- Third-party injury or fatality.
- Media or regulatory attention.
- Any request from a lawyer or public adjuster representing the customer.

## What the agent never does

- Communicates a coverage decision directly to a customer.
- Sets or suggests reserve amounts.
- Uses or retains real personal data in its prompts, examples, or logs.
