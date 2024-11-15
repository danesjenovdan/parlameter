/* eslint-disable */

// HEADER LOGIC
$(function() {
  // show/hide mobile menu
  $('.mobile-menu__button').on('click', function(e) {
    e.preventDefault();
    $('mobile-menu__hamburger').removeClass('mobile-menu__hambuger--closed');
    $('.menu-container').toggleClass('open');
  });

  // show/hide header search
  $('.open-search').on('click', function() {
    $('.menu').addClass('hidden');
    $('.menu-search').removeClass('hidden');
    $('.open-search').addClass('hidden');
    $('.close-search').removeClass('hidden');
    $('.menu-search .search-dropdown-input').focus();
  });
  $('.close-search').on('click', function() {
    $('.menu').removeClass('hidden');
    $('.menu-search').addClass('hidden');
    $('.open-search').removeClass('hidden');
    $('.close-search').addClass('hidden');
  });

  // mandate selector
  $('select.mandate-select').on('change', function() {
    window.location.href = $(this).val();
  });
});

// LEGAL TEXT
$(function() {
  // all links in legal text should open in a new tab
  $('.legal-text-container a').attr('target', '_blank');
});
