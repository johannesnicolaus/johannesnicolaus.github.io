---
layout: archive
title: "Publications"
permalink: /publications/
author_profile: true
---

{% if site.author.googlescholar %}
<div class="wordwrap">You can also find my articles on <a href="{{ site.author.googlescholar }}">my Google Scholar profile</a>.</div>
{% endif %}

{% include base_path %}

{% include publication-list.html category="research" heading="Research papers" %}

{% include publication-list.html category="review"   heading="Review articles" %}

{% include publication-list.html category="chapter"  heading="Book chapters" %}
