$(document).ready(function() {


        // Fetch data from the backend
        async function fetchChartData() {
            const response = await fetch('/generate_chart');
            const data = await response.json();
            return data;
        }

        // Render the chart
        async function renderChart() {
            const chartData = await fetchChartData();

            const ctx = document.getElementById('paymentChart').getContext('2d');
            new Chart(ctx, {
                type: 'bar',  // You can change this to 'bar', 'pie', etc.
                data: {
                    labels: chartData.labels,  // Dates for the X-axis
                    datasets: [{
                        label: 'Total Payments (Last 7 Days)',
                        data: chartData.data,  // Amounts for the Y-axis
                        backgroundColor: 'rgba(75, 192, 192, 0.2)',
                        borderColor: 'rgba(75, 192, 192, 1)',
                        borderWidth: 2
                    }]
                },
                options: {
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        }

        // Call the function to render the chart
        renderChart();



    if(localStorage.getItem('role') !== 'Administrator') {
        window.location.href = '/';
    }

    $.ajax({
        url: "/api/count_total_students",
        method: "GET",
        success: function(response) {
            $('#student_total_count').text(response.total_students);
        }
    })
    $.ajax({
        url: "/api/get_energy_fee",
        method: "GET",
        success: function(response) {
            var energyFee = response.energy_fee;
            if (energyFee === null || energyFee === 0) {
                energyFee = 0.00;
            }
            $('#total_energy_fee').text("₱" + energyFee.toFixed(2));
        },
        error: function(error) {
            console.error('Error fetching energy fee:', error);
            $('#total_energy_fee').text("₱0.00");
        }
    })

    
    $.ajax({
        url: "/api/get_pending_fees",
        method: "GET",
        success: function(response) {
            var pending_fee = response.pending_fee;
            if (pending_fee === null || pending_fee === 0) {
                pending_fee = 0.00;
            }
            $('#total_pending_fee').text("₱" + pending_fee.toFixed(2));
        },
        error: function(error) {
            console.error('Error fetching pending fee:', error);
            $('#total_pending_fee').text("₱0.00");
        }
    })
    
    $.ajax({
        url: "/api/get_fully_paid_fees",
        method: "GET",
        success: function(response) {
            var full_fee = response.full_fee;
            if (full_fee === null || full_fee === 0) {
                full_fee = 0.00;
            }
            $('#total_full_fee').text("₱" + full_fee.toFixed(2));
        },
        error: function(error) {
            console.error('Error fetching full fee:', error);
            $('#total_full_fee').text("₱0.00");
        }
    })
});