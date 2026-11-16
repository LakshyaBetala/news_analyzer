# CloudForge AI: Demo Guide (about 8 minutes)

## What to open before you start

| Tab | URL | What it shows |
|---|---|---|
| 1. Analyzer | http://localhost:8081 | The product, served by Kubernetes |
| 2. Release Control Room | http://localhost:8081/releases | Every release: PROMOTED / BLOCKED / ROLLED BACK, accuracy chart |
| 3. Platform | http://localhost:8081/platform | The pipeline, tools, cloud resources, and which pod served you |
| 4. Jenkins | http://localhost:8090 (admin / admin) → `cloudforge` | The CD pipeline stage view |
| 5. GitHub Actions | https://github.com/LakshyaBetala/news_analyzer/actions | CI on every push |
| 6. VS Code + terminal | this folder | For the live "bad change" |

Before the review: Docker Desktop running, `docker compose up -d`, and the Jenkins job has at least one green build (Control Room shows a green row).

## Live script

**1. The problem (30 s, slides 2–4).**
"A normal pipeline checks the build and the health endpoint. A model can pass both and still give worse answers. CloudForge blocks that."

**2. The product (90 s, tab 1).**
- Click **Clickbait** → the article fills in → press **Analyze credibility** → low score (0–34), red, risk factors listed.
- Click **News report** → press Analyze → high score (70–100), green.
- Click **Borderline** → press Analyze → middle score (53–71), amber "Treat with caution" or just over the line.
- Point at **Signals found**: credible words, suspicious words, emotional patterns, source score. "It is explainable, not a black box."
- Each button picks a random article from 28 samples, so press it again for a new one.

**3. The platform (90 s, tabs 3 and 4).**
- Platform page: "This page was served by pod `news-analyzer-…`, version `build.commit`, history in S3 bucket `cloudforge-reports-…`." Walk the 9 pipeline stages.
- Jenkins stage view: Test → Provision (Terraform) → Quality Gate → Build Image → Deploy (Kubernetes) → Canary Check.
- Terminal, to prove Kubernetes is real:
  ```
  docker exec cloudforge-k3s kubectl get pods
  docker exec cloudforge-k3s kubectl get deployment news-analyzer -o wide
  ```
  Two pods Running, image tag = the release version.

**4. Versioning (30 s, tab 2).**
Every release is `<Jenkins build number>.<git commit>`, e.g. `10.2014493`. The Control Room lists each with accuracy, latency and a verdict; the chart shows accuracy per release against the 85% line.

**5. The bad change (2 min).**
- In `app/model.py` line 88 change `base_score -= suspicious_score * 6` to `base_score += suspicious_score * 6` (a one-character sign typo that rewards clickbait).
- `git commit -am "tweak weights" && git push`
- GitHub Actions (tab 5) turns red at "Quality gate".
- Jenkins starts within a minute and stops at **Quality Gate** (58% accuracy, 14 of 24). Build, Deploy and Canary never run.
- Refresh the Control Room: a red **BLOCKED** row: "accuracy 58% is below minimum 85%; accuracy dropped 100% -> 58%… previous version is still live".
- Tab 1 still works and the version tag in the corner has not changed.

**6. The fix (1 min).**
`git revert HEAD --no-edit && git push` → pipeline green → new PROMOTED row; the chart dips and recovers.

**7. Close (30 s).**
"Same Terraform and pipeline deploy to real AWS (EC2, S3, IAM, CloudWatch) with one Jenkins parameter, `TARGET=aws`."

## Backup if something fails live

- No network: show the slides' screenshots, and run the gate locally:
  `python eval/run_eval.py` (24/24, GATE PASSED), make the bad change, run again (58%, GATE FAILED), `git checkout app/model.py`.
- App not on :8081: `uvicorn app.main:app --port 8000` and use http://localhost:8000.
- Jenkins stuck: `docker compose restart jenkins`, then **Build Now**.
- Everything stuck: `docker compose down && docker compose up -d`, then one fresh build.
- Pods not Ready: `docker exec cloudforge-k3s kubectl describe pods`

## Questions faculty may ask

- **Is AWS real?** Locally, LocalStack emulates S3, IAM and CloudWatch, so it runs free. The same Terraform targets real AWS with `TARGET=aws`; that path is validated but needs an AWS account to apply.
- **Why both GitHub Actions and Jenkins?** Actions gives fast CI feedback on every push; Jenkins holds credentials and runs the deployment.
- **Is the model real ML?** It is a deterministic heuristic (report section 3.4.2). The gate works for any scorer.
- **How is accuracy measured?** 24 labelled articles in `eval/dataset.json`; a score of 60 or more counts as credible.
- **What if a deploy breaks?** Kubernetes rollout fails or the canary fails → `kubectl rollout undo`, recorded as ROLLED BACK.
