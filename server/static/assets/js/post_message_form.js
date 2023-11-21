(function ($) {
    'use strict';
    var form = $('#post-form'),
        message = $('#result'),
        button = $('#button'),
        form_data;

    // success function
    function done_func(response) {
        message.fadeIn().removeClass('alert-danger').addClass('alert-success');
        message.text(response);
        setTimeout(function () {
            message.fadeOut();
        }, 5000);
    }

    // fail function
    function fail_func(response) {
        message.fadeIn().removeClass('alert-success').addClass('alert-danger');
        message.text(response);
        setTimeout(function () {
            message.fadeOut();
        }, 5000);
    }

    form.submit(function (e) {
        e.preventDefault();
        form_data = $(this).serialize();
        $.ajax({
            type: 'POST',
            url: form.attr('action'),
            data: form_data,
            processData: false,
            contentType: false,
        })
            .done(done_func, form[0].reset())
            .fail(fail_func);
    });
})(jQuery);


