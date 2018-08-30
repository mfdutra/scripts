/*
 * Call example:
 *
 * var gauge = new verticalGauge({
 * 	x: 100,
 * 	y: 100,
 * 	red: [[0,10], [80, 100]],
 * 	yellow: [[40,70]],
 * 	green: [[15,30]],
 * 	marker: 53,
 * });
 * gauge.setMarker(90);
 */
function verticalGauge(p)
{
	var paper = Raphael(p.x, p.y, 50, 150);

	var box = paper.path('M 16 0 L 0 0 L 0 100 L 16 100');
	box.attr({stroke: 'white'});

	var drawArea = function(points, color)
	{
		points[0] = 100 - points[0];
		points[1] = 100 - points[1];

		var path = 'M 0 ' + points[0] + ' l 8 0 l 0 ' + (points[1] - points[0]) + ' l -8 0 z';

		var area = paper.path(path);
		area.attr({fill: color, 'stroke-width': 0});
	}

	if (p.green)
		for (var i = 0; i < p.green.length; i++)
			drawArea(p.green[i], 'green');

	if (p.yellow)
		for (var i = 0; i < p.yellow.length; i++)
			drawArea(p.yellow[i], 'yellow');

	if (p.red)
		for (var i = 0; i < p.red.length; i++)
			drawArea(p.red[i], 'red');

	// Method to set marker position
	this.marker = 0;
	this.setMarker = function(markerPos)
	{
		// Marker limits
		if (markerPos > 100) markerPos = 100;
		if (markerPos < 0) markerPos = 0;

		var t = markerPos - this.marker;
		this.marker = markerPos;

		markerArrow.animate({'translation': '0 ' + (t * -1)}, 1000, '>');
	}

	var markerArrow = paper.path('M 4 100 l 12 -8 l 0 16 z');
	markerArrow.attr({fill: 'white'});

	if (p.marker)
		this.setMarker(p.marker);

	box.toFront();

	var title = paper.text(0, 110, '');
	title.attr({fill: 'white', 'font-size': '12px', 'text-anchor': 'start'});

	var value = paper.text(0, 125, '');
	value.attr({fill: '#0ff', 'font-size': '14px', 'text-anchor': 'start'});

	this.setValue = function(valueStr)
	{
		value.attr({'text': valueStr});
	}

	this.setTitle = function(valueStr)
	{
		title.attr({'text': valueStr});
	}

	if (p.value) this.setValue(p.value);
	if (p.title) this.setTitle(p.title);

	this.setInvalid = function(state)
	{
		if (state)
		{
			this.redCross = paper.path('M 0 0 L 16 100 M 0 100 L 16 0');
			this.redCross.attr({stroke: 'red', 'stroke-width': '3px'});
		}
		else
		{
			if (this.redCross)
			{
				this.redCross.remove();
			}
		}
	}
}

/*
 * var speed = new speedometer({
 * 	x: 0,
 * 	y: 0,
 * 	marker: 60,
 * 	green: [[10,50]],
 * 	yellow: [[50, 70]],
 * 	red: [[0,10], [70,100]],
 * 	value: 2260,
 * 	title: 'RPM',
 * });
 * speed.setMarker(90);
 */
