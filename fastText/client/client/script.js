function goodorbadColor(howmuch) {
	var redAmount = Math.min(2 * (1 - howmuch), 1);
	var greenAmount = Math.min(howmuch * 2, 1);
	var res = "rgba(" + parseInt(redAmount * 255) + ", " + parseInt(greenAmount * 255) + ", 0, 0.7)";
	console.log(res);
	return res;
}
function transferFailed(error) {
	console.log("ERROR :(", error);
}

function fetchCategories(text, callback) {
	var url = "http://localhost:3000/fetch_categories/";
	var request = new XMLHttpRequest();
	request.addEventListener('load', function(response) {
		console.log(response);
		if(typeof callback == "function") {
			var json = {error: ":("};
			try {
				json = JSON.parse(response.currentTarget.response);
			} catch(e) {
				transferFailed({error: ":("});
			}
			callback(json);
		}
	});
	request.addEventListener("error", transferFailed);
	request.addEventListener("abort", transferFailed);
	request.open("POST", url);
	//Send the proper header information along with the request
	request.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
	request.send("text=" + encodeURIComponent(text));
}

window.addEventListener('load', function() {
	var timeOutNumber = -1;
	document.querySelector('.large-text').addEventListener('input', function(event) {
		console.log(event.target.value);
		clearTimeout(timeOutNumber);
		timeOutNumber = setTimeout(function() {
			fetchCategories(event.target.value, function (response) {
				var container = document.querySelector('.categories');
				while(container.firstChild) {
					container.removeChild(container.firstChild);
				}
				for(var i in response.keywords) {
					var category = response.keywords[i];
					category.label = category.label;
					var categoryElm = document.createElement('span');
					categoryElm.classList.add('category');
					categoryElm.style.borderColor = goodorbadColor(category.probability);
					category.probability = Math.round(category.probability * 1000)/10 + ' %';
					categoryElm.innerHTML = category.label + ' ' + category.probability;
					container.appendChild(categoryElm);
				}
				document.querySelector('.summary').innerHTML = response.abstract;
			});
		}, 1000);
	});
	document.querySelector('.large-text').addEventListener('focus', function (event) {
		this.selectionStart = 0;
		this.selectionEnd = this.value.length;
	})
});