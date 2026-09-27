#!/bin/sh
# Starts Playwright's browser server in the official Docker image, if it isn't running yet.
# The story tests connect to it (see vite.config.ts), so no browser is installed on the host.
# The image tag follows the installed playwright package: client and server must match exactly.
# Stop it with `pnpm pw:stop`.
set -e

if [ -n "$CHROMIUM_EXECUTABLE" ]; then
	exit 0 # a preinstalled Chromium is used instead (Claude Code cloud sessions have no Docker)
fi

NAME=but-the-sample-size-playwright
PORT=${PLAYWRIGHT_PORT:-53333}
VERSION=$(node -p "require('playwright/package.json').version")
IMAGE=mcr.microsoft.com/playwright:v$VERSION-noble

running=$(docker ps --filter "name=^$NAME$" --format '{{.Image}}')
if [ "$running" = "$IMAGE" ]; then
	exit 0
fi
if [ -n "$running" ]; then
	docker rm -f "$NAME" >/dev/null # left over from another playwright version
fi

docker run -d --rm --init --name "$NAME" -p "127.0.0.1:$PORT:3000" \
	--user pwuser --workdir /home/pwuser "$IMAGE" \
	/bin/sh -c "npx -y playwright@$VERSION run-server --port 3000 --host 0.0.0.0" >/dev/null

# Ready once the server logs that it's listening. Docker's port proxy accepts connections
# before that, so probing the port isn't enough. The first run also downloads the image.
for _ in $(seq 1 120); do
	if docker logs "$NAME" 2>&1 | grep -q '^Listening on'; then
		exit 0
	fi
	sleep 1
done
echo "Playwright server didn't start on port $PORT; see: docker logs $NAME" >&2
exit 1
