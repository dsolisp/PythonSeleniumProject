---
mode: agent
---
Portfolio JS/TS Test Automation Repo
Objective:
Generate a modern, portfolio-quality JavaScript/TypeScript test automation repository that mirrors the features, structure, and best practices of my Python Selenium/Playwright framework. The repo must be self-contained, idiomatic, and demonstrate advanced automation capabilities.

1. Tech Stack
Test Runner: Playwright Test (TypeScript)
API Testing: Axios (with typed API helpers)
DB Testing: SQLite (Chinook DB sample, with TypeORM or better-sqlite3)
Visual Testing: pixelmatch, Playwright screenshots
Performance Testing: k6 (JS scripts)
Reporting: Allure
Logging: pino
Linting/Formatting: ESLint, Prettier
Pre-commit: Husky, lint-staged
CI: GitHub Actions (with Allure, k6, and artifact upload)
Optional: TensorFlow.js (for ML demo)
Unit Testing: Jest (for all new functions/utilities)
2. Project Structure
.
├── README.md
├── .github/
│   └── workflows/
│       └── ci.yml
├── docs/
│   └── ...
├── playwright.config.ts
├── package.json
├── tsconfig.json
├── src/
│   ├── pages/
│   │   └── search_engine_page.ts
│   ├── api/
│   │   └── search_engine_api.ts
│   ├── db/
│   │   └── chinook.db
│   ├── utils/
│   │   └── logger.ts
│   └── tests/
│       ├── e2e/
│       │   └── search_engine.e2e.spec.ts
│       ├── api/
│       │   └── search_engine_api.spec.ts
│       ├── db/
│       │   └── chinook_db.spec.ts
│       ├── visual/
│       │   └── search_engine.visual.spec.ts
│       ├── perf/
│       │   └── search_engine.k6.js
│       └── unit/
│           └── logger.spec.ts
├── allure-results/
├── k6/
│   └── search_engine.k6.js
├── .husky/
├── .eslintrc.js
├── .prettierrc
└── ...
3. Representative Examples
E2E: Search Engine (generic, parameterized page object, test, locator)
API: Search Engine instant answer API (typed helper, test)
DB: Chinook sample DB (query, test)
Visual: Search Engine homepage visual regression (pixelmatch)
Performance: Search Engine search with k6 (JS script)
Unit: All new functions/utilities must have Jest unit tests
4. Documentation
README.md with:
Project overview
Tech stack
Setup instructions
Example usage
Project structure tree
How to run tests (all types)
How to view Allure reports
How to run k6 scripts
How to use Husky/pre-commit
docs with:
Feature guides (E2E, API, DB, Visual, Perf)
CI/CD and contribution guide
5. Git & Commit Strategy
Use feature branches for each logical unit (e.g., feature/e2e-search-engine, feature/api-search-engine, etc.)
Each commit must be atomic and leave the repo in a working state (tests pass, lint clean)
Each new function or utility must include a unit test in the same commit
Use conventional commit messages (e.g., feat(e2e): add search engine test)
CI must enforce lint, typecheck, and all tests on PRs
6. Acceptance Criteria
All representative files and tests are present and working
Allure and k6 integration is functional
Husky/pre-commit is set up and working
README and docs are clear and complete
CI workflow is present and passes
All code is idiomatic, typed, and follows best practices
Start by scaffolding the repo, then add features in atomic, working commits as described.

### 1. Initial Setup (main branch)

**a.** Create a `.gitignore` file **before** any code or dependency installation. It must include at least:
```
node_modules/
dist/
allure-results/
allure-report/
coverage/
.env
.DS_Store
*.log
*.sqlite
*.db
output/
tmp/
*.png
*.mp4
*.webm
```
Commit: `chore: add .gitignore to exclude node_modules and non-essential dirs`

**b.** Initialize the repo and install dependencies:
- Playwright Test (TypeScript)
- Axios
- better-sqlite3
- pixelmatch
- k6
- Allure
- pino
- Jest
- ESLint, Prettier
- Husky, lint-staged

**c.** Scaffold config files:
- `package.json` (with scripts for all test types, lint, format, prepare, Allure, k6)
- `tsconfig.json`
- `playwright.config.ts`
- `.eslintrc.js`
- `.prettierrc`
- `.husky/pre-commit`
- `.github/workflows/ci.yml`
- `README.md` (with project overview, setup, usage, structure, and test instructions)

**d.** Ensure `npm run lint`, `npm test`, and `npx playwright test` all pass before first commit of code/config files.

### 2. Feature Branches: Add Features Step-by-Step

#### 2.1. E2E: Search Engine (DuckDuckGo Example)
- Create `src/pages/search_engine_page.ts` (generic, parameterized page object)
- Create `src/locators/search_engine_locators.ts` (centralized locators, with DuckDuckGo as one option)
- Create `src/tests/e2e/search_engine.e2e.spec.ts` (E2E test for DuckDuckGo, using the generic page object)
- Ensure Playwright E2E test passes locally and in CI
- Commit: `feat(e2e): add generic search engine page and DuckDuckGo E2E test`

#### 2.2. API: DuckDuckGo Instant Answer
- Create `src/api/search_engine_api.ts` (typed API helper, with support for DuckDuckGo)
- Create `src/tests/api/search_engine_api.spec.ts` (Jest test for DuckDuckGo API)
- Ensure API test passes locally and in CI
- Commit: `feat(api): add generic search engine API helper and DuckDuckGo API test`

#### 2.3. DB: Chinook Sample
- Add Chinook DB to `src/db/chinook.db`
- Create `src/db/chinook_db.ts` (DB helper)
- Create `src/tests/db/chinook_db.spec.ts` (Jest test)
- Ensure DB test passes locally and in CI
- Commit: `feat(db): add Chinook DB queries`

#### 2.4. Visual Regression: Search Engine (DuckDuckGo Example)
- Create `src/tests/visual/search_engine.visual.spec.ts` (Playwright + pixelmatch, using the generic page object and locators for DuckDuckGo)
- Add baseline image to repo
- Ensure visual test passes locally and in CI
- Commit: `feat(visual): add generic search engine visual regression test (DuckDuckGo)`

#### 2.5. Performance: Search Engine (DuckDuckGo Example) with k6
- Create `k6/search_engine.k6.js` (k6 script for DuckDuckGo)
- Add test runner script to `package.json`
- Ensure k6 script runs and passes locally and in CI
- Commit: `feat(perf): add generic search engine k6 performance test (DuckDuckGo)`

#### 2.6. Utilities: Logger
- Create `src/utils/logger.ts` (pino logger)
- Create `src/tests/unit/logger.spec.ts` (Jest unit test)
- Ensure unit test passes locally and in CI
- Commit: `feat(utils): add pino logger with unit test`

---

- Use a generic, parameterized page object and centralized locators for all search engines, including DuckDuckGo.
- Do not create DuckDuckGo-specific page classes or files.
- All tests and helpers should be generic, with configuration/locators for DuckDuckGo as needed.