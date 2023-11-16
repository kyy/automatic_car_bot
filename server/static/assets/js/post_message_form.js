$(document).ready(function() {
  $('#post-form').submit(function(e){
    e.preventDefault();
    var serializedData = $(this).serialize();

    $.ajax({
      type:"POST",
      url: "/submit_message",
      data:  serializedData,
      success: function(data){
        $("#result").text(data["result"]);
      },
    });
  })
});