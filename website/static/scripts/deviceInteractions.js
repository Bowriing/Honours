document.addEventListener("DOMContentLoaded", function()
{
    let selectedDevice = null;

    //event listner for the tables rows
    const rows = document.querySelectorAll(".device-table-row");
    rows.forEach(row => 
        {
            row.addEventListener("click", function()
            {
                //remove any previously selected row
                if (selectedDevice !== null)
                {
                    selectedDevice.classList.remove("selected");
                }
                
                //highlight selected row
                selectedDevice = row;
                selectedDevice.classList.add("selected");

                //store selected device name
                const deviceName = selectedDevice.dataset.deviceName;
                console.log("Selected device: ", deviceName)
            });
        });
});

const deleteButton = document.getElementById("deleteButton");
deleteButton.addEventListener("click", function()
{
    if (selectedDevice !== null)
    {
        const deviceName = selectedDevice.dataset.deviceName;
        if (confirm("Are you sure you want to delete " + deviceName + "?"))
        {
            // Send selected device to backend
            fetch('/delete-device',
            {
                method: 'POST',

                headers:
                {
                    'Content-Type': 'application/json'
                },

                body: JSON.stringify({device_name: deviceName})
            })
        }
    } 
});
