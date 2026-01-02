$ErrorActionPreference = "Stop"

# Configuration
$PG_BIN = "C:\Program Files\PostgreSQL\17\bin"
$DUMP_FILE = "prod_schema.sql"

# Production Details (Source)
$PROD_HOST = "dpg-d3ii4fruibrs73cukdtg-a.oregon-postgres.render.com"
$PROD_DB = "noltrion_hrm"
$PROD_USER = "noltrion_admin"
$PROD_PASS = "1UzH1rVxlnimPf1qvyLEnuEeOnrybn7f"

# Development Details (Target)
$DEV_HOST = "dpg-d2kq4015pdvs739uk9h0-a.oregon-postgres.render.com"
$DEV_DB = "pgnoltrion"
$DEV_USER = "noltrion_admin"
$DEV_PASS = "xa5ZvROhUAN6IkVHwB4jqacjV2r9gJ5y"

Write-Host ">>> STARTING MIGRATION: PROD -> DEV" -ForegroundColor Cyan

# 1. Dump Production Schema
Write-Host "`n1. Dumping Production Schema..." -ForegroundColor Yellow
$env:PGPASSWORD = $PROD_PASS
& "$PG_BIN\pg_dump.exe" -h $PROD_HOST -U $PROD_USER -d $PROD_DB --schema-only --no-owner --no-privileges -f $DUMP_FILE
if ($LASTEXITCODE -ne 0) { throw "pg_dump failed" }
Write-Host "   Dump successful: $DUMP_FILE" -ForegroundColor Green

# 2. Drop & Recreate Public Schema on Dev
Write-Host "`n2. Resetting Dev Database (Drop/Create Schema public)..." -ForegroundColor Yellow
$env:PGPASSWORD = $DEV_PASS
$RESET_SQL = "DROP SCHEMA public CASCADE; CREATE SCHEMA public; GRANT ALL ON SCHEMA public TO public;"
& "$PG_BIN\psql.exe" -h $DEV_HOST -U $DEV_USER -d $DEV_DB -c $RESET_SQL
if ($LASTEXITCODE -ne 0) { throw "Schema reset failed" }
Write-Host "   Schema reset successful." -ForegroundColor Green

# 3. Restore Schema to Dev
Write-Host "`n3. Restoring Schema to Dev..." -ForegroundColor Yellow
& "$PG_BIN\psql.exe" -h $DEV_HOST -U $DEV_USER -d $DEV_DB -f $DUMP_FILE
if ($LASTEXITCODE -ne 0) { throw "Restore failed" }
Write-Host "   Restore successful." -ForegroundColor Green

Write-Host "`n>>> MIGRATION COMPLETE!" -ForegroundColor Cyan
