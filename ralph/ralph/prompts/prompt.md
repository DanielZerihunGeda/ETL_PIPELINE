# ISSUES

Local issue files from `issues/` are provided at start of context. Parse them to understand the open issues.

You will work on the AFK issues only, not the HITL ones.

If all AFK tasks are complete, output `<promise>NO MORE TASKS</promise>`.

# TASK SELECTION

Pick the next task. Prioritize tasks in this order:

1. Critical bugfixes
2. Development infrastructure

Getting development infrastructure like tests, linting, formatting, typing, and dev scripts ready is an important precursor to building features.

3. Tracer bullets for new features

Tracer bullets are small slices of functionality that go through all layers of the system, allowing you to test and validate your approach early. This helps in identifying potential issues and ensures that the overall architecture is sound before investing significant time in development.

Start with one narrow tracer bullet, then expand it out.

4. Polish and quick wins
5. Refactors

# EXPLORATION

Explore the repo.

# IMPLEMENTATION

Use `$Tdd` to complete the task.

# FEEDBACK LOOPS

run the Python feedback loops available in the repo:

- `pytest` to run the tests
- `ruff check .` to run linting, if configured
- `ruff format --check .` to check formatting, if configured
- `mypy .` or `pyright` to run type checks, if configured

If a tool is not installed or not configured, do not invent setup unless the selected issue is about development infrastructure. Note what was skipped and why.



# THE ISSUE

If the task is complete, move the issue file to `issues/done/`.

If the task is not complete, add a note to the issue file with what was done and what remains.