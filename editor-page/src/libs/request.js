
function getRequest(url, callback) {
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.onreadystatechange = function() { 
        if (xmlHttp.readyState == 4 && xmlHttp.status == 200) {
        	if(typeof callback === "function") {
	        	try {
	            	callback(JSON.parse(xmlHttp.responseText));
	        	} catch(e) {
	        		callback(xmlHttp.responseText);
	        	}
        	}
        }
        console.log(xmlHttp.readyState);
    }
    xmlHttp.open("GET", url, true); // true for asynchronous 
    xmlHttp.send(null);
}
function postRequest(url, params, callback) {
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.onreadystatechange = function() { 
        if (xmlHttp.readyState == 4 && xmlHttp.status == 200) {
        	if(typeof callback === "function") {
	        	try {
	            	callback(JSON.parse(xmlHttp.responseText));
	        	} catch(e) {
	        		callback(xmlHttp.responseText);
	        	}
        	}
        }
        // console.log(xmlHttp.readyState);
    }
    xmlHttp.open("POST", url, true); // true for asynchronous 
    xmlHttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xmlHttp.send(JSON.stringify(params));
}

module.exports = {
	get: getRequest,
	post: postRequest
}