---
layout: default
title: Bookmarks
permalink: /bookmarks/
---

<div class="filter-chips">
  <button class="chip active" data-cat="all">All</button>
  {% for cat in site.bookmark_categories %}
  <button class="chip" data-cat="{{ cat | downcase | replace: ' ', '-' }}">{{ cat }}</button>
  {% endfor %}
</div>

{% for cat in site.bookmark_categories %}
{% assign cat_slug = cat | downcase | replace: ' ', '-' %}
{% assign items = site.bookmarks | where: 'category', cat %}
<section class="bookmark-section" data-cat="{{ cat_slug }}">
  <h2>{{ cat }}</h2>
  {% if items.size > 0 %}
  <ul class="bookmark-list">
    {% for bm in items %}
    <li class="bookmark-card bookmark-{{ cat_slug }}">
      <a class="bookmark-link" href="{{ bm.url_link }}" target="_blank" rel="noopener noreferrer">
        <span class="bookmark-title">{{ bm.title }}</span>
        {% if bm.description %}
        <span class="bookmark-desc">{{ bm.description }}</span>
        {% endif %}
      </a>
    </li>
    {% endfor %}
  </ul>
  {% else %}
  <p class="section-empty">No bookmarks yet.</p>
  {% endif %}
</section>
{% endfor %}

<script>
(function () {
  const chips = document.querySelectorAll('.filter-chips .chip');
  const sections = document.querySelectorAll('.bookmark-section');
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
