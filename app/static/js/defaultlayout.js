/**
 * Created by anthonyfox on 10/5/15.
 */

var $flaskData = $("#flaskData").data();

$(document).ready(function () {

    $("#signInButton").on("click", function () {
        var payload = {
            email: $("#signInEmail").val(),
            password: $("#signInPassword").val()
        };

        $.ajax({
            type: 'POST',
            url: '/signIn',
            data: JSON.stringify(payload),
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function(data) {
                console.log(data);
                // Fail message
                if (data.status > 0) {
                    var errorMsg = data.message;
                    $('#signInAlert').html("<div class='alert alert-danger'>");
                    $('#signInAlert > .alert-danger').html("<button type='button' class='close' data-dismiss='alert' aria-hidden='true'>&times;")
                        .append("</button>");
                    $('#signInAlert > .alert-danger').append("<strong>" + errorMsg +"</strong>" );
                    $('#signInAlert > .alert-danger').append('</div>');

                } else {
                    window.location.href = data.url;
                }
            }
        });
    });
});

//TODO: Does user already exist?

var $form = $("#signUpForm");
$(document).ready(function () {
    $("#btnSignUp").on("click", function () {
        $form.submit();
    });

});
