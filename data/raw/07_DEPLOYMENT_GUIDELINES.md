# Deployment Guidelines for Hotel Booking System

---

Version: 1.0  
Updated: October 27, 2025

Purpose: This document describes recommended deployment practices for the Hotel Booking System (HBS). It targets SREs, DevOps engineers, release managers, and developers who operate CI/CD and production infrastructure.

Scope: Azure-first deployment using AKS (Azure Kubernetes Service), Azure Container Registry (ACR), Terraform/Bicep for IaC, and Azure DevOps for CI/CD. The patterns are adaptable to GitHub Actions, Terraform Cloud, or other clouds.

---

## 1. Environments & Topology

Environments:
- Local developer environment (optional)
- Sandbox (automated test/dev) — ephemeral, auto-reset weekly
- Staging — pre-production for integration/regression tests; mirrors prod size/config where feasible
- Production — multi-region where required (Primary: East US, Secondary: West Europe)

Network & Regions:
- Use separate Azure subscriptions or Resource Groups per environment.
- Apply network segmentation (VNet per environment) and private endpoints for PaaS services (SQL, Key Vault).
- For multi-region: deploy read replicas and failover policies for databases; use Traffic Manager or Front Door for global traffic management.

Availability:
- Production: AKS with at least 3 nodes per node pool across availability zones. Use horizontal pod autoscaling and cluster autoscaler.

---

## 2. Artifact Management & Tagging

- Build immutable container images and store them in ACR.
- Tagging strategy:
  - `sha-<commit-sha>` (immutable)
  - `pr-<id>` (temporary for PR deployments)
  - `canary-<build>` (canary releases)
  - `latest` (avoid using in production; optional for internal QA)
  - `v<semver>` for release images

- Use digest references for deployments (e.g., `image: myacr.azurecr.io/hbs/backend@sha256:<digest>`) to ensure immutability.

---

## 3. Infrastructure as Code (IaC)

Recommendations:
- Prefer Terraform for multi-cloud or complex stateful infra; prefer Bicep if you want ARM-native templates.
- Keep modules small and reusable (network, database, AKS, monitoring).
- Store state in remote backend (Terraform: Azure Storage with locking via Azure Blob Lease; Bicep: deployments in Resource Groups).
- Manage secrets via Azure Key Vault and avoid secrets in source code or state files.

Terraform layout (example):
```
infra/
├─ modules/
│  ├─ network/
│  ├─ aks/
│  ├─ sql/
│  └─ keyvault/
├─ envs/
│  ├─ sandbox/
│  ├─ staging/
│  └─ production/
└─ README.md
```

---

## 4. Kubernetes & Helm

- Package app components as Helm charts. Keep charts in `deploy/charts/` or a separate `helm` repo.
- Use per-environment values files: `values.sandbox.yaml`, `values.staging.yaml`, `values.prod.yaml`.
- Recommended chart structure:
  - `charts/hbs-backend/` (service, deployment, configmap, secret templates)
  - `charts/hbs-frontend/` (ingress, deployment)
  - `charts/hbs-common/` (rbac, networkpolicy, serviceaccount)

Deployment patterns:
- Canary: deploy a small percentage of traffic to a canary deployment using service mesh (Istio/Linkerd) or ingress rules.
- Blue/Green: deploy new version to green namespace, run smoke tests, switch traffic (DNS or ingress weight), then decommission old.

Helm release example (CI step):
```
helm upgrade --install hbs-backend ./charts/hbs-backend \
  -f values.prod.yaml \
  --set image.tag=sha-<commit-sha> \
  --namespace production
```

---

## 5. CI/CD (Azure DevOps) — Recommended Pipeline Flow

High-level stages:
1. Build (PR/CI)
   - Restore, build, unit tests, lint
   - Build container image and push to ACR with commit SHA tag
   - Publish build artifacts (image metadata, helm chart package)
2. Test (PR/CI)
   - Run integration tests against sandbox or ephemeral environment
   - Run contract tests (OpenAPI, schema validation)
3. Release to Staging (CD)
   - Deploy helm chart to staging with image digest
   - Run smoke/regression tests and readiness checks
4. Production Release (CD)
   - Progressive rollout (canary/blue-green)
   - Post-deploy health checks and automated smoke tests

Sample Azure DevOps YAML snippets (simplified):

Build + Push Image (azure-pipelines.yml):
```yaml
trigger:
  branches:
    include: [ main ]

pool:
  vmImage: 'ubuntu-latest'

variables:
  imageName: 'hbs/backend'

steps:
- task: Docker@2
  displayName: Build and push image
  inputs:
    command: buildAndPush
    repository: $(acrName)/$(imageName)
    dockerfile: src/Backend/Dockerfile
    tags: $(Build.SourceVersion)
```

CD: Deploy to AKS (release pipeline job):
```yaml
- stage: DeployToStaging
  jobs:
  - deployment: HelmDeploy
    environment: 'staging'
    pool:
      vmImage: 'ubuntu-latest'
    strategy:
      runOnce:
        deploy:
          steps:
          - script: |
              az aks get-credentials --resource-group rg-staging --name aks-staging --overwrite-existing
          - script: |
              helm upgrade --install hbs-backend ./charts/hbs-backend -f values.staging.yaml --set image.tag=$(Build.SourceVersion) --namespace staging
```

