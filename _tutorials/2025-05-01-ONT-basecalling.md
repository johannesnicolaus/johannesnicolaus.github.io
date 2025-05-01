---
layout: single
published: false
title: "Tutorial: ONT basecalling on R10 ONT data"
author_profile: true
toc: true
toc_sticky: true
feature_image: "/assets/images/2023-11-07/Logo.svg"
---


I have been working on many ONT data and is super excited for the new R10 flow cells. With the new R10 flow cells, Dorado has models for 6ma calling for this flow cell.

## Prerequisites

Dorado installed in the system

## Step 1: Load required modules

At OIST, the Dorado module is installed under the bioinfo-ugrp-modules.

```shell
module load bioinfo-ugrp-modules Dorado/0.9.0
```

## Step 2: Run basecalling

For some reason, Dorado does not run using GPU other than the v100.



```shell
srun --time 4-0 --mem 16G -p gpu --gres gpu:v100:1 \
        dorado basecaller sup,6mA,5mCG_5hmCG \
        input_pod5 > calls.bam

```
