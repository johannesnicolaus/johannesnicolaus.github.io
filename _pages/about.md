---
title: About me
toc: true
toc_label: On this page
permalink: /
author_profile: true
toc_sticky: true
redirect_from:
  - /about/
  - /about.html
  - /cv/
  - /resume/
---

{% include base_path %}

<p class="page-actions">
  <a href="{{ '/files/cv.pdf' | relative_url }}" class="btn btn--large" target="_blank" rel="noopener noreferrer"><i class="fas fa-download" aria-hidden="true"></i> Download my CV</a>
  <a href="{{ site.author.googlescholar }}" class="btn btn--large btn--inverse" target="_blank" rel="noopener noreferrer"><i class="ai ai-google-scholar" aria-hidden="true"></i> Google Scholar</a>
</p>

I have always been interested in science, especially biology, since I was little. This brought me to Osaka University, where I conducted research on transcription regulation during my undergraduate and master's studies. I have since moved to the Okinawa Institute of Science and Technology in Okinawa, Japan, where I work on the transcriptional regulation of the scrambled genome of _Oikopleura dioica_.

My research combines genomics, single-cell transcriptomics, and epigenomics to understand how gene regulation contributes to the conservation of morphology despite extreme genome rearrangement. I am also trying to build a pangenome for _O. dioica_. I mostly use R, Python, bash, and Nextflow, with a focus on reproducibility, and I build tools for the lab and the wider community — including a genome browser for _O. dioica_ at [oikobrowser.jnicolaus.com](https://oikobrowser.jnicolaus.com) (soon to be migrated to [oikobrowser.com](https://oikobrowser.com)).

In my spare time, I take care of my carnivorous plants, 3D print, watch football, fish, and scuba dive.

## Education

{% include education-list.html %}

## Honors and awards

{% include honors-list.html %}

## Peer review

{% include peer-review-list.html %}

## Research experience

{% include experience-list.html data=site.data.experience %}

## Workshops attended

{% include workshop-list.html %}

## Organizational experience

{% include experience-list.html data=site.data.organizations %}
