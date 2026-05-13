---
layout: default
title: About
---

<header class="about-hero">
  <h1>Ke Yu</h1>
  <p class="about-tagline">Software Engineer at GMO Pepabo</p>
  <p class="about-contact">
    <a href="mailto:keith991001@gmail.com" aria-label="Email" title="keith991001@gmail.com">
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
        <rect x="3" y="5" width="18" height="14" rx="2"/>
        <path d="m3 7 9 6 9-6"/>
      </svg>
    </a>
    <a href="https://github.com/keith991001" target="_blank" rel="noopener noreferrer" aria-label="GitHub" title="GitHub">
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
        <path d="M15 22v-4a4.8 4.8 0 0 0-1-3.5c3 0 6-2 6-5.5.08-1.25-.27-2.48-1-3.5.28-1.15.28-2.35 0-3.5 0 0-1 0-3 1.5-2.64-.5-5.36-.5-8 0C6 2 5 2 5 2c-.3 1.15-.3 2.35 0 3.5A5.403 5.403 0 0 0 4 9c0 3.5 3 5.5 6 5.5-.39.49-.68 1.05-.85 1.65-.17.6-.22 1.23-.15 1.85v4"/>
        <path d="M9 18c-4.51 2-5-2-7-2"/>
      </svg>
    </a>
    <a href="https://www.linkedin.com/in/yuke991001" target="_blank" rel="noopener noreferrer" aria-label="LinkedIn" title="LinkedIn">
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
        <path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-4 0v7h-4v-7a6 6 0 0 1 6-6z"/>
        <rect x="2" y="9" width="4" height="12"/>
        <circle cx="4" cy="4" r="2"/>
      </svg>
    </a>
  </p>
</header>

<section class="about-bio">
  <div class="bio-text">
    <p>I'm a software engineer at GMO Pepabo. I recently completed my Master of Engineering in System Innovation at The University of Tokyo, with an undergraduate background in Electronic Business from Zhejiang Gongshang University. My research has focused on synthetic tabular data generation guided by knowledge graphs and large language models, and on multimodal data fusion for object detection.</p>
    <p>Before joining Pepabo, I interned as a data scientist at Quollio Technologies, building graph-based data networks for lineage tracking and natural-language-to-SQL pipelines. I'm interested in bridging cutting-edge AI research with practical software engineering.</p>
  </div>
  <img class="bio-photo" src="{{ '/assets/images/profile.jpg' | relative_url }}" alt="Ke Yu" />
</section>

<section class="about-skills">
  <div class="skill-row">
    <span class="skill-label">Languages</span>
    <span class="skill-list">Chinese (native), English, Japanese</span>
  </div>
  <div class="skill-row">
    <span class="skill-label">Programming</span>
    <span class="skill-list">Python, Java, SQL</span>
  </div>
  <div class="skill-row">
    <span class="skill-label">AI &amp; ML</span>
    <span class="skill-list">Machine Learning, Deep Learning, Reinforcement Learning, Explainable AI, NLP</span>
  </div>
  <div class="skill-row">
    <span class="skill-label">Tools</span>
    <span class="skill-list">Flask, Neo4j, Tableau, Git, Docker, AWS, Linux</span>
  </div>
</section>

{% include visitor-map.html %}
