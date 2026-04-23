---
name: test-driven-development
description: Use when implementing any feature or bugfix, before writing implementation code
---

# Test-Driven Development (TDD)

## Overview

Write the test first. Watch it fail. Write minimal code to pass.

**Core principle:** If you didn't watch the test fail, you don't know if it tests the right thing.

**Violating the letter of the rules is violating the spirit of the rules.**

## Required Companion Skills

- Use `context-map` before implementation to map files, dependencies, related tests, and risks.
- Use `pytest-coverage` after behavior is green to find and fix uncovered lines.

## When to Use

**Always:**
- New features
- Bug fixes
- Refactoring
- Behavior changes

**Exceptions (ask your human partner):**
- Throwaway prototypes
- Generated code
- Configuration files

Thinking "skip TDD just this once"? Stop. That's rationalization.

## The Iron Law

```
NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST
```

Write code before the test? Delete it. Start over.

**No exceptions:**
- Don't keep it as "reference"
- Don't "adapt" it while writing tests
- Don't look at it
- Delete means delete

Implement fresh from tests. Period.

## Docker Test Environment (Mandatory)

All test execution in this repository must use the Docker test environment.

Before each test run:

```bash
docker compose -f compose.yml -f compose.test.yml down
docker compose -f compose.yml -f compose.test.yml up --build -d --wait --wait-timeout 60
```

Run tests in the backend container:

```bash
docker compose -f compose.yml -f compose.test.yml exec backend pytest
```

After finishing each test run:

```bash
docker compose -f compose.yml -f compose.test.yml down
```

For focused RED/GREEN loops, execute a specific test path instead of the full suite.

## Red-Green-Refactor

```dot
digraph tdd_cycle {
    rankdir=LR;
    red [label="RED\nWrite failing test", shape=box, style=filled, fillcolor="#ffcccc"];
    verify_red [label="Verify fails\ncorrectly", shape=diamond];
    green [label="GREEN\nMinimal code", shape=box, style=filled, fillcolor="#ccffcc"];
    verify_green [label="Verify passes\nAll green", shape=diamond];
    refactor [label="REFACTOR\nClean up", shape=box, style=filled, fillcolor="#ccccff"];
    next [label="Next", shape=ellipse];

    red -> verify_red;
    verify_red -> green [label="yes"];
    verify_red -> red [label="wrong\nfailure"];
    green -> verify_green;
    verify_green -> refactor [label="yes"];
    verify_green -> green [label="no"];
    refactor -> verify_green [label="stay\ngreen"];
    verify_green -> next;
    next -> red;
}
```

### RED - Write Failing Test

Write one minimal test showing what should happen.

<Good>
```python
def test_retries_failed_operations_three_times():
    attempts = {"count": 0}

    def operation():
        attempts["count"] += 1
        if attempts["count"] < 3:
            raise ValueError("fail")
        return "success"

    result = retry_operation(operation)

    assert result == "success"
    assert attempts["count"] == 3
```
Clear name, tests real behavior, one thing
</Good>

<Bad>
```python
from unittest.mock import Mock


def test_retry_works():
    operation = Mock(side_effect=[ValueError("fail"), ValueError("fail"), "success"])
    retry_operation(operation)
    assert operation.call_count == 3
```
Vague name, tests mock not code
</Bad>

**Requirements:**
- One behavior
- Clear name
- Real code (no mocks unless unavoidable)

### Verify RED - Watch It Fail

**MANDATORY. Never skip.**

```bash
docker compose -f compose.yml -f compose.test.yml down
docker compose -f compose.yml -f compose.test.yml up --build -d --wait --wait-timeout 60
docker compose -f compose.yml -f compose.test.yml exec backend pytest tests/test_target.py::test_case_name -q
docker compose -f compose.yml -f compose.test.yml down
```

Confirm:
- Test fails (not errors)
- Failure message is expected
- Fails because feature missing (not typos)

**Test passes?** You're testing existing behavior. Fix test.

**Test errors?** Fix error, re-run until it fails correctly.

### GREEN - Minimal Code

Write simplest code to pass the test.

