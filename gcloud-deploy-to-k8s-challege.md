### 1.Create a Docker image and store the Dockerfile

Now we have to clone the valkyrie-app source code repository in our project.   
Then, run the commands below to clone it in your project.{Replace YOUR_PROJECT with your Project ID}  

    gcloud source repos clone valkyrie-app --project=YOUR_PROJECT
    
Create a Dockerfile under the valkyrie-app directory and add the configuration to the file. Copy the command below and run it on the cloud shell.

    cd valkyrie-app
    cat > Dockerfile <<EOF  
    FROM golang:1.10
    WORKDIR /go/src/app
    COPY source .
    RUN go install -v
    ENTRYPOINT ["app","-single=true","-port=8080"]
    EOF

We have created an Image Now we have to build by command.

    docker build -t valkyrie-app:v0.0.1 .

### 2. Test the created Docker image

Now we have to test our Docker Image built-in task 1 and show the running application by Web Preview on port 8080. Write a command on Cloud Shell

  cd ..
  cd valkyrie-app
  docker run -p 8080:8080 valkyrie-app:v0.0.1 

### 3.Push the Docker image in the Container Repository

In this task, you will push the Docker image valkyrie-app:v0.0.1 into the Container Registry.
Make sure you re-tag the container to gcr.io/YOUR_PROJECT/valkyrie-app:v0.0.1.{replace YOUR_PROJECT with your Project ID}

    cd ..
    cd valkyrie-app
    docker tag valkyrie-app:v0.0.1 gcr.io/$GOOGLE_CLOUD_PROJECT/valkyrie-app:v0.0.1docker push gcr.io/$GOOGLE_CLOUD_PROJECT/valkyrie-app:v0.0.1

### 4.Create and expose a deployment in Kubernetes

In the Cloud Shell, go to the valkyrie-app/k8s subdirectory.
To check the Kubernetes credentials before you deploy the image onto the Kubernetes cluster.

gcloud container clusters get-credentials valkyrie-dev -- zone us-east1-d

Now we have to and replace IMAGE_HERE with

    sed -i s#IMAGE_HERE#gcr.io/$GOOGLE_CLOUD_PROJECT/valkyrie-app:v0.0.1#g k8s/deployment.yaml

    gcr.io/YOUR-PROJECT-ID/valkyrie-app:v0.0.1

in deployment.yaml through text editor.

Deploy deployment.yaml and service.yaml

    gcloud container clusters get-credentials valkyrie-dev --zone us-east1-dkubectl create -f k8s/deployment.yamlkubectl create -f k8s/service.yaml

### 5.Update the deployment with a new version of valkyrie-app

Now we have to do two steps we will go one by one.

Increase the replicas from 1 to 3

    git merge origin/kurt-devkubectl edit deployment valkyrie-dev

2. Build and push the new version

    docker build -t gcr.io/$GOOGLE_CLOUD_PROJECT/valkyrie-app:v0.0.2 .docker push gcr.io/$GOOGLE_CLOUD_PROJECT/valkyrie-app:v0.0.2

Trigger a rolling update by running the following command:

    kubectl edit deployment valkyrie-dev

Save and Exit. Make sure you replaced as version from v0.0.1 . to v0.0.2 .
### 6.Create a pipeline in Jenkins to deploy your app

In this task, we have to do Continuous Delivery with Jenkins in Kubernetes Engine

To connect the Jenkins

Get the password with the following command:

    printf $(kubectl get secret cd-jenkins -o jsonpath="{.data.jenkins-admin-password}" | base64 --decode);echo

2.Connect to the Jenkins console using the commands below:

    export POD_NAME=$(kubectl get pods --namespace default -l "app.kubernetes.io/component=jenkins-master" -l "app.kubernetes.io/instance=cd" -o jsonpath="{.items[0].metadata.name}")

If there is another running container, use the docker commands below to kill it

    docker ps
    docker kill container_id

Click on the Web Preview button in the cloud shell, then click “Preview on port 8080” to connect to the Jenkins console.

    kubectl port-forward $POD_NAME 8080:8080 >> /dev/null &printf $(kubectl get secret cd-jenkins -o jsonpath="{.data.jenkins-admin-password}" | base64 --decode);echo

Open web-preview and login as admin with password from last command
Go to click credentials -> Jenkins -> Global Credentials
Go to Click add credentials
Select Google Service Account from metadata
Click ok

Creating the Jenkins job on top left

Click new item
Name valkyrie-app to Multibranch Pipeline option and click OK.
Now go to the next page, in the Branch Sources section, click Add Source and select git.
Paste the HTTPS clone URL of your sample-app repo in Cloud Source Repositories https://source.developers.google.com/p/YOUR_PROJECT/r/valkyrie-app into the Project Repository field.
Set credentials to qwiklabs and Click on ok
We can change color by following Command

    sed -i "s/green/orange/g" source/html.go

Update project in Jenkinsfile

    sed -i "s/YOUR_PROJECT/$GOOGLE_CLOUD_PROJECT/g" Jenkinsfilegit config --global user.email "you@example.com"git config --global user.name "student"git add .git push origin master

{Replace YOUR_PROJECT with your Project ID}
