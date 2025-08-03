# Simple script to build and run container without using compose
export TAG="eduvisor"
export PORT=8000
docker rm -f $TAG || true && DOCKER_BUILDKIT=1 docker build -t $TAG . && docker run --env-file .env -it -p $PORT:$PORT --name $TAG $TAG