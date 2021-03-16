### kubernetes

```gcloud config set compute/zone us-central1-a``` - Your compute zone is an approximate regional location in which your clusters and their resources live.   
To create a cluster, run the following command, replacing [CLUSTER-NAME] with the name you choose for the cluster :   
```gcloud container clusters create [CLUSTER-NAME]```

To authenticate the cluster, run the following command, replacing [CLUSTER-NAME] with the name of your cluster:  
```gcloud container clusters get-credentials [CLUSTER-NAME]```  

To create a new Deployment hello-server from the hello-app container image, run the following kubectl create command:  
```kubectl create deployment hello-server --image=gcr.io/google-samples/hello-app:1.0```   
This Kubernetes command creates a Deployment object that represents hello-server. In this case, --image specifies a container image to deploy. The command pulls the example image from a Container Registry bucket. gcr.io/google-samples/hello-app:1.0 indicates the specific image version to pull. If a version is not specified, the latest version is used.


To create a Kubernetes Service, which is a Kubernetes resource that lets you expose your application to external traffic, run the following kubectl expose command:   
```kubectl expose deployment hello-server --type=LoadBalancer --port 8080```   

In this command:
- ```--port``` specifies the port that the container exposes.
- ```type="LoadBalancer"``` creates a Compute Engine load balancer for your container.

To inspect the hello-server Service, run kubectl get:     
```kubectl get service```    
```
NAME              TYPE              CLUSTER-IP        EXTERNAL-IP      PORT(S)           AGE
hello-server      loadBalancer      10.39.244.36      35.202.234.26    8080:31991/TCP    65s
kubernetes        ClusterIP         10.39.240.1       <none>           433/TCP           5m13s
```   
Note: It might take a minute for an external IP address to be generated. Run the previous command again if the EXTERNAL-IP column status is pending.

o view the application from your web browser, open a new tab and enter the following address, replacing ```[EXTERNAL IP]``` with the ```EXTERNAL-IP``` for ```hello-server```:  
```http://[EXTERNAL-IP]:8080```

To delete the cluster, run the following command:  
```gcloud container clusters delete [CLUSTER-NAME]```
