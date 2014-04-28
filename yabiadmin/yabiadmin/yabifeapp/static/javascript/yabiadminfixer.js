/*
 * Yabi Admin Fixer -- using a little jQuery to make certain admin
 * views easier for users.
 */

django.jQuery(document).ready(function($) {
    'use strict';

    // Backend admin
    (function() {
        var admin = $("body.yabi-backend");

        // load caps dict from hidden form field
        var caps = $.parseJSON(admin.find("#id_caps").val());
        admin.find(".field-caps").hide();
        admin.find("#id_caps").val("");

        // show the fieldsets according to caps of the selected scheme
        admin.find("select#id_scheme").change(function(ev) {
            var val = $(this).val();

            admin.find(".fsbackend-only").toggle(caps && caps[val] && caps[val].fs);
            admin.find(".execbackend-only").toggle(caps && caps[val] && caps[val].exec);
        }).change();
    }());
});
