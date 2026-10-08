# CloudForge AI: News Credibility Analyzer with a Quality-Gated Cloud Pipeline

A news-credibility scoring service, shipped by an automated DevOps pipeline that **refuses to deploy a release that makes the model worse**.

```
 git push
    │
    ├─► GitHub Actions (CI): unit tests · accuracy gate · docker build + container smoke test · terraform validate
    │
    └─► Jenkins (CD):
          pytest ─► Terraform ─► QUALITY GATE ─► Docker build ─► deploy to Kubernetes ─► canary check ─► record release
                                      │                              │                        │
                        accuracy vs previous release         rollout fails → auto rollback    live accuracy + latency
                        too low → BLOCKED, old version stays live
```

| Tool | Role |
|---|---|
| **GitHub + GitHub Actions** | Source control, CI on every push |
| **Jenkins** | CD pipeline (`Jenkinsfile`), pre-configured via Configuration-as-Code |
| **Docker** | Packages the app (`Dockerfile`) and runs the whole demo stack (`docker-compose.yml`) |
| **Terraform** | Creates the cloud resources (`infra/`) |
| **AWS S3 / IAM / CloudWatch** | Release history, access role, accuracy metric + alarm |
| **AWS EC2** | (real AWS only) runs the cluster |
| **Kubernetes (k3s)** | 2 replicas, health probes, rolling updates, rollback (`k8s/app.yaml`) |
| **LocalStack** | Free AWS emulator, so the demo needs no AWS account |
| **Prometheus metrics** | App exposes `/metrics`; pods carry scrape annotations |

## The idea

Normal CI/CD asks "did it build, is the server up?". For a model, a release can be perfectly healthy and quietly get worse at its job.
Every release is scored on `eval/dataset.json` (24 labeled articles). If accuracy is below 85%, or drops more than 5 points vs the last promoted release, the pipeline stops and the old version keeps running. Each outcome (promoted / blocked / rolled back) shows up in the **Release Control Room** at `/releases`.

## Two targets, one codebase

| | `TARGET=local` (default) | `TARGET=aws` |
|---|---|---|
| S3 / IAM / CloudWatch | LocalStack container | real AWS |
| Kubernetes | k3s container | k3s on a real EC2 instance |
| Cost / account | free, none | ~$0.02/h, AWS account |
| Switch | Jenkins build parameter `TARGET` | |

## Run locally without Docker (app only)

```bash
pip install -r requirements.txt
uvicorn app.main:app --port 8000        # http://localhost:8000  and  /releases
pytest tests/ -v
python eval/run_eval.py                 # the quality gate on its own
```

## Run the full platform (Docker Desktop required, no AWS account)

```bash
docker compose up -d --build            # first build ~10 min, downloads ~2 GB
```

| Service | URL |
|---|---|
| Jenkins (login `admin` / `admin`, job `cloudforge` already created) | http://localhost:8080 |
| Deployed app, after the first pipeline run | http://localhost:8081 and http://localhost:8081/releases |
| LocalStack health | http://localhost:4566/_localstack/health |

Push the repo to GitHub (the Jenkins job clones `https://github.com/LakshyaBetala/news_analyzer.git`, branch `main`), then in Jenkins click **Build with Parameters** (TARGET = local). Jenkins also polls GitHub every minute, so later pushes build on their own.
Stop everything: `docker compose down` (add `-v` to wipe state).

## Switching to real AWS later

1. Create an SSH key pair: `ssh-keygen -t ed25519 -f cloudforge -N ""`, and copy `cloudforge.pub` into the Jenkins container at `/var/jenkins_home/cloudforge.pub`.
2. In Jenkins add two credentials: `aws-credentials` (username/password = access key ID / secret) and `ec2-ssh-key` (SSH username `ubuntu` + contents of `cloudforge`).
3. Build with Parameters → `TARGET=aws`. Terraform creates the EC2 + k3s, the pipeline deploys onto it, and the app URL is the EC2 public IP.
4. Stop billing afterwards: run `terraform destroy` from the Jenkins workspace's `infra/` folder with the same variables.

## API

| Endpoint | |
|---|---|
| `GET /` | analyzer UI |
| `POST /api/analyze` | `{title, content, source?}` → score, risk factors, recommendations |
| `GET /api/health`, `/api/version` | liveness, running version |
| `GET /api/releases`, `GET /releases` | release history / Control Room page |
| `GET /metrics` | Prometheus metrics |

## Layout

```
app/             FastAPI app + scoring logic + templates
eval/            labeled dataset + the quality gate
scripts/         smoke_test.py (live canary), record_release.py (writes releases.json)
infra/           Terraform (local_mode toggles LocalStack vs real AWS)
k8s/             Deployment + Service
jenkins/         Jenkins image (all tools + plugins) and casc.yaml (admin user + job)
docker-compose.yml   LocalStack + k3s + Jenkins
.github/         CI workflow
DEMO.md          review demo script
```
