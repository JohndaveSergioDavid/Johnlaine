document.getElementById('loginForm').addEventListener('submit', function(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);
    fetch(form.action, {
      method: form.method,
      body: formData
    })
    .then(response => {
      if (response.headers.get('content-type')?.includes('application/json')) {
        return response.json();
      } else {
        throw new Error('Login failed! Please check your username and password.');
      }
    })
    .then(data => {
      if (data.username && data.role) {
        localStorage.setItem('username', data.username);
        localStorage.setItem('role', data.role);

        if(data.role == "Student") {
          localStorage.setItem('student_id', data.student_id);
        }
        else if(data.role == "Adviser") {
          localStorage.setItem('adviser_id', data.adviser_id);
        }

        window.location.href = data.redirect_url;
      }
    })
    .catch(error => {
      console.error('Error:', error);
      alert(error.message);
      $('#username').val('');
      $('#password').val('');
      $('#username').focus();
    });
  });

$(document).ready(function() {
    if (localStorage.getItem('role') === 'Administrator') {
        window.location.href = '/admin';
    }
    else if(localStorage.getItem('role') === 'Student') {
        window.location.href = '/student';
    }
    else if(localStorage.getItem('role') === 'Adviser') {
        window.location.href = '/adviser';
    }
});