---
published: true
date: '2019-11-04'
title: "Tutorial: TPM calculation with library size normalization"
toc: true
excerpt: "Calculating transcripts per million (TPM) from raw RNA-seq counts in R, with library size normalization using edgeR."
redirect_from:
  - /tutorials-old/tpm_calculation.html
---

This tutorial covers transcripts per million (TPM) calculation with library size
normalization using edgeR. It was originally written in December 2019 for the
Laboratory of Cell Systems, Institute for Protein Research, Suita, Osaka, Japan.

## Setting up

Load the libraries we need.

```r
library(tidyverse)
library(data.table)
library(edgeR)
```

Read the raw counts table. This example uses a `featureCounts` output.

```r
counts <- read_csv(file = "D:/lab_rmd/tpm/counts_trimmed.csv")
head(counts)
```

```
## # A tibble: 6 x 10
##   Geneid          Chr               Start          End            Strand  Length B00_A01 B00_A02 B00_A03 B00_A04
##   <chr>           <chr>             <chr>          <chr>          <chr>    <dbl>   <dbl>   <dbl>   <dbl>   <dbl>
## 1 ENSGALG0000005… 1;1;1;1;1;1;1;1;… 5273;5273;55…  5524;5524;59…  -;-;-;…   2018       0       0       0       0
## 2 ENSGALG0000005… 1;1;1;1;1         9441;9681;97…  10053;9683;1…  +;+;+;…   4754       0       0       0       0
## 3 ENSGALG0000004… 1;1;1;1;1         27209;32230;…  27503;32331;…  +;+;+;…    955     105      73      35      42
## 4 ENSGALG0000005… 1;1;1;1;1         31439;32230;…  31484;32331;…  +;+;+;…   1050     285     220     124     230
## 5 ENSGALG0000004… 1;1;1;1;1;1;1;1;1 39057;39080;…  39867;39867;…  -;-;-;…   2161     224     138     134     178
## 6 ENSGALG0000004… 1                 58427          58617          +          191       0       0       0       0
```

## Keeping only what we need

Remove `Chr`, `Start`, `End` and `Strand`. We only keep the gene ID, the gene
length and the sample columns.

```r
counts <- counts[, !colnames(counts) %in% c("Chr", "Start", "End", "Strand")]
head(counts)
```

```
## # A tibble: 6 x 6
##   Geneid             Length B00_A01 B00_A02 B00_A03 B00_A04
##   <chr>               <dbl>   <dbl>   <dbl>   <dbl>   <dbl>
## 1 ENSGALG00000054818   2018       0       0       0       0
## 2 ENSGALG00000053455   4754       0       0       0       0
## 3 ENSGALG00000045540    955     105      73      35      42
## 4 ENSGALG00000051297   1050     285     220     124     230
## 5 ENSGALG00000042023   2161     224     138     134     178
## 6 ENSGALG00000047594    191       0       0       0       0
```

## Normalizing by gene length

Divide each sample's read count by the gene length, then multiply by 1000. This
gives the reads per kilobase (RPK).

```r
counts_tpm <- (counts[, 3:ncol(counts)] / counts$Length) * 1000

# return to a tibble, just because I like tibbles
counts_tpm <- cbind(Geneid = counts$Geneid, counts_tpm) %>% as_tibble()
```

## Getting the normalization factor

Here we use RLE, but you can change the method to whichever edgeR supports.

```r
normfactor <- DGEList(
  counts = counts_tpm[, 2:ncol(counts_tpm)],
  group  = colnames(counts_tpm[, 2:ncol(counts_tpm)])
)

# you can change the normalization method here
normfactor <- calcNormFactors(normfactor, method = "RLE")

normfactor_samples <- normfactor$samples

# multiply normalization factor with the library size
normfactor_samples$normlib <- normfactor_samples$lib.size * normfactor_samples$norm.factors
```

## Final TPM table

Loop over the samples and scale to per-million.

```r
for (i in 1:(dim(counts_tpm)[2] - 1)) {
  counts_tpm[, i + 1] <- (counts_tpm[, i + 1] / normfactor_samples$normlib[i]) * 1000000
}

head(counts_tpm)
```

```
## # A tibble: 6 x 5
##   Geneid             B00_A01 B00_A02 B00_A03 B00_A04
##   <fct>                <dbl>   <dbl>   <dbl>   <dbl>
## 1 ENSGALG00000054818     0       0       0       0
## 2 ENSGALG00000053455     0       0       0       0
## 3 ENSGALG00000045540    54.6    49.4    37.3    33.1
## 4 ENSGALG00000051297   135.    135.    120.    165.
## 5 ENSGALG00000042023    51.5    41.3    63.1    61.9
## 6 ENSGALG00000047594     0       0       0       0
```
