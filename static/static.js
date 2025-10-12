function getLocation(){
    if (navigator.geolocation){
        navigator.geolocation.getCurrentPosition(showPosition, showError);
    } else {
        alert("Geolocation is not supported by this browser")
    }
}
function showPosition(position){
    const longitude =position.coords.longitude;
    const latitude = position.coords.latitude

    //display in input thing box
    document.getElementById("location").value = latitude + ", " + longitude;

    //will send to the backend views.py
    // fetch("/save-location/", {
    //     method: "POST",
    //     headers: {
    //         "Content-Type": "application/json",
    //         "X-CSRFTOKEN": getcookie("csrftoken")
    //     },
    //     body: JSON.stringify({location:  latitude + ", " + longitude})
    // })
    // .then(response => response.json())
    // .then(data=>{
    //     console.log("Location saved:", data); 
    // })
    // .catch(error =>{
    //     console.error("Error:", Error);
    // });    
}


function showError(error){
    switch(error.code) {
        case error.PERMISSION_DENIED:
            alert("User denied the request for Geolocation.");
            break;
        case error.POSITION_UNAVAILABLE:
            alert("Location information is unavailable.");
            break;
        case error.TIMEOUT:
            alert("The request to get user location timed out.");
            break;
        case error.UNKNOWN_ERROR:
            alert("An unknown error occurred.");
            break;
    }
}

// function getCookie(name) {
//     let cookieValue = null;
//     if (document.cookie && document.cookie !== '') {
//         const cookies = document.cookie.split(';');
//         for (let i = 0; i < cookies.length; i++) {
//             const cookie = cookies[i].trim();
//             if (cookie.substring(0, name.length + 1) === (name + '=')) {
//                 cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
//                 break;
//             }
//         }
//     }
//     return cookieValue;
// }

// things to find nearby hospital
function findHospital(){
    const locationInput = document.getElementById("location").value;

    if (!locationInput) {
        alert("Please set your location first!");
        return;
    }

    const [lat, lon] = locationInput.split(",").map(x => x.trim());

    fetch(`/get_hospitals/?lat=${lat}&lon=${lon}`)
        .then(response => response.json())
        .then(data => {
            // ✅ now target dummy select
            const hospitalSelect = document.getElementById("dummy_hospital");  
            hospitalSelect.innerHTML = ""; // clear old options

            if (data.hospitals.length === 0) {
                hospitalSelect.innerHTML = `<option>No hospitals found nearby</option>`;
            } else {
                data.hospitals.forEach(h => {
                    let opt = document.createElement("option");
                    opt.value = h.id;
                    opt.textContent = h.name;
                    hospitalSelect.appendChild(opt);
                });
            }
        })
        .catch(error => console.error("Error fetching hospitals:", error));
}

