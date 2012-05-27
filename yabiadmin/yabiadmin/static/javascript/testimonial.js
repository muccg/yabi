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
