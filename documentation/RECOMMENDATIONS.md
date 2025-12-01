# QA Automation Project: Enhancement Recommendations

## Central Dashboard
- Use Jinja2 to generate a single HTML dashboard that aggregates:
  - Analytics (CSV/HTML)
  - Test analytics insights (flaky tests, reliability scores)
  - Test run summaries
- Link to all individual reports and outputs from one place.

## Notification System
- Integrate optional notifications (email, Slack, etc.) for:
  - Test failures
  - Performance regressions
  - Detected flaky tests
- Trigger notifications from the workflow script or as a post-processing step.

## Test Filtering Support
- Allow the workflow script to accept arguments for:
  - Running only specific test markers/tags (e.g., smoke, regression)
  - Selecting test directories or files
- Pass these arguments to pytest for flexible test selection.

## Enhanced Pre-Checks
- Expand environment validation to include:
  - Browser driver presence (chromedriver, geckodriver, etc.)
  - Playwright browser installation
  - Required environment variables (e.g., API_BASE_URL)
- Fail early with clear error messages if any checks fail.

## Configurable Retention Policy
- Allow the number of retained result files in `data/results/` to be set via:
  - A config file (YAML/JSON)
  - Or an environment variable (e.g., RESULTS_RETENTION=30)
- Make this value easy to change without editing code.

## (Optional) Database Integration
- For advanced analytics and cross-feature queries, consider:
  - Storing test results in a lightweight database (e.g., SQLite)
  - Enabling easier correlation of web, API, and performance results
  - Supporting richer dashboards and historical queries

## General Best Practices
- Use the workflow script for all test runs to ensure full integration.
- Keep documentation and usage instructions up to date as features evolve.
- Regularly review analytics outputs to guide test suite improvements.

---

**Use this checklist as a prompt for future enhancements and as a guide for project evolution.**
