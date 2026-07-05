# Refactor Candidates

After TDD cycle, look for:

- **Duplication** -> Extract Python function, class, dataclass, or fixture
- **Long route handlers/services** -> Break into private helpers or application services (keep tests on public interface)
- **Shallow modules** -> Combine or deepen behind a smaller FastAPI/service/repository interface
- **Feature envy** -> Move logic to the module that owns the data or protocol
- **Primitive obsession** -> Introduce Pydantic models, enums, dataclasses, or value objects
- **Existing code** the new code reveals as problematic
