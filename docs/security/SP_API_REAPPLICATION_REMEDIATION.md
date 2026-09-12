# SP-API Reapplication Remediation Plan

## Why the first application was rejected

Amazon rejected the developer registration because two baseline security control answers were not compliant:

1. Network security controls: firewall, IDS/IPS, anti-malware, and network segmentation.
2. Password and authentication controls: 12+ character complexity, MFA, password lifecycle, and annual credential rotation.

This project must not reapply by simply changing answers. Reapplication should occur only after the controls below are actually implemented and can be evidenced.

## Scope for Forgewood / Amazon AI COO

The initial private application will use non-restricted SP-API roles only and will not request buyer PII. The production SP-API runtime should be treated as a controlled environment separate from local development.

## Required remediation before reapplication

### 1. Repository and secret handling

- Change `longgold888evan/amazon-ai-coo` from public to private before any SP-API credential exists.
- Never commit LWA client secrets, refresh tokens, access tokens, API keys, passwords, or encryption keys.
- Store production secrets in AWS Secrets Manager encrypted with AWS KMS.
- Keep local `.env` for development only; it must never contain production SP-API credentials once the AWS runtime is live.
- Enable MFA on GitHub, Amazon/Seller Central, and AWS administrative identities.

### 2. Production network architecture

Deploy the SP-API runtime in a dedicated AWS account or tightly controlled AWS environment:

- VPC with separate public, private-application, and isolated-data subnets.
- No public IP on application compute or databases.
- Security Groups and Network ACLs using least-privilege rules.
- AWS Network Firewall (or equivalent firewall + IDS/IPS control) on relevant ingress/egress paths.
- GuardDuty / Security Hub for threat detection and alerting.
- Private encrypted data stores; database access allowed only from the application security group.
- TLS 1.2+ for all SP-API/LWA and service-to-service traffic.
- Centralized CloudWatch/CloudTrail logging.

### 3. Anti-malware and endpoint controls

- Every endpoint that can access Amazon information must have active, automatically updated anti-malware/endpoint protection.
- For the operator Mac, ensure OS security updates, FileVault, host firewall, Gatekeeper/XProtect, and a managed endpoint-protection control appropriate to the organization.
- Users must not be able to disable required endpoint protection without administrator authorization.
- Review anti-malware status at least monthly.

### 4. Password and authentication policy

For every approved user with access to Amazon information or SP-API credentials:

- Minimum 12 characters.
- Uppercase, lowercase, number, and special character requirements.
- Password must not contain the user's name, username, or email components.
- Prevent reuse of the previous 10 passwords where the identity platform supports password history.
- Minimum password age: 1 day.
- Maximum password age: 365 days.
- MFA required for all approved users.
- Lock or otherwise block authentication after 10 or fewer failed attempts where the identity platform supports this control.
- Unique accounts only; no shared credentials.

For programmatic credentials:

- Store encrypted in AWS Secrets Manager / KMS.
- Rotate at least annually and immediately upon suspected or confirmed compromise.
- Maintain an inventory of credentials and ownership.

### 5. Access management

- Apply least privilege to all human and service identities.
- Review access at least quarterly.
- Remove access within 24 hours of role change or termination.
- Production write permissions remain disabled until separately approved and guarded.

### 6. Incident response

Use `docs/security/INCIDENT_RESPONSE.md` as the formal plan:

- named incident owner / technical responder / business owner;
- 24-hour Amazon notification requirement for incidents involving Amazon information;
- review at least every 6 months;
- containment, credential rotation, recovery, and post-incident review.

### 7. Validation before appeal / reapplication

Before selecting "Yes" to the rejected questions:

- run Amazon Selling Partner API Guard against the AWS environment;
- remediate material Guard findings;
- retain the Guard report and relevant AWS configuration evidence;
- verify MFA is enabled on all approved identities;
- verify password-policy settings;
- verify endpoint protection is active;
- verify the GitHub repository is private;
- verify production secrets are stored only in the approved secret store.

## Recommended reapplication wording

### Network security question

Select **Yes** only after the above environment is operational. If Amazon requests details, state that the application is deployed in a segmented AWS VPC with least-privilege Security Groups/NACLs, firewall/IDS-IPS controls, centralized threat detection, encrypted private data stores, and managed endpoint anti-malware controls for approved users.

### Password/authentication question

Select **Yes** only after the above policy is enforced. If Amazon requests details, state that all approved users use unique identities, mandatory MFA, 12+ character complex passwords with a 365-day maximum lifetime and password-history controls, while API credentials are encrypted in Secrets Manager/KMS and rotated at least annually or immediately upon suspected compromise.

## Important

Documentation alone does not make these controls true. Reapply only after the technical and account-level controls are actually enabled.