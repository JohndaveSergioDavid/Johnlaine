$(document).ready(function() {
    var studentTable = $('#student_table').DataTable({
        "processing": true,
        "serverSide": true,
        "ajax": {
            "url": "/api/fetch_students_records",
            "type": "GET"
        },
        "columns": [
            { "data": "id" },
            { "data": "lrn" },
            { "data": "firstname" },
            { "data": "lastname" },
            { "data": "email" },
            { "data": "strand" },
            {
                "data": null,
                "defaultContent": `
                <div class = "btn-group">
                <button class="btn btn-primary btn-sm edit-btn">Edit</button>
                <button class="btn btn-dark btn-sm edit-btn">Change Password</button>
                </div>
                `
            }
        ]
    });

    $.ajax({
        url: "/api/get_strand_choices",
        method: "GET",
        success: function(response) {
            var strandSelect = $('#strand');
            var editStrandSelect = $('#edit_strand');
            response.forEach(function(strand) {
                strandSelect.append(new Option(strand[1], strand[0]));
                editStrandSelect.append(new Option(strand[1], strand[0]));
            });
        },
        error: function(error) {
            console.error('Error fetching strand choices:', error);
        }
    });

    $('#saveStudent').click(function() {
        $.ajax({
            url: "/api/add_student",
            method: "POST",
            data: {
                lrn: $('#lrn').val(),
                firstname: $('#firstname').val(),
                lastname: $('#lastname').val(),
                email: $('#email').val(),
                strand_id: $('#strand').val(),
                username: $('#username').val(),
                password: $('#password').val()
            },
            success: function(response) {
                console.log(response);
                $('#student_table').DataTable().ajax.reload();
                $('#exampleModal').modal('hide');
            },
        })
    });


    $('#student_table tbody').on('click', '.edit-btn', function() {
        var data = studentTable.row($(this).parents('tr')).data();
        console.log(data);
        $('#edit_id').val(data.id);
        $('#edit_lrn').val(data.lrn);
        $('#edit_firstname').val(data.firstname);
        $('#edit_lastname').val(data.lastname);
        $('#edit_email').val(data.email);
        $('#edit_strand').val(data.strand_id); // Assuming strand_id is available in the data
        $('#edit_username').val(data.username);
        $('#edit_password').val('');
        $('#editModal').modal('show');
    });

    $('#updateStudent').click(function() {
        $.ajax({
            url: "/api/update_student",
            method: "POST",
            data: {
                id: $('#edit_id').val(),
                lrn: $('#edit_lrn').val(),
                firstname: $('#edit_firstname').val(),
                lastname: $('#edit_lastname').val(),
                email: $('#edit_email').val(),
                strand_id: $('#edit_strand').val(),
            },
            success: function(response) {
                console.log(response);
                $('#student_table').DataTable().ajax.reload();
                $('#editModal').modal('hide');
            },
        })
    });
});