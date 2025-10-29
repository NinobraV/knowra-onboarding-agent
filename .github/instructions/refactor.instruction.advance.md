GOLDEN RULES (MANDATORY)

No destructive changes without explicit confirmation.
Never delete or modify these files unless you list the reason and obtain explicit confirmation:
.env, .env.*, package.json, pyproject.toml, requirements.txt, poetry.lock, Pipfile, Pipfile.lock, yarn.lock, package-lock.json, docker-compose.yml, Dockerfile, .gitignore, any .sln/.csproj, composer.json, go.mod, CI config files (e.g. .github/workflows/*, .gitlab-ci.yml).

Preserve buildability.
After refactor the project must still build/start with the same commands (unless you document command updates briefly). If tests existed, they must still run — if some tests fail due to the refactor, provide a short report explaining why.

Single responsibility & readability.
Files/modules should have one clear responsibility. Prefer small functions/classes, explicit names, docstrings, and type hints where applicable.

No behavior-changing refactors without tests.
If a change modifies behavior or public API, add a small test or example demonstrating expected behavior (unless equivalent tests already exist). If tests are missing, avoid behavioral changes and note this.

PRIMITIVE RULES (APPLY ALWAYS)

Detect language & framework by file signatures (e.g., requirements.txt/pyproject.toml → Python; package.json → Node; .csproj → .NET; go.mod → Go; composer.json → PHP).

Naming conventions: follow canonical style for each ecosystem:

Python: snake_case for functions/files, PascalCase for classes.

C#: PascalCase for classes/methods.

JS/TS: camelCase for variables/functions, PascalCase for React components.

CLI/tooling files: kebab-case when idiomatic.

Imports order: stdlib → third-party → local packages. Prefer absolute imports for backend projects when idiomatic; use relative imports for tightly coupled modules where appropriate.

Type hints & interfaces: add or preserve types/interfaces where common (Python typing, TypeScript types/interfaces, C# types). Avoid inventing unnecessary complex generics.

Max file length guideline: prefer files < ~300 lines. If a file exceeds this and contains multiple responsibilities, split logically.

No circular imports: detect and resolve — move shared code into utils/core or reorganize dependencies.

Centralized configuration: centralize env/config loading in a single module (e.g., core/config.*) for backend; frontends use .env + a config loader.

ADVANCED RULES (CONTEXT-AWARE)
Backend

Group controllers/routes under api/ or controllers/.

Move business logic into services/ (no HTTP code inside services).

Models/schemas in models/ or schemas/ (Pydantic, ORM models).

DB, migrations, repository patterns under infrastructure/ or persistence/.

Use dependency injection where idiomatic (FastAPI Depends, .NET DI, NestJS providers).

Centralize error handling & response shaping in middleware or exceptions module.

Frontend

Separate presentational vs container/logic components (components/ vs containers/ or hooks//services/).

Centralize global state under store/ and restrict direct state usage in components.

Extract UI primitives into ui/ or components/ui/.

Isolate routing (e.g., routes/ or framework pages/ patterns).

Monorepo

Treat each project (e.g., frontend/, backend/, shared/) independently; do not move code across boundaries unless creating/updating a proper shared/ package with exports.

Tests

Preserve tests. If splitting files, update import paths in tests.

If no tests exist, consider adding a minimal smoke test per major module only if safe and straightforward; avoid inventing large test suites.

SAFETY RULES

Backups: create .bak copies for changed files before destructive edits, with timestamp suffix (only in the working branch). Example: service.py → service.py.bak.20251029T120000.

Dry-run & plan: present a plan summary before executing destructive actions. The plan must list files to be deleted, moved, or split.

One logical change = one commit: each logical change should be its own commit with an imperative-style message and phase prefix. Example: refactor(api): extract user service from main.

Lockfiles: do not remove third-party dependency declarations from lockfiles; only update them if needed and report changes.

Minimize blast radius: prefer non-destructive moves (create new file, update imports, leave original until verified).

EXECUTION PLAN (STEP-BY-STEP)
1) Scan & Classify

Walk [Folder_Dir] recursively and list files.

Classify files by category: routes, controllers, services, models, utils, tests, config, static, build-artifacts, others.

Output a short JSON-like plan. Example schema:

{
  "routes": ["api/users.py"],
  "controllers": ["controllers/user_controller.py"],
  "services": ["services/user_service.py"],
  "models": ["models/user.py"],
  "utils": ["utils/validators.py"],
  "tests": ["tests/test_user.py"],
  "config": ["core/config.py"],
  "others": []
}

2) Plan Summary (Dry-run)

Produce a readable plan listing files to create, move, split, modify, or delete.

Do not perform edits yet. Show a short rationale for each proposed change.

3) Execute Non-destructive Refactors

Apply reversible refactors first: create new files, copy content, add docstrings, split large files. Keep originals until verification.

For every moved/split file, add a header comment:

# Moved from: <old-path>

# Reason: <short reason>

Update imports (relative/absolute) accordingly.

Create .bak copies for modified files as described.

4) Lint & Format (if toolchain available)

Python: black --check (or ruff --fix), then apply formatting.

JS/TS: eslint --fix and prettier --check then apply fixes.

C#/.NET: dotnet format or run configured analyzers.

Report lint errors that cannot be auto-fixed.

5) Execute Safe Deletions

After verification and approval, delete files marked for removal. Keep .bak backups until final confirmation.

6) Run Tests / Smoke Checks

Run test suite or basic startup command:

If tests exist: run full test suite and report failures, categorizing them as pre-existing or introduced.

If no tests: run a smoke/startup command and report status.

7) Commit Changes

Group commits logically. Provide suggested commit messages for each commit.

Example commit message style: refactor(service): extract email validation to utils.

8) Final Report

Provide a summary containing:

Files moved / created / deleted.

Lint/format results and fixes applied.

Tests run and outcomes.

Any failing checks and whether they are pre-existing or introduced.

Manual follow-ups required (e.g., update CI, DB migrations, docs).

List of .bak files created and where to find them.