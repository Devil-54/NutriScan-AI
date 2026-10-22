# Security Policy

## Supported versions

Security fixes are currently considered for the latest code on the default branch. No released version support schedule is published yet.

## Reporting a vulnerability

Please do not post exploitable vulnerability details in a public issue. Use GitHub's private vulnerability reporting for `Devil-54/NutriScan-AI` if it is enabled, or contact the maintainer privately through the [GitHub profile](https://github.com/Devil-54). Include affected files/versions, impact, reproduction steps, and a safe contact method. The maintainer will acknowledge reports as soon as reasonably possible and coordinate a fix and disclosure.

## Secret and data handling

Never commit `.env` files, private keys, tokens, passwords, database dumps, personal food-label images, or logs that may contain personal information. If a secret is exposed, revoke or rotate it first; removing it in a later commit does not make the exposed value safe.

The development email adapter does not send mail and deliberately does not print reset or verification tokens. Configure a real provider before relying on password recovery or verification. Uploads are disabled outside development/test until a real virus scanner is configured.
