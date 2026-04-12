---
layout: default
title: Thoughts
permalink: /thoughts/
---

<div class="page-header">
  <h1>Thoughts</h1>
  <p>Notes, ideas, and reflections.</p>
</div>

<ul class="post-list">
{% for post in site.posts %}
  <li>
    <span class="post-date">{{ post.date | date: "%B %d, %Y" }}</span>
    <div class="post-title"><a href="{{ post.url | relative_url }}">{{ post.title }}</a></div>
    {% if post.excerpt %}<p style="color: #7f8c8d; font-size: 0.9rem;">{{ post.excerpt | strip_html | truncatewords: 30 }}</p>{% endif %}
  </li>
{% endfor %}
</ul>

{% if site.posts.size == 0 %}
<p style="color: #7f8c8d; text-align: center; padding: 3rem 0;">No thoughts yet. Start writing!</p>
{% endif %}
