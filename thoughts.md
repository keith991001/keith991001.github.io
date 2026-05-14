---
layout: default
title: Thoughts
permalink: /thoughts/
---

<div class="filter-chips">
  <button class="chip active" data-cat="all">All</button>
  {% for cat in site.thought_categories %}
  <button class="chip" data-cat="{{ cat | downcase | replace: ' ', '-' }}">{{ cat }}</button>
  {% endfor %}
</div>

{% for cat in site.thought_categories %}
{% assign cat_slug = cat | downcase | replace: ' ', '-' %}
{% assign items = site.posts | where: 'category', cat | sort: 'date' | reverse %}
<section class="thought-year-section" data-cat="{{ cat_slug }}">
  <h2 class="thought-year">{{ cat }}</h2>
  {% if items.size > 0 %}
  <ul class="thought-list">
    {% for post in items %}
    {% assign words = post.content | strip_html | number_of_words %}
    {% assign minutes = words | divided_by: 220 | plus: 1 %}
    <li class="thought-card">
      <a class="thought-link" href="{{ post.url | relative_url }}">
        {% if post.cover %}
        <img class="thought-image" src="{{ post.cover | relative_url }}" alt="{{ post.title }}" />
        {% else %}
        <div class="thought-image thought-image-placeholder"></div>
        {% endif %}
        <div class="thought-body">
          <h3 class="thought-title">{{ post.title }}</h3>
          <div class="thought-meta">
            <span>{{ post.date | date: "%-d %B %Y" }}</span>
            <span class="thought-meta-sep">·</span>
            <span>{{ words }} words</span>
            <span class="thought-meta-sep">·</span>
            <span>{{ minutes }} min read</span>
          </div>
        </div>
      </a>
    </li>
    {% endfor %}
  </ul>
  {% else %}
  <p class="section-empty">No thoughts yet.</p>
  {% endif %}
</section>
{% endfor %}

<script>
(function () {
  const chips = document.querySelectorAll('.filter-chips .chip');
  const sections = document.querySelectorAll('.thought-year-section');
  chips.forEach(chip => {
    chip.addEventListener('click', () => {
      chips.forEach(c => c.classList.remove('active'));
      chip.classList.add('active');
      const cat = chip.dataset.cat;
      sections.forEach(s => {
        s.style.display = (cat === 'all' || s.dataset.cat === cat) ? '' : 'none';
      });
    });
  });
})();
</script>
