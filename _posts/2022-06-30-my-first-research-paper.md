---
layout: single
title: "Publishing my first research paper"
author_profile: true
toc: true
toc_sticky: true
feature_image: "/assets/images/"
canonical_url: "https://jnicolaus.com/my-first-research-paper/"
header:
  og_image: "/assets/images/2022-04-17/"
---

After a year long review, my first paper finally got published: link. The paper went through 3 rounds of revision, where I believe that the 3rd round was not really necessary and added ~2 months to the review process. Nevertheless, I'm delighted that the paper is finally published on PLoS Genetics

Just to summarize my paper, it's a study about the transcription factor (TF) NF-kB. This transcription factor translocates to the nucleus upon cell activation, in this case B cell. I visualized the formation of molecular aggregates that occur in the nucleus that involve NF-kB, DNA and other transcription related proteins using fluorescence microscopy, and finally predicted that the generation of enhanced genomic interactions because of this aggregates eventually lead to variability in gene expression.

# The long path to publication

While it may sound straightforward. Reaching the end of this project took quite a bit of time and a lot of trial and error.



## How it all started

It all started when I was an undergrad, looking at labs for my 4th year thesis project. I was told by my former PI that there was a project that involved fluorescence imaging, . Moreover, I also had around a month of free time before the start of my undergraduate research and being involved in this project means that I can do some kind of work at that time. 

This project was very exciting to me as it gives me independence, I was able to do it by myself.

I initially planned to leave Japan at the end of my undergrad, 


### Initial ideas and plans

At first, the project was simple. To investigate what the 

### The discovery and change of ideas

By reading more and more papers, I got several ideas on these aggregates. 

## Things that did not go according to plan

### Software dependencies

Reproducibility has been plagueing bioinformatics research since forever and my limited bioinformatics knowledge at that time was in no way immune to that.

The problem at that time was because of COVID, we had to work from home and I tried to switch to a different high performance computing environment in the middle of my research. I tried to replicate my previous environment including software versions. Here, I tried to use conda,
it turned out to be a disaster as some software actually showed different computational results. While most of the differences were minor, they were large enough to change the outcome of the major genes I was focusing on.

At that time, I learnt everything mostly by myself and certainly no one ever taught me about reproducible research. This is one of the reasons why I chose to move here to OIST, where I'm learning to create reproducible bioinformatics pipelines.

### COVID-19

COVID-19 hindered my progress by quite a bit. Firstly, it was difficult to work from home, while I had a pretty decent PC back then, it was still difficult as it was not as good as the PC at the lab. I also had to access my data remotely, which was not really convenient. However, what was most difficult was the inability to do wet experiments. As at that time I still needed more data, it was quite a hindrance when we were unable to go to the lab for several months.

### Creating a mutant cell line

With the cell line I was using, immunofluorescence (IF) was almost impossible. At that time, I was trying to figure out the co-localization between NF-kB (GFP) and BRD4. At first, we thought we did IF properly and we were able to get decent amount of co-localization between these proteins, but I realized that most of the signal was just autofluorescence of the GFP and thus were artifacts.

Well, that was not good, so I discussed with Prof. Akira Imamoto from Chicago University to ask about creating my own cell line that expresses RFP-tagged BRD4 proteins. I found out that it was not that simple, as it included sooo many steps to confirm that the experiments were not flawed or biased. I firstly needed to design the experiments using cloning software, sequence all the 

In this case, I extracted the gene to be expressed
used the gateway cloning technique to


I actually had some problems along the way as I was using a fairly old reagent and found out that some of the clonings failed multiple times because the efficiency was too low. I'm glad that I was able to solve this problem after using unopened (albeit old) reagents which had fairly higher efficiency.

I also had problems with transfection efficiency, where it was possibly less than 50%. Despite that, I managed to get a single clone after using serial dilution to culture transfected cell on a 96-well plate, it took me more than 3 months in total to finish these experiments.

### Failed CRISPR-Cas9 experiments

