/*
 * Yabi - a sophisticated online research environment for Grid, High Performance and Cloud computing.
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

$.fn.randomTestimonial = function(testimonials, interval, prevText) {

  var obj = $(this);
  var textCont = $('#testimonial');
  var t_head = $('#t_head');
  var t_body = $('#t_body');
  var t_source = $('#t_source');

  textCont.fadeOut('slow', function() {
    var randobj = randomise(testimonials);
    if (prevText) {
      while (randobj.body == prevText.body) {
        randobj = randomise(testimonials);
      }
    }
    t_head.empty().html(randobj.head);
    t_body.empty().html(randobj.body);
    t_source.empty().html(randobj.source);
    textCont.fadeIn('slow');
    prevText = randobj;
  });
  timeOut = setTimeout(function() {
    obj.randomTestimonial(testimonials, interval, prevText);
  }, interval);
};

function randomise(a) {
  var rand = Math.floor(Math.random() * a.length + a.length);
  var randobj = a[rand - a.length];
  return randobj;
}
