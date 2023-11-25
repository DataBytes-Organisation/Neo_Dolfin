
    window.onload = function () {
      var chartDom = document.getElementById('chartContainer');
      var myChart = echarts.init(chartDom);

      
      var option = {
        tooltip: {
          trigger: 'item',
          formatter: '{a} <br/>{b}: {c} ({d}%)'
        },
      
        series: [
          {
            name: 'Expenditure Sturcture',
            type: 'pie',
            selectedMode: 'single',
            radius: [0, '30%'],
            label: "",
            labelLine: {
              show: false
            },
            data: [
              { value: 186695.0, name: 'Level 2' },
              { value: 33252.53, name: 'Level 0' },
              { value: 103785.85, name: 'Level 1' }
            ]
          },
          {
            name: 'Expenditure Pattern',
            type: 'pie',
            radius: ['45%', '60%'],
            selectedMode: 'single',
            labelLine: {
              length: 30
            },
            label: {
              formatter: '{a|{a}}{abg|}\n{hr|}\n  {b|{b}：}{c}  {per|{d}%}  ',
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
            data: [
              { value: 6289, name: 'Clothes' },
              { value: 8129, name: 'Energy' },
              { value: 9011, name: 'Entertainment' },
              { value: 39897, name: 'Food' },
              { value: 9025, name: 'Others' },
              { value: 6372, name: 'Phone' },
              { value: 62045, name: 'Rent' }
            ]
          }
        ]
      };

      myChart.setOption(option);

      var outerSeriesName = 'Expenditure Pattern';
      var innerSeriesName ='Expenditure Sturcture';

      var outerSeriesIndex = myChart.getOption().series.findIndex(series => series.name === outerSeriesName);
      var innerSeriesIndex = myChart.getOption().series.findIndex(series => series.name === innerSeriesName);


      myChart.on('mouseover', function (params) {
        var hoveredIndex = params.seriesIndex;

        if (hoveredIndex === outerSeriesIndex) {
          option.series[outerSeriesIndex].radius = ['45%', '65%'];
      option.series[innerSeriesIndex].radius = [0, '30%'];
        } else if (hoveredIndex === innerSeriesIndex) {
          option.series[outerSeriesIndex].radius = ['75%', '85%'];
      option.series[innerSeriesIndex].radius = [0, '65%'];
        }

        myChart.setOption(option);
        var imageElement = document.getElementById('image');
        imageElement.style.opacity = 0;
      });


      myChart.on('click', function (params) {
  var clickedIndex = params.seriesIndex;


  if (clickedIndex === outerSeriesIndex) {

    var imageElement = document.getElementById('image');
    imageElement.src = '../static/img/word_cloud.png';


    imageElement.width = 300;  
    imageElement.height = 200; 


    imageElement.style.position = 'absolute'; 
    imageElement.style.top = '50px';         
    imageElement.style.left = '1000px';        
  } else if (clickedIndex === innerSeriesIndex) {

    var imageElement = document.getElementById('image');
    imageElement.src = '../static/img/word_cloud_2.png';

    imageElement.width = 400;  
    imageElement.height = 250; 

  
    imageElement.style.position = 'absolute'; 
    imageElement.style.top = '50px';        
    imageElement.style.left = '1000px';       
  }
  setTimeout(function () {
          imageElement.style.opacity = 1;
        }, 50); 
      });




      myChart.on('mouseout', function () {
        myChart.setOption(option);
      });
    }