<Good>
```python
def retry_operation(fn):
    for attempt in range(3):
        try:
            return fn()
        except Exception:
            if attempt == 2:
                raise
    raise RuntimeError("unreachable")
```
Just enough to pass
</Good>

<Bad>
```python
def retry_operation(
    fn,
    max_retries=3,
    backoff="exponential",
    on_retry=None,
    retryable_exceptions=(Exception,),
):
    # YAGNI
    ...
```
Over-engineered
</Bad>

Don't add features, refactor other code, or "improve" beyond the test.

### Verify GREEN - Watch It Pass

**MANDATORY.**

```bash
docker compose -f compose.yml -f compose.test.yml down
docker compose -f compose.yml -f compose.test.yml up --build -d --wait --wait-timeout 60
docker compose -f compose.yml -f compose.test.yml exec backend pytest tests/test_target.py::test_case_name -q
docker compose -f compose.yml -f compose.test.yml down
```

Confirm:
- Test passes
- Other tests still pass
- Output pristine (no errors, warnings)

**Test fails?** Fix code, not test.

**Other tests fail?** Fix now.

### REFACTOR - Clean Up

After green only:
- Remove duplication
- Improve names
- Extract helpers

Keep tests green. Don't add behavior.

### Repeat

Next failing test for next feature.

## Good Tests

| Quality | Good | Bad |
|---------|------|-----|
| **Minimal** | One thing. "and" in name? Split it. | `def test_validates_email_and_domain_and_whitespace(): ...` |
| **Clear** | Name describes behavior | `def test_thing(): ...` |
| **Shows intent** | Demonstrates desired API | Obscures what code should do |

## Why Order Matters

**"I'll write tests after to verify it works"**

Tests written after code pass immediately. Passing immediately proves nothing:
- Might test wrong thing
- Might test implementation, not behavior
- Might miss edge cases you forgot
- You never saw it catch the bug

Test-first forces you to see the test fail, proving it actually tests something.

**"I already manually tested all the edge cases"**

Manual testing is ad-hoc. You think you tested everything but:
- No record of what you tested
- Can't re-run when code changes
- Easy to forget cases under pressure
- "It worked when I tried it" != comprehensive

Automated tests are systematic. They run the same way every time.

**"Deleting X hours of work is wasteful"**

Sunk cost fallacy. The time is already gone. Your choice now:
- Delete and rewrite with TDD (X more hours, high confidence)
- Keep it and add tests after (30 min, low confidence, likely bugs)

The "waste" is keeping code you can't trust. Working code without real tests is technical debt.

**"TDD is dogmatic, being pragmatic means adapting"**

TDD IS pragmatic:
- Finds bugs before commit (faster than debugging after)
- Prevents regressions (tests catch breaks immediately)
- Documents behavior (tests show how to use code)
- Enables refactoring (change freely, tests catch breaks)

"Pragmatic" shortcuts = debugging in production = slower.

**"Tests after achieve the same goals - it's spirit not ritual"**

No. Tests-after answer "What does this do?" Tests-first answer "What should this do?"

Tests-after are biased by your implementation. You test what you built, not what's required. You verify remembered edge cases, not discovered ones.

