#!/bin/sh

#   1. Install cURL
#   2. Build and tag the new image
#   3. Log in to the Heroku Container Registry
#   4. Push the image up to the registry
#   5. Create a new release via the Heroku API using the image ID
#      within the release.sh script


IMAGE_ID=$(docker inspect ${HEROKU_REGISTRY_IMAGE} --format={{.Id}})
PAYLOAD='{"updates": [{"type": "web", "docker_image": "'"$IMAGE_ID"'"}]}'

curl -n -X PATCH https://api.heroku.com/apps/$HEROKU_APP_NAME/formation \
  -d "${PAYLOAD}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/vnd.heroku+json; version=3.docker-releases" \
  -H "Authorization: Bearer ${HEROKU_AUTH_TOKEN}"
