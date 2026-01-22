(function($) {
  "use strict";

  $(document).ready(function() {       
    var leftArrow = '<i class="ri-arrow-left-line"></i>';
    var rightArrow = '<i class="ri-arrow-right-line"></i>';
   
    $('.onboard-slider').owlCarousel({
        loop:true,
        nav:false,
        dots: false,
        margin: 10,
        items: 1,
        autoplay:true,
        autoplayTimeout:10000,
        smartSpeed:2000,
        navText: [leftArrow,rightArrow],
    })
  });
    // console.log('Load Carousel');
    // var advCarousel = document.querySelector('#advCarousel')
    // var carousel = new bootstrap.Carousel(advCarousel, {
    //   interval: 2000,
    //   wrap: false
    // })
    // var elem = document.documentElement;
    
    function openFullscreen() {
      if (elem.requestFullscreen) {
        elem.requestFullscreen();
      } else if (elem.webkitRequestFullscreen) { /* Safari */
        elem.webkitRequestFullscreen();
      } else if (elem.msRequestFullscreen) { /* IE11 */
        elem.msRequestFullscreen();
      }
    }

    /* Close fullscreen */
    function closeFullscreen() {
      if (document.exitFullscreen) {
        document.exitFullscreen();
      } else if (document.webkitExitFullscreen) { /* Safari */
        document.webkitExitFullscreen();
      } else if (document.msExitFullscreen) { /* IE11 */
        document.msExitFullscreen();
      }
    }

    
})(jQuery);
