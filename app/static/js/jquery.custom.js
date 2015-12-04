$(document).ready(function(){
    //Automatic scroll arrow
     $(window).scroll(function () {
        if ($(this).scrollTop() > 50) {
            $('#back-to-top').fadeIn();
        } else {
            $('#back-to-top').fadeOut();
        }
    });
    $('#back-to-top').click(function () {
        $('#back-to-top').tooltip('hide');
        $('body,html').animate({
            scrollTop: 0
        }, 800);
        return false;
    });
    $('#back-to-top').tooltip('show');

    //Datepicker call list
/*    var form = document.getElementById("form-date");
    document.getElementById("your-id").addEventListener("click", function () {
        form.submit();
    });*/

   
     $("div.selector-club-tab-menu>div.list-group>a").click(function(e) {
        e.preventDefault();
        $(this).siblings('a.active').removeClass("active");
        $(this).addClass("active");
        var index = $(this).index();
        $("div.selector-club-tab>div.selector-club-tab-content").removeClass("active");
        $("div.selector-club-tab>div.selector-club-tab-content").eq(index).addClass("active");
    });

});

$(function(){
    //Calendar
    $(".datepicker").datepick({
        minDate:0,
        firstDay: 1,
        dateFormat: 'dd-mm-yyyy'
    });

});

/*  $(function dateChange(tBox) {
       alert("jola");
    }
   });*/





