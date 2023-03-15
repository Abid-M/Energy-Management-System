window.onload = function () {
    document.getElementById("titlee").innerHTML = "Energy Usage";

    document.getElementById("dash").classList.remove("active");
    document.getElementById("usage").classList.add("active");
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
        document.getElementById("elecTitle").innerHTML = `Your Electricity Cost Breakdown`;
        document.getElementById("currentMonth").innerHTML = `[${months[currentMonthIndex]}, 2023]`;
        // Update the appliances displayed in the template based on the new currentMonth value
        updateAppliances("electricity");
    }
    if (type === "gas") {
        // Update the currentMonth element with the new month
        document.getElementById("gasTitle").innerHTML = `Your Gas Cost Breakdown`;
        document.getElementById("gasCurrentMonth").innerHTML = `[${months[currentMonthIndex]}, 2023]`;
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
        document.getElementById("elecTitle").innerHTML = `Your Electricity Cost Breakdown`;
        document.getElementById("currentMonth").innerHTML = `[${months[currentMonthIndex]}, 2023]`;
        // Update the appliances displayed in the template based on the new currentMonth value
        updateAppliances("electricity");
    }
    if (type === "gas") {
        // Update the currentMonth element with the new month
        document.getElementById("gasTitle").innerHTML = `Your Gas Cost Breakdown`;
        document.getElementById("gasCurrentMonth").innerHTML = `[${months[currentMonthIndex]}, 2023]`;
        // Update the appliances displayed in the template based on the new currentMonth value
        updateAppliances("gas");
    }
}


async function updateAppliances(type) {
    if (type === "electricity") {
        try {
            // Make a GET request to the server to retrieve updated appliance data for the current month
            const response = await fetch(`/get_appliances/${months[currentMonthIndex]}/${type}`, {
                headers: {
                    'X-Custom-Header': 'costs',
                }
            });
            const data = await response.json();
            // If the response contains updated appliance data, update the template
            if (data) {
                const tbody = document.querySelector("#elec-appliance-list tbody");
                tbody.innerHTML = "";
                console.log("DATA", data)

                totalDailyCost = 0

                if (data.length > 1) {
                    for (let i = 0; i < data.length - 1; i++) {
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
                            <p>£${appliance.dailyCosts}</p>
                        </td>
                        <td>
                            <p>£${appliance.weeklyCosts}</p>
                        </td>
                        <td>
                            <p>£${appliance.monthlyCosts}</p>
                        </td>
                    `;
                        tbody.appendChild(tr);
                    }

                    const tr = document.createElement("tr")
                    tr.classList.add("text-center");

                    tr.innerHTML = `<td colspan="4"><h5 style="margin: 0; padding: 0;"><i style="color:red">Est. Total Daily Cost:</i> <u>£${data[data.length - 1].totalDailyCosts}</u></h5></td>
                        <td colspan="3"><h5 style="margin: 0; padding: 0;"><i style="color:red">Est. Total Weekly Cost:</i> <u>£${data[data.length - 1].totalWeeklyCosts}</u></h5></td>`;
                    tbody.appendChild(tr)

                    const trMonthly = document.createElement("tr")
                    trMonthly.classList.add("text-center");
                    trMonthly.innerHTML = `<td colspan="7"><h5 style="margin: 0; padding: 0;"><i style="color:red">Est. Total Monthly Cost:</i> <u>£${data[data.length - 1].totalMonthlyCosts}</u></h5></td>`;
                    tbody.appendChild(trMonthly)

                } else {
                    const tr = document.createElement("tr");
                    tr.innerHTML = `<td colspan="7" class="fw-bold text-center">You do not have any Electric Appliances added for ${months[currentMonthIndex]}</td>`;
                    tbody.appendChild(tr);
                }
            }
        } catch (error) {
            console.error(error);
        }
    }

    if (type === "gas") {
        try {
            // Make a GET request to the server to retrieve updated appliance data for the current month
            const response = await fetch(`/get_appliances/${months[currentMonthIndex]}/${type}`, {
                headers: {
                    'X-Custom-Header': 'costs',
                }
            });
            const data = await response.json();
            // If the response contains updated appliance data, update the template
            if (data) {
                const tbody = document.querySelector("#gas-appliance-list tbody");
                tbody.innerHTML = "";
                console.log("DATA", data)

                totalDailyCost = 0

                if (data.length > 1) {
                    for (let i = 0; i < data.length - 1; i++) {
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
                            <p>£${appliance.dailyCosts}</p>
                        </td>
                        <td>
                            <p>£${appliance.weeklyCosts}</p>
                        </td>
                        <td>
                            <p>£${appliance.monthlyCosts}</p>
                        </td>
                    `;
                        tbody.appendChild(tr);
                    }

                    const tr = document.createElement("tr")
                    tr.classList.add("text-center");

                    tr.innerHTML = `<td colspan="4"><h5 style="margin: 0; padding: 0;"><i style="color:red">Est. Total Daily Cost:</i> <u>£${data[data.length - 1].totalDailyCosts}</u></h5></td>
                        <td colspan="3"><h5 style="margin: 0; padding: 0;"><i style="color:red">Est. Total Weekly Cost:</i> <u>£${data[data.length - 1].totalWeeklyCosts}</u></h5></td>`;
                    tbody.appendChild(tr)

                    const trMonthly = document.createElement("tr")
                    trMonthly.classList.add("text-center");
                    trMonthly.innerHTML = `<td colspan="7"><h5 style="margin: 0; padding: 0;"><i style="color:red">Est. Total Monthly Cost:</i> <u>£${data[data.length - 1].totalMonthlyCosts}</u></h5></td>`;
                    tbody.appendChild(trMonthly)

                } else {
                    const tr = document.createElement("tr");
                    tr.innerHTML = `<td colspan="7" class="fw-bold text-center">You do not have any Gas Appliances added for ${months[currentMonthIndex]}</td>`;
                    tbody.appendChild(tr);
                }
            }
        } catch (error) {
            console.error(error);
        }
    }
}