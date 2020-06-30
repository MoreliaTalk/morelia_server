function chekrazmer(){
	if (document.documentElement.clientWidth < 670) {
		document.getElementById("zag").style.marginBottom = "-10px";
		document.getElementById("zag").style.marginTop = "-10px";
	}else{
		document.getElementById("zag").style.marginBottom = "0px";
		document.getElementById("zag").style.marginTop = "0px";
	}
}
setInterval(chekrazmer)
