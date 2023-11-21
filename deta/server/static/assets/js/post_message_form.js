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
        }, 2000);
    }

    // fail function
    function fail_func(data) {
        message.fadeIn().removeClass('alert-success').addClass('alert-success');
        message.text(data.responseText);
        setTimeout(function () {
            message.fadeOut();
        }, 2000);
    }

    form.submit(function (e) {
        e.preventDefault();
        form_data = $(this).serialize();
        $.ajax({
            type: 'POST',
            url: form.attr('action'),
            data: form_data,
            dataType: 'False'
        })
            .done(done_func, form[0].reset())
            .fail(fail_func);
    });
})(jQuery);