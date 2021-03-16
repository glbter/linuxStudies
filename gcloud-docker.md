### start 
```gcloud auth list``` - list the active account name

(Output)
```
Credentialed accounts:
 - <myaccount>@<mydomain>.com (active)
```

```gcloud config list project``` - list the project ID

(Output)
```
[core]
project = <project_ID>
```

### docker
```docker ps -a``` - to see all containers, including ones that have finished executing

```docker build -t node-app:0.1 .``` The -t is to name and tag an image with the name:tag syntax. The name of the image is node-app and the tag is 0.1. The tag is highly recommended when building Docker images.

```docker run -p 4000:80 --name my-app node-app:0.1``` - The --name flag allows you to name the container if you like. The -p instructs Docker to map the host's port 4000 to the container's port 80. Now you can reach the server at http://localhost:4000. Without port mapping, you would not be able to reach the container at localhost.

You can look at the logs by executing ```docker logs [container_id]```

```docker logs -f [container_id]``` - f you want to follow the log's output as the container is running, use the -f option.

```docker exec -it [container_id] bash``` - The -it flags let you interact with a container by allocating a pseudo-tty and keeping stdin open. Opens bash

```docker inspect [container_id]``` - You can examine a container's metadata in Docker by using Docker inspect:

```docker inspect --format='{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' [container_id]``` - Use ```--format``` to inspect specific fields from the returned JSON. For example

output: ```192.168.9.3```

### docker-publish
Now you're going to push your image to the Google Container Registry (gcr). After that you'll remove all containers and images to simulate a fresh environment, and then pull and run your containers. This will demonstrate the portability of Docker containers.

To push images to your private registry hosted by gcr, you need to tag the images with a registry name. The format is ```[hostname]/[project-id]/[image]:[tag]```.

For gcr:
- ```[hostname]```= gcr.io
- ```[project-id]```= your project's ID
- ```[image]```= your image name
- ```[tag]```= any string tag of your choice. If unspecified, it defaults to "latest".

```gcloud config list project``` - You can find your project ID by running
```
[core]
project = [project-id]

Your active configuration is: [default]
```

Tag ```node-app:0.2```. Replace ```[project-id]```  with your configuration

```docker tag node-app:0.2 gcr.io/[project-id]/node-app:0.2```

```docker push gcr.io/[project-id]/node-app:0.2``` - Push this image to gcr

Check that the image exists in gcr by visiting the image registry in your web browser ```http://gcr.io/[project-id]/node-app```

Stop and remove all containers
```
docker stop $(docker ps -q)
docker rm $(docker ps -aq)
``` 

```-q``` - only id

```docker rmi node-app:0.2 gcr.io/[project-id]/node-app node-app:0.1``` - rm image

Pull the image and run it:
```
docker pull gcr.io/[project-id]/node-app:0.2
docker run -p 4000:80 -d gcr.io/[project-id]/node-app:0.2
``` 