Notes:
- Use service connections with least privilege for deployments.
- Protect production branches with branch policies and required approvals.

---

## 6. Configuration & Secrets

- Use Azure Key Vault for secrets, certificates, and sensitive configuration.
- Use Kubernetes secrets only for non-sensitive config or store references to Key Vault via CSI provider.
- Prefer Managed Identity for AKS to access Key Vault (no client secrets in manifests).
- Example: use `aad-pod-identity` or the AKS-managed identity + Key Vault provider to fetch secrets at runtime.

Configuration management:
- Use ConfigMaps for non-sensitive app config.
- Store immutable configuration in Git and use Helm to render per-environment values.
- Avoid embedding secrets in Helm values files for prod — instead inject via pipeline from Key Vault.

---

## 7. Database Migrations

- Prefer migration tools: EF Core Migrations (for .NET) or Flyway for language-agnostic migrations.
- Apply migrations as part of the deployment pipeline with guarded checks:
  - Run migrations in staging first and verify
  - For production, run migrations in maintenance window or use backward-compatible migration patterns (expand-then-contract)

Migration best practices:
- Keep migrations small and reversible when feasible
- Use feature toggles when deploying code that depends on new schema fields
- Backup database before destructive migrations

---

## 8. Feature Flags & Progressive Releases

- Integrate a feature flag service (LaunchDarkly, Unleash) or roll-your-own via database flags.
- Use flags to decouple deploy from release; toggle features for canaries and A/B testing.

---

## 9. Rollback & Recovery

Rollback strategies:
- Fast rollback: revert to previous Helm release or deploy previous image digest and validate.
- DB-sensitive rollback: if DB schema changed, follow migration reversal plan; sometimes rollback requires running compensating migrations and business process handling.

Runbooks:
- Include step-by-step rollback runbook per environment. Example steps:
  1. Disable external traffic (stop ingress or scale down replica to 0 for new pods)
  2. Deploy previous Helm release with previous image digest
  3. Monitor readiness and health checks
  4. If DB changes were applied, run compensating migration or escalate to DB runbook owner
  5. Notify stakeholders and update incident ticket

---

## 10. Monitoring, Logging & Alerting

Metrics & Tracing:
- App Insights for .NET telemetry and distributed tracing
- Prometheus + Grafana for cluster and custom metrics
- Use OpenTelemetry to standardize traces and spans across services

Logging:
- Structured JSON logs
- Centralized log store (Azure Monitor / Log Analytics)
- Correlate logs with trace IDs and request IDs

Alerting & SLOs:
- Define SLIs (error rate, latency), SLOs and error budgets per service
- Configure alerts for:
  - Elevated error rates (5xx)
  - Increased latency (P95 above threshold)
  - Resource pressure (CPU, memory)
  - Failed deployments

---

## 11. Security & Compliance in Pipeline

- Static code analysis (SAST) during CI (SonarQube)
- Dependency scanning (Snyk/WhiteSource) for vulnerable packages
- Container image scanning (Trivy) for CVEs
- Secrets scanning and blocking accidental commits
- Require sign-off for production deploys and run automated compliance checks

---

## 12. Disaster Recovery & Backups

- Backup databases daily; geo-redundant backups for production
- Test restore procedures quarterly
- Define RTO and RPO for each environment; verify during DR drills
- Use point-in-time restore for critical failures where supported

---

## 13. Release Checklist (Production)

Before release to production:
- [ ] All PR checks passed (unit, integration, lint)
- [ ] Security scans passed (SAST, dependency, container)
- [ ] Migration plan reviewed and approved
- [ ] Backups/snapshots completed
- [ ] Monitoring dashboards ready
- [ ] Runbook verified and on-call notified
- [ ] Rollback tested in staging

Post-deploy verification:
- Run automated smoke tests
- Validate business-critical flows (search, booking, payment)
- Confirm alerts are not firing
- Monitor metrics for at least 30 minutes

---

## 14. Runbooks & Incident Response

Include per-service runbooks that cover:
- How to access environments and incident consoles
- Quick mitigation steps for common failures (restart pods, scale down/up)
- Contact info for on-call engineers and escalation path
- Links to logs, dashboards, and deployment history

---

## 15. Example Commands & Snippets

Note: these commands assume you have `az`, `kubectl`, `helm` configured and proper permissions.

Get AKS credentials:
```powershell
az aks get-credentials --resource-group rg-prod --name aks-prod --overwrite-existing
```

Deploy Helm chart to production:
```powershell
helm upgrade --install hbs-backend ./charts/hbs-backend -f values.prod.yaml --namespace production --set image.digest=sha256:<digest>
```

Rollback Helm release:
```powershell
helm rollback hbs-backend 2
```

---

## 16. Governance & Documentation

- Keep deployment and infra runbooks in `docs/` and link them from the on-call wiki.
- Document changes to IaC in PR descriptions and in a CHANGELOG for infra.
- Ensure least-privilege principles for service principals and managed identities.

---

## 17. Appendix & References

- Azure AKS best practices: https://learn.microsoft.com/azure/aks/
- Helm docs: https://helm.sh/docs/
- Terraform on Azure: https://learn.hashicorp.com/collections/terraform/azure
- Azure DevOps pipelines: https://learn.microsoft.com/azure/devops/pipelines/
- OpenTelemetry: https://opentelemetry.io/

---

**End of Deployment Guidelines**
