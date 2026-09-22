---
layout: single
title: "Contact"
permalink: /contact/
author_profile: true
---

Feel free to get in touch about research, collaborations, or anything on this
site. You can email me directly at
[{{ site.author.email }}](mailto:{{ site.author.email }}), or use the form below.

<!--
  The form posts to Formspree. Your old site used the legacy endpoint
  https://formspree.io/johannes.nicolaus@gmail.com, which Formspree retired.
  Create a form at https://formspree.io/forms and replace YOUR_FORM_ID below
  with the ID it gives you. Until then the form will not deliver mail.
-->
<form class="contact-form" action="https://formspree.io/f/YOUR_FORM_ID" method="POST" accept-charset="UTF-8">
  <p>
    <label for="contact-name">Name</label>
    <input id="contact-name" name="name" type="text" maxlength="255" required placeholder="Your name">
  </p>
  <p>
    <label for="contact-email">Email address <small>(will remain private)</small></label>
    <input id="contact-email" name="email" type="email" maxlength="255" required placeholder="email@address.com">
  </p>
  <p>
    <label for="contact-message">Message</label>
    <textarea id="contact-message" name="message" rows="10" required></textarea>
  </p>
  <p class="contact-form__honeypot">
    <label for="contact-gotcha">Do not fill this out</label>
    <input id="contact-gotcha" type="text" name="_gotcha" tabindex="-1" autocomplete="off">
  </p>
  <p>
    <button class="btn btn--large" type="submit">Send message</button>
  </p>
</form>
