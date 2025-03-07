$(document).ready(function() {
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