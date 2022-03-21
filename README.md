# python-sam-app-3

## ScrapingFunction

```bash
pipenv lock -r > sam/packages/requirements.txt
sam build PackageLayer
sam local invoke --docker-network python-sam-app-3_default ScrapingFunction
```