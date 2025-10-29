A Docker commands cheat sheet provides a quick reference for commonly used commands to manage containers, images, volumes, and networks.

Container Management:
docker ps: Lists running containers. Use docker ps -a to list all containers (running and stopped).
docker start <container_name_or_id>: Starts a stopped container.
docker stop <container_name_or_id>: Stops a running container gracefully.
docker restart <container_name_or_id>: Restarts a container.
docker rm <container_name_or_id>: Removes a stopped container.
docker exec -it <container_name_or_id> <command>: Executes a command inside a running container. For example, docker exec -it my_container /bin/bash opens a shell inside my_container.
docker logs <container_name_or_id>: Displays logs from a container. Use -f to follow logs in real-time.
docker inspect <container_name_or_id>: Provides detailed information about a container.


Image Management:
docker images: Lists all local Docker images.
docker pull <image_name>[:tag]: Pulls an image from a registry (e.g., Docker Hub).
docker build -t <image_name>[:tag] .: Builds a Docker image from a Dockerfile in the current directory.
docker rmi <image_name_or_id>: Removes a local Docker image.
docker push <image_name>[:tag]: Pushes an image to a registry.


Volume Management:
docker volume create <volume_name>: Creates a new Docker volume.
docker volume ls: Lists all Docker volumes.
docker volume inspect <volume_name>: Displays detailed information about a volume.
docker volume rm <volume_name>: Removes a Docker volume.


Network Management:
docker network create <network_name>: Creates a new Docker network.
docker network ls: Lists all Docker networks.
docker network inspect <network_name>: Displays detailed information about a network.
docker network rm <network_name>: Removes a Docker network.


System Commands:
docker system df: Shows Docker disk space usage.
docker system prune: Removes unused Docker data (stopped containers, unused networks, dangling images, and build cache). Use -a for more aggressive pruning.

target rag_evaluation: failed to solve: error getting credentials - err: exec: "docker-credential-desktop": executable file not found in $PATH, out: ``
vi ~/.docker/config.json
credsStore -> credStore