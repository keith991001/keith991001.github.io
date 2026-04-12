---
layout: default
title: Bookmarks
permalink: /bookmarks/
---

<div class="page-header">
  <h1>Bookmarks</h1>
  <p>Useful websites and resources I've collected.</p>
</div>

<div class="bookmark-grid">

{% for bookmark in site.bookmarks %}
<div class="bookmark-card">
  <h3><a href="{{ bookmark.url_link }}">{{ bookmark.title }}</a></h3>
  {% if bookmark.tags %}
  <div>
    {% for tag in bookmark.tags %}
    <span class="tag">{{ tag }}</span>
    {% endfor %}
  </div>
  {% endif %}
  {% if bookmark.description %}
  <p>{{ bookmark.description }}</p>
  {% endif %}
</div>
{% endfor %}

</div>

{% if site.bookmarks.size == 0 %}
<p style="color: #7f8c8d; text-align: center; padding: 3rem 0;">No bookmarks yet. Add your first one!</p>
{% endif %}
