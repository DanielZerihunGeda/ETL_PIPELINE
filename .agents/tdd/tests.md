# Good and Bad Tests

## Good Tests

**Integration-style**: Test through real FastAPI route contracts, stable application-service interfaces, or repository/provider protocols. Use fakes at provider boundaries so normal pytest runs stay local and credential-free.

```python
# GOOD: Tests observable API behavior
def test_draft_patch_rejects_unknown_fields(api_client, auth_headers, draft):
    response = api_client.patch(
        f"/api/profiles/{draft.profile_id}/draft",
        headers={**auth_headers, "If-Match": str(draft.version)},
        json={"unknown": "rejected"},
    )

    assert response.status_code == 422
    assert response.json()["code"] == "validation_error"
```

Characteristics:

- Tests behavior users/callers care about
- Uses public API only
- Survives internal refactors
- Describes WHAT, not HOW
- One logical assertion per test

## Bad Tests

**Implementation-detail tests**: Coupled to internal structure.

```python
# BAD: Tests implementation details
import asyncio
from unittest.mock import AsyncMock


def test_confirm_calls_replace_child_records(confirm_service, draft):
    confirm_service.active_children.replace_all = AsyncMock()

    asyncio.run(confirm_service.confirm(draft.profile_id))

    confirm_service.active_children.replace_all.assert_called_once()
```

Red flags:

- Mocking internal collaborators
- Testing private methods
- Asserting on call counts/order
- Test breaks when refactoring without behavior change
- Test name describes HOW not WHAT
- Verifying through external means instead of interface

```python
# BAD: Bypasses the route/detail interface to verify route behavior
def test_catalog_create_writes_to_fake_repository(
    api_client,
    fake_catalog_repo,
    auth_headers,
):
    api_client.post(
        "/api/catalogs/ventures",
        headers={**auth_headers, "Idempotency-Key": "catalog-create-1"},
        json={"code": "ASE", "display_name": "ASE"},
    )

    assert fake_catalog_repo.rows["ASE"]["display_name"] == "ASE"


# GOOD: Verifies through the public interface
def test_catalog_create_makes_value_retrievable(api_client, auth_headers):
    create_response = api_client.post(
        "/api/catalogs/ventures",
        headers={**auth_headers, "Idempotency-Key": "catalog-create-1"},
        json={"code": "ASE", "display_name": "ASE"},
    )

    list_response = api_client.get("/api/catalogs/ventures", headers=auth_headers)

    assert create_response.status_code == 201
    assert {
        "code": "ASE",
        "display_name": "ASE",
        "active": True,
    } in list_response.json()["items"]
```
