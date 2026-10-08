# Review-1 Demo Script (about 5 minutes)

## Before the review (do once, at home, ~20 min)

- [ ] Docker Desktop running
- [ ] `docker compose up -d --build` finished with no errors (`docker compose ps` shows 3 services Up)
- [ ] Repo pushed to GitHub `main`
- [ ] Open http://localhost:8080, log in `admin` / `admin`, run **Build with Parameters** (TARGET = local) once, and wait for green
- [ ] http://localhost:8081 and http://localhost:8081/releases open; Control Room shows 1 green PROMOTED row
- [ ] Take screenshots for the slides: Jenkins stage view, Control Room, GitHub Actions run, `docker compose ps`
- [ ] Keep the "bad change" ready in your editor (below), but do not push it yet

## Live script

1. **Explain** (30 s): "Normal pipelines check the build. Ours also checks the model's quality and blocks releases that make it worse."
2. **Show the product** (45 s): open http://localhost:8081, paste a clickbait article ("SHOCKING secret miracle cure!!!") and then a factual one with a source of "Reuters". Point out the scores.
3. **Show the platform** (45 s): Jenkins stage view (Test, Terraform, Quality Gate, Build, Deploy, Canary). Mention Terraform created S3, IAM and CloudWatch in LocalStack (AWS emulator) and the app runs as 2 pods on Kubernetes.
   Terminal: `docker exec cloudforge-k3s k3s kubectl get pods` shows 2 Running pods.
4. **Bad change** (90 s):
   - In `app/model.py` change `base_score += credible_score * 6` to `base_score += credible_score * 0`
   - `git commit -am "tweak weights" && git push`
   - GitHub Actions turns red on "Quality gate". Within about a minute Jenkins starts, stops at **Quality Gate**.
   - Refresh `/releases`: red **BLOCKED** row ("accuracy 50% is below minimum 85%... previous version is still live"). The app on :8081 is still the old version.
5. **Fix** (45 s): `git revert HEAD --no-edit && git push`. Pipeline goes green and a new PROMOTED row appears.
6. **Close** (30 s): "Same Terraform and pipeline switch to real AWS with one parameter, TARGET=aws; that's our Review 2."

## If something goes wrong

| Problem | Fix |
|---|---|
| Jenkins does not start a build after push | click **Build Now** (polling runs every minute) |
| Pipeline fails at Provision | `docker compose restart localstack`, rebuild |
| Pods not Ready | `docker exec cloudforge-k3s k3s kubectl describe pods` |
| Everything is stuck | `docker compose down -v && docker compose up -d --build`, then one fresh build |
| No internet at the venue | have the screenshots and a screen recording of a full run as backup |

## Questions faculty may ask

- **Why is it not on AWS yet?** AWS is emulated with LocalStack so the pipeline is proven end to end for free; the Terraform has a tested real-AWS path (validated) and is activated by one parameter.
- **Why two CI tools?** GitHub Actions is fast feedback on every push (CI). Jenkins is the deployment pipeline (CD) with credentials and infrastructure access.
- **Is the model real ML?** It is a keyword heuristic on purpose. The project is about the delivery platform; the gate works the same for any scorer, including a transformer.
- **How is accuracy measured?** 24 labeled articles in `eval/dataset.json`; "credible" if score is 60 or above.
