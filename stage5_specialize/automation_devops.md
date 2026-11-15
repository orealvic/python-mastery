# Track: Automation & DevOps

**Stack:** subprocess · pathlib · typer / click · rich · httpx · paramiko / Fabric · boto3 (or a cloud SDK) · Ansible · GitHub Actions · Docker

## Milestone 1: Shell-level automation
- **Learn:** `subprocess.run` (check, capture_output, never use `shell=True` with user input), `shutil`, `pathlib`, `os.environ`, exit codes, signals.
- **Build:** a backup tool: compress a directory, rotate old archives (keep N), and log what it did.
- **Done when:** it's idempotent, has `--dry-run`, returns non-zero on failure, and is tested with `tmp_path`.

## Milestone 2: Polished CLIs
- **Learn:** typer or click, subcommands, config files (TOML via `tomllib`), `rich` for tables and progress bars, shell completion.
- **Build:** a "dev environment doctor" CLI that checks installed tool versions, env vars and ports, and reports problems.
- **Done when:** it's installable with `uv tool install .`, has `--json` output for machines, and has a clear help screen.

## Milestone 3: Talking to APIs & remote machines
- **Learn:** REST APIs with httpx (auth, retries, pagination), SSH with paramiko or Fabric, secrets handling.
- **Build:** a tool that lists your GitHub repos with stale PRs and posts a summary to a Slack or Discord webhook.
- **Done when:** retries use backoff, no secrets appear in the code or logs, and it's scheduled with cron or a GitHub Actions schedule.

## Milestone 4: Cloud automation
- **Learn:** boto3 (or the GCP/Azure SDK), IAM least privilege, pagination, waiters, and testing with `moto`.
- **Build:** a cost-hygiene script that finds untagged or idle resources and reports (doesn't delete) them.
- **Done when:** it's tested with mocked AWS (`moto`), has a read-only IAM policy, and produces a CSV report.

## Milestone 5: Config management & containers
- **Learn:** Docker and compose, Ansible playbooks (and how to write a custom module in Python), infrastructure as code concepts (Terraform or Pulumi, where Pulumi uses Python).
- **Build:** provision a VM or container running a service from Stage 5, entirely from code.
- **Done when:** destroying and recreating it from scratch takes one command.

## Milestone 6: CI/CD
- **Learn:** GitHub Actions (matrix builds, caching, secrets, reusable workflows), pre-commit hooks, release automation.
- **Build:** a full pipeline for your Stage 3 package: lint, type-check, test on a matrix of 3 Python versions, build, and publish to TestPyPI on tag.
- **Done when:** pushing a git tag produces a published release with no manual steps.

## Capstone
Automate a real, recurring task from your work or life end to end: scheduled, observable (logs and alerts), tested, and documented.

## Key reading
- *Automate the Boring Stuff* (part II) · *Python for DevOps* (Gift et al.)
- subprocess, pathlib and shutil docs · GitHub Actions docs
