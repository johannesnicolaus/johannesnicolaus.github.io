---
permalink: /
title: "About me"
author_profile: true
toc: true
toc_sticky: true
toc_label: "On this page"
redirect_from:
  - /about/
  - /about.html
  - /cv/
  - /resume/
  - /publications/
  - /talks/
  - /teaching/
---

{% include base_path %}

<p class="page-actions">
  <a href="{{ '/files/cv.pdf' | relative_url }}" class="btn btn--large" target="_blank" rel="noopener noreferrer"><i class="fas fa-download" aria-hidden="true"></i> Download my CV</a>
  <a href="{{ site.author.googlescholar }}" class="btn btn--large btn--inverse" target="_blank" rel="noopener noreferrer"><i class="ai ai-google-scholar" aria-hidden="true"></i> Google Scholar</a>
</p>

I have always been interested in science, especially biology, since I was little. This brought me to Osaka University, where I was able to do research on transcription regulation for my undergraduate and master's thesis. I have since moved to the Okinawa Institute of Science and Technology in Okinawa, Japan, where I work on the transcriptional regulation of the scrambled genome of *Oikopleura dioica*.

My research combines genomics, single-cell transcriptomics and epigenomics to understand how gene regulation is conserved despite extreme genome rearrangement. I mostly use R, Python, bash and Nextflow, with a focus on reproducibility, and I build tools for the lab and the wider community — including a genome browser for *O. dioica* at [oikobrowser.jnicolaus.com](https://oikobrowser.jnicolaus.com).

In my spare time, I take care of my carnivorous plants, 3D print, watch football, fish and scuba dive.

## Education

{% include education-list.html %}

## Publications

{% include publication-list.html category="research" heading="Research articles" %}

{% include publication-list.html category="review" heading="Review articles" %}

{% include publication-list.html category="chapter" heading="Book chapters" %}

## Conference presentations

{% include talk-list.html scope="international" heading="International" %}

{% include talk-list.html scope="domestic" heading="Domestic" %}

## Honours and awards

{% include honors-list.html %}

## Research experience

{% include experience-list.html data=site.data.experience %}

## Teaching and training

{% include teaching-list.html %}

## Workshops attended

{% include workshop-list.html %}

## Organizational experience

{% include experience-list.html data=site.data.organizations %}
