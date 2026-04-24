---
name: djlint-template-validation
description: Validate Django templates using djlint for HTML/template linting. Use whenever Django template files are modified to ensure code quality and consistency.
---

# Django Template Linting with djlint

## When to Use

**Use this skill whenever:**
- Creating or modifying Django template files (`.html` files in `book_tracker/templates/`)
- Refactoring existing templates
- Adding new HTMX partials
- Updating base templates or includes
- Performing template cleanup or reorganization

## Workflow

### 1. Spin Up Docker Test Environment

Start the Docker test environment (database and backend container must be healthy):

```bash
docker compose -f compose.yml -f compose.test.yml down
docker compose -f compose.yml -f compose.test.yml up --build -d --wait --wait-timeout 60
```

Wait for containers to reach "Healthy" status (typically ~10-15 seconds, up to 90 seconds if building from scratch).

### 2. Run djlint Validation

Execute djlint on the templates directory in the backend container:

```bash
docker compose -f compose.yml -f compose.test.yml exec -T backend djlint book_tracker/templates
```

The `-T` flag disables pseudo-TTY allocation (required for non-interactive execution).

### 3. Review djlint Output

djlint output shows:
- **Line numbers** of violations
- **Severity levels** (error, warning, info)
- **Rule codes** (H001, H002, H003, etc.)
- **Detailed messages** explaining each issue

Example output:
```
book_tracker/templates/base.html
  3:0  H001  Doctype should be declared at the top of the file

book_tracker/templates/book_tracker/authors/list.html
  5:4  H025  Tag should be preceded by a newline
  12:10  I001  Unused <style> tag (Django safe, but djlint may flag)
```

### 4. Fix Issues (If Any)

Common djlint violations and fixes:

| Rule | Issue | Fix |
|------|-------|-----|
| H001 | Missing doctype | Add `<!DOCTYPE html>` at top of base.html (if not inheriting) |
| H006 | Missing closing tag | Ensure all HTML tags are properly closed |
| H025 | Missing newline before tag | Add newline for readability |
| H017 | Empty tag | Remove tags with no content, or add semantic content |
| H003 | Incorrect indentation | Use consistent 2 or 4 space indents (configure in `.djlintrc` if needed) |

### 5. Tear Down Environment

Clean up the test environment after validation:

```bash
docker compose -f compose.yml -f compose.test.yml down
```

## Automated Workflow (Single Command)

For convenience, run the entire workflow in one command:

```bash
docker compose -f compose.yml -f compose.test.yml down && \
docker compose -f compose.yml -f compose.test.yml up --build -d --wait --wait-timeout 60 && \
docker compose -f compose.yml -f compose.test.yml exec -T backend djlint book_tracker/templates && \
docker compose -f compose.yml -f compose.test.yml down
```

This:
1. Tears down any existing containers
2. Builds and starts fresh test environment
3. Waits for containers to be healthy
4. Runs djlint validation
5. Cleans up afterward

**Terminal Setup:**
- Run in `sync` mode with at least 60 second timeout to allow for container startup
- Adjust timeout if your Docker build is slower: `timeout_ms = startup_time + lint_time + teardown_time`

## Configuration

djlint behavior is configured via `.djlintrc` (if present) or `pyproject.toml`. Check project root for:
```toml
[tool.djlint]
# Configuration options
```

Common options:
- `ignore`: Rule codes to skip (e.g., `["H001", "H003"]`)
- `indent`: Space count for indentation (default: 4)
- `profile`: Template engine profile ("django", "jinja", "nunjucks")

## Integration with Template Development

**Workflow:**
1. Create/modify template file
2. Run djlint validation (single command above)
3. Fix any violations reported
4. Commit changes

**Best Practices:**
- Run djlint after each significant template change
- Fix violations immediately rather than deferring
- Use consistent indentation and tag closing throughout
- Understand why rules exist (accessibility, maintainability, consistency)

## Troubleshooting

**"Container is not running" error**
- Ensure `docker compose -f compose.yml -f compose.test.yml up --build -d --wait` completed successfully
- Check container logs: `docker compose -f compose.yml -f compose.test.yml logs backend`

**"djlint: command not found"**
- djlint is installed in the backend container (check Dockerfile)
- Ensure you're using `exec -T backend` (targeting the correct container)

**False positives with Django template tags**
- djlint may flag Django-specific syntax as errors (e.g., `{% if %}`, `{{ variable }}`)
- Verify violations are actual HTML/template issues, not Django constructs
- Ignore non-issues if they don't affect readability or functionality

**No violations found**
- Exit code 0 = templates pass validation ✅
- No output = all templates conform to djlint rules
