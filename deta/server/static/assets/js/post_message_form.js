(function ($) {
    'use strict';
    var form = $('#post-form'),
        message = $('#result'),
        form_data;

    // success function
    function done_func(response) {
        if (response['success']) {
            message.fadeIn().removeClass('alert-danger').addClass('alert-success');
            form[0].reset();
        } else {
            message.fadeIn().removeClass('alert-success').addClass('alert-danger');
        }
        message.text(response['message']);
        setTimeout(function () {
            message.fadeOut();
        }, 5000);
    }

    form.submit(function (e) {
        e.preventDefault();
        form_data = $(this).serialize();
        $.ajax({
            type: 'POST',
            dataType: 'json',
            url: form.attr('action'),
            data: form_data,
        })
            .done(done_func)
    });
})(jQuery);


