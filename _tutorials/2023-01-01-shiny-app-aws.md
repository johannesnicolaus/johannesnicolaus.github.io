---
layout: single
published: false
title: "Tutorial: Deploying shiny app on AWS"
author_profile: true
toc: true
toc_sticky: true
feature_image: "/assets/images/2022-04-30/renv-singularity-docker.png"
---

## Introduction

The other day, I was supposed to do calculations to normalize qPCR results generated from Bio-rad qPCR thermocyclers using the Pfaffl method (which I was not familiar at the time). I found out that doing it one by one is very tedious, especially for people in the lab who couldn't write codes. Therefore, I was thinking if I could create a simple shiny app that does exactly that, which are:

1. Read Cq/Ct values, metadata, and primer efficiency CSV files
2. Visualize gene expression using bar plots with error bars
3. Output CSV file containing normalized gene expression data

As the app does not include secret infromation, I made my app public and so I did not add any layer of security for people who want to access the app.

While it shouldn't matter which machine you are working with, steps to access the virtual machine might be slightly different. Here, I am using a unix system.

## 1. Creating a shiny app

Creating a shiny app is straightforward. I have my codes on github: github.com/johannesnicolaus/
I prefer having it on github, which makes it easier to deploy on the server.

## 2. Setting up AWS EC2 server

If you haven't, make an AWS account:
https://aws.amazon.com/premiumsupport/knowledge-center/create-and-activate-aws-account/

From my understanding, usage of the smaller virtual machines are free for the first year, which is the virtual machine I will be using.

### Choose AMI

**PICTURE**

AMI (Amazon Machine Image) is a pre-packaged server containing basic dependencies that are necessary to setup a server. I choose Ubuntu 18.04 LTS here.

### Choose EC2 instance and storage size

**PICTURE**

This EC2 instance will decide how powerful the machine will be. For what I am setting up, I don't need a powerful machine, so I settled for the `t2.micro` which can be used for free on a new account.

**PICTURE**

By default, the space is minimum 8GB, and as I don't need more than that, I left it as it is.

Once this is done, you can launch.

### Generate SSH key pair

Key pair consists of public key on the EC2 instance, and private key that we store. 

Here, we create a new key pair and download the private key. Then, I locate it somewhere I can easily access.

### SSH to EC2 instance

Now we can connect to the instance using SSH.

You can check the command that can be used to connect to the instance


### Install shiny server and required dependencies

Install latest version of Shiny Server from https://www.rstudio.com/products/shiny/download-server/

Run the following codes
```shell
$ sudo apt-get install gdebi-core
$ wget https://download
$ sudo gdebi shiny-server...deb
```

Now, we have a server that contains the default Shiny app.

### Accessing default Shiny App

We need:
1. IP address
2. Open port 3838 on firewall

Firstly, to open port on the firewall

Then, on the EC2 dashboard, IPv4 Public IP is displayed.

To access the 


## 3. Deploying shiny app on AWS server

Now this step can be quite tricky. Firstly we need to clone the github repository and replace the 

### SSH to EC2 instance

### Clone github repository

### Making renv to work

### Other preferences to change

## 4. Making it accessible with google domains

### Notes

There are several directories that will be important here:

- `/srv/shiny-server` Location of the shiny app
- `/var/log/shiny-server` Location of the logs
- `/etc/shiny-server/shiny-server.conf`



## References
I would not have been able to make this tutorial without the following references:
- https://www.charlesbordet.com/en/guide-shiny-aws/#how-to-access-your-new-server
- https://deanattali.com/2015/05/09/setup-rstudio-shiny-server-digital-ocean/#shiny-user-perms