As I was predicting DNA-DNA interactions, I wanted to validate if these regions actually behave like how I predicted in-silico. I resorted to using CRISPR-Cas9 to . I was lucky that my lab had connections with Prof. Kawaoka at Kyoto University (currently in Tohoku Univ.). I discussed with him about the strategies needed to remove these putative interacting genomic regions before performing further gene expression validation experiments.

With the experience I had from making cell lines, I was up for the challenge. I was so wrong to think that this time, it was gonna be easier, it never got easier. Firstly, to remove a certain stretch of genomic region, I would need to target 2 different sites of deletion, where the Cas9 proteins can induce double strand break and by chance non-homologous end joining may occur. As I was targeting multiple targets, and that for each target I prepared multiple guide RNAs (gRNA), I ended up with so many combinations of plasmids which I needed to make. This is also caused by the difficulty in transfecting the cell line, which required me to design plasmids that each include 2 different gRNAs, as transfecting 2 different plasmids with single gRNA is too inefficient and is probably statistically almost impossible.

Indeed, while the cloning experiments were relatively optimized and rather easy, it was still very very laborious. Further, I had to get single-cell clones which took weeks, and sometimes the clone only have half of the chromosomes deleted, in which I needed to do another round of selection.

These experiments took me in total almost half a year to complete, only to realize that somehow the cells are not doing well after the deletion of some minor genomic regions. I wasn't even able to induce deletions at some of the regions I targeted. So, the CRISPR-Cas9 experiments were pretty much a failure, but I learned a lot and implemented the techniques to help other people too!

## Review, review and review

We decided to submit the paper

### First revision

After around 2 months, we received the first set of reviews from a total of 2 reviewers. The first reviewer was fairly supportive of our results and only demanded a bit mo. 

Reviewer 2 however, was more critical of the results and demanded quite a bit of further exploration

In general, we were told that the conclusions and results taken over the course of the paper was not conclusive and did not show major "conceptual advance". At this stage, I do agree with the 

Therefore, we decided to do a major revision, where we add new data and perform many new experiments. 

### Submission to PLoS Genetics

As the paper was on Reviewcommons, we were able to submit to a select number of journals. We firstly submitted the paper to another journal, which is actually one of my favorite journals. Unfortunately, it was rejected, as it lacked "conceptual advance". I honestly thought that the editor only looked at the first version of the manuscript and the reviewers' comments and did not really went through the final revisions.

Then, we submitted the paper to PLoS Genetics, which was also a good journal, but I felt like it was a bit out of topic, as my paper wasn't really about genetics. Nevertheless, it went through, and after 2-3 weeks it was under another set of reviews.

The 2nd round of reviews were actually very helpful, as the reviewers pointed out some of the weaknesses in our paper which we agreed. Thus, we added further justifications and analysis, and alter some of the text.

However, what was really annoying was that there was a 3rd round of review, which did not add anything useful to the paper and took us another 1.5 months.

In total, after about a year of the review process, our paper was finally formally accepted. Honestly, it could've been faster.

# Explaining the paper

I will now explain the paper step-by-step, to make it easier for people which are not as well-versed in this field to understand.

## Introduction

Basically, this research builds up on the previous papers by Shinohara et al., and Michida et al. I'm not particularly fond of the latter paper as they tried to use single-cell data as bulk data, where the results are averaged and doesn't capture the actual gene expression dynamics in single-cells. While it is valid and was able to explain the expression dynamics from the macroscopic point of view, I don't think that the data is explored enough.

Therefore, in my research, I aimed to utilize the single-cell data as much as possible, while adding experimental data to validate the results. By investigating the data more intensively, and leveraging the single-cell resolution of the acquired data, I was able to obtain interesting new insights about heterogeneous gene expression. Previously, the analysis was averaged across all of the cells, losing single-cell resolution which is highly important in immune cells such as the B cell.

## Materials and Methods

As explained before, I performed all sorts of experiments along the course of this research.

Firstly, fluorescence imaging experiments and analyses.

Secondly, single-cell RNA-seq

Thirdly, single-cell ATAC-seq



## Results


## Conclusions


# Future prospects

