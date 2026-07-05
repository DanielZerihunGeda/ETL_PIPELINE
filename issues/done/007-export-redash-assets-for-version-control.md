# Export Redash Assets for Version Control

## Type
AFK

## Blocked by
`006-build-redash-dashboard-from-transformed-models.md`

## User stories covered
- User Story 10 - Version Control Redash Assets

## Goal
Add a configurable script that exports Redash dashboard and query definitions through the Redash API into local version-control-friendly files.

## Implementation notes
- Add a script that calls the Redash API to export query and dashboard definitions.
- Configure the script through environment variables such as Redash URL, API key, dashboard identifiers, and output directory.
- Store exported assets as stable JSON files in a local folder suitable for version control.
- Avoid committing secrets or API keys.
- Document how to run the export script after Redash has a configured dashboard.

## Acceptance criteria
- The export script reads Redash URL and API key from environment variables.
- The script exports dashboard definitions and related query definitions.
- Exported files are saved in a deterministic, version-control-friendly folder structure.
- The script fails clearly when required configuration is missing.
- Documentation explains the required environment variables and command.

## Verification steps
- Set Redash URL and API key environment variables for the local stack.
- Run the export script against the dashboard created in issue 006.
- Confirm dashboard and query JSON files are written locally.
- Confirm secrets are not written into exported files.
- Re-run the script and confirm output remains stable enough for version control diffs.