function speedometer(p)
{
	var paper = Raphael(p.x, p.y, 120, 120);
	var border = paper.circle(60, 60, 55);
	border.attr({stroke: '#444', 'stroke-width': '6px'});

	function drawBand(from, to, color)
	{
		var radius = 49;

		// Band limits
		if (to > 100) to = 100;
		if (from < 0) from = 0;

		// Translate % into angles (220 deg total, from -20 to 200)
		from = 200 - (from * 2.2);
		to   = 200 - (to * 2.2);

		// Determine points of arc
		var x1 = 60 + Math.cos(to * Math.PI/180) * radius;
		var y1 = 60 + Math.sin(to * Math.PI/180) * radius * -1;
		var x2 = 60 + Math.cos(from * Math.PI/180) * radius;
		var y2 = 60 + Math.sin(from * Math.PI/180) * radius * -1;

		// If the arc is greather than 180, turn the large-arc-flag on
		var largeArcFlag = ((from-to) >= 180) ? 1 : 0;

		var path = paper.path('M ' + x1 + ',' + y1 + ' A ' + radius + ',' + radius + ' 0 ' + largeArcFlag + ',0 ' + x2 + ',' + y2);
		path.attr({stroke: color, 'stroke-width': '5px'});
	}

	if (p.green)
		for (var i = 0; i < p.green.length; i++)
			drawBand(p.green[i][0], p.green[i][1], 'green');
	if (p.yellow)
		for (var i = 0; i < p.yellow.length; i++)
			drawBand(p.yellow[i][0], p.yellow[i][1], 'yellow');
	if (p.red)
		for (var i = 0; i < p.red.length; i++)
			drawBand(p.red[i][0], p.red[i][1], 'red');

	var outline = paper.path('M 11.135983719 77.785047453 a 52,52 0 1,1 97.728032562 0');
	outline.attr({stroke: 'white'});

	var markerArrow = paper.path('M 57 60 L 60 10 L 63 60 z');
	markerArrow.attr({fill: 'white', 'stroke-width': 0});
	markerArrow.rotate(-110, 60, 60);

	this.marker = 0;
	this.setMarker = function(markerPos)
	{
		// Marker limits
		if (markerPos > 100) markerPos = 100;
		if (markerPos < 0) markerPos = 0;

		// markerArrow.rotate(-110 + (p.marker * 2.2), 60, 60);
		markerArrow.animate({'rotation': (-110 + (markerPos * 2.2)) + ' 60 60'}, 1000, '>');

		this.marker = markerPos;
	}

	if (p.marker)
		this.setMarker(p.marker);

	var lineDots = paper.set();
	lineDots.push(
		paper.path('M 11.135983719 77.785047453 l 9.396926208 -3.420201433'),
		paper.path('M 108.864016281 77.785047453 l -9.396926208 -3.420201433')
	);
	lineDots.attr({stroke: 'white'});

	var pivot = paper.circle(60, 60, 5);
	pivot.attr({fill: '#444', 'stroke-width': 0});

	this.setValue = function(valueStr)
	{
		value.attr({'text': valueStr});
	}

	this.setTitle = function(valueStr)
	{
		title.attr({'text': valueStr});
	}

	var value = paper.text(60, 95, '');
	value.attr({fill: '#0ff', 'font-size': '16px'});

	var title = paper.text(60, 80, '');
	title.attr({fill: 'white', 'font-size': '12px'});

	if (p.value)
	{
		this.setValue(p.value);
	}

	if (p.title)
	{
		this.setTitle(p.title);
	}

	this.setInvalid = function(state)
	{
		if (state)
		{
			this.cover = paper.circle(60, 60, 53);
			this.cover.attr({fill: '#444', 'stroke-width': 0, opacity: .7});
			this.redCross = paper.path('M 23.230447388 23.230447388 L 96.769552612 96.769552612 M 23.230447388 96.769552612 L 96.769552612 23.230447388');
			this.redCross.attr({stroke: 'red', 'stroke-width': '8px'});
		}
		else
		{
			if (this.cover)
			{
				this.cover.remove();
				this.redCross.remove();
			}
		}
	}
}

