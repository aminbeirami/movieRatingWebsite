//raw data from firebase
var recordData = [];
var queryData = [];
var snapshotData = [];
var timeScale = [];
var minDate = 0;
var maxDate = 0;

const graphWidth =document.querySelector('.content').offsetWidth;
const graphHeight = document.querySelector('.content').offsetHeight;
const labelWidth = document.querySelector('.label').offsetWidth;
const axisHeight = document.querySelector('.ticks').offsetHeight;
const axisWidth = document.querySelector('.ticks').offsetWidth;
const tooltipHeight = document.querySelector('.tooltipTxt').offsetHeight;
const tooltipWidth = document.querySelector('.tooltipTxt').offsetWidth;

//record svg and graph initialization
const recordSvg = d3.select('.records .content')
	.append('svg')
	.attr('width', graphWidth)
	.attr('height', graphHeight);

const recGraph = recordSvg.append('g')
	.attr('width',graphWidth)
	.attr('height',graphHeight);

const recSeparator = recGraph.append('line')
	.attr('stroke', 'white')
	.attr('stroke-width', 0.5)
	.attr('x1', 0)
	.attr('x2', graphWidth)
	.attr('y1', graphHeight/2)
	.attr('y2', graphHeight/2);

//query svg and graph initialization
const querySvg = d3.select('.queries .content')
	.append('svg')
	.attr('width', graphWidth)
	.attr('height', graphHeight);

const queryGraph = querySvg.append('g')
	.attr('width',graphWidth)
	.attr('height',graphHeight);

const querySeparator = queryGraph.append('line')
	.attr('stroke', 'white')
	.attr('stroke-width', 0.5)
	.attr('x1', 0)
	.attr('x2', graphWidth)
	.attr('y1', graphHeight/2)
	.attr('y2', graphHeight/2);

//snapshot svg and graph initialization
const snapSvg = d3.select('.snapshots .content')
	.append('svg')
	.attr('width', graphWidth)
	.attr('height', graphHeight);

const snapGraph = snapSvg.append('g')
	.attr('width',graphWidth)
	.attr('height',graphHeight);

const snapSeparator = snapGraph.append('line')
	.attr('stroke', 'white')
	.attr('stroke-width', 0.5)
	.attr('x1', 0)
	.attr('x2', graphWidth)
	.attr('y1', graphHeight/2)
	.attr('y2', graphHeight/2);

//axis svg and graph initialization
const axisSvg = d3.select('.axis .ticks')
	.append('svg')
	.attr('width', axisWidth)
	.attr('height', axisHeight);

const axisGraph = axisSvg.append('g')
	.attr('width', axisWidth)
	.attr('height', axisHeight);

// the x and y positions
const x = d3.scaleTime().range([0,graphWidth-20]); 
const y = graphHeight/2; 

// set the x axes
const xAxisGroup = axisGraph.append('g')
	.attr('class', 'x-axis');

//hover line
var vertical = d3.select(".content")
    .append("div")
    .attr("class", "remove")
    .style("position", "absolute")
    .style("margin-left", `${labelWidth+495}px`)
    .style("width", "1px")
    .style("height", `${graphHeight*3+5}px`)
    .style("top", `${tooltipHeight+72}px`)
    .style("bottom", "10px")
    .style("left", "0px")
    .style("background", "#fff");

var tooltip = d3.select(".tooltipTxt")
    .append("div")
    .attr("class", "info")
    .style("position", "absolute")
    .style("margin-left", `${(labelWidth+455)}px`)
    .style("width", "80px")
    .style("height", `${tooltipHeight}px`)
    .style("background", "#708090")
    .style("visibility","hidden")
    .style("color", '#fff')
    .style("text-align", "center")
	.style("vertical-align", "middle")
	.style("border-radius", "3px");

d3.selectAll(".content")
      .on("mousemove", function(){  
         mousex = d3.mouse(this);
         mousex = mousex[0];
         vertical.style("left", mousex + "px")
         tooltip.style("left",mousex + "px")
         document.querySelector(".date").innerHTML = mousex;
     });

