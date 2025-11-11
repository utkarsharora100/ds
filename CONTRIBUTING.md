# Contributing to Distributed Movie Booking System

Thank you for your interest in contributing! This project is designed for educational purposes and welcomes improvements.

## 🎯 Areas for Contribution

### High Priority

1. **Persistent Storage**
   - Replace in-memory SQLite with PostgreSQL/MySQL
   - Implement database migrations
   - Add connection pooling

2. **Security Enhancements**
   - Add password hashing (bcrypt/argon2)
   - Implement JWT authentication
   - Add rate limiting
   - Input validation and sanitization

3. **Test Coverage**
   - Complete `tests/test_raft.py`
   - Complete `tests/test_booking.py`
   - Add integration tests
   - Add load tests

4. **Raft Improvements**
   - Persistent log storage
   - Log compaction/snapshots
   - Dynamic cluster membership
   - Better failure recovery

### Medium Priority

5. **API Enhancements**
   - RESTful API documentation (OpenAPI/Swagger)
   - WebSocket support for real-time updates
   - GraphQL endpoint

6. **Frontend**
   - Web-based UI (React/Vue)
   - Mobile app (React Native/Flutter)
   - Improved UX in existing GUI

7. **Monitoring**
   - Prometheus metrics
   - Health check endpoints
   - Structured logging
   - Distributed tracing

8. **Features**
   - Payment gateway integration
   - Email notifications
   - Seat map visualization
   - Multi-city support

### Low Priority

9. **Documentation**
   - API examples
   - Video tutorials
   - Architecture diagrams
   - Blog posts

10. **DevOps**
    - Docker/Docker Compose setup
    - Kubernetes manifests
    - CI/CD pipeline (GitHub Actions)
    - Infrastructure as Code (Terraform)

---

## 🔧 Development Setup

### 1. Fork and Clone

```bash
git clone https://github.com/YOUR_USERNAME/ds.git
cd ds
```

### 2. Create Branch

```bash
git checkout -b feature/your-feature-name
```

### 3. Set Up Environment

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Make Changes

- Follow existing code style
- Add tests for new features
- Update documentation

### 5. Test Your Changes

```bash
# Run tests
pytest tests/

# Run the system
./start.sh  # Option 1 - Full system
```

### 6. Commit and Push

```bash
git add .
git commit -m "feat: add amazing feature"
git push origin feature/your-feature-name
```

### 7. Create Pull Request

- Go to GitHub
- Create PR from your branch
- Fill in the PR template
- Wait for review

---

## 📝 Code Style

### Python

- Follow PEP 8
- Use type hints where possible
- Add docstrings to functions/classes

**Example:**
```python
def book_seat(
    self, 
    movie: str, 
    city: str, 
    seats: int = 1
) -> Dict[str, Any]:
    """
    Book seats for a movie.
    
    Args:
        movie: Name of the movie
        city: City where movie is playing
        seats: Number of seats to book (default: 1)
        
    Returns:
        Dictionary with booking status and ID
    """
    # Implementation
    pass
```

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation only
- `style:` Formatting, missing semicolons, etc.
- `refactor:` Code restructuring
- `test:` Adding tests
- `chore:` Maintenance tasks

**Examples:**
```
feat: add payment gateway integration
fix: resolve race condition in leader election
docs: update API documentation for bookings endpoint
test: add unit tests for authentication module
```

---

## 🧪 Testing Guidelines

### Unit Tests

Place in `tests/` directory:

```python
# tests/test_authentication.py
import pytest
from Application_server.Application_server import ApplicationServer

def test_user_registration():
    server = ApplicationServer()
    result = server.register_user("testuser", "pass123")
    assert result["status"] == "success"

def test_duplicate_registration():
    server = ApplicationServer()
    server.register_user("testuser", "pass123")
    result = server.register_user("testuser", "pass123")
    assert result["status"] == "failure"
```

### Integration Tests

Test component interactions:

