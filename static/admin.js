$(document).ready(function() {
    if(localStorage.getItem('role') !== 'Administrator') {
        window.location.href = '/';
    }

    $.ajax({
        url: "/api/count_total_students",
        method: "GET",
        success: function(response) {
            console.log(response);
            $('#student_total_count').text(response.total_students);
        }
    })
});