---
layout: default
title: Projects
permalink: /projects/
---

<ul class="project-list">
{% assign sorted = site.projects | sort: "year" | reverse %}
{% for p in sorted %}
<li class="project-card">
  {% if p.image %}
  <img class="project-image" src="{{ p.image | relative_url }}" alt="{{ p.title }}" />
  {% endif %}
  <div class="project-body">
    <div class="project-header">
      <span class="project-title">{{ p.title }}</span>
      {% if p.year %}<span class="project-year">{{ p.year }}</span>{% endif %}
    </div>
    {% if p.description %}
    <p class="project-desc">{{ p.description }}</p>
    {% endif %}
    {% if p.tags %}
    <p class="project-tags">
      {% for t in p.tags %}<span class="project-tag">{{ t }}</span>{% endfor %}
    </p>
    {% endif %}
    <p class="project-links">
      {% if p.demo_url %}
      <a href="{{ p.demo_url }}" target="_blank" rel="noopener noreferrer">Live Demo →</a>
      {% endif %}
      {% if p.repo_url %}
      <a href="{{ p.repo_url }}" target="_blank" rel="noopener noreferrer">Source ↗</a>
      {% endif %}
    </p>
  </div>
</li>
{% endfor %}
</ul>

{% if site.projects.size == 0 %}
<p style="color: #888; padding: 3rem 0;">No projects yet.</p>
{% endif %}
