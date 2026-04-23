# Testing Anti-Patterns

**Load this reference when:** writing or changing tests, adding mocks, or tempted to add test-only methods to production code.

## Overview

Tests must verify real behavior, not mock behavior. Mocks are a means to isolate, not the thing being tested.

**Core principle:** Test what the code does, not what the mocks do.

**Following strict TDD prevents these anti-patterns.**

## Python/Django Test Execution Rule

Run tests in Docker only, and always use the required lifecycle:

```bash
docker compose -f compose.yml -f compose.test.yml down
docker compose -f compose.yml -f compose.test.yml up --build -d --wait --wait-timeout 60
docker compose -f compose.yml -f compose.test.yml exec backend pytest
docker compose -f compose.yml -f compose.test.yml down
```

Use focused test selection during RED/GREEN loops.

## The Iron Laws

```
1. NEVER test mock behavior
2. NEVER add test-only methods to production classes
3. NEVER mock without understanding dependencies
```

## Anti-Pattern 1: Testing Mock Behavior

**The violation:**
```python
# BAD: Testing that the mock exists
from unittest.mock import patch


def test_book_list_renders_sidebar_mock(client):
    with patch("book_tracker.views.render_sidebar"):
        response = client.get("/books/")
    assert "sidebar-mock" in response.content.decode()
```

**Why this is wrong:**
- You're verifying the mock works, not that the view/template works
- Test passes when mock marker is present, fails when it is not
- Tells you nothing about real behavior

**your human partner's correction:** "Are we testing the behavior of a mock?"

**The fix:**
```python
# GOOD: Test real behavior
import pytest


@pytest.mark.django_db
def test_books_page_contains_navigation(client):
    response = client.get("/books/")
    assert response.status_code == 200
    assert b"Books" in response.content
```

### Gate Function

```
BEFORE asserting on any mocked output:
  Ask: "Am I testing real component behavior or just mock existence?"

  IF testing mock existence:
    STOP - Delete the assertion or remove the mock

  Test real behavior instead
```

## Anti-Pattern 2: Test-Only Methods in Production

**The violation:**
```python
# BAD: cleanup() only used in tests
class PracticeSession:
    def cleanup_for_tests(self):
        self._temp_files.clear()
        self._cache.clear()


def test_session_teardown():
    session = PracticeSession()
    session.cleanup_for_tests()
```

**Why this is wrong:**
- Production class polluted with test-only code
- Dangerous if accidentally used in production flow
- Violates YAGNI and separation of concerns

**The fix:**
```python
# GOOD: Put test cleanup in test utilities/conftest fixtures
import pytest


@pytest.fixture
def practice_session(tmp_path):
    session = create_practice_session(tmp_path)
    yield session
    cleanup_practice_session(session)
```

### Gate Function

```
BEFORE adding any method to production class:
  Ask: "Is this only used by tests?"

  IF yes:
    STOP - Don't add it
    Put it in test utilities or fixtures instead

  Ask: "Does this class own this resource lifecycle?"

  IF no:
    STOP - Wrong class for this method
```

## Anti-Pattern 3: Mocking Without Understanding

**The violation:**
```python
# BAD: Mock breaks side effects test depends on
from unittest.mock import patch


@patch("book_tracker.services.sync_notation")
def test_duplicate_exercise_detection(mock_sync, client):
    mock_sync.return_value = None  # Removes behavior that writes identifier

    client.post("/exercises/create/", data={"identifier": "RUD-001"})
    response = client.post("/exercises/create/", data={"identifier": "RUD-001"})

    assert response.status_code == 400  # May fail for wrong reason
```

**Why this is wrong:**
- Mocked function may remove side effects the test relies on
- Over-mocking to "be safe" breaks real behavior
- Test can pass/fail for the wrong reason

**The fix:**
```python
# GOOD: Mock only slow/external boundary and keep required side effects
from unittest.mock import patch


@patch("book_tracker.integrations.audiveris_client.run")
def test_duplicate_exercise_detection(mock_audiveris, client):
    mock_audiveris.return_value = {"status": "ok"}

    client.post("/exercises/create/", data={"identifier": "RUD-001"})
    response = client.post("/exercises/create/", data={"identifier": "RUD-001"})

    assert response.status_code == 400
```

