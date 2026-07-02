---
layout: default
title: Daily
permalink: /daily/
---

<section class="daily-feed">
  <header class="daily-header">
    <h1 class="daily-title">Daily</h1>
    <p class="daily-subtitle">Short notes and half-thoughts. Posted whenever the mood strikes.</p>
  </header>

  {% assign entries = site.daily | sort: 'date' | reverse %}

  {% if entries.size == 0 %}
  <p class="daily-empty">No thoughts yet.</p>
  {% endif %}

  {% for entry in entries %}
  <article class="daily-day">
    <h2 class="daily-day-header">
      <time datetime="{{ entry.date | date: '%Y-%m-%d' }}">{{ entry.date | date: '%B %-d, %Y' }}</time>
    </h2>
    <div class="daily-day-body">
      {{ entry.content | markdownify }}
    </div>
  </article>
  {% endfor %}
</section>
