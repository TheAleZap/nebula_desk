#!/usr/bin/env bash
# =============================================================================
# Nebula Desk - ONE-TIME initial Azure setup (group sdd-3a-g6).
# Run ONCE, by ONE person (Alejandro), in Azure Cloud Shell (Bash), with the
# directory switched to "IE Instituto de Empresa". After this, only the CD
# pipeline changes anything in Azure.
#
#   export GH_REPO=TheAleZap/nebula_desk
#   bash infra/setup.sh
#
# Passwords are generated here and stored ONLY as GitHub secrets and Container
# Apps secrets. Nothing secret is written to a file or committed.
# =============================================================================
set -euo pipefail

PREFIX="sdd-3a-g6"
RG="rg-sdd-3a-g6"
LOCATION="westeurope"                                  # the region the RG lives in
TENANT_ID="5ca2bc70-353c-4d1f-b7d7-7f2b2259df68"         # IE Instituto de Empresa
SUBSCRIPTION_ID="e0b9cada-61bc-4b5a-bd7a-52c606726b3b"
GH_REPO="${GH_REPO:?Set GH_REPO=owner/repo first}"

SQL_SERVER="$PREFIX-sql"
SQL_HOST="$SQL_SERVER.database.windows.net"
SQL_ADMIN="nebulaadmin"
ENVIRONMENT="$PREFIX-env"
IDENTITY="$PREFIX-github"

# Generate cryptographically random, unique passwords for the SQL administrator
# and each application database user, avoiding hardcoded or reused credentials.
# All three are stored as GitHub secrets; each app user's password is also stored
# in its Container App's database-url secret. None is ever written to a file.
gen_password() { echo "Nb$(openssl rand -hex 14)7"; }   # upper, lower, digits; URL-safe
SQL_ADMIN_PASSWORD="$(gen_password)"
CONVERSATION_DB_PASSWORD="$(gen_password)"
INTELLIGENCE_DB_PASSWORD="$(gen_password)"

echo "== 0. Account and what already exists in the resource group"
az account set --subscription "$SUBSCRIPTION_ID"
az account show --query "{subscription:name, tenant:tenantId}" -o table
az resource list -g "$RG" -o table

echo "== 1. SQL server (one logical server) + firewall: allow Azure services"
az sql server create -n "$SQL_SERVER" -g "$RG" -l "$LOCATION" \
  --admin-user "$SQL_ADMIN" --admin-password "$SQL_ADMIN_PASSWORD" -o none
az sql server firewall-rule create -g "$RG" -s "$SQL_SERVER" -n AllowAzureServices \
  --start-ip-address 0.0.0.0 --end-ip-address 0.0.0.0 -o none

echo "== 2. Two serverless databases (IE subscription: no free offer -> 15 min auto-pause, 2 GB)"
for svc in conversation intelligence; do
  az sql db create -g "$RG" -s "$SQL_SERVER" -n "$PREFIX-$svc-db" \
    --edition GeneralPurpose --compute-model Serverless --family Gen5 \
    --min-capacity 0.5 --capacity 1 --auto-pause-delay 15 --max-size 2GB \
    --backup-storage-redundancy Local -o none
done

echo "== 3. One contained user per database (firewall opened to this shell's IP, then closed)"
MY_IP="$(curl -s https://api.ipify.org)"
az sql server firewall-rule create -g "$RG" -s "$SQL_SERVER" -n setup-temp \
  --start-ip-address "$MY_IP" --end-ip-address "$MY_IP" -o none
create_user() { # $1 = database, $2 = user, $3 = password
  sqlcmd -S "tcp:$SQL_HOST,1433" -d "$1" -U "$SQL_ADMIN" -P "$SQL_ADMIN_PASSWORD" -b -Q "
    IF USER_ID('$2') IS NULL CREATE USER [$2] WITH PASSWORD = '$3';
    ALTER ROLE db_ddladmin ADD MEMBER [$2];
    ALTER ROLE db_datareader ADD MEMBER [$2];
    ALTER ROLE db_datawriter ADD MEMBER [$2];"
}
create_user "$PREFIX-conversation-db" conversation_app "$CONVERSATION_DB_PASSWORD"
create_user "$PREFIX-intelligence-db" intelligence_app "$INTELLIGENCE_DB_PASSWORD"
az sql server firewall-rule delete -g "$RG" -s "$SQL_SERVER" -n setup-temp -o none

