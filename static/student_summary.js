$(document).ready(function() { 
    const student_id = localStorage.getItem('student_id');
    console.log(student_id);
    $('#payments_table').DataTable({
        "order": [[ 0, "desc" ]],
        "processing": true,
        "serverSide": true,
        "ajax": {
            "url": "/api/fetch_payments_student",
            "type": "GET",
            data: {
                student_id: student_id
            }
        },
        "columns": [
            { "data": "id" },
            { "data": "transaction_timestamp" },
            { "data": "payment_type" },
            { "data": "amount" },
            { "data": "status" },
            { "data": "transaction_completed" }
        ],
        "createdRow": function(row, data, dataIndex) {
            if (data.status === 'Fully Paid') {
                $(row).addClass('table-success');
            } else if (data.status === 'Unpaid') {
                $(row).addClass('table-danger');
            }
        }
    });
});