# Password and Authentication Policy

## Scope

This policy applies to every human or service identity that can access Amazon SP-API information, SP-API credentials, production infrastructure, production logs, backups, or administrative systems for Amazon AI COO.

## Human identities

- Every person must use a unique account. Shared and generic accounts are prohibited.
- Passwords must contain at least 12 characters and include uppercase letters, lowercase letters, numbers, and special characters.
- Passwords must not include the user's first name, last name, username, or email components.
- The previous 10 passwords must not be reused where the identity platform supports password history.
- Minimum password age is 1 day where the identity platform supports this control.
- Maximum password age is 365 days.
- MFA is mandatory for every approved user. Approved factors are TOTP, hardware security keys, or platform biometric authentication where supported.
- Authentication must be blocked or the account locked after 10 or fewer consecutive unsuccessful attempts where supported by the identity platform.

## Administrative systems

MFA must be enabled for:

- Amazon / Seller Central / Solution Provider Portal;
- AWS administrative identities;
- GitHub accounts that can access the private Amazon AI COO repository;
- any future production database, secret-management, observability, or deployment console accessible by a human user.

## Programmatic credentials

- SP-API LWA client secrets, refresh tokens, access tokens, API keys, database credentials, and encryption keys must not be hardcoded or stored in source control.
- Production secrets must be stored in an encrypted secret-management service such as AWS Secrets Manager protected by AWS KMS.
- Programmatic credentials must be rotated at least annually and immediately upon suspected or confirmed compromise.
- Maintain an inventory with credential purpose, owner, creation date, last rotation date, and next required rotation date.

## Access lifecycle

- Access is granted only for documented business need and according to least privilege.
- Human and service access is reviewed quarterly.
- Access must be removed within 24 hours of termination, role change, or loss of business need.

## Evidence

Before claiming compliance in the SP-API developer profile, retain screenshots or exported settings showing:

- MFA enabled for all approved users;
- password policy configuration showing the required length/complexity and 365-day maximum age;
- password history setting where supported;
- secret storage in the approved encrypted secret manager;
- credential-rotation inventory.