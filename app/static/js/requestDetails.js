/**
 * Created by afox on 12/14/2015.
 */
var $slider = $(".slider");
var currentPercent = 0;
var currentAmountNeeded = 0;
var currentPlatformFee = 0;
var currentTransferFee = 0;

$(document).ready(function () {
    var $form = $(".offerForm");
    $slider.slider();
    $currentPercent = $form.find(".currentPercent");
    $currentAmountNeeded = $form.find(".currentAmountNeeded");
    $currentPlatformFee = $form.find(".currentPlatformFee");
    $currentTransferFee = $form.find(".currentTransferFee");

    currentPercent = Number($currentPercent.val());
    currentAmountNeeded = Number($currentAmountNeeded.val());
    currentPlatformFee = Number($currentPlatformFee.val());
    currentTransferFee = Number($currentTransferFee.val());

    $(".currentOfferAmount").text(currentAmountNeeded.toFixed(2));

    $slider.on("slide", function (slideEvt) {
        var amountOwedBack = currentAmountNeeded + (currentAmountNeeded * (slideEvt.value / 100) + currentPlatformFee + currentTransferFee);
        $(".sliderVal").text(slideEvt.value);
        $(".currentOfferAmount").text(amountOwedBack.toFixed(2));
    });

    $("#submitOfferFormBtn").on("click", function (e) {
        e.preventDefault();
        $form.submit();
    });
});