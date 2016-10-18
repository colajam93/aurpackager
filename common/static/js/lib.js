'use strict';

// enable row click
function enableTableRowClick() {
    $('tr[data-href]').addClass('clickable').click(function (e) {
        if (!$(e.target).is('a')) {
            window.location = $(e.target).closest('tr').data('href');
        }
    });
}

// https://docs.djangoproject.com/en/1.9/ref/csrf/#ajax
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == name + '=') {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method)
    );
}

function initializeModalWindow() {
    const label = document.getElementById('modalLabel');
    label.innerHTML = '';
    const content = document.getElementById('modalContent');
    content.innerHTML = '';
    const extraModalFooter = document.getElementById('extraModalFooter');
    extraModalFooter.innerHTML = '';
}
