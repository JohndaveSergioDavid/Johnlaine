$(document).ready(function() {
    if(localStorage.getItem('role') !== 'Administrator') {
        window.location.href = '/';
    }
    var paymentsTable = $('#payments_table').DataTable({
        "processing": true,
        "serverSide": true,
        "ajax": {
            "url": "/api/fetch_payments_records",
            "type": "GET"
        },
        "columns": [
            { "data": "id" },
            { "data": "transaction_timestamp" },
            { "data": "student_id" },
            { "data": "name" },
            { "data": "payment_type" },
            { "data": "amount" },
            { "data": "status" },
            { "data": "transaction_completed" },
        ],
        "createdRow": function(row, data, dataIndex) {
            if (data.status === 'Fully Paid') {
                $(row).addClass('table-success');
            } else if (data.status === 'Partially Paid') {
                $(row).addClass('table-warning');
            } else if (data.status === 'Unpaid') {
                $(row).addClass('table-danger');
            }
        }
    });
    $.ajax({
        url: "/api/get_payment_type",
        method: "GET",
        success: function(response) {
            var paymentTypeSelect = $('#payment_type');
            response.forEach(function(paymentType) {
                paymentTypeSelect.append(new Option(paymentType[1], paymentType[0]));
                paymentTypeSelect.data('amount-' + paymentType[0], paymentType[2]);
            });
        },
        error: function(error) {
            console.error('Error fetching payment types:', error);
        }
    });

    $('#payment_type').change(function() {
        var selectedPaymentType = $(this).val();
        var amount = $(this).data('amount-' + selectedPaymentType);
        $('#amount').val(amount);
    });
    $('#savePayment').click(function() {
        $.ajax({
            url: "/api/add_payment",
            method: "POST",
            data: {
                student_id: $('#student_id').val(),
                payment_type: $('#payment_type').val(),
                amount: $('#amount').val(),
                status: $('#status').val()
            },
            success: function(response) {
                console.log(response);
                $('#payments_table').DataTable().ajax.reload();
                $('#addPaymentModal').modal('hide');
            },
            error: function(error) {
                console.error('Error adding payment:', error);
            }
        });
    });
});