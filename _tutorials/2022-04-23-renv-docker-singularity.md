---
layout: single
title: "Tutorial: Docker and singularity image containing R and Renv for package version control"
author_profile: true
toc: true
toc_sticky: true
feature_image: "/assets/images/2022-04-30/renv-singularity-docker.png"
---

Renv is a package manager for R, by using Renv, it is possible to control the exact versions of R packages used within a project. In this project, I wanted to create a singularity image where I can control the R version, and have fixed package dependencies versions. Note that using the R command `install.packages()` will install the newest version of a certain package, and thus for reproducibility purposes I'm using Renv. The ultimate goal is to have a singularity image to be run on an HPC cluster, which contains a custom R 
package and an R script that can be run through command line interface.

Basically, here are the list of things I wanted to do:

- Create a custom R package for my analysis hosted on github with package control using Renv
- Create an executable R script within the R package that can be executed from the terminal
- Make the Renv cache (library) visible to R wherever R is run from
- Package them into a docker and singularity container

While using Renv with docker is somewhat documented, I had a problem with making the Renv environment visible from outside the project (github repo folder). Fortunately, I was able to fix this by following the 2nd answer to this stackoverflow post: [link](https://stackoverflow.com/questions/66311017/rscript-to-use-renv-environment).

Nevertheless, while this fixed the problem with docker, there are still some other problems when converting it to a singularity image as follows:

Here are the main problems:

## 1. `$HOME` problem with `.Renviron` in singularity

In docker, the `$HOME` directory is within the image itself, and thus editing the `.Renviron` file is ok:

```shell
RUN echo $(cd $RENV_DIR && Rscript -e "cat(paste0('R_LIBS=', renv::paths\$library()), sep = '\n')") >> $HOME/.Renviron
```

However, in a singularity image, the `$HOME` variable refers to the host `$HOME` directory and thus doing this does not work.

## 2. Permission problem

While I'm not 100% sure if this step is necessary, it doesn't do any harm.

By default the renv library is located in a directory that requires root permission to access. While it is readable in Docker, it is not in Singularity.

# How I managed to solve the problem

I managed to find a workaround by moving the renv symlink library, which has the same structure as a normal R library, but contains the symlink to a particular version of the package in the renv library (cache).

## 1. Understanding Renv directory structure

The default R library only supports installation of one package version. Renv alleviates this problem by having a separate library (termed cache) which can include multiple different versions of a certain package. However, as R does not suppor this, Renv gets around this limitation by having a "library" for each project that contains symlink to a specific version of a certain project. This symlink library is structured identical to default R library directory.

More details here: [link](https://rstudio.github.io/renv/articles/renv.html)

## 2. Completed docker recipe

For people who are advanced enough to understand the complete Dockerfile, below is my working Dockerfile. If you are not familiar with the processes, you might want to look at the next section.

```Dockerfile
FROM rocker/r-base:4.1.3

# set work directory
WORKDIR /opt

# Install libraries required for R packages
RUN apt update && \
    apt install -y libxml2-dev \
    libcurl4-openssl-dev \
    libssl-dev \
    libfftw3-dev \
    libtiff-dev \
    libgsl-dev \
    git

# set argument for git access token
ARG GIT_ACCESS_TOKEN
ENV GITHUB_PAT ${GIT_ACCESS_TOKEN}

# set git credentials
RUN git config --global credential.helper \
  '!f() { echo username=author; echo "password=${GIT_ACCESS_TOKEN}"; };f'

# Install renv
ENV RENV_VERSION 0.15.4
RUN R -e "install.packages('remotes', repos = c(CRAN = 'https://cloud.r-project.org'))" && \
  R -e "remotes::install_github('rstudio/renv@${RENV_VERSION}')"

# Add ENV variables for Renv cache (not symlink)
RUN mkdir /opt/renvcache && \
 echo RENV_PATHS_CACHE='/opt/renvcache' >> $(R RHOME)/etc/Renviron.site

# set the project directory to a variable
ENV RENV_DIR='/opt/PACKAGE_REPO_NAME'

# clone repo, install additional packages outside of renv and move symlinks
RUN git clone https://github.com/username/PACKAGE_REPO_NAME.git && \
  cd PACKAGE_REPO_NAME && \
  R -e 'renv::restore()' && \
  Rscript -e 'install.packages("ADDITIONAL_PACKAGES")' && \
  R CMD INSTALL . && \
  chmod +x /opt/PACKAGE_REPO_NAME/inst/*.R && \
  mv $(cd $RENV_DIR && Rscript -e "cat(paste0(renv::paths\$library()))") /opt/Rlibsymlinks && \
  echo "R_LIBS=/opt/Rlibsymlinks" >> $(R RHOME)/etc/Renviron.site

# set environment variables for R scripts within package
ENV PATH=/opt/PACKAGE_REPO_NAME/inst:$PATH

```

## Explanation of the docker recipe

Here I'm' going to explain the Dockerfile step-by-step.

### initialization

Pull R base image from rocker. Ideally, the R version should be the same with the system where you created your package and thus the `renv.lock` file.

```Dockerfile
FROM rocker/r-base:4.1.3
```

Set work directory to `/opt`, and thus subsequent `RUN` commands will be run from within the `/opt` directory.

```Dockerfile
WORKDIR /opt
```

Install required libraries for R packages and also git as we will be downloading the package from github.

```Dockerfile
RUN apt update && \
    apt install -y libxml2-dev \
    libcurl4-openssl-dev \
    libssl-dev \
    libfftw3-dev \
    libtiff-dev \
    libgsl-dev \
    git
```

Set github PAT (Personal Access Token) that can be passed as an argument when building the image.

```Dockerfile
ARG GIT_ACCESS_TOKEN
ENV GITHUB_PAT ${GIT_ACCESS_TOKEN}

RUN git config --global credential.helper \
  '!f() { echo username=author; echo "password=${GIT_ACCESS_TOKEN}"; };f'
```

### Initialize renv

Install renv from github, specifying the exact version.

```Dockerfile
ENV RENV_VERSION 0.15.4
RUN R -e "install.packages('remotes', repos = c(CRAN = 'https://cloud.r-project.org'))" && \
  R -e "remotes::install_github('rstudio/renv@${RENV_VERSION}')"

```

Set default renv library cache to `/opt/renvcache` by setting the `RENV_PATHS_CACHE` variable to `/etc/Renviron.site`. The `Renviron.site` file will be read by R when running.

```Dockerfile
# Add ENV variables for Renv cache (not symlink)
RUN mkdir /opt/renvcache && \
 echo RENV_PATHS_CACHE='/opt/renvcache' >> $(R RHOME)/etc/Renviron.site

```

### Cloning package from github and installing additional packages

To explain the steps here:

- Set `RENV_DIR`, which is a bash variable for the project directory.
- `git clone` to clone the project repository.
- `cd` to enter the project repository directory.
- `R -e 'renv::restore()'` to restore the packages from the `renv.lock` file at the top level of the project directory.
- `R CMD INSTALL .` to install the package contained in the repository itself.
- `chmod +x /opt/PACKAGE_REPO_NAME/inst/*.R` to set the R scripts to be run from shell as executables. Keep in mind that I have put these scripts in the `inst` directory located at the top level of the repository. I used `optparse` to parse arguments for this scripts.
- `mv $(cd $RENV_DIR && Rscript -e "cat(paste0(renv::paths\$library()))") /opt/Rlibsymlinks &&` to move the renv symlink library to the directory `/opt/Rlibsymlinks`.
- `echo "R_LIBS=/opt/Rlibsymlinks" >> $(R RHOME)/etc/Renviron.site` to make the symlink library generated by renv visible to R, wherever it is run from.

```Dockerfile
ENV RENV_DIR='/opt/PACKAGE_REPO_NAME'

RUN git clone https://github.com/username/PACKAGE_REPO_NAME.git && \
  cd PACKAGE_REPO_NAME && \
  R -e 'renv::restore()' && \
  Rscript -e 'install.packages("ADDITIONAL_PACKAGES")' && \
  R CMD INSTALL . && \
  chmod +x /opt/PACKAGE_REPO_NAME/inst/*.R && \
  mv $(cd $RENV_DIR && Rscript -e "cat(paste0(renv::paths\$library()))") /opt/Rlibsymlinks && \
  echo "R_LIBS=/opt/Rlibsymlinks" >> $(R RHOME)/etc/Renviron.site
```

### Add custom R scripts to the PATH environment variable

The following command adds the R scripts located within the `inst` directory to the PATH environment variable.

```Dockerfile
ENV PATH=/opt/PACKAGE_REPO_NAME/inst:$PATH
```

## Command to build image

```shell
docker build --build-arg GIT_ACCESS_TOKEN=YOUR_ACCESS_TOKEN -t username/imgname:tag . && docker push username/imgname:tag
```

and that's it, the docker image can then be pushed to dockerhub and pulled as a singularity image using `singularity pull docker://username/repo:tag`.