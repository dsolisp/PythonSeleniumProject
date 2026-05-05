import fs from 'fs';
import path from 'path';

function readJson(p) {
  return JSON.parse(fs.readFileSync(p, 'utf8'));
}

function safeNum(n) {
  return typeof n === 'number' && Number.isFinite(n) ? n : 0;
}

function computeFromAllureResults(allureDir) {
  if (!fs.existsSync(allureDir)) {
    return {
      total: 0,
      passed: 0,
      failed: 0,
      broken: 0,
      skipped: 0,
      duration_ms: 0,
    };
  }

  const files = fs
    .readdirSync(allureDir)
    .filter((f) => f.endsWith('-result.json'))
    .map((f) => path.join(allureDir, f));

  let total = 0;
  let passed = 0;
  let failed = 0;
  let broken = 0;
  let skipped = 0;
  let durationMs = 0;

  for (const f of files) {
    const j = readJson(f);
    total += 1;
    const status = String(j.status ?? '').toLowerCase();
    if (status === 'passed') passed += 1;
    else if (status === 'failed') failed += 1;
    else if (status === 'broken') broken += 1;
    else if (status === 'skipped') skipped += 1;

    const start = safeNum(j.time?.start);
    const stop = safeNum(j.time?.stop);
    if (stop > start) durationMs += stop - start;
  }

  return { total, passed, failed, broken, skipped, duration_ms: durationMs };
}

const repo = process.env.REPO_NAME || process.env.GITHUB_REPOSITORY?.split('/').pop() || 'unknown';
const runId = process.env.GITHUB_RUN_ID || 'local';
const timestamp = new Date().toISOString();
const suite = process.env.TEST_SUITE || 'all';

const allureDir = process.env.ALLURE_RESULTS_DIR || 'allure-results';
const metrics = computeFromAllureResults(allureDir);

const out = {
  repo,
  run_id: runId,
  timestamp,
  suite,
  ...metrics,
};

fs.writeFileSync('summary.json', JSON.stringify(out, null, 2));
console.log(`✅ Wrote summary.json (${repo} run ${runId})`);

