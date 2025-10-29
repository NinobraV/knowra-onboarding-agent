# INSTRUCTION: Generate Feature Implementation Guide from Existing Source Code

## GOAL
Analyze the existing source code in this repository and automatically generate a **new instruction document** that guides developers on how to implement a new feature inside this project, while strictly following the existing architecture, naming conventions, coding patterns, and dependency flow.

The resulting instruction must help a developer understand **how to implement the new feature in this exact project context**, not just in theory.

---

## PRIMITIVE RULES
1. The instruction must be written **as if it were part of the current project documentation**.
2. Analyze the existing structure: layers (Controllers, Services, Repositories), dependency injection, database context, models, DTOs, and helper patterns.
3. Use the same conventions and patterns observed in the source.
4. Include realistic code examples aligned with the project’s existing syntax and structure.
5. Do not introduce new frameworks or styles unless explicitly requested.

---

## ADVANCED RULES
1. When describing implementation steps:
   - Clearly define where each new file, method, or class should be added.
   - Explain how to wire up the new functionality (DI registration, routing, database access, etc.).
   - If the project uses layered architecture, specify changes per layer.
2. Provide a **step-by-step breakdown**:
   - Folder / file to modify or create.
   - Code snippet example.
   - Explanation of logic.
3. If dependencies or patterns are not explicitly visible, use placeholders but mark them as `[To Verify]`.
4. Include post-implementation tasks: Unit Tests, documentation update, API validation, etc.

---

## SAFETY RULES
- Do **not** refactor existing logic unless required by the new feature.
- Do **not** remove or alter unrelated modules.
- Do not make architectural assumptions not proven by the current source code.
- If context is missing, clearly mark `[Missing Context]`.

---

## EXECUTION PLAN
1. Read and analyze the source code base.
2. Identify the architectural layers and coding conventions.
3. Generate a **feature implementation instruction** in Markdown format:
   - Include sections: GOLDEN RULE, PRIMITIVE RULE, ADVANCED RULE, SAFETY RULE, EXECUTION PLAN.
   - Use the same tone, vocabulary, and patterns found in the current project.
4. The new instruction should be directly usable as part of the developer documentation (e.g., `feature_x_instruction.md`).

---

## INPUT
> - The full source code (or the repo context already loaded by Copilot).
> - A short description of the new feature to be implemented.

Example feature description:
> "Add a reporting API that aggregates transaction history by category and month."

---

## OUTPUT EXPECTED
A full instruction document that:
- Aligns with the existing code structure.
- Describes in detail how to implement the new feature step-by-step.
- Is ready to be committed under `/docs/instructions/feature_name.md`.
