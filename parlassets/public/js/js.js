/* eslint-disable */

// HEADER LOGIC
$(function () {
  // show/hide mobile menu
  $(".mobile-menu__button").on("click", function (e) {
    e.preventDefault();
    $(".menu-container").toggleClass("open");
    if ($(".menu-container").hasClass("open")) {
      $("a.mobile-menu__hamburger").attr("aria-label", "Close navigation");
    } else {
      $("a.mobile-menu__hamburger").attr("aria-label", "Open navigation");
    }
  });

  function toggleInert() {
    if (window.innerWidth > 992) {
      $(".menu-container").removeClass("open");
      $(".mobile-menu__button").attr("inert", "");
    } else {
      $(".mobile-menu__button").removeAttr("inert");
    }
  }

  window.addEventListener("resize", function () {
    toggleInert();
  });
  toggleInert();

  // mandate selector
  $("select.mandate-select").on("change", function () {
    window.location.href = $(this).val();
  });

  // search info modal
  $("#modal-search-how")
    .on("show.bs.modal", function (event) {
      $(".searchinfo").attr("aria-expanded", "true");
    })
    .on("hide.bs.modal", function (event) {
      $(".searchinfo").attr("aria-expanded", "false");
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