### Gate Function

```
BEFORE mocking any method:
  STOP - Don't mock yet

  1. Ask: "What side effects does the real method have?"
  2. Ask: "Does this test depend on any of those side effects?"
  3. Ask: "Do I fully understand what this test needs?"

  IF depends on side effects:
    Mock at lower level (actual external/slow operation)
    OR use a test double that preserves required behavior

  IF unsure what test depends on:
    Run with real implementation first
    Observe required behavior
    THEN add minimal mocking
```

## Anti-Pattern 4: Incomplete Mocks

**The violation:**
```python
# BAD: Partial mock - only fields you think you need
mock_result = {
    "status": "ok",
    "notation": {"page": 1},
    # Missing fields your code may use later (e.g., "confidence", "source")
}
```

**Why this is wrong:**
- Partial mocks hide structural assumptions
- Downstream code may depend on omitted fields
- Tests pass but integration fails

**The Iron Rule:** Mock the complete data structure the real dependency returns.

**The fix:**
```python
# GOOD: Mirror complete response structure
mock_result = {
    "status": "ok",
    "notation": {"page": 1, "system": 2},
    "confidence": 0.98,
    "source": "audiveris",
}
```

### Gate Function

```
BEFORE creating mock responses:
  Check: "What fields does the real response contain?"

  Actions:
    1. Inspect docs/examples/real output
    2. Include all fields consumed downstream
    3. Keep schema parity with production response
```

## Anti-Pattern 5: Integration Tests as Afterthought

**The violation:**
```
Implementation complete
No tests written
"Ready for testing"
```

**Why this is wrong:**
- Testing is part of implementation, not follow-up
- TDD would have caught this earlier
- Can't claim complete without tests

**The fix:**
```
TDD cycle:
1. Write failing pytest test
2. Run in Docker and verify RED
3. Implement minimal code to pass
4. Re-run in Docker and verify GREEN
5. Refactor while staying green
```

## Coverage Is Part of Done

After GREEN, run coverage and close gaps using `pytest-coverage`:

```bash
docker compose -f compose.yml -f compose.test.yml down
docker compose -f compose.yml -f compose.test.yml up --build -d --wait --wait-timeout 60
docker compose -f compose.yml -f compose.test.yml exec backend pytest --cov --cov-report=annotate:cov_annotate
docker compose -f compose.yml -f compose.test.yml down
```

Use `cov_annotate` output and add tests first for lines marked with `!`.

## When Mocks Become Too Complex

**Warning signs:**
- Mock setup longer than test logic
- Mocking everything to make test pass
- Test breaks when mock changes

**your human partner's question:** "Do we need to be using a mock here?"

**Consider:** Integration tests with real Django components are often simpler than deep mock trees.

## TDD Prevents These Anti-Patterns

**Why TDD helps:**
1. **Write test first** -> Forces clarity on intended behavior
2. **Watch it fail** -> Confirms test is meaningful
3. **Minimal implementation** -> Prevents test-only production code
4. **Minimal mocking** -> Encourages understanding real dependencies

## Quick Reference

| Anti-Pattern | Fix |
|--------------|-----|
| Assert on mocked artifacts | Test real behavior or remove mock |
| Test-only methods in production | Move to fixtures/test helpers |
| Mock without understanding | Understand dependencies, mock minimally |
| Incomplete mocks | Match real schema fully |
| Tests as afterthought | TDD: RED -> GREEN -> REFACTOR |
| Over-complex mocks | Prefer integration tests where practical |

## Red Flags

- Assertion checks only mocked artifacts
- Methods used only by tests appear in production code
- Mock setup is >50% of test
- Can't explain why mock is needed
- Mocking "just to be safe"

## The Bottom Line

**Mocks are tools to isolate, not the thing to validate.**

If TDD reveals you're testing mock behavior, you've gone wrong.

Fix: test real behavior or remove unnecessary mocking.
