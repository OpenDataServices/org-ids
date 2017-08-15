$(function() {
  // General
  // -------
  $('select').chosen();

  var progressBarConfig = {
    easing: 'easeInOut',
    color: 'white',
    trailColor: 'rgba(255, 255, 255, 0.5)',
    svgStyle: null
  };

  $('.sidebar form select').change(function() {
    if (this.value) {
      if (this.name === 'coverage') {
        $('select[name=subnational]').val('');
      }
      if (this.name === 'structure') {
        $('select[name=substructure]').val('');
      }
      this.form.submit();
    }
  });

  // Home
  // ----
  $('.has-suboption').change(function() {
    if (this.value) {
      if (this.name === 'coverage') {
        $('select[name=subnational]').val('');
      }
      if (this.name === 'structure') {
        $('select[name=substructure]').val('');
      }
      var params = '?' + $('form').serialize();
      window.location.href = window.location.pathname + params;
    }
  });

  // Results
  // -------
  if ($('.quality-chart-container').length) {
    progressBarConfig.duration = 1600;
    progressBarConfig.trailWidth = 4;
    progressBarConfig.strokeWidth = 4;

    $('.quality-chart-container').each(function() {
      var value = $(this).data('chart') / 100;
      var bar = new ProgressBar.Circle(this, progressBarConfig);
      bar.animate(value);
    });
  }

  // List Detail
  // -----------
  if ($('#quality-chart-container').length) {
    progressBarConfig.duration = 800;
    progressBarConfig.trailWidth = 2;
    progressBarConfig.strokeWidth = 2;

    var value = $('#quality-chart-container').parent().data('chart') / 100;
    var bar = new ProgressBar.Circle('#quality-chart-container', progressBarConfig);
    bar.animate(value);
  }
});