/* Call example
	var speed = new dblSpeedometer({
		x: 0,
		y: 0,
		greenA: [[10,50]],
		yellowA: [[50, 70]],
		redA: [[0,10], [70,100]],
		greenB: [[0,50]],
		yellowB: [[50, 70]],
		redB: [[70,100]],
		markerA: 12,
		markerB: 80,
		valueA: '12345',
		valueB: '67890',
		title: 'EBT',
		subtitleA: 'In',
		subtitleB: 'Out',
	});
	speed.setMarkerA(70);
	speed.setMarkerB(24);
	speed.setMarkerAB(70, 24);
	speed.setValueA('1234');
	speed.setValueB('5678');
	speed.setTitle('bla');
	speed.subtitleA('In');
	speed.subtitleB('Out');
*/ 
function dblSpeedometer(p)
{
	var paper = Raphael(p.x, p.y, 120, 120);

	// Outer border
	var border = paper.circle(60, 60, 55);
	border.attr({stroke: '#444', 'stroke-width': '6px'});

	// Outer white line
	var radius = 52;
	var x1 = 60 - Math.cos(40 * Math.PI/180) * radius;
	var y1 = 60 + Math.sin(40 * Math.PI/180) * radius;
	var x2 = 60 - Math.cos(60 * Math.PI/180) * radius;
	var y2 = 60 - Math.sin(60 * Math.PI/180) * radius;
	var outLineA = paper.path('M '+x1+' '+y1+' A 52 52 0 0 1 '+x2+' '+y2);
	outLineA.attr({stroke: 'white'});

	var x1 = 60 + Math.cos(40 * Math.PI/180) * radius;
	var y1 = 60 + Math.sin(40 * Math.PI/180) * radius;
	var x2 = 60 + Math.cos(60 * Math.PI/180) * radius;
	var y2 = 60 - Math.sin(60 * Math.PI/180) * radius;
	var outLineB = paper.path('M '+x1+' '+y1+' A 52 52 0 0 0 '+x2+' '+y2);
	outLineB.attr({stroke: 'white'});

	// Outer line limits

	// bottom left
	var x1 = 60 - Math.cos(40 * Math.PI/180) * radius;
	var y1 = 60 + Math.sin(40 * Math.PI/180) * radius;
	var x2 = 60 - Math.cos(40 * Math.PI/180) * (radius-10);
	var y2 = 60 + Math.sin(40 * Math.PI/180) * (radius-10);
	paper.path('M '+x1+' '+y1+' L '+x2+' '+y2).attr({stroke: 'white'});

	// top left
	var x1 = 60 - Math.cos(60 * Math.PI/180) * radius;
	var y1 = 60 - Math.sin(60 * Math.PI/180) * radius;
	var x2 = 60 - Math.cos(60 * Math.PI/180) * (radius-10);
	var y2 = 60 - Math.sin(60 * Math.PI/180) * (radius-10);
	paper.path('M '+x1+' '+y1+' L '+x2+' '+y2).attr({stroke: 'white'});

	// bottom right
	var x1 = 60 + Math.cos(40 * Math.PI/180) * radius;
	var y1 = 60 + Math.sin(40 * Math.PI/180) * radius;
	var x2 = 60 + Math.cos(40 * Math.PI/180) * (radius-10);
	var y2 = 60 + Math.sin(40 * Math.PI/180) * (radius-10);
	paper.path('M '+x1+' '+y1+' L '+x2+' '+y2).attr({stroke: 'white'});

	// top right
	var x1 = 60 + Math.cos(60 * Math.PI/180) * radius;
	var y1 = 60 - Math.sin(60 * Math.PI/180) * radius;
	var x2 = 60 + Math.cos(60 * Math.PI/180) * (radius-10);
	var y2 = 60 - Math.sin(60 * Math.PI/180) * (radius-10);
	paper.path('M '+x1+' '+y1+' L '+x2+' '+y2).attr({stroke: 'white'});

	// Method to draw the color bands
	function drawBand(from, to, color, leftRight)
	{
		var radius = 49;

		// Band limits
		if (to > 100) to = 100;
		if (from < 0) from = 0;

		// Translate % into angles (220 deg total, from -20 to 200)
		if (leftRight) // right
		{
			from = -40 + from;
			to   = -40 + to;
			sweepFlag = 1;
		}
		else // left
		{
			from = 220 - from;
			to   = 220 - to;
			sweepFlag = 0;
		}

		// Determine points of arc
		var x1 = 60 + Math.cos(to * Math.PI/180) * radius;
		var y1 = 60 + Math.sin(to * Math.PI/180) * radius * -1;
		var x2 = 60 + Math.cos(from * Math.PI/180) * radius;
		var y2 = 60 + Math.sin(from * Math.PI/180) * radius * -1;

		// If the arc is greather than 180, turn the large-arc-flag on
		var largeArcFlag = ((from-to) >= 180) ? 1 : 0;

		var path = paper.path('M ' + x1 + ',' + y1 + ' A ' + radius + ',' + radius + ' 0 ' + largeArcFlag + ' '+sweepFlag+' ' + x2 + ',' + y2);
		path.attr({stroke: color, 'stroke-width': '5px'});
		path.toBack();
	}

	// draw left color bands
	if (p.greenA)
		for (var i = 0; i < p.greenA.length; i++)
			drawBand(p.greenA[i][0], p.greenA[i][1], 'green', false);
	if (p.yellowA)
		for (var i = 0; i < p.yellowA.length; i++)
			drawBand(p.yellowA[i][0], p.yellowA[i][1], 'yellow', false);
	if (p.redA)
		for (var i = 0; i < p.redA.length; i++)
			drawBand(p.redA[i][0], p.redA[i][1], 'red', false);

	// draw right color bands
	if (p.greenB)
		for (var i = 0; i < p.greenB.length; i++)
			drawBand(p.greenB[i][0], p.greenB[i][1], 'green', true);
	if (p.yellowB)
		for (var i = 0; i < p.yellowB.length; i++)
			drawBand(p.yellowB[i][0], p.yellowB[i][1], 'yellow', true);
	if (p.redB)
		for (var i = 0; i < p.redB.length; i++)
			drawBand(p.redB[i][0], p.redB[i][1], 'red', true);

	// marker pointers
	var markerArrowA = paper.path('M 57 60 L 60 10 L 63 60 z');
	markerArrowA.attr({fill: 'white', 'stroke-width': 0});
	markerArrowA.rotate(-130, 60, 60);
	var markerArrowB = paper.path('M 57 60 L 60 10 L 63 60 z');
	markerArrowB.attr({fill: 'white', 'stroke-width': 0});
	markerArrowB.rotate(130, 60, 60);

	this.markerA = 0;
	this.markerB = 0;

	this.setMarker = function(markerPos, leftRight)
	{
		// Marker limits
		if (markerPos > 100) markerPos = 100;
		if (markerPos < 0) markerPos = 0;

		if (leftRight) // right
		{
			markerArrowB.animate({'rotation': (130 - markerPos) + ' 60 60'}, 1000, '>');
			this.markerB = markerPos;
		}
		else // left
		{
			markerArrowA.animate({'rotation': (-130 + markerPos) + ' 60 60'}, 1000, '>');
			this.markerA = markerPos;
		}
	}
	this.setMarkerA = function(markerPos) { this.setMarker(markerPos, false) };
	this.setMarkerB = function(markerPos) { this.setMarker(markerPos, true) };
	this.setMarkerAB = function(mA, mB)
	{
		this.setMarker(mA, false);
		this.setMarker(mB, true);
	}

	if (p.markerA) this.setMarkerA(p.markerA);
	if (p.markerB) this.setMarkerB(p.markerB);

	// center pivot
	var pivot = paper.circle(60, 60, 5);
	pivot.attr({fill: '#444', 'stroke-width': 0});

	// set invalid method
	this.setInvalid = function(state)
	{
		if (state)
		{
			this.cover = paper.circle(60, 60, 53);
			this.cover.attr({fill: '#444', 'stroke-width': 0, opacity: .7});
			this.redCross = paper.path('M 23.230447388 23.230447388 L 96.769552612 96.769552612 M 23.230447388 96.769552612 L 96.769552612 23.230447388');
			this.redCross.attr({stroke: 'red', 'stroke-width': '8px'});
		}
		else
		{
			if (this.cover)
			{
				this.cover.remove();
				this.redCross.remove();
			}
		}
	}

	// value and title
	this.setValueA = function(valueStr)
	{
		valueA.attr({'text': valueStr});
	}

	this.setValueB = function(valueStr)
	{
		valueB.attr({'text': valueStr});
	}

	this.setTitle = function(valueStr)
	{
		title.attr({'text': valueStr});
	}

	this.setSubtitleA = function(valueStr)
	{
		subtitleA.attr({'text': valueStr});
	}

	this.setSubtitleB = function(valueStr)
	{
		subtitleB.attr({'text': valueStr});
	}

	var valueA = paper.text(42, 98, '');
	valueA.attr({fill: '#0ff', 'font-size': '10px'});
	var valueB = paper.text(78, 98, '');
	valueB.attr({fill: '#0ff', 'font-size': '10px'});

	var subtitleA = paper.text(34, 40, '');
	subtitleA.attr({fill: 'white', 'font-size': '10px'});
	var subtitleB = paper.text(87, 40, '');
	subtitleB.attr({fill: 'white', 'font-size': '10px'});

	var title = paper.text(60, 18, '');
	title.attr({fill: 'white', 'font-size': '10px'});

	if (p.valueA) this.setValueA(p.valueA);
	if (p.valueB) this.setValueB(p.valueB);
	if (p.title) this.setTitle(p.title);
	if (p.subtitleA) this.setSubtitleA(p.subtitleA);
	if (p.subtitleB) this.setSubtitleB(p.subtitleB);
}

