
	function renderRect(ctx, percentage, color, width, height) {
		ctx.fillStyle = "#000";
		ctx.fillRect(percentage * width - 6,height/2 - 6,12,27);
		ctx.fillStyle = color;
		ctx.fillRect(percentage * width - 5,height/2 - 5,10,25);
	}
	function renderSlider (percentage) {
		// var canvas = document.getElementById("polarity").getElementsByTagName("canvas")[0];
		canvas.height = 110;
		canvas.width = canvas.parentNode.offsetWidth;
		// canvas.style.borderRadius = "40px";
		// canvas.style.boxShadow = "0 0 40px rgba(0,0,0,0.3)";
		// canvas.style.background = "rgba(0,0,0,0.14)";
		canvas.style.marginTop = "-100px";
		var offsetWidth = 70;
		var width = canvas.offsetWidth - offsetWidth;
		var height = canvas.offsetHeight;
		var ctx = canvas.getContext("2d");
		ctx.translate(offsetWidth/2, 0);
		ctx.clearRect(0,0, width, height);
		if(!isNaN(percentage) && isFinite(percentage)) {
			var redColor = Math.floor(Math.min(0xff, 0xff * (1-percentage) * 2)).toString(16);
			var greenColor = Math.floor(Math.min(0xff, 0xff * percentage * 2)).toString(16);
			if(redColor.length < 2) redColor = "0" + redColor;
			if(greenColor.length < 2) greenColor = "0" + greenColor;

			var grd=ctx.createLinearGradient(0,0,width,0);
			grd.addColorStop(0,"red");
			grd.addColorStop(0.5, "yellow");
			grd.addColorStop(1,"green");

			ctx.fillStyle=grd;
			ctx.translate(10,0);
			ctx.fillRect(0,height/2-2.5,width,20);
			renderRect(ctx, 0.0, "#fff", width, height);
			renderRect(ctx, 0.25, "#fff", width, height);
			renderRect(ctx, 0.5, "#fff", width, height);
			renderRect(ctx, 0.75, "#fff", width, height);
			renderRect(ctx, 1, "#fff", width, height);
			renderRect(ctx, percentage, "#" + redColor + greenColor + "00", width, height);
			if(!isNaN(highlightPolarity))
				renderRect(ctx, highlightPolarity, "#fa1", width, height);
			ctx.translate(-10,0);

			ctx.fillStyle = "#000";
			var classify = "Vilken grad av likhet har dessa meningar";
			var veryPositive = "Matchar väldigt bra";
			var positive = "Det är en match";
			var neutral = "Samma område";
			var negative = "Orelevant";
			var veryNegative = "Helt olika texter";
			ctx.font = "15px Arial";
			ctx.fillText(veryPositive, 10 + width - ctx.measureText(veryPositive).width, height/2 - 10);
			ctx.fillText(positive, 	0.75 * width - ctx.measureText(positive).width/2, height/2 - 10);
			ctx.fillText(neutral, 	0.50 * width - ctx.measureText(neutral).width/2, height/2 - 10);
			ctx.fillText(negative, 	0.25 * width - ctx.measureText(negative).width/2, height/2 - 10);
			ctx.fillText(veryNegative, 0, height/2 - 10);
			ctx.font = "10px Arial";
			var sentenceWidth =  ctx.measureText(classify).width;
			ctx.fillText(classify, Math.max(0, Math.min(width - sentenceWidth, percentage * width - sentenceWidth/2)),height/2 + 35); 
			var textPercentage = Math.floor(10000 * percentage)/100 +" %";
			ctx.font = "35px Arial";
			ctx.fillText(textPercentage, width/2 - ctx.measureText(textPercentage).width/2, height/2 - 30); 
		}
		ctx.translate(-offsetWidth/2, 0);
	}
	var currentPolarity = 0.5;
	var targetPolarity = 0.5;
	var highlightPolarity = NaN;

	function interpolate (target, current, speed) {
		return current + (1/(target-current)) * speed;
		// var dist = target - current;
		// var dir = dist / Math.abs(dist);
		// return current + dir * Math.abs(Math.pow(dist, speed));
		// return Math.pow(target / (current - target), speed);
		// return current*(1-speed)+target*speed;
	}
	setInterval(function () {
		if(typeof currentPolarity == "undefined") currentPolarity = targetPolarity + 0.002;
		if(Math.abs(currentPolarity - targetPolarity) > 0.15) {
			// console.log(currentPolarity);
			currentPolarity = interpolate(targetPolarity, currentPolarity, 0.04);
			renderSlider(Math.floor(currentPolarity * 100 ) / 100);
		} else /*if(currentPolarity != targetPolarity)*/ {
			currentPolarity = targetPolarity;
			renderSlider(Math.floor(currentPolarity * 100 ) / 100);
		}
	}, 40);
	function getOffsets (element) {
		var totalOffset = {x: 0, y: 0};
		while(element != null && element.tagName.toLowerCase() != "body") {
			totalOffset.x += element.offsetLeft;
			totalOffset.y += element.offsetTop;
			element = element.parentNode;
		}
		return totalOffset;
	}

	var canvas = document.getElementById("polarity").getElementsByTagName("canvas")[0];
	function getRealPercentage (newPercentage) {
		if(newPercentage < 0.1)
			return 0;
		else if(Math.abs(newPercentage - 0.25) < 0.1)
			return 0.25;
		else if(Math.abs(newPercentage - 0.5) < 0.1)
			return 0.5;
		else if(Math.abs(newPercentage - 0.75) < 0.1)
			return 0.75;
		else if(Math.abs(newPercentage - 1) < 0.1)
			return 1;
	}
	canvas.onmousemove = function (event) {
		var offsets = getOffsets(this);
		var width = this.offsetWidth;
		var height = this.offsetHeight;
		var sliderOffset = 70;
		var newPercentage = (event.pageX - (offsets.x + sliderOffset/2))/(width-sliderOffset);
		highlightPolarity = getRealPercentage(newPercentage);
	}
	canvas.onmouseout = function () {
		highlightPolarity = NaN;
	}
	canvas.onclick = function (event) {
		var offsets = getOffsets(this);
		var width = this.offsetWidth;
		var height = this.offsetHeight;
		var sliderOffset = 70;
		var newPercentage = (event.pageX - (offsets.x + sliderOffset/2))/(width-sliderOffset);
		newPercentage = getRealPercentage(newPercentage);
		if(typeof newPercentage != "undefined")
			targetPolarity = newPercentage;
		// console.log(targetPolarity);
	}