setTimeout(function () {
    window.location.href = "/main"; // Replace with your desired route
}, 5000); // 55 seconds in milliseconds


// progress bar
var progressBar = $('.progress-bar');
var percentVal = 0;

window.setInterval(function(){
    
    progressBar.css("width", percentVal+ '%').attr("aria-valuenow", percentVal+ '%'); 
    percentVal += 25; // move 25%
    
    if (percentVal > 100)
    {
        percentVal = 0;      
    }

},800); // progress bar change position every 0.8 sec