var svg = dimple.newSvg("#plot", 800, 600);

function replot(data) {
    svg.selectAll('*').remove();

    var myChart = new dimple.chart(svg, data);
    var x = myChart.addCategoryAxis("x", "date");
    var y = myChart.addMeasureAxis("y", "n_clashes");
    x.title = "Date";
    y.title = "Number of clashes";
    y.tickFormat = "d";

    var series = myChart.addSeries('group', dimple.plot.line, [x, y]);
    series.data = data[$('#grouping').val()];

    myChart.addLegend(60, 10, 500, 60, "right");
    myChart.draw();
}

$.getJSON($('#data_url').text(), function (response) {
    var data = response;
    $.each(data, function (key, value) {
        $('#grouping').append($('<option>', {value: key}).text(key));
    });
    $('#grouping option[value="Total clashes"]').attr('selected', true);
    replot(data);

    var mySelect = document.getElementById("grouping");
    mySelect.addEventListener('change', function () {
        var current_grouping = $('#grouping').val();
        replot(data);
        if (current_grouping === 'Total clashes') {
          $('#description').html('Summary of clashes over time');
        } else {
          $('#description').html('Summary of clashes over time as grouped by ' + $('#grouping').val().toLowerCase());
        }
    });
});
