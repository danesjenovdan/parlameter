/* eslint-disable */

// HEADER LOGIC
$(function () {
  // show/hide mobile menu
  $(".mobile-menu__button").on("click", function (e) {
    e.preventDefault();
    $("mobile-menu__hamburger").removeClass("mobile-menu__hambuger--closed");
    $(".menu-container").toggleClass("open");
  });

  // mandate selector
  $("select.mandate-select").on("change", function () {
    window.location.href = $(this).val();
  });
});

// LEGAL TEXT
$(function () {
  // all links in legal text should open in a new tab
  $(".legal-text-container a").attr("target", "_blank");
});

// NEWSLETTER FORM
$(function () {
  $(".newsletter-form").on("submit", function (event) {
    event.preventDefault();

    const campaign_slug = "danes-je-nov-dan";
    const segment_id = 21;
    const email = $(this).find("#newsletter-email").val();

    let url = `https://moj.djnd.si/${campaign_slug}/prijava?segment_id=${segment_id}`;
    url += `&email=${encodeURIComponent(email)}`;
    window.open(`${url}`, `_blank`);
  });
});
