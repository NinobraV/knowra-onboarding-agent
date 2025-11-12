# CODE CONVENTION

## Overview
This project follows the **"One Code Style for All"** principle –  
Both Frontend (React + TypeScript) and Backend (Python) use **opinionated auto formatters** to ensure consistent and easily reviewable code.

---

## Backend (Python)
**Formatter:** [Black](https://github.com/psf/black)  
**Linter:** [Flake8](https://flake8.pycqa.org/)  
**Import Sorter:** [isort](https://pycqa.github.io/isort/)

### Main Rules
- `line-length = 88`
- Use **4 spaces**, **no tabs**.
- **Trailing commas:** always add a comma at the end of multi-line constructs.
- **Strings:** use single quotes `'` whenever possible.
- **No manual formatting:** Black decides the formatting.
- **isort:** automatically sorts imports (following the `black` profile).
- **Flake8:** checks for code smells & style violations.

---

## Frontend (React + TypeScript)
**Formatter:** [Prettier](https://prettier.io)  
**Linter:** [ESLint](https://eslint.org) (optional)

### Standard `.prettierrc`
```json
{
  "semi": true,
  "trailingComma": "all",
  "singleQuote": true,
  "printWidth": 88,
  "tabWidth": 4,
  "useTabs": false,
  "bracketSpacing": true,
  "bracketSameLine": false,
  "arrowParens": "always",
  "endOfLine": "lf",
  "jsxSingleQuote": true,
  "quoteProps": "as-needed"
}