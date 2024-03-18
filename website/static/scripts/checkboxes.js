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

    document.getElementById('deviceConstant').addEventListener('change', function() {
        var checkboxes = document.querySelectorAll('input[name="deviceTimezone"]');

        if (this.value === 'yes') {
            checkboxes.forEach(function(checkbox) {
                checkbox.checked = true;
                document.getElementById('randomZone').checked = false;
            });
        }

        else if (this.value === 'no') {
            checkboxes.forEach(function(checkbox){
                checkbox.checked = false;
            })
        }

    });

    document.getElementById('add_device_button').addEventListener('click', function() {
        document.getElementById('add_form').submit()
    });
    
});



