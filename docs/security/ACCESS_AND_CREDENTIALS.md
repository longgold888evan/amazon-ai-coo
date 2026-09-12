# Access and Credential Security Baseline

## Scope

This policy applies to Amazon SP-API credentials and Amazon information processed by the Amazon AI COO private application.

## Access control

- Access is limited to authorized personnel with a business need to operate or maintain the seller system.
- During the current single-operator phase, Amazon information and SP-API credentials are accessible only to the authorized application/business owner through that person's protected operating-system account.
- Shared accounts and shared credentials are prohibited.
- If additional operators are added, access must be granted individually according to role and business need and removed when no longer required.
- Production write permissions remain disabled until separately approved and guarded by application controls.

## Data in transit

- Amazon SP-API and LWA traffic must use HTTPS/TLS endpoints only.
- Plaintext transmission of Amazon information over public or untrusted networks is prohibited.
- Any future remote service-to-service transport that carries Amazon information must use encrypted transport.

## Credential storage

- LWA client secrets, refresh tokens, access tokens, API keys, passwords, encryption keys, and private access keys must never be committed to Git or hard-coded in source code.
- Local development credentials are stored outside source control in `.env` or an equivalent local secret store.
- `.env` is excluded through `.gitignore` and should be restricted to the local authorized OS account, for example `chmod 600 .env` on macOS/Linux.
- Credentials must not be placed in public/shared cloud documents, issue trackers, chat messages, screenshots, logs, or source-control history.
- Credentials must be rotated or revoked promptly if exposure is suspected.

## Third-party processing

- Raw Amazon SP-API data is not sent to third-party LLMs or external processors in the initial private-app phase.
- A third-party processor may be introduced only after evaluating Amazon data-protection requirements and updating disclosures and controls as required.

## Device and repository controls

- The development device must use a protected local user account and device-level security controls appropriate to the operating system.
- Repository access must be limited to authorized maintainers.
- Sensitive configuration remains outside the repository.

## Review

Review this baseline whenever access patterns, hosting, external processors, or the application's data scope materially changes.
