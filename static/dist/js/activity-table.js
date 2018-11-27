activityData = []

const action2txt = (d =>{
	var text = "";
	var action = d.action._binaryString;
	var user = d.user._binaryString;
	var timestamp = d.time._binaryString;
	if (action === 'delete'){
		text = `The user ${user} deleted a record at ${timestamp}`
	}
	else{
		var movie = d.movie._binaryString;
		var rating = d.rating;
		if(action === 'insert'){
			text = `The user ${user} rated the ${movie} as ${rating} star at ${timestamp}.`
		}
		else{
			text = `The user ${user} modified the ${movie} as ${rating} star at ${timestamp}.`
			console.log(d.time)
		}
	}
	return text
});

const add_data = (d=>{
	var table = document.getElementById("customers");
	for (var j = 0;j <d.length ; j++){
		var text = action2txt(d[j]);
		var row = table.insertRow(1);
		var cell1 = row.insertCell(0);
		cell1.innerHTML = text;
	}
});

db.collection('activity').onSnapshot(res => {
	res.docChanges().forEach(change => {
		const doc = {...change.doc.data(), id: change.doc.id};

		switch (change.type){
			case 'added':
				activityData.push(doc);
				break;
			case 'modified':
				const index = activityData.findIndex(item => item.id == doc.id);
				activityData[index] = doc;
				break;
			case 'removed':
				activityData = activityData.filter(item => item.id !== doc.id);
				break;
			default:
				break;
		}
	});
	add_data(activityData)
});