window.onload = function () {
    document.getElementById("titlee").innerHTML = "Appliances";

    document.getElementById("dash").classList.remove("active");
    document.getElementById("appl").classList.add("active");
};

document.addEventListener('DOMContentLoaded', function () {
    const electricityApplianceSelect = document.getElementById('electricity_appliance_select');
    const electricityApplianceName = document.getElementById('electricity_appliance_name');

    const gasApplianceSelect = document.getElementById('gas_appliance_select');
    const gasApplianceName = document.getElementById('gas_appliance_name');

    electricityApplianceSelect.addEventListener('change', function () {
        if (this.value === 'Other') {
            electricityApplianceName.style.display = 'block';
        } else {
            electricityApplianceName.style.display = 'none';
        }
    });
    gasApplianceSelect.addEventListener('change', function () {
        if (this.value === 'Other') {
            gasApplianceName.style.display = 'block';
        } else {
            gasApplianceName.style.display = 'none';
        }
    });
});

function validateForm() {
    var selectedElecDate = new Date(document.querySelector('input[name="electricity_date"]').value);
    var selectedGasDate = new Date(document.querySelector('input[name="gas_date"]').value);
    var selectedGasDuration = document.querySelector('input[name="gas_duration"]').value;
    var selectedElecDuration = document.querySelector('input[name="electricity_duration"]').value;

    var currentDate = new Date();

    if (selectedElecDate > currentDate) {
        alert('Date cannot be in the future!');
        return false;
    }
    if (selectedGasDate > currentDate) {
        alert('Date cannot be in the future!');
        return false;
    }

    if (selectedGasDuration > 24) {
        alert("Daily hours cannot exceed 24!");
        return false;
    }

    if (selectedElecDuration > 24) {
        alert("Daily hours cannot exceed 24!");
        return false;
    }

    return true;
};

function validateUpdateForm() {
    var updateDate = new Date(document.querySelector('input[name="update_date"]').value);
    var updateDuration = document.querySelector('input[name="update_duration"]').value;
    var updateWattage = document.querySelector('input[name="update_wattage"]').value;
    var updateName = document.querySelector('input[name="update_name"]').value;

    var currentDate = new Date();

    if (updateDate > currentDate) {
        alert('Date cannot be in the future!');
        return false;
    }

    if (updateDuration > 24) {
        alert("Daily hours cannot exceed 24!");
        return false;
    }

    alert(("Appliance has been Updated!"))
    return true;
};

function confirmDelete() {
    alert(("Appliance has been Updated!"))

};

async function getAppliances() {
    const response = await fetch('/api/appliances/0');
    const data = await response.json();
    return data;
};

