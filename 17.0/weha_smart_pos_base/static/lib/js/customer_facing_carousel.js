(function($) {
  "use strict";

  $(document).ready(async function() {      
    console.log("Document Ready");
    var leftArrow = '<i class="ri-arrow-left-line"></i>';
    var rightArrow = '<i class="ri-arrow-right-line"></i>';
    $('.owl-carousel').owlCarousel({
        loop:true,
        nav:true,
        // dots:false,
        margin: 10,
        items: 3,
        autoplay:true,
        autoplayTimeout:10000,
        smartSpeed:2000,
        navText: [leftArrow,rightArrow],
    });
  });    
})(jQuery);
