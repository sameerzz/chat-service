#!/usr/bin/env bash
set -euo pipefail

# Cloud Build supplies these arguments. Resolve the image once for both targets.
project_id="$1"
region="$2"
repository="$3"
image_name="$4"
build_id="$5"
pipeline="$6"
image_tag="${region}-docker.pkg.dev/${project_id}/${repository}/${image_name}:${build_id}"
digest="$(gcloud artifacts docker images describe "$image_tag" --project="$project_id" --format='value(image_summary.digest)')"
if [[ ! "$digest" =~ ^sha256:[a-f0-9]{64}$ ]]; then
  echo 'Could not resolve a valid image digest' >&2
  exit 1
fi
image_ref="${image_tag%:*}@${digest}"

# Upload only deployment manifests, never application files or local secrets.
bundle_dir="$(mktemp -d)"
mkdir -p "$bundle_dir/deploy"
cp skaffold.yaml "$bundle_dir/skaffold.yaml"
cp deploy/staging-service.yaml deploy/production-service.yaml "$bundle_dir/deploy/"
gcloud deploy releases create "release-${build_id}" \
  --project="$project_id" --region="$region" \
  --delivery-pipeline="$pipeline" \
  --source="$bundle_dir" \
  --gcs-source-staging-dir="gs://${project_id}-deploy-source/releases" \
  --images="book-chat-image=${image_ref}" --quiet
