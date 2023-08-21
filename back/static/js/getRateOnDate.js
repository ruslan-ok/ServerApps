function getRateOnDate(init, id_date, id_currency, id_rate, django_host_api='http://localhost:8000') {  // DJANGO_HOST_API
  var el_rate = document.getElementById(id_rate);

  if (!el_rate)
    return;

  if (init == 1) {
    var old_rate = el_rate.value;
    if ((old_rate != "") && (old_rate != "0.0000"))
      return;
  }
  
  var el_date = document.getElementById(id_date);
  if (!el_date)
    return;

  var dt = el_date.value;
  if (dt == "")
    return;
  var z1 = new Date(dt);
  s_date = z1.toISOString().split('T')[0]

  var el_curr = document.getElementById(id_currency);
  if (!el_curr)
    return;

  var currency = el_curr.value;
  if (currency == "")
    return;

  const request = new XMLHttpRequest();
  const url = `${django_host_api}/api/tasks/get_exchange_rate/?currency=${currency}&date=${s_date}&format=json`;
  request.responseType = "json";
  request.open("GET", url, true);
  request.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
  request.addEventListener("readystatechange", () => {
    if (request.readyState === 4 && request.status === 422)
      el_rate.value = '';
    if (request.readyState === 4 && request.status === 200) {
      if (!request.response)
        console.log('[x] Empty response');
      else {
        let obj = request.response;
        console.log(obj);
        var rate = obj.rate_usd;
        console.log(rate);
        el_rate.value = rate;
      }
    }
  });
 
  request.send();
}