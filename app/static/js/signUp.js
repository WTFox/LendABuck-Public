/**
 * Created by anthonyfox on 10/5/15.
 */

var $flaskData = $("#flaskData").data();
var $form = $("#signUpForm");

//TODO: Does user already exist?

$(document).ready(function () {
    $("#btnSignUp").on("click", function () {
        submitSignUpForm();
    });

});

function submitSignUpForm() {
    var payload = $form.serialize();
    $form.submit();
}
