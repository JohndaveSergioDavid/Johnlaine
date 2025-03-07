$(document).ready(function() { 
    const adviser_id = localStorage.getItem('adviser_id');
    $('#section_handle_table').DataTable({
        "processing": true,
        "serverSide": true,
        "ajax": {
            "url": "/api/fetch_section_handle",
            "type": "GET",
            data: {
                adviser_id: adviser_id
            }
        },
        "columns": [
            { "data": "id" },
            { "data": "name" },
        ],
    });

    var paymentsTable = $('#payments_table').DataTable({
        "processing": true,
        "serverSide": true,
        "ajax": {
            "url": "/api/adviser_fetch_payments_records",
            "type": "GET",
            "data": {
                adviser_id: adviser_id
            }
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
            {
                "data": null,
                "defaultContent": '<button class="btn btn-primary btn-sm edit-btn">Edit</button>'
            }
        ],
        "createdRow": function(row, data, dataIndex) {
            if (data.status === 'Fully Paid') {
                $(row).addClass('table-success');
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
            var editPaymentTypeSelect = $('#edit_payment_type');
            response.forEach(function(paymentType) {
                paymentTypeSelect.append(new Option(paymentType[1], paymentType[0]));
                editPaymentTypeSelect.append(new Option(paymentType[1], paymentType[0]));
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

    $('#payments_table tbody').on('click', '.edit-btn', function() {
        $('#edit_payment_type').focus();
        var data = paymentsTable.row($(this).parents('tr')).data();
        $('#edit_id').val(data.id);
        $('#edit_payment_type').val(data.payment_type);

        var payment_type = data.payment_type;
        $.ajax({
            url: "/api/get_payment_type_id",
            method: "GET",
            data: {
                payment_type_name: payment_type
            },
            success: function(response) {
                var paymentTypeSelect = $("#paymentTypeDropdown");
                paymentTypeSelect.append(new Option(payment_type, response));
                $('#edit_payment_type').val(response[0]);
            },
            error: function(error) {
                console.error('Error fetching payment type id:', error);
            }
        });
        $('#edit_amount').val(data.amount);
        $('#edit_status').val(data.status);
        $('#editPaymentModal').modal('show');
    });

    $('#edit_payment_type').on('change', function() {
        var selectedPaymentType = $(this).val();
        $.ajax({
            url: "/api/get_payment_type_amount",
            method: "get",
            data: {
                payment_type_id: selectedPaymentType
            },
            success: function(response) {
                $('#edit_amount').val(response[0]);
            },
            error: function(error) {
                console.error('Error fetching payment type amount:', error);
            }
        })
    });

    $('#updatePayment').click(function() {
        $.ajax({
            url: "/api/update_payment",
            method: "POST",
            data: {
                id: $('#edit_id').val(),
                payment_type: $('#edit_payment_type').val(),
                amount: $('#edit_amount').val(),
                status: $('#edit_status').val()
            },
            success: function(response) {
                $('#payments_table').DataTable().ajax.reload();
                $('#editPaymentModal').modal('hide');
                $('#editPaymentForm')[0].reset();
            },
            error: function(error) {
                console.error('Error updating payment:', error);
            }
        });
    });
});