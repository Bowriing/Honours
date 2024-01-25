document.addEventListener("DOMContentLoaded", function() {
    // Target the file input element
    var fileInput = document.getElementById('csv_file');
    fileInput.addEventListener('change', function(e) {
        // Retrieve the name of the selected file
        var fileName = e.target.files[0].name;
        // Find the label corresponding to the file input and update its text
        var fileLabel = document.querySelector("label[for='csv_file']");
        fileLabel.textContent = fileName;
    });
});