function svgClock(x, y)
{
	var center = 80;
	var paper = Raphael(x, y, 160, 160);
    var previousHRotation = 0;
    var previousMRotation = 0;

	// Outer border
	var border = paper.circle(center, center, 75);
	border.attr({stroke: '#444', 'stroke-width': '6px'});

	// 1-minute ticks
	for (var angle=0; angle < 360; angle += 6)
	{
		var tick = paper.path('M ' + center + ' 11 v -3');
		tick.attr({stroke: '#555', 'stroke-width': '1px'});
		tick.rotate(angle, center, center);
	}

	// 5-minute ticks
	for (var angle=0; angle < 360; angle += 30)
	{
		var tick = paper.path('M ' + center + ' 15 v -7');
		tick.attr({stroke: '#555', 'stroke-width': '1px'});
		tick.rotate(angle, center, center);
	}

	// date and week day
	var months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
	var weekDays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
	var date = paper.text(center, 110, '');
	date.attr({fill: '#999', 'font-size': '16px', 'font-weight': "bold"})
	var weekDay = paper.text(center, 125, '');
	weekDay.attr({fill: '#999', 'font-size': '12px', 'font-weight': ""})

	// clock pointers
	var minute = paper.path('M 78.5 80 v -58 l 1.5 -4 l 1.5 4 v 58 z');
	minute.attr({'stroke-width': 0, 'fill': 'blue'});
	var minuteL = paper.path('M 80 80 v -58');
	minuteL.attr({'stroke-width': '1px', 'stroke': '#aaa'});

	var hour = paper.path('M 78.5 80 v -38 l 1.5 -4 l 1.5 4 v 38 z');
	hour.attr({'stroke-width': '0', 'fill': '#44f'});
	var hourL = paper.path('M 80 80 v -38');
	hourL.attr({'stroke-width': '1px', 'stroke': '#aaa'});

	// pivot
	var pivot = paper.circle(center, center, 5);
	pivot.attr({'stroke-width': 0, fill: '#444'});

	var drawClock = function()
	{
		var now = new Date();
		var m = now.getMinutes() + (now.getSeconds() / 60.0);
		var h = now.getHours() + (m / 60.0);
        var m_deg = m * 6;
        var h_deg = h * 30;

		minute.rotate(m_deg - previousMRotation, center, center);
		minuteL.rotate(m_deg - previousMRotation, center, center);
		hour.rotate(h_deg - previousHRotation, center, center);
		hourL.rotate(h_deg - previousHRotation, center, center);

        previousHRotation = h_deg;
        previousMRotation = m_deg;

		date.attr({text: now.getDate() + '/' + months[now.getMonth()]});
		weekDay.attr({text: weekDays[now.getDay()]});
	}

	var setClock = function()
	{
		drawClock();
		setTimeout(function(){setClock()}, 1000);
	}

	setClock();
}
