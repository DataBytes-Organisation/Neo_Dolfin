var currentLevel='Level 0';
var currentMode='default';
function request_word_cloud(){
    let requestData = {
        level: currentLevel,
        mode: currentMode
    };

    fetch('dash/epv/generate_word_cloud', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestData)
    })
    .then(response => response.json())
    .then(data => {
        let image = data.image;
        let imgTag = document.getElementById('word_cloud');
        imgTag.src = 'data:image/png;base64,' + image;
    })
    .catch(error => console.error('Error:', error));
}

window.onload = function () {
fetch('/dash/epv')
        .then(response => response.json())
        .then(data => {

            var chartDom = document.getElementById('chartContainer');
            var myChart = echarts.init(chartDom);
            var option;
            data.data_cluster[0].selected = true;

            option = {
              tooltip: {
                trigger: 'item',
                formatter: '{a} <br/>{b}: {c} ({d}%)'
              },
              series: [
                {
                  name: 'Expenditure Pattern',
                  type: 'pie',
                  selectedMode: 'single',
                    labelLine: {
                      length: 30
                    },
                  label: {
                    formatter: '{a|{a}}{abg|}\n{hr|}\n  {b|{b}：}${c}  {per|{d}%}  ',
                    backgroundColor: '#F6F8FC',
                    borderColor: '#8C8D8E',
                    borderWidth: 1,
                    borderRadius: 4,
                    rich: {
                      a: {
                        color: '#6E7079',
                        lineHeight: 22,
                        align: 'center'
                      },
                      hr: {
                        borderColor: '#8C8D8E',
                        width: '100%',
                        borderWidth: 1,
                        height: 0
                      },
                      b: {
                        color: '#4C5058',
                        fontSize: 14,
                        fontWeight: 'bold',
                        lineHeight: 33
                      },
                      per: {
                        color: '#fff',
                        backgroundColor: '#4C5058',
                        padding: [3, 4],
                        borderRadius: 4
                      }
                    }
                  },
                  data: data.data_cluster
                }
              ]
            };

            option && myChart.setOption(option);
            request_word_cloud()
            myChart.on('click', function (params) {
                set_current_level_and_mode(params.name.toString())
            console.log('currentLevel:', params.name);
                request_word_cloud()
});
        })
        .catch(error => console.error('Error:', error));
};


function set_current_level_and_mode(level=currentLevel,mode=currentMode){
    currentLevel=level;
    currentMode=mode;
}

function default_onclick(){
    set_current_level_and_mode(currentLevel,'default')
    request_word_cloud()
}

function amount_onclick(){
    set_current_level_and_mode(currentLevel,'amount')
    request_word_cloud()
}