async function deleteAppliance(id) {
    if (confirm("Do you really want to delete these records?\nThis process cannot be undone.")) {
        // Make an AJAX call to delete the appliance
        const csrfToken = getCookie('csrftoken');
        const response = await fetch(`/api/appliances/${id}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken,
            }
        });

        const data = await response.json();
        if (data.success) {
            window.location.reload();
        } else {
            alert("Error deleting appliance");
        }
    }
};

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
async function updateModal(id) {
    // Find the appliance with the matching id
    console.log(id)
    let userAppliances = await getAppliances();
    console.log(userAppliances)
    let appliance = null;

    for (let i = 0; i < userAppliances.length; i++) {
        if (userAppliances[i].id == id) {
            appliance = userAppliances[i];
            console.log("Saved appliance", appliance)
            break;
        }
    }

    if (appliance) {
        // Update the values in the modal
        document.querySelector("#applianceId").value = appliance.id;

        document.querySelector("#applianceName").value = appliance.name;
        document.querySelector("#applianceWattage").value = appliance.wattage;
        document.querySelector("#applianceUsage").value = appliance.duration;
        document.querySelector("#applianceDate").value = appliance.date;

        // Show the modal
        document.getElementById("updateModal").style.display = "block";
    }
};
let currentMonthIndex = new Date().getMonth();
let months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
let currentMonth = months[currentMonthIndex];

function showPreviousMonth(type) {
    // Decrement the current month index
    currentMonthIndex = currentMonthIndex - 1;
    if (currentMonthIndex < 0) {
        currentMonthIndex = 11;
    }
    if (type === "electricity") {
        // Update the currentMonth element with the new month
        document.getElementById("currentMonth").innerHTML = `Your Electricity Appliances [${months[currentMonthIndex]}, 2023]`;
        // Update the appliances displayed in the template based on the new currentMonth value
        updateAppliances("electricity");
    }
    if (type === "gas") {
        // Update the currentMonth element with the new month
        document.getElementById("gasCurrentMonth").innerHTML = `Your Gas Appliances [${months[currentMonthIndex]}, 2023]`;
        // Update the appliances displayed in the template based on the new currentMonth value
        updateAppliances("gas");
    }
}

function showNextMonth(type) {
    // Increment the current month index
    currentMonthIndex = currentMonthIndex + 1;
    if (currentMonthIndex > 11) {
        currentMonthIndex = 0;
    }

    if (type === "electricity") {
        // Update the currentMonth element with the new month
        console.log("hiiii")
        document.getElementById("currentMonth").innerHTML = `Your Electricity Appliances [${months[currentMonthIndex]}, 2023]`;
        // Update the appliances displayed in the template based on the new currentMonth value
        updateAppliances("electricity");
    }
    if (type === "gas") {
        // Update the currentMonth element with the new month
        document.getElementById("gasCurrentMonth").innerHTML = `Your Gas Appliances [${months[currentMonthIndex]}, 2023]`;
        // Update the appliances displayed in the template based on the new currentMonth value
        updateAppliances("gas");
    }
}


async function updateAppliances(type) {
    if (type === "electricity") {
        try {
            // Make a GET request to the server to retrieve updated appliance data for the current month
            const response = await fetch(`/get_appliances/${months[currentMonthIndex]}/${type}`);
            const data = await response.json();
            // If the response contains updated appliance data, update the template
            if (data) {
                const tbody = document.querySelector("#elec-appliance-list tbody");
                tbody.innerHTML = "";

                if (data.length > 0) {
                    for (let i = 0; i < data.length; i++) {
                        const appliance = data[i];
                        const tr = document.createElement("tr");

                        // Converting the date to the desired format
                        const date = new Date(appliance.date);
                        const formattedDate = date.toLocaleString('default', { month: 'short' }) + ". " + date.getDate() + ", " + date.getFullYear();

                        tr.innerHTML = `
                    <td>${appliance.name}</td>
                    <td>${appliance.wattage} watts</td>
                    <td>${appliance.duration}h per day</td>
                    <td>${formattedDate}</td>
                    <td>
                    <button type="button" class="btn btn-warning" onclick="updateModal('${appliance.id}')" data-bs-toggle="modal" data-bs-target="#updateModal">↻</button>
                    <button class="btn btn-danger" onclick="deleteAppliance('${appliance.id}')">x</button>
                    </td>
                `;
                        tbody.appendChild(tr);
                    }
                } else {
                    const tr = document.createElement("tr");
                    tr.innerHTML = `<td colspan="5" class="fw-bold text-center">You do not have any Electric Appliances added for ${months[currentMonthIndex]}</td>`;
                    tbody.appendChild(tr);
                }
            }
        } catch (error) {
            console.error(error);
        }
    }

    if (type == "gas") {
        try {
            // Make a GET request to the server to retrieve updated appliance data for the current month
            const response = await fetch(`/get_appliances/${months[currentMonthIndex]}/${type}`);
            const data = await response.json();

            // If the response contains updated appliance data, update the template
            if (data) {
                const tbody = document.querySelector("#gas-appliance-list tbody");
                tbody.innerHTML = "";

                if (data.length > 0) {
                    for (let i = 0; i < data.length; i++) {
                        const appliance = data[i];
                        const tr = document.createElement("tr");

                        // Convert the date to the desired format
                        const date = new Date(appliance.date);
                        console.log("normal date from db", appliance.date)
                        console.log("converted with new date", date)
                        const formattedDate = date.toLocaleString('default', { month: 'short' }) + ". " + date.getDate() + ", " + date.getFullYear();
                        console.log("formattedDate", formattedDate)


                        tr.innerHTML = `
                    <td>${appliance.name}</td>
                    <td>${appliance.wattage} watts</td>
                    <td>${appliance.duration}h per day</td>
                    <td>${formattedDate}</td>
                    <td>
                    <button type="button" class="btn btn-warning" onclick="updateModal('${appliance.id}')" data-bs-toggle="modal" data-bs-target="#updateModal">↻</button>
                    <button class="btn btn-danger" onclick="deleteAppliance('${appliance.id}')">x</button>
                    </td>
                `;
                        tbody.appendChild(tr);
                    }
                } else {
                    const tr = document.createElement("tr");
                    tr.innerHTML = `<td colspan="5" class="fw-bold text-center">You do not have any Gas Appliances added for ${months[currentMonthIndex]}!</td>`;
                    tbody.appendChild(tr);
                }
            }
        } catch (error) {
            console.error(error);
        }
    }
}
