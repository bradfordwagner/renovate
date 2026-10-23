# Renovate runner

## Scaling the matrix

`renovate.yaml` fans out one job per repo in `config.js`. It holds to roughly 100 repos; plan for these limits:

- A matrix is capped at 256 jobs. Past about 250 repos, split into several matrices or chunk repos per job.
- All jobs share one App installation, so one API rate limit. Add `max-parallel: 10` to the `renovate` job once past about 30 repos.
- Each job repeats checkout, token mint and image pull. Past about 100 repos, chunk about 10 repos per job for scheduled runs and keep per-repo jobs for scoped dispatch.
- Chunking breaks the per-repo concurrency group (it becomes per chunk), so a scoped dispatch could overlap a scheduled chunk.
- Merging many role PRs at once rebases each repo's PRs in turn and re-runs a ~15-job matrix per rebase. Actions queues for 20+ minutes, so merge repos in waves.
