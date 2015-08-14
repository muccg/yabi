/*
 * Yabi - a sophisticated online research environment for Grid, High Performance
 * and Cloud computing.
 * Copyright (C) 2015  Centre for Comparative Genomics, Murdoch University.
 *
 *  This program is free software: you can redistribute it and/or modify
 *  it under the terms of the GNU Affero General Public License as
 *  published by the Free Software Foundation, either version 3 of the
 *  License, or (at your option) any later version.
 *
 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU Affero General Public License for more details.
 *
 *  You should have received a copy of the GNU Affero General Public License
 *  along with this program.  If not, see <http://www.gnu.org/licenses/>.
 *  */

/*
 * Yabi Admin Fixer -- using a little jQuery to make certain admin
 * views easier for users.
 */

django.jQuery(document).ready(function($) {
    'use strict';

    var get_caps = function($form) {
        // Loads caps dict from hidden form field and then removes it.
        var caps = $.parseJSON($form.find('#id_caps').val());
        $form.find('.field-caps').hide();
        return caps;
    };

    // Backend admin
    (function() {
        var admin = $('body.yabi-backend');

        var caps = get_caps(admin);

        // show the fieldsets according to caps of the selected scheme
        admin.find('select#id_scheme').change(function(ev) {
            var val = $(this).val();

            admin.find('.fsbackend-only').toggle(
                caps && caps[val] && caps[val].fs);
            admin.find('.execbackend-only').toggle(
                caps && caps[val] && caps[val].exec);

            // unset lcopy and link if the backend doesn't support them
            $.each(['lcopy_supported', 'link_supported'], function(i, attr) {
                if (caps && caps[val] && !caps[val][attr]) {
                    admin.find('#id_' + attr).attr('checked', false);
                }
            });
        }).change();
    }());

    // Credential admin
    (function() {
        var admin = $('body.yabi-credential');
        var caps = get_caps(admin);

        var get_form_container = function($input) {
            var cls = '.field-' + $input.attr('name');
            var container = $input.parents('.field-box' + cls);
            if (!container.length) {
                container = $input.parents('.form-row' + cls);
            }
            return container;
        };

        var get_auth_from_class = function(auth_class) {
            // search through caps for an auth object with the given class
            var auth = null;
            $.each(caps, function(scheme, cap) {
              if (cap.auth && cap.auth['class'] === auth_class) {
                auth = cap.auth;
                return false;
              }
            });
            return auth;
        };

        // store the associated input element, div container, help element
        var fields = {};
        $.each(['username', 'password', 'cert', 'key'], function(i, f) {
            var input = admin.find('#id_' + f);
            fields[f] = { input: input,
                          help: input.parent().find('.help'),
                          container: get_form_container(input) };
            fields[f].initial_help = fields[f].help.text();
        });

        // Show different field help texts depending on the selected
        // backend scheme. Hide fields which aren't applicable to the
        // selected scheme. If there are no auth field descriptions at
        // all for the scheme, then show all fields and their initial
        // help text.
        admin.find('select#id_auth_class').change(function(ev) {
            var auth = get_auth_from_class($(this).val());

            $.each(fields, function(field, o) {
                o.help.text(auth === null ? o.initial_help : auth[field] || '');
                o.container.toggle(auth === null || auth[field] ? true : false);
            });

            // The username field is required by the django admin
            // form, but some backends don't really require it. In
            // this case, just enter a placeholder value because the
            // field will be hidden.
            if (auth && !auth.username && !fields.username.input.val()) {
                fields.username.input.val('username');
            }
        }).change();
    }());
});
