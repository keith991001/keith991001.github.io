---
layout: default
title: Bookmarks
permalink: /bookmarks/
---

{% assign grouped = site.bookmarks | group_by: "category" | sort: "name" %}

{% for group in grouped %}
<section class="bookmark-section">
  <h2>{% if group.name == "" %}Other{% else %}{{ group.name }}{% endif %}</h2>
  <ul class="bookmark-list">
    {% for bm in group.items %}
    <li class="bookmark-card bookmark-{{ bm.category | downcase | replace: ' ', '-' | default: 'other' }}">
      <a class="bookmark-link" href="{{ bm.url_link }}" target="_blank" rel="noopener noreferrer">
        <span class="bookmark-title">{{ bm.title }}</span>
        {% if bm.description %}
        <span class="bookmark-desc">{{ bm.description }}</span>
        {% endif %}
      </a>
    </li>
    {% endfor %}
  </ul>
</section>
{% endfor %}

{% if site.bookmarks.size == 0 %}
<p style="color: #888; padding: 3rem 0;">No bookmarks yet.</p>
{% endif %}
