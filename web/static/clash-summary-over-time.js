var svg = dimple.newSvg("#plot", 800, 600);

function replot(data) {
    svg.selectAll('*').remove();
    console.log($('#grouping').val())
    console.log(data['owner'])

    var myChart = new dimple.chart(svg, data);
    var x = myChart.addCategoryAxis("x", "date");
    var y = myChart.addMeasureAxis("y", "n_clashes");

    var series = myChart.addSeries('group', dimple.plot.line, [x, y]);
    series.data = data[$('#grouping').val()];

    myChart.addLegend(60, 10, 500, 60, "right");
    myChart.draw();
}

$.getJSON($('#data_url').text(), function (response) {
    var data = response;
    $.each(data, function (key, value) {
        $('#grouping').append($('<option>', {key: key}).text(key));
    });
    replot(data);

    var mySelect = document.getElementById("grouping");
    mySelect.addEventListener('change', function () {
        replot(data)
    });
});
