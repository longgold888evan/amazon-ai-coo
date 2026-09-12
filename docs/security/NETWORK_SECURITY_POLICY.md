# Network Security Policy

## Scope

This policy applies to systems and endpoints that access, process, transmit, or store Amazon SP-API information for Amazon AI COO.

## Network segmentation

Production infrastructure must be segmented into separate trust zones:

- internet-facing edge / egress controls;
- private application network;
- isolated data network.

Application compute and databases must not have public IP addresses. Data stores must accept traffic only from explicitly authorized application identities or security groups.

## Firewall and ACL controls

- Use network firewalls, security groups, and network access-control lists with least-privilege rules.
- Deny unnecessary inbound access by default.
- Restrict egress to required destinations and protocols where practical.
- Administrative access must not expose production hosts directly to the public internet.

## IDS/IPS and threat detection

- Deploy IDS/IPS or equivalent managed threat-detection controls for production network traffic.
- Centralize relevant security findings and alerts.
- Investigate anomalous access, unexpected request rates, repeated authentication failures, and suspected data exfiltration.

## Anti-malware and endpoint protection

- All operator endpoints that access Amazon information must run active and current anti-malware / endpoint protection.
- Anti-malware definitions and agents must be updated at least monthly and preferably automatically.
- Required endpoint protection must not be removable or disableable by ordinary users.
- Operating-system security updates must be applied regularly.

## Encryption in transit

All Amazon information transmitted across network boundaries must use TLS 1.2 or higher or another approved secure protocol. Plaintext transfer is prohibited.

## Logging and monitoring

- Maintain centralized security logs for production network and application access.
- Review security logs at least bi-weekly or use automated analysis and alerting.
- Protect logs against unauthorized modification.

## Validation

Before SP-API production access is requested, validate the AWS environment using Amazon Selling Partner API Guard or equivalent evidence and remediate material findings.