/*
 * Yabi Admin Fixer -- using a little jQuery to make certain admin
 * views easier for users.
 */

django.jQuery(document).ready(function($) {
    'use strict';

    var get_caps = function($form) {
        // Loads caps dict from hidden form field and then removes it.
        var caps = $.parseJSON($form.find("#id_caps").val());
        $form.find(".field-caps").hide();
        return caps;
    };

    // Backend admin
    (function() {
        var admin = $("body.yabi-backend");

        var caps = get_caps(admin);

        // show the fieldsets according to caps of the selected scheme
        admin.find("select#id_scheme").change(function(ev) {
            var val = $(this).val();

            admin.find(".fsbackend-only").toggle(caps && caps[val] && caps[val].fs);
            admin.find(".execbackend-only").toggle(caps && caps[val] && caps[val].exec);

            // unset lcopy and link if the backend doesn't support them
            $.each(["lcopy_supported", "link_supported"], function(i, attr) {
                if (caps && caps[val] && !caps[val][attr]) {
                    admin.find("#id_" + attr).attr("checked", false);
                }
            });
        }).change();
    }());

    // Credential admin
    (function() {
        var admin = $("body.yabi-credential");
        var caps = get_caps(admin);

        var get_form_container = function($input) {
            var cls = ".field-" + $input.attr("name");
            var container = $input.parents(".field-box" + cls);
            if (!container.length) {
                container = $input.parents(".form-row" + cls);
            }
            return container;
        };

        // store the associated input element, div container, help element
        var fields = {};
        $.each(["username", "password", "cert", "key"], function(i, f) {
            var input = admin.find("#id_" + f);
            fields[f] = { input: input,
                          help: input.parent().find(".help"),
                          container: get_form_container(input) };
            fields[f].initial_help = fields[f].help.text();
        });

        // Show different field help texts depending on the selected
        // backend scheme. Hide fields which aren't applicable to the
        // selected scheme. If there are no auth field descriptions at
        // all for the scheme, then show all fields and their initial
        // help text.
        admin.find("select#id_scheme").change(function(ev) {
            var val = $(this).val();
            var auth = (caps && caps[val] ? caps[val].auth : null) || null;
            $.each(fields, function(field, o) {
                o.help.text(auth === null ? o.initial_help : auth[field] || "");
                o.container.toggle(auth === null || auth[field] ? true : false);
            });

            // The username field is required by the django admin
            // form, but some backends don't really require it. In
            // this case, just enter a placeholder value because the
            // field will be hidden.
            if (auth && !auth.username && !fields.username.input.val()) {
                fields.username.input.val("username");
            }
        }).change();
    }());
});
