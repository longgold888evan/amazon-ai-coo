# Security Incident Response Plan

## Scope

This plan applies to Amazon SP-API information, credentials, access tokens, application logs, normalized seller data, backups, and any system that stores or processes those assets for the Amazon AI COO private application.

## Roles and responsibilities

- **Incident owner:** the authorized business/application owner for the private SP-API application.
- **Technical responder:** the authorized maintainer of the Amazon AI COO codebase and runtime.
- **Business decision owner:** the authorized seller-account owner who can revoke credentials, disable the application, or stop data processing.

For the current single-operator phase, these responsibilities may be performed by the same authorized person, but the responsibilities remain explicit.

## What is a security incident

Examples include:

- suspected exposure of an LWA client secret, refresh token, access token, API key, password, encryption key, or private access key;
- unauthorized access to Amazon information or the host that stores it;
- accidental publication of Amazon information or credentials to GitHub, logs, cloud storage, chat systems, or other external services;
- malware, device theft, account compromise, or other events that could expose Amazon information;
- unexpected third-party access to systems processing Amazon information.

## Immediate response

On discovery of a suspected incident:

1. Stop affected processing and isolate the affected system when practical.
2. Revoke or rotate affected credentials and tokens.
3. Preserve relevant logs and evidence without copying sensitive data into public or shared locations.
4. Determine what Amazon information was affected, the time window, and the likely exposure path.
5. Document containment and remediation actions.

## Amazon notification

Any security incident involving Amazon information must be reported to **security@amazon.com within 24 hours of discovery**, together with the information reasonably available at that time. Follow-up details must be supplied as the investigation develops.

## Recovery

Before resuming normal operation:

- verify that exposed credentials have been revoked or rotated;
- patch or remove the root cause;
- confirm access is limited to authorized users;
- verify secrets are not present in source control, logs, or public/shared storage;
- validate that data processing again follows the project's security controls.

## Post-incident review

After an incident, document root cause, impact, corrective actions, and any required changes to application controls or operating procedures.

## Review cadence

This plan must be reviewed **at least every 6 months** and after any material security incident or material architecture change. The review date and any changes should be recorded in version control or an internal audit log.

## Effective date

Adopted for the Amazon AI COO private SP-API application when approved by the organization/app owner.
