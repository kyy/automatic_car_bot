const form = $('#post-form'),
    message = $('#result'),
    csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

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
    $.ajax({
        type: 'POST',
        dataType: 'json',
        url: form.attr('action'),
        headers: {'X-CSRFToken': csrftoken},
        data: $(this).serialize(),
    })
        .done(done_func)
});



