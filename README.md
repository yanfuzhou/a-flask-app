Build:
```bash
docker build --rm -t a-flask-app .
```
Deploy:
```bash
cd deployments
kubectl kustomize | kubectl apply -f -
```