# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000     # dashboard at /, Control Room at /releases, docs at /docs
pytest tests/ -v                              # all tests
pytest tests/test_api.py::test_health -v      # single test
python eval/run_eval.py [--baseline releases.json]   # the quality gate (exit 1 = fail)
python scripts/smoke_test.py http://127.0.0.1:8000    # live canary (use 127.0.0.1, "localhost" is slow on Windows)
terraform -chdir=infra init -backend=false && terraform -chdir=infra validate
```

No linter is configured. `terraform fmt` is enforced in CI.

## Architecture

FastAPI service (`app/main.py`) wrapping a keyword-heuristic scorer (`app/model.py`). Around it is a delivery pipeline whose distinguishing feature is a **model-quality gate**: `eval/run_eval.py` scores `eval/dataset.json` and fails if accuracy is under 85% or drops more than 5 points vs the last PROMOTED entry in `releases.json`.

Two targets share one pipeline: `TARGET=local` (default; LocalStack for S3/IAM/CloudWatch, a k3s container as the cluster, both from `docker-compose.yml`) and `TARGET=aws` (real AWS + EC2 k3s). Terraform switches with `local_mode`; the Jenkinsfile's `withTarget{}` helper sets the env (`RUN` = `docker exec -i cloudforge-k3s` or `ssh ... sudo`) so stages are identical. In local mode pods can't resolve compose names, so Jenkins passes LocalStack's IP as `S3_ENDPOINT`.

Flow: GitHub Actions (`.github/workflows/ci.yml`) is CI only (tests, gate, docker build + smoke, terraform validate). Jenkins (`Jenkinsfile`) is CD: pytest → `terraform apply` (`infra/`: EC2 with k3s, S3 bucket, IAM role, CloudWatch alarm/dashboard) → quality gate → docker build → `docker save | ssh ... k3s ctr images import` (no registry) → `kubectl apply` of `k8s/app.yaml` with `__IMAGE__/__VERSION__/__BUCKET__/__REGION__` placeholders substituted by sed → rollout status (auto `rollout undo` on failure) → `scripts/smoke_test.py` canary → `scripts/record_release.py` appends to `releases.json` and uploads to S3 in the `post { always }` block.

The app reads `releases.json` for `/api/releases`: from S3 (via the EC2 instance role; IMDS hop limit is 2 so pods can reach it) when `S3_BUCKET` is set, else from `RELEASES_FILE` (default `./releases.json`). Release statuses: `PROMOTED`, `BLOCKED` (gate failed), `ROLLED_BACK`.

## Gotchas

- Jenkins runs in Docker via `docker compose up -d --build` (admin/admin, job `cloudforge` created by `jenkins/casc.yaml` from the GitHub repo, so changes must be pushed to build). The Jenkinsfile uses `sh` only.
- The local compose stack and the real-AWS path have not been exercised end to end yet; only the app, gate, scripts and `terraform validate` were tested.
- Terraform state is local (in the Jenkins workspace/volume). Deleting it orphans the AWS resources.
- Demo regression: changing `credible_score * 6` to `* 0` in `app/model.py` drops eval accuracy to 50% and trips the gate.
- `releases.json`, `eval_result.json`, `smoke.json` are generated and git-ignored.
