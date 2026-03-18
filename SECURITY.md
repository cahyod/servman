# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.1.x   | :white_check_mark: |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take the security of Service Manager seriously. If you discover a security vulnerability, please follow these steps:

### How to Report

1. **DO NOT** create a public GitHub issue
2. Send an email to the maintainers or use GitHub's private vulnerability reporting feature
3. Include as much information as possible:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

### What to Expect

- **Initial Response**: Within 48 hours
- **Status Update**: Within 1 week
- **Resolution Timeline**: Depends on severity
  - Critical: 24-48 hours
  - High: 1 week
  - Medium: 2 weeks
  - Low: 1 month

### Security Considerations

This application:
- Uses `pkexec` for privilege escalation (requires root password)
- Executes `systemctl` commands based on user selection
- Does not store credentials
- Does not transmit data over network

### Known Limitations

- Application requires polkit to be properly configured
- User must have sudo/polkit privileges to modify services
- No sandboxing - runs with user privileges

## Security Best Practices for Users

1. Only run this application on trusted systems
2. Keep your system updated
3. Review service changes before applying
4. Use standard Linux security practices

## Acknowledgments

We appreciate responsible disclosure and will credit researchers who report valid security issues (with permission).

---

*Last updated: January 2024*
