# Security Policy

## Supported Versions

The following versions of the RPG Engine v2.0 are currently supported with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 2.0.x   | :white_check_mark: |
| 1.x.x   | :x:                |

## Reporting a Vulnerability

We take security seriously in the RPG Engine project. If you discover a security vulnerability, please follow these steps:

### 🔒 **Private Reporting**

**DO NOT** create a public GitHub issue for security vulnerabilities.

Instead, please:

1. **Email**: Send details to the maintainers via GitHub's private vulnerability reporting feature
2. **Include**:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if known)

### 📝 **What to Include**

Please provide as much information as possible:

- **Component**: Which part of the engine is affected (AsyncGameEngine, ServiceContainer, EventBus, UI System)
- **Version**: Which version(s) are affected
- **Environment**: Python version, OS, specific configuration
- **Reproduction**: Step-by-step instructions
- **Impact**: Potential security implications
- **Evidence**: Screenshots, logs, or code snippets (if safe to share)

### ⏱️ **Response Timeline**

- **Initial Response**: Within 48 hours
- **Assessment**: Within 1 week
- **Fix Development**: Depends on severity and complexity
- **Disclosure**: Coordinated with reporter

### 🛡️ **Security Considerations**

The RPG Engine v2.0 is designed with security in mind:

#### **Async Safety**
- Thread-safe operations
- Proper resource cleanup
- Safe cross-thread communication

#### **Input Validation**
- Type checking throughout
- Event validation
- Service container safety

#### **Resource Management**
- Memory leak prevention
- Proper async cleanup
- Resource limits

### 🔍 **Common Security Areas**

When reporting vulnerabilities, consider these areas:

1. **Async Context**
   - Race conditions
   - Resource leaks
   - Deadlock scenarios

2. **Event System**
   - Event injection
   - Middleware vulnerabilities
   - Serialization issues

3. **Service Container**
   - Service hijacking
   - Dependency confusion
   - Lifecycle manipulation

4. **UI System**
   - Cross-thread safety
   - Input validation
   - Resource exhaustion

### 🏆 **Recognition**

Security researchers who responsibly disclose vulnerabilities will be:
- Credited in the security advisory (if desired)
- Listed in our security acknowledgments
- Given priority support for future reports

### 📚 **Security Best Practices**

When using the RPG Engine:

1. **Keep Updated**: Use the latest version
2. **Validate Input**: Check all external inputs
3. **Resource Limits**: Set appropriate limits
4. **Monitor Usage**: Watch for unusual patterns
5. **Follow Async Patterns**: Use proper async/await patterns

### ❌ **Out of Scope**

The following are typically **not** considered security vulnerabilities:

- Performance issues (unless they enable DoS)
- UI/UX issues
- Feature requests
- Configuration issues
- Third-party dependency issues (report to those projects)

### 📞 **Contact Information**

For security-related questions or concerns:
- Use GitHub's private vulnerability reporting
- Check existing security advisories
- Review the security policy updates

---

**Thank you for helping keep the RPG Engine secure!** 🛡️
