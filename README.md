# python-sam-app-3

## ScrapingFunction

```bash
pipenv lock -r > sam/packages/requirements.txt
sam build PackageLayer
sam local invoke --docker-network python-sam-app-3_default ScrapingFunction
```

## ScheduleApiFunction

```bash
pipenv lock -r > sam/packages/requirements.txt
sam build PackageLayer
sam local start-api --docker-network python-sam-app-3_default
```

## デプロイ

```bash
sam build  --parameter-overrides Env=dev
sam deploy --parameter-overrides Env=dev --guided --no-confirm-changeset --config-file samconfig.toml
```