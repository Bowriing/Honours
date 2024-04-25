$(document).ready(function() {
    $('#fetchPowerButton').on('click', function() {
        var deviceName = $('#deviceName').val();
        var deviceType = $('#deviceType').val();

        $.ajax({
            url: '/fetch-power-rating',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                deviceName: deviceName,
                deviceType: deviceType
            }),
            success: function(data) {
                console.log('Success:', data);
                $('#powerRating').val(data.power_rating);
            },
            error: function(status, error) {
                console.log('Error:', status, error);
            }
        });
    });
});

