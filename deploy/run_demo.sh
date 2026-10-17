#!/usr/bin/env bash
# Builds and runs the backend and frontend containers on a shared Docker network,
# publishes ports 7860 and 8501, runs API inference and captures UI screenshots.
cd "$(dirname "$0")/.."
ROOT=$PWD
EV=$ROOT/evidence; mkdir -p $EV
exec > >(tee -a $EV/run_log.txt) 2>&1
for i in $(seq 1 90); do docker info >/dev/null 2>&1 && break; sleep 2; done
echo "== $(date -u) start"
docker network create superkart-network || true
(cd backend && docker build -t superkart-backend .) 
(cd frontend && docker build -t superkart-frontend .)
docker rm -f backend frontend 2>/dev/null
docker run -d --name backend --network superkart-network -p 7860:7860 superkart-backend
# In Codespaces the nested Docker bridge did not pass container-to-container traffic, so the
# hostname "backend" is mapped to the Docker host gateway; app.py still calls http://backend:7860.
docker run -d --name frontend --network superkart-network --add-host backend:host-gateway -p 8501:8501 superkart-frontend
for i in $(seq 1 60); do curl -s localhost:7860/ | grep -q Welcome && break; sleep 2; done
for i in $(seq 1 60); do curl -s localhost:8501/ >/dev/null && break; sleep 2; done
DOMAIN=${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN:-app.github.dev}
BACK="https://${CODESPACE_NAME}-7860.${DOMAIN}"
FRONT="https://${CODESPACE_NAME}-8501.${DOMAIN}"
echo "$BACK" > $EV/backend_url.txt; echo "$FRONT" > $EV/frontend_url.txt
echo "Setting ports 7860 and 8501 to public"
for i in $(seq 1 30); do
  GH_TOKEN=$GH_PAT gh codespace ports visibility 7860:public 8501:public -c "$CODESPACE_NAME" && break
  sleep 5
done
GH_TOKEN=$GH_PAT gh codespace ports -c "$CODESPACE_NAME" > $EV/ports.txt 2>&1
for i in $(seq 1 60); do curl -s "$BACK/" | grep -q Welcome && break; sleep 3; done
{ docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}'; echo; docker network inspect superkart-network --format '{{range .Containers}}{{.Name}} {{.IPv4Address}}{{"\n"}}{{end}}'; } > $EV/docker_ps.txt
docker logs backend > $EV/backend_log.txt 2>&1
docker logs frontend > $EV/frontend_log.txt 2>&1
python -m pip install -q requests pandas playwright
python -m playwright install --with-deps chromium > /dev/null 2>&1
python deploy/inference.py "$BACK" > $EV/inference_output.txt 2>&1
python deploy/capture.py "$FRONT" "$EV" > $EV/capture_log.txt 2>&1
git config user.name "Tony Philip"; git config user.email "313515307+tphilipBG@users.noreply.github.com"
git add evidence && git commit -m "Add deployment evidence" && git push origin HEAD:main
echo DONE > $EV/done.txt; git add evidence && git commit -m "Deployment evidence complete" && git push origin HEAD:main