var activity_generator = (d=>{
	var activity = ''
	if (d.f === 0)
	{
		activity = `The film '${d.other_info[0].mv_name._binaryString}' rated as ${d.other_info[0].star} star by ${d.other_info[0].username._binaryString}`
	} 
	else 
	{
		activity = `The record number ${d.other_info[0].id} deleted by ${d.other_info[0].username._binaryString}`
	}
	return activity
});
//visualize the records
const visualizeRec = (d =>{
	x.domain(d3.extent(recordData, d => new Date(d.timestamp._binaryString)));


	const circles = recGraph.selectAll('circle')
	.data(d);

	circles.attr('cx', d => x(new Date(d.timestamp._binaryString)))
		   .attr('cy', y);

	circles.exit().remove();

	circles.enter()
		.append('circle')
			.attr('r', 6)
			.attr('cx', d => x(new Date(d.timestamp._binaryString)))
			.attr('cy', y)
			.attr('fill', '#fff')
			.attr('stroke','#808080')
			.attr('stroke-width','3');

	//mouse hover
	recGraph.selectAll('circle')
	.on('mouseover', (d,i,n) => {
		d3.select(n[i])
			.transition().duration(100)
				.attr('r',8)
				.attr('fill','#fff')
				.attr('stroke','#D3D3D3')
				.attr('stroke-width','3');
		tooltip.style("visibility","visible");
		document.querySelector('.info').innerHTML = `Record ${d.id}`;
		activity = activity_generator(d)
		document.querySelector('#data-info').innerHTML = activity;
	})
	.on('mouseleave',(d,i,n) => {
		d3.select(n[i])
			.transition().duration(100)
				.attr('r',6)
				.attr('fill','#fff')
				.attr('stroke','#808080')
				.attr('stroke-width','3');
		tooltip.style("visibility","hidden");
		document.querySelector('.info').innerHTML = "";
		document.querySelector('#data-info').innerHTML = "";
	});

	//generate the axis
	const xAxis = d3.axisBottom(x)
	.ticks(8);

	//call the x axis
	xAxisGroup.call(xAxis);
});

//visualize the queries
const visualizeQury = (d =>{
	console.log(d[0].timestamp._binaryString)
	x.domain(d3.extent(recordData, d => new Date(d.timestamp._binaryString)));
	
	const circles = queryGraph.selectAll('circle')
	.data(d);

	circles.attr('cx', d => x(new Date(d.timestamp._binaryString)))
		   .attr('cy', y);

	circles.exit().remove();

	circles.enter()
		.append('circle')
			.attr('r', 6)
			.attr('cx', d => x(new Date(d.timestamp._binaryString)))
			.attr('cy', y)
			.attr('fill', '#fff')
			.attr('stroke','#808080')
			.attr('stroke-width','3');

	//mouse hover
	queryGraph.selectAll('circle')
		.on('mouseover', (d,i,n) => {
			d3.select(n[i])
				.transition().duration(100)
					.attr('r',8)
					.attr('fill','#fff')
					.attr('stroke','#D3D3D3')
					.attr('stroke-width','3');
		tooltip.style("visibility","visible");
		document.querySelector('.info').innerHTML = d.name._binaryString;
		document.querySelector('#data-info').innerHTML = d.timestamp._binaryString;
		})

		.on('mouseleave',(d,i,n) => {
			d3.select(n[i])
				.transition().duration(100)
					.attr('r',6)
					.attr('fill','#fff')
					.attr('stroke','#808080')
					.attr('stroke-width','3');
		tooltip.style("visibility","hidden");
		document.querySelector('.info').innerHTML = "";
		document.querySelector('#data-info').innerHTML = "";
		});
});

