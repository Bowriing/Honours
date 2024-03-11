document.addEventListener('DOMContentLoaded', function () {
    var checkboxes = document.querySelectorAll('.form-check-input');
    checkboxes.forEach(function(checkbox) {
        checkbox.addEventListener('change', function() {
            // if current check is random then uncheck others
            if(checkbox.id === 'randomZone' && checkbox.checked) {
                checkboxes.forEach(function(other) {
                    if(other !== checkbox) other.checked = false;
                });
            }
            // if current check is not random but checked, uncheck random
            else if (checkbox.checked) {
                document.getElementById('randomZone').checked = false;
            }
        });
    });
});