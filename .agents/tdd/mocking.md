# When to Mock

Mock at **system boundaries** only:

- External APIs/providers (Microsoft JWT/JWKS, Dataverse service-principal client, OpenAI, Tesseract/OCR, embeddings, etc.)
- Dataverse persistence boundary (prefer fake repositories for default tests; live Dataverse only through opt-in integration tests)
- Time/randomness
- File system or mounted FAISS index storage (sometimes)

Don't mock:

- Your own classes/modules inside the current behavior slice
- Internal collaborators
- Anything you control

## Designing for Mockability

At system boundaries, design Python interfaces that are easy to fake or mock:

**1. Use dependency injection**

Pass external dependencies in rather than creating them internally:

```python
# Easy to fake
async def parse_resume(job: ParseJob, parser: ResumeParser) -> ParseResult:
    return await parser.parse(job.redacted_text)


# Hard to fake
async def parse_resume(job: ParseJob) -> ParseResult:
    client = OpenAIResumeParser(api_key=os.environ["OPENAI_API_KEY"])
    return await client.parse(job.redacted_text)
```

**2. Prefer SDK-style interfaces over generic fetchers**

Create specific functions for each external operation instead of one generic function with conditional logic:

```python
# GOOD: Each operation has one clear fake behavior
class ProfileRepository(Protocol):
    async def get_draft(self, profile_id: str) -> DraftProfile: ...
    async def save_draft(self, draft: DraftProfile) -> DraftProfile: ...
    async def get_active_by_employee_code(self, employee_code: str) -> ActiveProfile | None: ...


# BAD: Fakes need conditional logic for every route-style operation
class DataverseGateway(Protocol):
    async def execute(self, table: str, operation: str, payload: dict) -> dict: ...
```

The SDK approach means:
- Each mock returns one specific shape
- No conditional logic in test setup
- Easier to see which endpoints a test exercises
- Typed operation boundaries per provider/repository method
