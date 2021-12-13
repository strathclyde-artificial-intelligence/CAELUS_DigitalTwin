SSH_KEY=$1
IMAGE_NAME="ghcr.io/h3xept/caelus_dt:latest"

docker build --no-cache -t $IMAGE_NAME --build-arg SSH_PRIVATE_KEY="$(cat $SSH_KEY)" .
docker push $IMAGE_NAME