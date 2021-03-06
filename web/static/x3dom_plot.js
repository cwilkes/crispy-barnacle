function plotAxis(scale, location, size, numTicks) {
    // the axis line
    var shape = scene.append("x3d:transform")
        .attr("translation",location.replace("D",(scale.range()[0]+scale.range()[1])/2))
        .append("x3d:shape");

    shape.append('x3d:appearance')
        .append('x3d:material')
        .attr("diffuseColor", function(){ return ".5 .5 .5"; });

    shape.append("x3d:box")
        .attr("size",location.replace(/0/g,size).replace("D",scale.range()[1]));


    // ticks along the axis
    ticks = scene.selectAll("abcd").data(scale.ticks(numTicks))
        .enter()
        .append("x3d:transform")
            .attr("translation", function(d) { return location.replace("D",scale(d))})

        ticks
            .append("x3d:shape")
                .append("x3d:box")
                    .attr("size",size*3+" "+size*3+" "+size*3);

    var billboard = ticks
            .append("x3d:billboard").append("x3d:shape");

    billboard.append('x3d:appearance')
        .append('x3d:material')
        .attr("diffuseColor", function(){ return ".5 .5 .5"; });

    billboard
                .append("x3d:text")
                    .attr("string",scale.tickFormat(10))
                    .attr("solid","true")
                    .append("x3d:fontstyle").attr("size",0.6).attr("justify","MIDDLE" )

}


function plotData() {
    datapoints = datapoints.data(d3.range(500).map(function() { return {x:Math.random()*100,y:Math.random()*100,z:Math.random()*100}}))

    datapoints.exit().remove()  // Remove any excess datapoints, if needed

    var shape = datapoints.enter()          // Draw a box for each new datapoint
        .append("x3d:transform")
            .attr("class","datapoints")
            .append("x3d:shape");

    shape.append('x3d:appearance')
        .append('x3d:material')
        .attr("diffuseColor", function(){ return Math.random()+' '+Math.random()+" "+Math.random(); });

    shape.append("x3d:box")
        .attr("size", "0.2 0.2 0.2");

    datapoints.transition()  // Move each box to the right point location
        .duration(2000)
        .attr("translation",function(d) { return x(d.x)+" "+y(d.y)+" "+z(d.z)})

}

function doPlot() {
// Create the x3d scene
    d3.ns.prefix.x3da = "http://www.web3d.org/specifications/x3d-namespace"
    x3d = d3.select("body")
        .append("x3d:x3d")
        .attr("height", "500px")
        .attr("width", "100%");
    scene = x3d.append("x3d:scene")


// set up the axes
    var x = d3.scale.linear().domain([0, 100]).range([0, 10]),
        y = d3.scale.linear().domain([0, 100]).range([0, 10]),
        z = d3.scale.linear().domain([0, 100]).range([0, 10]);

    plotAxis(x, "D 0 0", 0.01, 10)
    plotAxis(y, "0 D 0", 0.01, 10)
    plotAxis(z, "0 0 D", 0.01, 10)


// and plot random data every 2500 ms
    var datapoints = scene.selectAll(".datapoints");
    plotData();
    setInterval(plotData, 2500);


// zoom out the viewport
    setTimeout(function () {
        x3d[0][0].runtime.showAll()
    }, 50);

}