//visualize the snapshots
const visualizeSnapshot = (d =>{
	x.domain(d3.extent(recordData, d => new Date(d.timestamp._binaryString)));
	
	const circles = snapGraph.selectAll('circle')
	.data(d);

	circles.attr('cx', d => x(new Date(d.timestamp._binaryString)))
		   .attr('cy', y);

	circles.exit().remove();

	circles.enter()
		.append('circle')
			.attr('r', 6)
			.attr('cx', d => x(new Date(d.timestamp._binaryString)))
			.attr('cy', y)
			.attr('fill', '#fff')
			.attr('stroke','#808080')
			.attr('stroke-width','3');
	
	//mouse hover
	snapGraph.selectAll('circle')
	.on('mouseover', (d,i,n) => {
		d3.select(n[i])
			.transition().duration(100)
				.attr('r',8)
				.attr('fill','#fff')
				.attr('stroke','#D3D3D3')
				.attr('stroke-width','3');
	tooltip.style("visibility","visible");
	document.querySelector('.info').innerHTML = d.name._binaryString;
	document.querySelector('#data-info').innerHTML = d.timestamp._binaryString;
	})
	.on('mouseleave',(d,i,n) => {
		d3.select(n[i])
			.transition().duration(100)
				.attr('r',6)
				.attr('stroke','#808080')
				.attr('stroke-width','3');
	tooltip.style("visibility","hidden");
	document.querySelector('.info').innerHTML = "";
	document.querySelector('#data-info').innerHTML = "";
	});
});

//updating data
const update_timeline = (data =>{
	data.sort((a,b) => new Date(a.date) - new Date(b.date));
	var nested = d3.nest()
	.key(d => d.activity)
	.entries(data);
	nested.forEach(d =>{
		switch (d.key){
			case 'swimming':
				visualizeRec(d.values);
				break;
			case 'walking':
				visualizeQury(d.values);
				break;
			case 'running':
				visualizeSnapshot(d.values);
				break;
			default:
				break;
		}
	});
});

//getting data from firebase.
db.collection('activities').onSnapshot(res => {
	res.docChanges().forEach(change => {
		const doc = {...change.doc.data(), id: change.doc.id};

		switch (change.type){
			case 'added':
				data.push(doc);
				break;
			case 'modified':
				const index = data.findIndex(item => item.id == doc.id);
				data[index] = doc;
				break;
			case 'removed':
				data = data.filter(item => item.id !== doc.id);
				break;
			default:
				break;
		}
	});
	update_timeline(data)
});

db.collection('components').onSnapshot(res => {
	res.docChanges().forEach(change => {
		const doc = {...change.doc.data(), id: change.doc.id};
		switch (change.type){
			case 'added':
				recordData.push(doc);
				break;
			case 'modified':
				const index = recordData.findIndex(item => item.id == doc.id);
				recordData[index] = doc;
				break;
			case 'removed':
				recordData = recordData.filter(item => item.id !== doc.id);
				break;
			default:
				break;
		}
	});
	visualizeRec(recordData)
});

db.collection('queries').onSnapshot(res => {
	res.docChanges().forEach(change => {
		const doc = {...change.doc.data(), id: change.doc.id};

		switch (change.type){
			case 'added':
				queryData.push(doc);
				break;
			case 'modified':
				const index = queryData.findIndex(item => item.id == doc.id);
				queryData[index] = doc;
				break;
			case 'removed':
				queryData = queryData.filter(item => item.id !== doc.id);
				break;
			default:
				break;
		}
	});
	visualizeQury(queryData)
});


db.collection('snapshots').onSnapshot(res => {
	res.docChanges().forEach(change => {
		const doc = {...change.doc.data(), id: change.doc.id};

		switch (change.type){
			case 'added':
				snapshotData.push(doc);
				break;
			case 'modified':
				const index = snapshotData.findIndex(item => item.id == doc.id);
				snapshotData[index] = doc;
				break;
			case 'removed':
				snapshotData = snapshotData.filter(item => item.id !== doc.id);
				break;
			default:
				break;
		}
	});
	visualizeSnapshot(snapshotData)
});
