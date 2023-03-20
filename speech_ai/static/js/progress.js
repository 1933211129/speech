// progress.js

function updateProgress(percent) {
    var progressBar = document.querySelector('.progress-bar');
    progressBar.style.width = percent + '%';
    progressBar.setAttribute('aria-valuenow', percent);
    progressBar.textContent = percent + '%';
  }
  
  function getProgress() {
    $.get('/TextVisualizaton/', function(data) {
      updateProgress(data.percent);
      if (data.percent < 100) {
        setTimeout(getProgress, 1000);
      }
    });
  }
  
  $(document).ready(function() {
    getProgress();
  });
  