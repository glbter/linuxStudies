# Continuous Delivery with Jenkins in Kubernetes Engine  
In this lab, you will learn how to set up a continuous delivery pipeline with Jenkins on Kubernetes engine. Jenkins is the go-to automation server used by developers who frequently integrate their code in a shared repository. The solution you'll build in this lab will be similar to the following diagram:  
![зображення](https://user-images.githubusercontent.com/54221016/111686223-799c6600-8831-11eb-8633-fa62c70496e3.png)   
[more about jenkins on kubernetes](https://cloud.google.com/solutions/jenkins-on-kubernetes-engine)   
### What is Kubernetes Engine?   
Kubernetes Engine is Google Cloud's hosted version of Kubernetes - a powerful cluster manager and orchestration system for containers. Kubernetes is an open source project that can run on many different environments—from laptops to high-availability multi-node clusters; from virtual machines to bare metal. As mentioned before, Kubernetes apps are built on containers - these are lightweight applications bundled with all the necessary dependencies and libraries to run them. This underlying structure makes Kubernetes applications highly available, secure, and quick to deploy—an ideal framework for cloud developers.
### What is Jenkins?
[Jenkins](https://www.jenkins.io/) is an open-source automation server that lets you flexibly orchestrate your build, test, and deployment pipelines. Jenkins allows developers to iterate quickly on projects without worrying about overhead issues that can stem from continuous delivery.   
### What is Continuous Delivery / Continuous Deployment?
When you need to set up a continuous delivery (CD) pipeline, deploying Jenkins on Kubernetes Engine provides important benefits over a standard VM-based deployment.   
When your build process uses containers, one virtual host can run jobs on multiple operating systems. Kubernetes Engine provides ephemeral build executors—these are only utilized when builds are actively running, which leaves resources for other cluster tasks such as batch processing jobs. Another benefit of ephemeral build executors is speed—they launch in a matter of seconds.   
Kubernetes Engine also comes pre-equipped with Google's global load balancer, which you can use to automate web traffic routing to your instance(s). The load balancer handles SSL termination and utilizes a global IP address that's configured with Google's backbone network—coupled with your web front, this load balancer will always set your users on the fastest possible path to an application instance.   
Now that you've learned a little bit about Kubernetes, Jenkins, and how the two interact in a CD pipeline, it's time to go build one.

**code:**  
```git clone https://github.com/GoogleCloudPlatform/continuous-deployment-on-kubernetes.git```

### Provisioning Jenkins
Creating a Kubernetes cluster   
Now, run the following command to provision a Kubernetes cluster:    
```
gcloud container clusters create jenkins-cd \
--num-nodes 2 \
--machine-type n1-standard-2 \
--scopes "https://www.googleapis.com/auth/source.read_write,cloud-platform"
```   
This step can take up to several minutes to complete. The extra scopes enable Jenkins to access Cloud Source Repositories and Google Container Registry.      
Before continuing, confirm that your cluster is running by executing the following command:   
```gcloud container clusters list```   
Now, get the credentials for your cluster:   
```gcloud container clusters get-credentials jenkins-c```   
Kubernetes Engine uses these credentials to access your newly provisioned cluster—confirm that you can connect to it by running the following command:   
```kubectl cluster-info```

### Setup Helm
In this lab, you will use Helm to install Jenkins from the Charts repository. Helm is a package manager that makes it easy to configure and deploy Kubernetes applications. Once you have Jenkins installed, you'll be able to set up your CI/CD pipeline.   
Add Helm's stable chart repo:
```helm repo add jenkins https://charts.jenkins.io```   
Ensure the repo is up to date:    
```helm repo update```   

### Configure and Install Jenkins
You will use a custom ```values``` file to add the Google Cloud specific plugin necessary to use service account credentials to reach your Cloud Source Repository.   
Use the Helm CLI to deploy the chart with your configuration settings.   
```helm install cd jenkins/jenkins -f jenkins/values.yaml --version 1.2.2 --wait```    
Once that command completes ensure the Jenkins pod goes to the ```Running``` state and the container is in the READY state:   
```kubectl get pods```   
Configure the Jenkins service account to be able to deploy to the cluster.   
```kubectl create clusterrolebinding jenkins-deploy --clusterrole=cluster-admin --serviceaccount=default:cd-jenkins```   
Run the following command to setup port forwarding to the Jenkins UI from the Cloud Shell   
```
export POD_NAME=$(kubectl get pods --namespace default -l "app.kubernetes.io/component=jenkins-master" -l "app.kubernetes.io/instance=cd" -o jsonpath="{.items[0].metadata.name}")
kubectl port-forward $POD_NAME 8080:8080 >> /dev/null &
```   
Now, check that the Jenkins Service was created properly:   
```kubectl get svc```   
Example Output:   
```
NAME               CLUSTER-IP     EXTERNAL-IP   PORT(S)     AGE
cd-jenkins         10.35.249.67   <none>        8080/TCP    3h
cd-jenkins-agent   10.35.248.1    <none>        50000/TCP   3h
kubernetes         10.35.240.1    <none>        443/TCP     9h
```  
You are using the [Kubernetes Plugin](https://plugins.jenkins.io/kubernetes/) so that our builder nodes will be automatically launched as necessary when the Jenkins master requests them. Upon completion of their work, they will automatically be turned down and their resources added back to the clusters resource pool.  

Notice that this service exposes ports `8080` and `50000` for any pods that match the `selector`. This will expose the Jenkins web UI and builder/agent registration ports within the Kubernetes cluster. Additionally, the `jenkins-ui` services is exposed using a ClusterIP so that it is not accessible from outside the cluster.

### Connect to Jenkins
The Jenkins chart will automatically create an admin password for you. To retrieve it, run:  
`printf $(kubectl get secret cd-jenkins -o jsonpath="{.data.jenkins-admin-password}" | base64 --decode);echo`  

To get to the Jenkins user interface, click on the Web Preview button in cloud shell, then click Preview on port 8080:
![зображення](https://user-images.githubusercontent.com/54221016/111699985-7ad58f00-8841-11eb-8592-edb544973c58.png)


You should now be able to log in with username admin and your auto-generated password.   

You now have Jenkins set up in your Kubernetes cluster! Jenkins will drive your automated CI/CD pipelines in the next sections.

### Understanding the Application
You'll deploy the sample application, `gceme`, in your continuous deployment pipeline. The application is written in the Go language and is located in the repo's sample-app directory. When you run the gceme binary on a Compute Engine instance, the app displays the instance's metadata in an info card.
![зображення](https://user-images.githubusercontent.com/54221016/111700090-9771c700-8841-11eb-934b-22481f83f825.png)
The application mimics a microservice by supporting two operation modes. 
- In **backend** mode: gceme listens on port 8080 and returns Compute Engine instance metadata in JSON format.
- In **frontend** mode: gceme queries the backend gceme service and renders the resulting JSON in the user interface.
![зображення](https://user-images.githubusercontent.com/54221016/111700159-ae181e00-8841-11eb-99cd-eda9a7580942.png)

### Deploying the Application
You will deploy the application into two different environments:
  - Production: The live site that your users access.
  - Canary: A smaller-capacity site that receives only a percentage of your user traffic. Use this environment to validate your software with live traffic before it's released to all of your users.

In Google Cloud Shell, navigate to the sample application directory:  
`cd sample-app`

Create the Kubernetes namespace to logically isolate the deployment:  
`kubectl create ns production`

Create the production and canary deployments, and the services using the `kubectl apply` commands:  
`kubectl apply -f k8s/production -n production`    
`kubectl apply -f k8s/canary -n production`   
`kubectl apply -f k8s/services -n production`   

By default, only one replica of the frontend is deployed. Use the kubectl scale command to ensure that there are at least 4 replicas running at all times.   
Scale up the production environment frontends by running the following command:   
`kubectl scale deployment gceme-frontend-production -n production --replicas 4`

Now confirm that you have 5 pods running for the frontend, 4 for production traffic and 1 for canary releases (changes to the canary release will only affect 1 out of 5 (20%) of users):   
`kubectl get pods -n production -l app=gceme -l role=frontend`

Also confirm that you have 2 pods for the backend, 1 for production and 1 for canary:   
`kubectl get pods -n production -l app=gceme -l role=backend`

Retrieve the external IP for the production services:   
`kubectl get service gceme-frontend -n production`

Now, store the frontend service load balancer IP in an environment variable for use later:   
`export FRONTEND_SERVICE_IP=$(kubectl get -o jsonpath="{.status.loadBalancer.ingress[0].ip}" --namespace=production services gceme-frontend)`

Confirm that both services are working by opening the frontend external IP address in your browser. Check the version output of the service by running the following command (it should read 1.0.0):   
`curl http://$FRONTEND_SERVICE_IP/version`














