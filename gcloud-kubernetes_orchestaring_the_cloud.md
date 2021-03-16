```
gcloud auth list
gcloud config list project
gcloud config set compute/zone us-central1-b
gcloud container clusters create io
```

Clone the GitHub repository from the Cloud Shell command line:  
```gsutil cp -r gs://spls/gsp021/* .```  

The easiest way to get started with Kubernetes is to use the kubectl create command. Use it to launch a single instance of the nginx container:   
```kubectl create deployment nginx --image=nginx:1.10.0```   
Kubernetes has created a deployment -- more about deployments later, but for now all you need to know is that deployments keep the pods up and running even when the nodes they run on fail.

```kubectl get pods``` - view pods

Once the nginx container has a Running status you can expose it outside of Kubernetes using the kubectl expose command:   
```kubectl expose deployment nginx --port 80 --type LoadBalancer```

```kubectl get services``` - view services

## Pods
At the core of Kubernetes is the Pod.

Pods represent and hold a collection of one or more containers. Generally, if you have multiple containers with a hard dependency on each other, you package the containers inside a single pod.

![](https://cdn.qwiklabs.com/tzvM5wFnfARnONAXX96nz8OgqOa1ihx6kCk%2BelMakfw%3D)

In this example there is a pod that contains the monolith and nginx containers.

Pods also have Volumes. Volumes are data disks that live as long as the pods live, and can be used by the containers in that pod. Pods provide a shared namespace for their contents which means that the two containers inside of our example pod can communicate with each other, and they also share the attached volumes.

Pods also share a network namespace. This means that there is one IP Address per pod.

Now let's take a deeper dive into pods.

Pods can be created using pod configuration files. Let's take a moment to explore the monolith pod configuration file. Run the following:  
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: monolith
  labels:
    app: monolith
spec:
  containers:
    - name: monolith
      image: kelseyhightower/monolith:1.0.0
      args:
        - "-http=0.0.0.0:80"
        - "-health=0.0.0.0:81"
        - "-secret=secret"
      ports:
        - name: http
          containerPort: 80
        - name: health
          containerPort: 81
      resources:
        limits:
          cpu: 0.2
          memory: "10Mi"
```

- your pod is made up of one container (the monolith).
- you're passing a few arguments to our container when it starts up.
- you're opening up port 80 for http traffic.  
Create the monolith pod using kubectl:  
```kubectl create -f pods/monolith.yaml```  
```kubectl describe pods monolith```    
You'll see a lot of the information about the monolith pod including the Pod IP address and the event log. This information will come in handy when troubleshooting.


## interacting with pods 
By default, pods are allocated a private IP address and cannot be reached outside of the cluster. Use the ```kubectl port-forward``` command to map a local port to a port inside the monolith pod.    
```kubectl port-forward monolith 10080:80```   
Try logging in to get an auth token back from the monolith:   
```curl -u user http://127.0.0.1:10080/login```   
Logging in caused a JWT token to print out. Since Cloud Shell does not handle copying long strings well, create an environment variable for the token.   
```TOKEN=$(curl http://127.0.0.1:10080/login -u user|jq -r '.token')```  
```curl -H "Authorization: Bearer $TOKEN" http://127.0.0.1:10080/secure```   
```kubectl logs monolith```
use the -f flag to get a stream of the logs happening in real-time:
```kubectl logs -f monolith```   
Use the kubectl exec command to run an interactive shell inside the Monolith Pod. This can come in handy when you want to troubleshoot from within a container:    
```kubectl exec monolith --stdin --tty -c monolith /bin/sh```   
```ping -c 3 google.com``` 
```exit```

## Services

Pods aren't meant to be persistent. They can be stopped or started for many reasons - like failed liveness or readiness checks - and this leads to a problem:  
What happens if you want to communicate with a set of Pods? When they get restarted they might have a different IP address.    
That's where Services come in. Services provide stable endpoints for Pods.   

![](https://cdn.qwiklabs.com/Jg0T%2F326ASwqeD1vAUPBWH5w1D%2F0oZn6z5mQ5MubwL8%3D)

Services use labels to determine what Pods they operate on. If Pods have the correct labels, they are automatically picked up and exposed by our services.   
The level of access a service provides to a set of pods depends on the Service's type. Currently there are three types:
 - ClusterIP (internal) -- the default type means that this Service is only visible inside of the cluster,
 - NodePort gives each node in the cluster an externally accessible IP and
 - LoadBalancer adds a load balancer from the cloud provider which forwards traffic from the service to Nodes within it.   
Now you'll learn how to:
 - Create a service
 - Use label selectors to expose a limited set of Pods externally

## creating services
Before we can create our services -- let's first create a secure pod that can handle https traffic.   
Create the secure-monolith pods and their configuration data:    
```
kubectl create secret generic tls-certs --from-file tls/
kubectl create configmap nginx-proxy-conf --from-file nginx/proxy.conf
kubectl create -f pods/secure-monolith.yaml
```

Now that you have a secure pod, it's time to expose the secure-monolith Pod externally.To do that, create a Kubernetes service.   
Explore the monolith service configuration file:   
```yaml
kind: Service
apiVersion: v1
metadata:
  name: "monolith"
spec:
  selector:
    app: "monolith"
    secure: "enabled"
  ports:
    - protocol: "TCP"
      port: 443
      targetPort: 443
      nodePort: 31000
  type: NodePort
```

Things to note:
 - There's a selector which is used to automatically find and expose any pods with the labels ```app: monolith``` and ```secure: enabled```.
 - Now you have to expose the nodeport here because this is how you'll forward external traffic from port 31000 to nginx (on port 443).

Use the kubectl create command to create the monolith service from the monolith service configuration file:   
```kubectl create -f services/monolith.yaml```  

You're using a port to expose the service. This means that it's possible to have port collisions if another app tries to bind to port 31000 on one of your servers.    
Normally, Kubernetes would handle this port assignment. In this lab you chose a port so that it's easier to configure health checks later on.    
Use the ```gcloud compute firewall-rules``` command to allow traffic to the monolith service on the exposed nodeport:    
```
gcloud compute firewall-rules create allow-monolith-nodeport \
  --allow=tcp:31000
```

## Adding labels to pods
Currently the monolith service does not have endpoints. One way to troubleshoot an issue like this is to use the kubectl get pods command with a label query.   
We can see that we have quite a few pods running with the monolith label.   
```
kubectl get pods -l "app=monolith"
kubectl get pods -l "app=monolith,secure=enabled"
```   
Use the ```kubectl label``` command to add the missing ```secure=enabled``` label to the ```secure-monolith``` Pod. Afterwards, you can check and see that your labels have been updated.   

```
kubectl label pods secure-monolith 'secure=enabled'
kubectl get pods secure-monolith --show-labels
kubectl describe services monolith | grep Endpoints
gcloud compute instances list
curl -k https://<EXTERNAL_IP>:31000
```


## Deploying Applications with Kubernetes
The goal of this lab is to get you ready for scaling and managing containers in production. That's where Deployments come in. Deployments are a declarative way to ensure that the number of Pods running is equal to the desired number of Pods, specified by the user.
![](https://cdn.qwiklabs.com/1UD7MTP0ZxwecE%2F64MJSNOP8QB7sU9rTI0PSv08OVz0%3D)

The main benefit of Deployments is in abstracting away the low level details of managing Pods. Behind the scenes Deployments use Replica Sets to manage starting and stopping the Pods. If Pods need to be updated or scaled, the Deployment will handle that. Deployment also handles restarting Pods if they happen to go down for some reason.

Let's look at a quick example:

![](https://cdn.qwiklabs.com/fH4ZxGNxg5KLBy5ykbwKNIS9MIJ9cgcMEDuhB0a9uBo%3D)

Pods are tied to the lifetime of the Node they are created on. In the example above, Node3 went down (taking a Pod with it). Instead of manually creating a new Pod and finding a Node for it, your Deployment created a new Pod and started it on Node2.

That's pretty cool!

It's time to combine everything you learned about Pods and Services to break up the monolith application into smaller Services using Deployments.

## Creating Deployments
Get started by examining the auth deployment configuration file.  
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: auth
spec:
  selector:
    matchlabels:
      app: auth
  replicas: 1
  template:
    metadata:
      labels:
        app: auth
        track: stable
    spec:
      containers:
        - name: auth
          image: "kelseyhightower/auth:2.0.0"
          ports:
            - name: http
              containerPort: 80
            - name: health
              containerPort: 81
```

When you run the ```kubectl create``` command to create the auth deployment it will make one pod that conforms to the data in the Deployment manifest. This means you can scale the number of Pods by changing the number specified in the Replicas field.   
Anyway, go ahead and create your deployment object:   
```
kubectl create -f deployments/auth.yaml
kubectl create -f services/auth.yaml

kubectl create -f deployments/hello.yaml
kubectl create -f services/hello.yaml

kubectl create configmap nginx-frontend-conf --from-file=nginx/frontend.conf
kubectl create -f deployments/frontend.yaml
kubectl create -f services/frontend.yaml
```   
There is one more step to creating the frontend because you need to store some configuration data with the container.   
```
kubectl get services frontend
curl -k https://<EXTERNAL-IP>
```




