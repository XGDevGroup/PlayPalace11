# Documents Infrastructure Guide

How the documents system handles shared vs independent data, change detection, syncing from upstream, and exporting contributions.

Reference: issue #201, docs/design/plans/documents_system.md

## Directory layout

```
server/documents/
    _metadata.json          # Root categories (tracked in git)
    _attribution.json       # Who edited what in-app (gitignored, runtime only)
    _exports/               # ZIP exports land here (gitignored)
    shared/                 # Canonical documents (tracked in git)
        chess_rules/
            _metadata.json
            _history/
            en.md
            es.md
        uno_rules/
            ...
    independent/            # Server-local documents (gitignored)
        house_rules/
            _metadata.json
            en.md
```

## Scopes

Every document belongs to exactly one scope:

**Shared** (`shared/`): Tracked in git. These are canonical documents that every server should have. Edits to shared documents are detectable via `git diff` and can be exported for upstream contribution.

**Independent** (`independent/`): Gitignored. These are server-specific documents (house rules, server announcements, etc.). They never leave the server and are invisible to git.

When an admin creates a new document in-app, they choose the scope. The UI presents two options: "Shared (all servers)" and "Independent (this server only)".

### Promotion

An independent document can be promoted to shared via the admin menu. This moves the folder from `independent/` to `shared/`. The operation is one-way -- once shared, it cannot be reverted to independent through the UI (though it can be moved manually on the filesystem).

### Based-on tracking

An independent document can declare that it is derived from a shared document. The metadata stores a `based_on` field with the source document's slug and a content hash:

```json
{
    "based_on": {
        "slug": "chess_rules",
        "locale": "en",
        "content_hash": "a1b2c3..."
    }
}
```

If the upstream shared document changes, the hash will no longer match and the system flags the independent copy as stale. This is informational only -- no automatic merging happens. The admin decides whether to manually reconcile.

## Change detection

Change detection uses git directly. No duplicate files, no manifests, no shadow directories.

The system runs two git commands against the `shared/` directory:

