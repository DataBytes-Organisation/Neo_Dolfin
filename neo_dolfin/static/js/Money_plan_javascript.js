document.getElementById('calculate-income-btn').addEventListener('click', function() {
    const investmentAmount = parseFloat(document.getElementById('investment-amount').value);
    if (isNaN(investmentAmount)) {
        alert('Please enter a valid investment amount.');
        return;
    }

    // Simple income calculation (can be replaced with a more complex formula)
    const income = investmentAmount * 0.05; // 5% return on investment
    document.getElementById('income-result').innerText = `Projected Income: $${income.toFixed(2)}`;
});

// Example of generating a simple investment chart (can be replaced with a more complex charting library)
const investmentChart = document.getElementById('investment-chart');
for (let i = 1; i <= 10; i++) {
    const investment = 1000 + (i * 500); // Increase investment by $500 every year
    const year = new Date().getFullYear() + i;
    const div = document.createElement('div');
    div.textContent = `${year}: $${investment}`;
    investmentChart.appendChild(div);
}
