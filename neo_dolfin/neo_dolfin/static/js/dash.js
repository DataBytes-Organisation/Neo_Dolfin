//variables used for the data calculation of the dashborad
var previousMonthTotal = 0.00; // Initialize the total balance for the previous month
var previousMonthBalance = null;// Initialize the balance for the previous month

var monthsData = []; // Array to store months for the line chart
var balanceData = []; // Array to store balances for the line chart
var flagMonth = 0;//flag to Check if we have moved to a new month for drawing the line chart monthly balance
var currentMonthLine = null;//Check if we have moved to a new month for drawing the line chart monthly balance 

// Fetch data from the CSV file
fetch('/static/data/transaction_ut.csv')
    .then(response => response.text())
    .then(data => {
        data = data.trim();
        // Parse the CSV data into an array of objects
        var rows = data.split('\n');
        var spendingData = {};
        var balance = 0.00;

        for (var i = 1; i < rows.length; i++) {
            //var cols = rows[i].split(',');
            var cols = rows[i].split(',');

            // Extract the date from the "postDate" column (assuming it's in the format yyyy-MM-dd)
            var postDate = cols[13].split('T')[0];
            var postMonth = new Date(postDate).getMonth() + 1; // Get the month (0-indexed)
            var postYear = new Date(postDate).getFullYear();//Get the year
            var currentYear = new Date().getFullYear(); // Get the current year

            // Get the current month (0-indexed)
            var currentDate = new Date();
            var currentMonth = currentDate.getMonth();

            //posting the balance of the previous month in the field Balance
            if (postMonth === currentMonth && previousMonthBalance === null) {
                previousMonthBalance = parseFloat(cols[6]); // Assuming balance is in the 7th column
                document.getElementById("balance").textContent = previousMonthBalance;
            }

            // line chart graph
            // Check if we have moved to a new month for the line chart
            if (postMonth !== currentMonthLine) {
                flagMonth = 0;

            }
            if (flagMonth == 0) {
                // Push the month and balance data into the arrays
                monthsData.push(postDate);
                balanceData.push(parseFloat(cols[6]));
                flagMonth = 1;
                currentMonthLine = postMonth;
            }

            // pie chart for all the expensesof the previous month
            // the expensives are negative values in the csv file
            if (postMonth === currentMonth && postYear === currentYear) {
                //      balance += parseFloat(cols[2]);
                var value = parseFloat(cols[4]);

                if (cols.length > 10 && parseFloat(cols[4]) < 0) {
                    var label = cols[8].trim();
                    var value = parseFloat(cols[4]);

                    if (label.length > 20) {
                        label = label.replace(/(.{15})/g, "$1<br>");
                    }

                    // Check if the label already exists in the spendingData
                    if (spendingData[label]) {
                        // If it exists, add the value to the existing total
                        spendingData[label] += Math.abs(value);
                    } else {
                        // If it doesn't exist, create a new entry
                        spendingData[label] = Math.abs(value);
                    }
                }
                // add all the expensives together
                previousMonthTotal += value;

            }
        }
        // Convert the spendingData object into arrays for plotting
        var labels = Object.keys(spendingData);
        var values = labels.map(function (label) {
            return spendingData[label];
        });

        // Create the pie chart
        var layout = {
            title: "Spending Categories over the month",
            width: 500, // Set the width (in pixels)
            height: 500 // Set the height (in pixels)
        };

        var plotData = {
            values: values,
            labels: labels,
            type: "pie"
        };

        Plotly.newPlot("piechart", [plotData], layout);
        // displaying the balance of the previous month in the field closing balance "previous month" 
        document.getElementById("previous-month-balance").textContent = previousMonthTotal;

        // Create the line chart
        createLineChart(monthsData, balanceData);

        // Calculate if there has been a positive return over a year
        var currentYear1 = new Date().getFullYear();
        var isPositiveReturn = false; // Initialize as false
        var balanceIncreased = false; // Initialize as false

        // Check if there are at least two months of data for comparison
        if (monthsData.length >= 2) {
            var currentMonthBalance1 = balanceData[0]; // Get the balance for the current month
            var previousMonthBalance1 = balanceData[1]; // Get the balance for the previous month

            // Check if the current month's balance increased from the previous month
            if (currentMonthBalance1 > previousMonthBalance1) {
                balanceIncreased = true;
            }

        }
        // Display the result on the screen
        var returnStatusElement = document.getElementById("return-status");

        if (balanceIncreased) {
            returnStatusElement.textContent = "Positive Return";
            returnStatusElement.style.fill = "blue"; // Set text color to blue for positive return without increased balance
            document.getElementById("return-status-line2").style.fill = "blue";
            document.getElementById("balanceDifference").style.fill = "blue";
        } else {
            returnStatusElement.textContent = "No Positive Return";
            returnStatusElement.style.fill = "red"; // Set text color to red for no positive return
            document.getElementById("return-status-line2").style.fill = "red";
            document.getElementById("balanceDifference").style.fill = "red";
        }
        document.getElementById("return-status-line2").textContent = "For the month";
        document.getElementById("balanceDifference").textContent = currentMonthBalance1 - previousMonthBalance1;

    })
    .catch(error => console.error(error));

