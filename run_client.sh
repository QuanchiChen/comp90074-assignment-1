# You may need to give this script execute permission manually.
# Run the following command in the Terminal.
# chmod +x run_client.sh

docker build -t client-exploit-program .
docker run --add-host=host.docker.internal:host-gateway --rm client-exploit-program