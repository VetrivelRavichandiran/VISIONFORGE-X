# 🔒 Security Policy

## Supported Versions

The following versions of VISIONFORGE X are currently supported with security updates:

| Version | Supported |
|---------|-----------|
| Latest release (`main` branch) | ✅ Yes |
| Previous release | ✅ Yes (30 days after next release) |
| Older releases | ❌ No |

---

## Reporting a Vulnerability

We take the security of VISIONFORGE X seriously. If you discover a security vulnerability, we appreciate your responsible disclosure.

### How to Report

**Please do NOT open a public issue** for security vulnerabilities.

Instead, report vulnerabilities privately via one of these methods:

1. **GitHub Private Security Advisory**
   - Go to: https://github.com/VetrivelRavichandiran/VISIONFORGE-X/security/advisories
   - Click "Report a vulnerability"
   - Provide as much detail as possible

2. **Direct Message**
   - Send a private message to the maintainer on GitHub

### What to Include

Please provide the following information to help us understand and address the issue:

- **Description** of the vulnerability
- **Affected version(s)**
- **Steps to reproduce**
- **Potential impact**
- **Suggested fix** (if you have one)
- **Proof of concept** (optional but helpful)

---

## Response Process

1. **Acknowledgment**: You will receive an acknowledgment within 48 hours of your report.
2. **Assessment**: The maintainer will assess the vulnerability and determine its severity.
3. **Fix**: A fix will be developed and tested. You will be kept informed of progress.
4. **Disclosure**: Once a fix is released, you will be credited (unless you prefer anonymity).

### Severity Levels

| Level | Description | Response Time |
|-------|-------------|---------------|
| Critical | Remote code execution, data breach | 24-48 hours |
| High | Privilege escalation, auth bypass | 3-5 days |
| Medium | Information disclosure, DoS | 1-2 weeks |
| Low | Minor issues, best-practice violations | Next release |

---

## Security Best Practices

### For Users

- Always use the latest released version
- Keep your Python environment and dependencies up to date
- Do not run the application with elevated privileges unless necessary
- Review the `requirements.txt` before installing
- Use simulation mode for development/testing when hardware is not required

### For Developers

- Never commit secrets, tokens, or credentials to the repository
- Use environment variables for sensitive configuration
- Validate all inputs before processing
- Follow the principle of least privilege
- Keep dependencies updated and review for known vulnerabilities

---

## Dependency Management

This project uses the following security practices:

- Dependencies are pinned with minimum version constraints in `requirements.txt`
- Regular updates are reviewed for known CVEs
- Security audits can be run with:
  ```bash
  pip install pip-audit
  pip-audit
  ```

---

## Acknowledgments

We thank all security researchers who responsibly disclose vulnerabilities. Your contributions help make VISIONFORGE X safer for everyone.

---

*This policy is subject to change. Please refer to this page for the most current security information.*
