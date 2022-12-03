//x. funkcja generujaca wykres
//1. zapytanie o histryczne dane
//2. petla wykresow wedlug otrzymanych danych
//3. streamy live wedlug wykresow
//4. zapytanie updateowe dla wszystkich wykresow

function create_chart(currency,data){
  
  var chart = LightweightCharts.createChart(document.querySelector('#'+currency), {
    width: 0,
    height: 0,
    layout: {
      backgroundColor: window.getComputedStyle(document.querySelector('#'+currency)).backgroundColor,
      textColor: 'rgba(255, 255, 255, 0.9)',
    },
    grid: {
      vertLines: {
        color: 'rgba(197, 203, 206, 0.5)',
      },
      horzLines: {
        color: 'rgba(197, 203, 206, 0.5)',
      },
    },
    crosshair: {
      mode: LightweightCharts.CrosshairMode.Normal,
    },
    rightPriceScale: {
      borderColor: 'rgba(197, 203, 206, 0.8)',
    },
    timeScale: {
      borderColor: 'rgba(197, 203, 206, 0.8)',
    },
  
  });
   
  var candleSeries = chart.addCandlestickSeries();
  candleSeries.setData(data);
  new ResizeObserver(entries => {
    if (entries.length === 0 || entries[0].target !== document.querySelector('#'+currency)) { return; }
    const newRect = entries[0].contentRect;
    chart.applyOptions({ height: newRect.height, width: newRect.width });
  }).observe(document.querySelector('#'+currency))
  return candleSeries
}




  data=fetch('http://localhost:5000/data/history')
	.then((r) => r.json())
	.then((response) => {
		var stream_url="wss://stream.binance.com:9443/stream?streams="
    var chartDataList=[]  
    response.forEach(element => {
      
      var singlechart={}
      stream_url=stream_url+element.currency+"@kline_"+element.interval+"/"
      singlechart['data']=create_chart(element.name,element.data);
      singlechart['name']=element.name;
      singlechart['currency']=element.currency;
      singlechart['interval']=element.interval;
      singlechart['kline']=element.currency+"@kline_"+element.interval

      chartDataList.push(singlechart);
    });
		
    return [stream_url,chartDataList];
	}).then((data)=>{
    stream_url=data[0].slice(0, -1)
    

    var binanceSocket = new WebSocket(stream_url);

    binanceSocket.onmessage = function (event) {	
    
    var message = JSON.parse(event.data);
    //console.log(event.data)
    
    //console.log(message)
    data[1].forEach(element=>{
      if(element.kline==message.stream){
        
        var candlestick = message.data.k;
        
        element.data.update({
        time: candlestick.t / 1000,
        open: candlestick.o,
        high: candlestick.h,
        low: candlestick.l,
        close: candlestick.c
      })
      }
    })
   
}
  })



