(function ($) {
    "use strict";
    
    // JS Index
    //----------------------------------------
    // 1. sticky menu
    // 2. mobile-menu(mean-menu)
    // 3. preloader
    // 4. One Page Nav
    // 5. mobile-menu-sidebar
    // 6. background image
    // 7. brand active
    // 8. wow animation  active
    // 9. back top
    // 10. parallax
    //-------------------------------------------------

    // 1. sticky menu
    // ---------------------------------------------------------------------------
    var wind = $(window);
    var sticky = $("#header-sticky");
    wind.on('scroll', function () {
        var scroll = $(wind).scrollTop();
        if (scroll < 2) {
            sticky.removeClass("sticky-menu");
        } else {
            $("#header-sticky").addClass("sticky-menu");
        }
    });





    // 2. slider - active
    //---------------------------------------------------------------------------
    function mainSlider() {
        var BasicSlider = $('.slider-active');

        BasicSlider.on('init', function (e, slick) {
            var $firstAnimatingElements = $('.single-slider:first-child').find('[data-animation]');
            doAnimations($firstAnimatingElements);
        });

        BasicSlider.on('beforeChange', function (e, slick, currentSlide, nextSlide) {
            var $animatingElements = $('.single-slider[data-slick-index="' + nextSlide + '"]').find('[data-animation]');
            doAnimations($animatingElements);
        });

        BasicSlider.slick({
            dots: false,
            fade: true,
            // slidesToScroll:1,
            // initialSlide:1,
            speed: 800,
            autoplay: true,
            autoplaySpeed: 4000,
            arrows: true,
            prevArrow:'<b><i class="l-a fas fa-arrow-left"></i></b>',
            nextArrow:'<b><i class="r-a fas fa-arrow-right"></i></b>',
            responsive: [
                { breakpoint: 767, settings: {
                    arrows: false,
                } }
            ]
        });

        function doAnimations(elements) {
            var animationEndEvents = 'webkitAnimationEnd mozAnimationEnd MSAnimationEnd oanimationend animationend';
            elements.each(function () {
                var $this = $(this);
                var $animationDelay = $this.data('delay');
                var $animationType = 'animated ' + $this.data('animation');
                $this.css({
                    'animation-delay': $animationDelay,
                    '-webkit-animation-delay': $animationDelay
                });
                $this.addClass($animationType).one(animationEndEvents, function () {
                    $this.removeClass($animationType);
                });
            });
        }
    }
    mainSlider();




    // 3. mobile-menu(mean-menu)
    //---------------------------------------------------------------------------
    $("#mobile-menu").meanmenu({
        meanMenuContainer: ".mobile-menu",
        meanScreenWidth: "991",
    });



    // 4. preloader
    //---------------------------------------------------------------------------
    $(window).load(function(){
        $('#preloader').fadeOut('slow',function(){$(this).remove();});
    });
    


    // 5. One Page Nav
    //---------------------------------------------------------------------------
    var top_offset = $('.header-area').height() - 10;
    $('.main-menu nav ul').onePageNav({
        currentClass: 'active',
        scrollOffset: top_offset,
    });



    // 6. mobile-menu-sidebar
    //---------------------------------------------------------------------------
    $(".mobile-menubar").on("click", function(){
        $(".side-mobile-menu").addClass('open-menubar');
        $(".body-overlay").addClass("opened");
    });
    $(".close-icon").click(function(){
        $(".side-mobile-menu").removeClass('open-menubar');
        $(".body-overlay").removeClass("opened");
    });

    $(".body-overlay").on("click", function () {
		$(".side-mobile-menu").removeClass('open-menubar');
		$(".body-overlay").removeClass("opened");
	});



    // 7. background image
    //---------------------------------------------------------------------------
    $("[data-background]").each(function (){
        $(this).css("background-image","url(" + $(this).attr("data-background") + ")");
    });




    // 8. brand active
    //---------------------------------------------------------------------------
    $('.testimonial-active').slick({
        dots: false,
        arrows: true,
        prevArrow:'<b><i class="fas fa-angle-left l-a"></i></b>',
        nextArrow:'<b><i class="fas fa-angle-right r-a"></i></b>',
        infinite: true,
        speed: 300,
        slidesToShow: 1,
        slidesToScroll: 1,
        centerPadding: '30px',
        responsive: [
            {
                breakpoint: 480,
                settings: {
                    slidesToShow: 1,
                }
            }
        ]
    });






    // 9. wow animation  active
    // ---------------------------------------------------------------------------
    new WOW().init();



    // 10. Scroll To down Js
    //---------------------------------------------------------------------------
    function smoothSctollTop() {
    $('.smooth-scroll a').on('click', function (event) {
        var target = $(this.getAttribute('href'));
            if (target.length) {
            event.preventDefault();
            $('html, body').stop().animate({
                scrollTop: target.offset().top - 0
            }, 1500);

            }
        });
    }smoothSctollTop();


    // 11. Animate the scroll to top
    // --------------------------------------------------------------------------
    // Show or hide the sticky footer button
    $(window).on('scroll', function() {
        if($(this).scrollTop() > 600){
            $('#scroll').fadeIn(1000);
        } else{
            $('#scroll').fadeOut(1000);
        }
    });

    $('#scroll').on('click', function(event) {
        event.preventDefault();
        
        $('html, body').animate({
            scrollTop: 0,
        }, 1500);
    });






    // // 10. parallax
    // // ---------------------------------------------------------------------------
    // var scene = $('#scene').get(0);

    // var parallax = new parallax(scene, {
    //     limitX: true,
    //     scalarX: 10.0,
    //     originX: 0,
    //   });

/*================================================================= 
    Contact form 
==================================================================*/
$(function() {
    // Here is the form
    var form = $('#contact-form');

    // Getting the messages div
    var formMessages = $('.form-message p');


    // Setting up an event listener for the contact form
  $(form).submit(function(event) {
      // Stopping the browser to submit the form
      event.preventDefault();
      
      // Serializing the form data
    var formData = $(form).serialize();

    // Submitting the form using AJAX
    $.ajax({
        type: 'POST',
        url: $(form).attr('action'),
        data: formData
    }).done(function(response) {
      
        // Making the formMessages div to have the 'success' class
        $(formMessages).removeClass('error');
        $(formMessages).addClass('success');

        // Setting the message text
        $(formMessages).text(response);

        // Clearing the form after successful submission 
        $('#inputName').val('');
        $('#inputEmail').val('');
        $('#inputPhone').val('');
        $('#inputSubject').val('');
        $('#inputMessage').val('');
    }).fail(function(data) {
      
        // Making the formMessages div to have the 'error' class
        $(formMessages).removeClass('success');
        $(formMessages).addClass('error');

        // Setting the message text
        if (data.responseText !== '') {
            $(formMessages).text(data.responseText);
        } else {
            $(formMessages).text('Oops! An error occured and your message could not be sent.');
        }
    });

  });

});

})(jQuery);	  

