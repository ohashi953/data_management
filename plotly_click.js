// plotly_click.js
var plot = document.getElementById("{plot_id}");  // Note1
var info = document.getElementById("plotly-node-info"); // Note2
plot.on('plotly_selected', function (data) { // Note3
    {
        var points = data.points;
        console.log(points[0].customdata)
        while (info.firstChild) info.removeChild(info.firstChild);
        for (p in points) {
            info.appendChild(DictToTable(points[p].customdata));// Note4
        }
    }
})
function DictToTable(data) {
    var table = document.createElement("table");
    table.border = '1';
    for (key in data) {
        var tr = document.createElement('tr');
        var th = document.createElement('th');
        var td = document.createElement('td');
        th.textContent = key;
        td.textContent = data[key];
        tr.appendChild(th);
        tr.appendChild(td);
        table.appendChild(tr);
    }
    return table;
}