Tests-first force edge case discovery before implementing. Tests-after verify you remembered everything (you didn't).

30 minutes of tests after != TDD. You get coverage, lose proof tests work.

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "Too simple to test" | Simple code breaks. Test takes 30 seconds. |
| "I'll test after" | Tests passing immediately prove nothing. |
| "Tests after achieve same goals" | Tests-after = "what does this do?" Tests-first = "what should this do?" |
| "Already manually tested" | Ad-hoc != systematic. No record, can't re-run. |
| "Deleting X hours is wasteful" | Sunk cost fallacy. Keeping unverified code is technical debt. |
| "Keep as reference, write tests first" | You'll adapt it. That's testing after. Delete means delete. |
| "Need to explore first" | Fine. Throw away exploration, start with TDD. |
| "Test hard = design unclear" | Listen to test. Hard to test = hard to use. |
| "TDD will slow me down" | TDD faster than debugging. Pragmatic = test-first. |
| "Manual test faster" | Manual doesn't prove edge cases. You'll re-test every change. |
| "Existing code has no tests" | You're improving it. Add tests for existing code. |

## Red Flags - STOP and Start Over

- Code before test
- Test after implementation
- Test passes immediately
- Can't explain why test failed
- Tests added "later"
- Rationalizing "just this once"
- "I already manually tested it"
- "Tests after achieve the same purpose"
- "It's about spirit not ritual"
- "Keep as reference" or "adapt existing code"
- "Already spent X hours, deleting is wasteful"
- "TDD is dogmatic, I'm being pragmatic"
- "This is different because..."

**All of these mean: Delete code. Start over with TDD.**

## Example: Bug Fix

**Bug:** Empty email accepted

**RED**
```python
import pytest


@pytest.mark.django_db
def test_submit_form_rejects_empty_email(client):
    response = client.post("/submit-form/", data={"email": ""})
    assert response.status_code == 400
    assert response.json()["error"] == "Email required"
```

**Verify RED**
```bash
$ docker compose -f compose.yml -f compose.test.yml down
$ docker compose -f compose.yml -f compose.test.yml up --build -d --wait --wait-timeout 60
$ docker compose -f compose.yml -f compose.test.yml exec backend pytest tests/test_submit_form.py::test_submit_form_rejects_empty_email -q
FAIL: assert 200 == 400
$ docker compose -f compose.yml -f compose.test.yml down
```

**GREEN**
```python
from django.http import JsonResponse


def submit_form(request):
    email = request.POST.get("email", "").strip()
    if not email:
        return JsonResponse({"error": "Email required"}, status=400)
    ...
```

**Verify GREEN**
```bash
$ docker compose -f compose.yml -f compose.test.yml down
$ docker compose -f compose.yml -f compose.test.yml up --build -d --wait --wait-timeout 60
$ docker compose -f compose.yml -f compose.test.yml exec backend pytest tests/test_submit_form.py::test_submit_form_rejects_empty_email -q
PASS
$ docker compose -f compose.yml -f compose.test.yml down
```

**REFACTOR**
Extract validation for multiple fields if needed.

## Coverage Loop for Uncovered Lines

After behavior tests are green, run coverage and close gaps using `pytest-coverage`.

```bash
docker compose -f compose.yml -f compose.test.yml down
docker compose -f compose.yml -f compose.test.yml up --build -d --wait --wait-timeout 60
docker compose -f compose.yml -f compose.test.yml exec backend pytest --cov --cov-report=annotate:cov_annotate
docker compose -f compose.yml -f compose.test.yml down
```

Then:
- Open `cov_annotate` output in the repository.
- For each line marked with `!`, add or improve tests first.
- Re-run RED/GREEN cycle for each newly added behavior test.
- Re-run coverage until uncovered critical lines are resolved.

## Verification Checklist

Before marking work complete:

- [ ] Ran `context-map` and reviewed impacted files/tests before coding
- [ ] Every new function/method has a test
- [ ] Watched each test fail before implementing
- [ ] Each test failed for expected reason (feature missing, not typo)
- [ ] Wrote minimal code to pass each test
- [ ] All tests pass
- [ ] Output pristine (no errors, warnings)
- [ ] Tests use real code (mocks only if unavoidable)
- [ ] Edge cases and errors covered
- [ ] Ran `pytest --cov` in Docker and addressed uncovered lines with tests first
- [ ] Brought test environment down after each run

Can't check all boxes? You skipped TDD. Start over.

## When Stuck

| Problem | Solution |
|---------|----------|
| Don't know how to test | Write wished-for API. Write assertion first. Ask your human partner. |
| Test too complicated | Design too complicated. Simplify interface. |
| Must mock everything | Code too coupled. Use dependency injection. |
| Test setup huge | Extract helpers. Still complex? Simplify design. |

## Debugging Integration

Bug found? Write failing test reproducing it. Follow TDD cycle. Test proves fix and prevents regression.

Never fix bugs without a test.

## Testing Anti-Patterns

When adding mocks or test utilities, read @testing-anti-patterns.md to avoid common pitfalls:
- Testing mock behavior instead of real behavior
- Adding test-only methods to production classes
- Mocking without understanding dependencies

## Final Rule

```
Production code -> test exists and failed first
Otherwise -> not TDD
```

No exceptions without your human partner's permission.