// Fetch data from the CSV file
fetch('/static/data/Predicted_Balances.csv')
    .then(response => response.text())
    .then(data1 => {
        data1 = data1.trim();
        // Parse the CSV data into an array of objects
        var rows1 = data1.split('\n');
        var monthlyData = {}; // Object to store monthly data

        // Loop through the rows and extract the necessary data
        for (var i = 1; i < rows1.length; i++) {
            var cols = rows1[i].split(','); // Split by tab character
            var postDate = cols[0]; // Date with balance
            var dateSegments = postDate.split('\t'); // Split date by tab
            var balance = parseFloat(dateSegments[dateSegments.length - 1]); // Balance is in the last segment

            // Extract the year and month from the date (assuming yyyy-MM-dd format)
            var [year, month, _] = dateSegments[0].split('-');

            // Create a unique key for the month (e.g., "2023-03")
            var monthYear = year + '-' + month;

            // If the monthYear doesn't exist in monthlyData, initialize it
            if (!monthlyData[monthYear]) {
                monthlyData[monthYear] = [];
            }

            // Push the mean balance into the corresponding month
            monthlyData[monthYear].push(balance);
        }

        // Calculate the mean balance for each month
        var sortedMonthYears = Object.keys(monthlyData).sort();
        var sortedBalances = sortedMonthYears.map(monthYear => {
            var monthlyBalances = monthlyData[monthYear];
            var sum = monthlyBalances.reduce((acc, val) => acc + val, 0);
            var meanBalance = sum / monthlyBalances.length;
            return meanBalance + 22109.56
        });

        // Create the line chart
        createLineChart2(sortedMonthYears, sortedBalances, 'line-chart-2'); // Pass a unique ID for the new chart

    })
    .catch(error => console.error(error));





// Function to create the line chart
function createLineChart(xData, yData) {
    var lineChart = {
        x: xData,
        y: yData,
        type: 'scatter',
        mode: 'lines+markers',
        name: 'Balance',
        line: {
            shape: 'linear',
            color: 'blue',
        },
        marker: {
            size: 8,
            color: 'blue',
        },
    };

    var lineLayout = {
        title: 'Monthly Balance',
        xaxis: {
            title: 'Month',
            showgrid: true,
            tickvals: xData,  // Specify the tick values
            ticktext: xData,  // Specify the tick labels
        },
        yaxis: {
            title: 'Balance',
        },
        margin: {
            t: 30,
        },
    };

    var lineChartConfig = [lineChart];

    Plotly.newPlot('line-chart', lineChartConfig, lineLayout);
}

function createLineChart2(xData1, yData1) {
    var lineChart = {
        x: xData1,
        y: yData1,
        type: 'scatter',
        mode: 'lines+markers',
        name: 'Balance',
        line: {
            shape: 'linear',
            color: 'green',
        },
        marker: {
            size: 8,
            color: 'green',
        },
    };

    var lineLayout = {
        title: 'Predicted Balance',
        xaxis: {
            title: 'Monthly',
            showgrid: true,
            tickvals: xData1,  // Specify the tick values
            ticktext: xData1,  // Specify the tick labels
        },
        yaxis: {
            title: 'Predicted Balance',
        },
        margin: {
            t: 30,
        },
    };

    var lineChartConfig = [lineChart];

    Plotly.newPlot('line-chart2', lineChartConfig, lineLayout);
}

// Get the current date
var currentDate = new Date();

// Calculate the previous month
var previousMonth = new Date(currentDate);
previousMonth.setMonth(previousMonth.getMonth() - 1);

// Create an array of month names
var monthNames = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];

// Get the name of the previous month
var previousMonthName = monthNames[previousMonth.getMonth()];

// Set the previous month name in the <span> element
document.getElementById("previous-month-name").textContent = previousMonthName;