1. `git diff --name-only HEAD -- <shared_dir>` finds tracked files that have been modified, added, or deleted since the last commit.
2. `git ls-files --others --exclude-standard -- <shared_dir>` finds new untracked files (e.g. a brand new document created in-app that hasn't been committed yet).

Combined, these give a complete list of everything that differs from the last commit. This catches content edits, metadata changes (title renames, visibility toggles, category reassignments), new documents, and new translations -- anything that touches a file under `shared/`.

If git is not available or the documents directory is not inside a git repo, change detection gracefully returns an empty list.

## Attribution log

Git tells you *what* changed, but not *which in-app user* made the change. The attribution log fills that gap.

Location: `server/documents/_attribution.json` (gitignored).

Every time a shared document is edited, created, or has a translation added through the app, an entry is appended:

```json
[
    {
        "folder_name": "chess_rules",
        "locale": "en",
        "editor": "alice",
        "change_type": "edit",
        "timestamp": "2026-03-31T14:22:00+00:00"
    },
    {
        "folder_name": "chess_rules",
        "locale": "fr",
        "editor": "bob",
        "change_type": "translation_add",
        "timestamp": "2026-03-31T15:10:00+00:00"
    }
]
```

Change types: `edit`, `create`, `translation_add`.

The attribution log is append-only. Multiple edits to the same file accumulate (unlike the old manifest which used "latest wins"). This gives a full edit history for credit purposes.

The log is cleared after a successful export (see below).

Edits to independent documents are never logged.

## Syncing from upstream

The sync command pulls the latest shared documents from the remote repository.

What it does:
1. `git fetch origin` -- downloads the latest state from the remote without modifying the working tree.
2. `git checkout origin/main -- <shared_dir>` -- replaces the local `shared/` directory with the version from the remote's main branch.
3. Reloads all document metadata from disk.

This means any local uncommitted edits to shared documents are overwritten. The system warns the admin if there are uncommitted changes before syncing, so they can export first.

Sync does not touch `independent/`, the attribution log, or anything outside `shared/`.

### Requirements
- Git must be installed and in PATH.
- The server must be running inside a cloned git repository with an `origin` remote.
- The remote's default branch must be `main`.

### Access
Admin menu: Documents > Sync shared documents.

## Exporting changes

The export command packages all uncommitted changes to shared documents into a ZIP file that can be submitted as a pull request.

What it does:
1. Runs change detection (git diff + untracked files) to find everything that differs from HEAD.
2. Copies each changed file from `shared/` into a ZIP, preserving the directory structure.
3. Includes an `attribution.json` with the full attribution log.
4. Saves the ZIP to `server/documents/_exports/`.
5. Clears the attribution log.

### Example export ZIP contents

```
document_changes_20260331T142200Z.zip
    shared/chess_rules/en.md
    shared/chess_rules/_metadata.json
    shared/new_game_rules/en.md
    shared/new_game_rules/_metadata.json
    attribution.json
```

The server owner (or any contributor) takes this ZIP and submits the contents as a pull request through the normal GitHub workflow.

### Access
Admin menu: Documents > Export pending changes (N), where N is the number of changed files.

## Typical workflows

### Transcriber edits a translation

1. Transcriber opens a shared document, edits the Spanish translation, saves.
2. The `.md` file is written to `shared/<doc>/es.md` on disk.
3. An attribution entry is logged.
4. The change is now visible in `git diff`.
5. When the admin exports, the changed file and attribution are packaged.
6. The server owner submits the ZIP as a PR.

### Admin creates a new shared document

1. Admin clicks "New document", selects "Shared (all servers)".
2. Picks categories, enters a slug, title, and content.
3. A new folder appears in `shared/` with the `.md` and `_metadata.json`.
4. Since this folder is untracked (new to git), `git ls-files --others` picks it up.
5. It appears in the pending changes count and is included in the next export.

### Admin creates a server-specific document

1. Admin clicks "New document", selects "Independent (this server only)".
2. Same flow as above, but the folder goes to `independent/`.
3. The document is invisible to git, never shows up in pending changes, and is never exported.

### Server owner syncs to get latest documents

1. The upstream repo has new or updated documents (merged PRs from other contributors).
2. Admin clicks "Sync shared documents".
3. If there are local uncommitted changes, a warning is spoken. The admin should export first.
4. The system fetches from origin and checks out the latest `shared/` directory.
5. Documents reload from disk. New documents appear, updated ones reflect the upstream content.

### Full round-trip

1. Upstream repo has 30 shared documents.
2. Server is running, transcribers make edits over the course of a week.
3. Admin periodically checks the pending changes count in the documents menu.
4. When ready, admin exports. A ZIP is saved to `_exports/`.
5. Server owner opens the ZIP, copies the files into their local clone, commits, and opens a PR.
6. PR is reviewed and merged upstream.
7. Other server owners sync to receive those changes.

## What the system does NOT do

- It does not push to git automatically. Exporting produces a ZIP; submitting the PR is a manual step.
- It does not handle merge conflicts. If two servers edit the same document differently, the conflict is resolved during PR review, not by the system.
- It does not sync independent documents. They are strictly local.
- It does not require GitHub credentials on the server. Syncing uses read-only fetch; exporting produces a local file.

## File reference

| File | Role |
|---|---|
| `server/core/documents/manager.py` | DocumentManager: all data operations, change detection, sync, export |
| `server/core/documents/browsing.py` | UI menus: document browsing, editing, creation, scope selection, sync/export buttons |
| `server/core/documents/transcriber_role.py` | UI menus: transcriber assignment and management |
| `server/tests/test_document_manager.py` | 89 tests covering all manager functionality |
| `server/locales/en/main.ftl` | English locale strings for all documents UI |
| `.gitignore` | Ignores `independent/`, `_attribution.json`, `_exports/` |
