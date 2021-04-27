// plotly_click.js
var plot = document.getElementById("{plot_id}");  // 出力した<div>要素を取得
var info = document.getElementById("plotly-node-info"); // Tableを表示するための<div>要素（今回は、plotly-node-infoというID）を取得
plot.on('plotly_selected', function (data) { // plotly_selectedというイベントをトリガーにする
    {
        var points = data.points;
        //console.log(Object.values(data))
        while (info.firstChild) info.removeChild(info.firstChild);
        for (p in points) {
            info.appendChild(DictToFlow(points[p]));// dict形式のcustomdataからTableを生成して、<div>要素の子要素として追加
        }
    }
})
function DictToTable(data) {
    var table = document.createElement("table");
    //table.border = '1';
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
function DictToFlow(data) {
    var flow = document.createElement("ul");
    flow.className = "arrowlist";
    flow.title = "Change Log";

    var li1 = document.createElement('li');
    li1.appendChild(DictToTable(data.customdata));
    flow.appendChild(li1);

    var c_file = Object.values(data.customdata)[8]
    console.log(c_file)
    var c_date = Object.values(data.customdata)[1]
    console.log(c_date)
    for (p=Object.values(data)[0]["selectedpoints"][0]-1; p>=0; p--) {
        //if (data.data.customdata[p]["File_name"] == c_file && data.data.customdata[p]["author_date"] < c_date) {
        if (data.data.customdata[p]["author_date"] < c_date) {
        var li = document.createElement('li');
        li.appendChild(DictToTable(data.data.customdata[p]));
        flow.appendChild(li);
        c_file = data.data.customdata[p]["original_file"]
        c_date = data.data.customdata[p]["author_date"]
        if (c_file == null) break;
        }
        }

    return flow;
}