```python
# tests/test_integration.py
import requests

def test_full_booking_flow():
    # Register user
    register_resp = requests.post(
        "http://127.0.0.1:9000/register",
        json={"username": "user1", "password": "pass"}
    )
    assert register_resp.status_code == 200
    
    # Login
    login_resp = requests.post(
        "http://127.0.0.1:9000/login",
        json={"username": "user1", "password": "pass"}
    )
    token = login_resp.json()["token"]
    
    # Book seat
    booking_resp = requests.post(
        "http://127.0.0.1:9000/business",
        json={
            "requestId": "test-123",
            "payload": {
                "type": "book_seat",
                "data": {"movie": "Inception", "city": "NYC", "seats": 2}
            },
            "context": {"token": token}
        }
    )
    assert booking_resp.json()["status"] == "success"
```

### Running Tests

```bash
# All tests
pytest

# Specific file
pytest tests/test_raft.py

# With coverage
pytest --cov=. --cov-report=html
```

---

## 📚 Documentation Standards

### Code Comments

- Explain **why**, not **what**
- Keep comments up-to-date
- Use TODO for future improvements

```python
# Good
# Use exponential backoff to prevent election storms
timeout = base_timeout * (2 ** retry_count)

# Bad
# Set timeout to base times two to the power of retries
timeout = base_timeout * (2 ** retry_count)
```

### README Updates

When adding features:
1. Update main README.md
2. Add to ARCHITECTURE.md if architectural change
3. Update QUICKSTART.md if affects setup

---

## 🐛 Bug Reports

### Before Submitting

1. Search existing issues
2. Try latest version
3. Collect system info

### What to Include

```markdown
**Description:**
Brief description of the bug

**Steps to Reproduce:**
1. Start application server
2. Start 3 Raft nodes
3. Login as admin
4. Click "Simulate Clients"
5. Observe error

**Expected Behavior:**
Bookings should complete successfully

**Actual Behavior:**
Error: "Connection refused"

**Environment:**
- OS: Ubuntu 22.04
- Python: 3.10.6
- Dependencies: (paste requirements.txt versions)

**Logs:**
```
[error log output]
```

**Screenshots:**
[if applicable]
```

---

## 💡 Feature Requests

### Template

```markdown
**Feature Description:**
Add support for multiple cities with different movie listings

**Use Case:**
Users in different cities should see different available movies

**Proposed Solution:**
1. Add `city` field to database
2. Filter movies by user's city
3. Update UI to show city selector

**Alternatives Considered:**
- Separate databases per city (rejected - too complex)
- No filtering (rejected - bad UX)

**Additional Context:**
This would enable geographical scalability
```

---

## 🔍 Code Review Process

### For Reviewers

- Check code quality and style
- Verify tests pass
- Test functionality manually
- Review documentation updates
- Be constructive and respectful

### For Contributors

- Respond to feedback promptly
- Don't take criticism personally
- Ask questions if unclear
- Make requested changes

---

## 📋 PR Checklist

Before submitting:

- [ ] Code follows project style
- [ ] Tests added/updated
- [ ] All tests pass
- [ ] Documentation updated
- [ ] Commit messages follow convention
- [ ] No merge conflicts
- [ ] Self-reviewed code
- [ ] Added comments for complex logic

---

## 🏗️ Architecture Decisions

Major changes should include:

1. **Problem Statement**
2. **Proposed Solution**
3. **Alternatives Considered**
4. **Trade-offs**
5. **Implementation Plan**

Create an issue for discussion before starting work on major features.

---

## 🤝 Community Guidelines

### Be Respectful

- Welcome newcomers
- Assume good intentions
- Give constructive feedback
- Acknowledge contributions

### Communication Channels

- **Issues:** Bug reports, feature requests
- **Discussions:** Questions, ideas
- **PRs:** Code contributions

---

## 📄 License

By contributing, you agree that your contributions will be licensed under the same license as the project.

---

## 🎓 Learning Resources

### Distributed Systems

- [Raft Visualization](https://raft.github.io/)
- [Distributed Systems for Fun and Profit](http://book.mixu.net/distsys/)
- [MIT 6.824 Course](https://pdos.csail.mit.edu/6.824/)

### FastAPI

- [FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/)
- [Real Python - FastAPI](https://realpython.com/fastapi-python-web-apis/)

### gRPC

- [gRPC Python Quickstart](https://grpc.io/docs/languages/python/quickstart/)

---

## ❓ Questions?

- Create a [GitHub Discussion](https://github.com/utkarsharora100/ds/discussions)
- Check existing [Issues](https://github.com/utkarsharora100/ds/issues)

---

**Thank you for contributing! 🙌**
