function defined(obj)
{
	if (obj==undefined)
		throw('assertion error');
}

/*
Possible calls:

bandwidthMeter({
	host: 'router.domain',
	ifIndex: 3,
	interval: 60,
	maxIn: 1000000,
	maxOut: 1000000,
	callbackPercent: function(a,b){speedGauge.setMarkerAB(a,b)},
	callbackError: function(reason) {speedGauge.setInvalid(true);},
});

bandwidthMeter({
	host: 'router.domain',
	ifDescr: 'eth0',
	interval: 60,
	maxIn: 1000000,
	maxOut: 1000000,
	callbackPercent: function(a,b){speedGauge.setMarkerAB(a,b)},
	callbackError: function(reason) {speedGauge.setInvalid(true);},
});
 */
function bandwidthMeter(p)
{
	try { jQuery } catch(err)
	{
		alert('bandwidthMeter: jQuery is required');
	}

	// Check for expected parameters
	try
	{
		defined(p.host);
		defined(p.interval);
		defined(p.maxIn);
		defined(p.maxOut);
	}
	catch(err)
	{
		alert('bandwidthMeter: check required parameters');
	}

	if ((!p.ifIndex) && (!p.ifDescr))
	{
		alert('bandwidthMeter: either ifIndex or ifDescr must be provided');
	}

	// attributes

	this.currentIn = 0;
	this.currentOut = 0;
	this.deltaIn = 0;
	this.deltaOut = 0;
	this.percentIn = 0;
	this.percentOut = 0;
	this.oidIn = '.1.3.6.1.2.1.2.2.1.10.' + p.ifIndex;
	this.oidOut = '.1.3.6.1.2.1.2.2.1.16.' + p.ifIndex;
	this.p = p;

	// methods

	this.fetchIfData = function()
	{
		var data;
		if (this.p.ifIndex)
			data = {ifIndex: this.p.ifIndex, host: this.p.host};
		else
			data = {ifDescr: this.p.ifDescr, host: this.p.host};

		try
		{
			$.ajax({
				url: 'snmpget-if.cgi',
				data: data,
				dataType: 'json',
				context: this,
				success: this.processIfData,
				error: function(jqXHR, textStatus, errorThrown)
				{
					alert('Ajax error in fetchIfData');
				}
			})
		}
		catch(err)
		{
			console.log(err);
		}
	}

	this.processIfData = function(data, textStatus, jqXHR)
	{
		try {
			// check for errors
			if (data.error)
			{
				if (this.p.callbackError)
					this.p.callbackError(data.error);

				return false;
			}

			// do not calculate delta in the 1st read
			if ((this.currentIn > 0) || (this.currentOut > 0))
			{
				this.deltaIn = (data.inOctets - this.currentIn) / this.p.interval * 8;
				this.deltaOut = (data.outOctets - this.currentOut) / this.p.interval * 8;
			}

			this.currentIn = data.inOctets;
			this.currentOut = data.outOctets;

			this.percentIn = this.deltaIn / this.p.maxIn * 100;
			this.percentOut = this.deltaOut / this.p.maxOut * 100;

			// Callback for all data
			if (this.p.callback)
				this.p.callback(this.deltaIn, this.percentIn, this.deltaOut, this.percentOut);

			// Callback for percent only
			if (this.p.callbackPercent)
				this.p.callbackPercent(this.percentIn, this.percentOut);

			var self = this;
			setTimeout(function(){
				self.fetchIfData();
			}, this.p.interval * 1000);
		}
		catch(err)
		{
			console.log(err);
		}
	}

	// constructor

	this.fetchIfData();
}
