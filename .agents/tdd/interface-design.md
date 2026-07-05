# Interface Design for Testability

Good interfaces make testing natural:

1. **Accept dependencies, don't create them**

   ```python
   # Testable
   async def confirm_draft(
       profile_id: str,
       repositories: ProfileRepositories,
       clock: Clock,
   ) -> ConfirmationResult:
       ...

   # Hard to test
   async def confirm_draft(profile_id: str) -> ConfirmationResult:
       repositories = DataverseProfileRepositories.from_environment()
       ...
   ```

2. **Return results, don't produce side effects**

   ```python
   # Testable
   def validate_confirmation(draft: DraftProfile, catalogs: CatalogSnapshot) -> ValidationResult:
       ...

   # Hard to test
   def apply_confirmation_validation(draft: DraftProfile) -> None:
       draft.errors.append("missing_employee_code")
   ```

3. **Small surface area**
   - Fewer methods = fewer tests needed
   - Fewer params = simpler test setup
