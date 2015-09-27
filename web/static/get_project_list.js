

$.get('/projects', function(response) {
    var data = response.split('\n')
    var cp = $("#current_project").text()
    console.log("Current project: ", cp)
    $.each(data, function (index, value) {
        value = value.trim()
        if (cp == value) {
            $('#projects').append($('<option>', {key: value, selected: 'true'}).text(value));
        } else {
            $('#projects').append($('<option>', {key: value}).text(value));
        }
    });
})


 var mySelect2 = document.getElementById("projects");
    mySelect2.addEventListener('change', function () {
        var l = $(location)[0]
        var newUrl = "http://" + l.host + l.pathname + "?project=" + $("#projects").val()
        console.log("new url", newUrl)
        $(location)[0].href = newUrl
    });