echo "== 4. Container Apps environment (creates the Log Analytics workspace used for monitoring)"
az containerapp env create -n "$ENVIRONMENT" -g "$RG" -l "$LOCATION" -o none

echo "== 5. Static Web App for the UI (its URL is the only allowed CORS origin)"
az staticwebapp create -n "$PREFIX-ui" -g "$RG" -l "$LOCATION" --sku Free -o none
UI_ORIGIN="https://$(az staticwebapp show -n "$PREFIX-ui" -g "$RG" --query defaultHostname -o tsv)"

echo "== 6. Container Apps: scale 0..1, placeholder image (the first CD run replaces it)"
create_app() { # $1 = service, $2 = db password, $3.. = extra env vars
  local svc="$1" password="$2"; shift 2
  az containerapp create -n "$PREFIX-$svc" -g "$RG" --environment "$ENVIRONMENT" \
    --image mcr.microsoft.com/k8se/quickstart:latest \
    --target-port 8000 --ingress external \
    --min-replicas 0 --max-replicas 1 --cpu 0.25 --memory 0.5Gi \
    --secrets "database-url=mssql+pymssql://${svc}_app:${password}@${SQL_HOST}:1433/${PREFIX}-${svc}-db" \
    --env-vars DATABASE_URL=secretref:database-url CORS_ORIGINS="$UI_ORIGIN" "$@" -o none
}
create_app intelligence "$INTELLIGENCE_DB_PASSWORD"
INTELLIGENCE_URL="https://$(az containerapp show -n "$PREFIX-intelligence" -g "$RG" \
  --query properties.configuration.ingress.fqdn -o tsv)"
create_app conversation "$CONVERSATION_DB_PASSWORD" \
  INTELLIGENCE_URL="$INTELLIGENCE_URL" INTELLIGENCE_TIMEOUT_S=3

echo "== 7. Trust GitHub Actions (main branch only) on the existing identity $IDENTITY"
az identity federated-credential create -g "$RG" --identity-name "$IDENTITY" -n github-main \
  --issuer https://token.actions.githubusercontent.com \
  --subject "repo:${GH_REPO}:ref:refs/heads/main" \
  --audiences api://AzureADTokenExchange -o none
# GitHub sometimes sends the subject with numeric IDs: register that form too.
NUMERIC_SUBJECT="$(gh api "repos/$GH_REPO" \
  --jq '"repo:\(.owner.login)@\(.owner.id)/\(.name)@\(.id):ref:refs/heads/main"')"
az identity federated-credential create -g "$RG" --identity-name "$IDENTITY" -n github-main-ids \
  --issuer https://token.actions.githubusercontent.com \
  --subject "$NUMERIC_SUBJECT" --audiences api://AzureADTokenExchange -o none
CLIENT_ID="$(az identity show -n "$IDENTITY" -g "$RG" --query clientId -o tsv)"

echo "== 8. GitHub secrets and variables (gh must be logged in: gh auth login)"
gh secret set AZURE_CLIENT_ID -R "$GH_REPO" -b "$CLIENT_ID"
gh secret set AZURE_TENANT_ID -R "$GH_REPO" -b "$TENANT_ID"
gh secret set AZURE_SUBSCRIPTION_ID -R "$GH_REPO" -b "$SUBSCRIPTION_ID"
gh secret set SQL_ADMIN_PASSWORD -R "$GH_REPO" -b "$SQL_ADMIN_PASSWORD"
gh secret set CONVERSATION_DB_PASSWORD -R "$GH_REPO" -b "$CONVERSATION_DB_PASSWORD"
gh secret set INTELLIGENCE_DB_PASSWORD -R "$GH_REPO" -b "$INTELLIGENCE_DB_PASSWORD"
gh variable set PREFIX -R "$GH_REPO" -b "$PREFIX"
gh variable set RESOURCE_GROUP -R "$GH_REPO" -b "$RG"

echo
echo "Done. UI: $UI_ORIGIN   Intelligence: $INTELLIGENCE_URL"
echo "Next: merge the CD workflow. The first deploy fails on purpose until both GHCR"
echo "packages are made public (GitHub > Packages > package settings), then re-run it."
