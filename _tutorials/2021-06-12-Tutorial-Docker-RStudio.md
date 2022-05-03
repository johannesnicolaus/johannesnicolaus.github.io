---
layout: single
title: "Tutorial: Running RStudio using Docker for smoother collaboration"
author_profile: true
toc: true
toc_sticky: true
feature_image: "/assets/images/2021-06-12/rstudio-docker.png"
---

Sometimes, it is hard to replicate the same environment when you are collaborating in a project. Sometimes you might not want to downgrade some of the packages that you got installed in your system to replicate someone else's system. In this case, you might want to use Docker, which can give you an isolated environment to run your applications, in a way, it is similar to conda.

---

# What is Docker?

Essentially, Docker serves similar to a virtual machine (VM)

The term **Image** and **Container** got me confused avt first, and therefore I'd like to briefly introduce them. In short, Image consists of the packages/apps and the enironment required by the application to run. On the other hand, a container is a running instance of the image, which consists of the image and whatever other files you have inside.

![concept](/assets/images/2021-06-12/rstudio-docker.png)

---

# Prerequisites

- A Windows local system
- Internet

In this tutorial, I will be showing how to to the following workflow using Windows with WSL2 installed.

---

# Workflow

1. Installing Docker
2. Enabling file sharing with host (Optional if you want to access files in your disk)
3. Building a Docker Image
   1. Creating a Dockerfile and building an image
   2. Tips on not wasting your time troubleshooting building an image
   3. (Optional) Uploading your image to Dockerhub and pulling from Dockerhub instead of building image
4. Running a Docker container

---

# Procedures

## 1. Installing Docker
You can install Docker for Desktop from the following website
<https://docs.docker.com/get-docker/>

After finished downloading, just follow the instructions to install Docker for desktop.


## 2. Enabling file sharing with host (Optional if you want to access files in your disk)

Because in my case, I would like to access files that are present on the local disk, I needed to enable file sharing between Docker and the host.

To do this, you would need to open Docker Desktop, go to settings and select Resources > File sharing, where you can choose a specific directory to enable file share. If you don't see the option, go to General an uncheck the option "Use the WSL 2 based engine". Afterwards, you will be prompted to restart Docker and then you should be able to enable file sharing.


## 3. Building a Docker image


### Creating a Dockerfile and building an image

Dockerfile is a file that is similar to a Singularity definition file. It contains all the commands needed to build a image, including installation of packages and other things you want to have in your image. This file will come in handy as you can 

Below is an example Dockerfile that I used to build my RStudio image. This will be placed on the root of the directory we will be working on.

```shell
# Base image https://hub.docker.com/u/rocker/
FROM rocker/rstudio:4.0.4

RUN apt-get install -y \
  libcurl4-openssl-dev \
  libcairo2-dev \
  build-essential

## Install extra R packages using requirements.R
## Specify requirements as R install commands e.g.
## 
## install.packages("") or
## devtools::install("SymbolixAU/googleway")
RUN Rscript ./requirements.R

```

Now let me explain what's going on here. Firstly, we pull a base image using the command `FROM`, in this case, I am pulling an image that contains R and Rstudio 4.0.4. 

Then, the commands beginning with `RUN` are the commands you would normally execute on your terminal. In order to install some R packages, you would need to run R commands using the `Rscript` command.

Now, if you want to add R packages, you would normally need to install them using `install.packages()`. Here, we are going to make a `.R` file consisting of the commands needed for the installation of packages. In this case it is the `requirements.R` file placed in root. This file will then be run using the `Rscript` command.

With the Dockerfile setup, you can now build the image. Open powershell at the directory and run the following:

```shell
docker build .
```



### How to not waste your time on troubleshooting

Sometimes when you build images you get tons of error because of dependencies and whatnot, and in that case I would recommend you making a minimal image without a lot of packages. For example, you could start with the following:

```shell
# Base image https://hub.docker.com/u/rocker/
FROM rocker/rstudio:4.0.4
```

Then, you could run the container interactively:
```shell
docker run --rm -it testimage
```

After you get inside the container, you can install packages just like you would normally in the terminal (remember to take notes on what you installed). By doing so, you can test if your wanted packages will run while skipping the building step over and over again. After you managed to run all the packages you wanted, just reiterate all the steps you did interactively in the Dockerfile.


### Uploading an image to Dockerhub

Dockerhub is a cloud storage service for Docker images. It is nice when you want to share Docker images to other people as its usage is as simple as Github.

Firstly, you would need to setup an account at <https://hub.docker.com>. Then, you need to create a repository, for example we'll make a repository with the name test-repository.

Then, we want to push the image to the repository, you would firstly need to check the images that you have installed on your system.

```shell
docker images
```

Next, we need to specify a tag to push and push it to the repo (in this case latest)

```shell
docker tag testimage:latest username/test-repository:latest
docker push username/test-repository:latest
```

### Pulling an image from repository
Alternatively, you can pull an image from a repository and skip the building step. 

```shell
docker pull username/test-repository:latest
```

## 4. Running docker image

Now that you have your docker image, you just need to run it. To run it, you have to execute the following command on the terminal:

```shell
docker run --rm -v d:/directory:/local_dir -p 8888:8787 -d --name rstudio_server -e PASSWORD=password username/test-repository
```

Firstly, `--rm` flag indicates that the container will be deleted after the container is stopped. Then, `-v` is an argument used when you want to bind mount a directory in the host system, in this case the directory `d:/directory` will be bound to the directory `/local_dir` in the container. Then, `-p` specifies the port, `-d` runs the container in the background, `--name` specifies the container name and the `-e` are the environment variables which will be read by RStudio.

Once the container is run, you can run RStudio by opening your browser and accessing `localhost:8888` and you will be greeted by the RStudio server welcome screen. There you can input your username (defaults to "rstudio"), and the password (here we set it as "password"). You should be able to login to the RStudio server and access the files, however if no files are shown in the panel on the right hand side, you might want to press on the triple dot button on the right and set the path to `/` which is the root.


In the end, I'm still very new on this Docker thing and is currently trying to understand more, so this article might get updated when I understand more about new things.

# References

- <https://towardsdatascience.com/an-r-docker-hello-world-example-881e771214e2>
- <https://davetang.org/muse/2021/04/24/running-rstudio-server-with-docker/>
- <https://github.com/rocker-org/rocker/wiki/Sharing-files-with-host-machine>
- <https://rominirani.com/docker-on-windows-mounting-host-directories-d96f3f056a2c>
