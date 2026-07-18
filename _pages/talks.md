---
layout: archive
title: "Talks and presentations"
permalink: /talks/
author_profile: true
---

{% include base_path %}

{% if site.talkmap_link == true %}
<p style="text-decoration:underline;"><a href="{{ base_path }}/talkmap.html">See a map of all the places I've given a talk!</a></p>
{% endif %}

{% include talk-list.html type="oral"   heading="Oral presentations" %}

{% include talk-list.html type="poster" heading="Poster presentations" %}
