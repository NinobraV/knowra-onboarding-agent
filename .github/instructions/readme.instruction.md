# INSTRUCTION: Update Existing README.md Safely and Intelligently

## 🟡 GOAL
Update the existing `README.md` to reflect the latest project state — adding missing information and **cleanly removing outdated parts** — while **preserving structure, clarity, and style**.

The goal is to:
- Maintain consistency with the current codebase and architecture.
- Append new information minimally.
- Remove or rewrite only **verified outdated** sections.
- Keep the document visually and structurally consistent.

---

## 🧩 PRIMITIVE RULES
1. **Preserve structure:** Do not rewrite the README entirely. Maintain all heading levels and markdown hierarchy.
2. **Add minimally:** Insert only new or missing information relevant to the current version.
3. **Remove intelligently:** Outdated sections should be **either replaced** or **marked as deprecated**, not blindly deleted.
4. **Respect formatting:** Keep existing bullet styles, indentation, tables, code blocks, and emojis.
5. **Tone consistency:** Preserve the same writing style and tone used in the original README.

---

## ⚙️ ADVANCED RULES

### 1. Detect Change Context
- Identify new features, endpoints, services, or workflows added to the project (e.g., `/api/chat`, `rag_pipeline_service`, `embedding_service`).
- Identify outdated information (e.g., deprecated APIs, old setup instructions, renamed environment variables).

### 2. Update Strategy
- **For new content:**  
  - Integrate into existing relevant sections when possible.  
  - If no fitting section exists, create a new subsection:
    ```markdown
    ### 🆕 New in vX.X.X
    ```
- **For outdated content:**  
  - Replace directly **only if** new equivalent info exists.  
  - Otherwise, mark with:
    ```markdown
    > ⚠️ Deprecated since vX.X.X – this feature or setup is no longer valid.
    ```
  - Delete only if content is obsolete and verified irrelevant (e.g., references to removed dependencies).

### 3. Structural Integrity
- Ensure that after modifications, all Markdown still renders correctly.
- Preserve existing anchor links, TOC, and internal references.

---

## 🧠 SAFETY RULES
1. **Never remove key sections** (e.g., Project Overview, Installation, License).  
   → Only refine or append notes within them.
2. **Backup first:** Before modifying, create a `.bak` copy (e.g., `README.md.bak.20251029`).
3. **Dry-run summary:** List proposed additions/removals before applying changes.
4. **Minimal edits per section:** Avoid large text rewrites — keep diffs small and readable.
5. **Maintain coherence:** Each new addition or removal should make the README more accurate, not longer for no reason.

---

## 🚀 EXECUTION PLAN

### Step 1: Scan and Compare
- Parse the current `README.md` and extract section headers.
- Compare current documentation content with:
  - Source code changes (new endpoints, renamed classes).
  - New services (e.g., chunking_service, embedding_service).
  - Updated infrastructure or environment setup.

### Step 2: Plan Updates
- List **additions** (new endpoints, configs, workflows).
- List **removals or deprecations** (outdated references).
- Generate a short summary table before applying.

### Step 3: Apply Changes
- Add new sections or code snippets.
- Replace outdated references with new ones.
- Mark deprecated sections clearly (not hidden deletion unless necessary).