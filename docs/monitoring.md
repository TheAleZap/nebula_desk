cd nebula_desk
git checkout main
git pull
git checkout -b kohana/monitoring

# ...create / replace the files listed above in VS Code, save them...

git add docs/monitoring.md AI_USAGE.md
git commit -m "Add monitoring queries and SLO"
git pull origin main
git push -u origin kohana/monitoring
gh pr create --title "docs: monitoring queries and SLO" --body "See the team plan. Story/task: docs: monitoring queries and SLO" --reviewer thealezap