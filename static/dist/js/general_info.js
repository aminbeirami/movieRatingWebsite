data = []
snapshots= []
single_snapshot = []
chain_check = []
record_check = []

const update = (d =>{
	document.querySelector('#relationSpanTitle').innerHTML = 'rating';
	document.querySelector('#no_record').innerHTML = d[0].relation_records;
	document.querySelector('#relation_size').innerHTML = `${d[0].relation_size} Bytes`;
	document.querySelector('#logSpanTitle').innerHTML = 'timeline';
	document.querySelector('#timeline_record').innerHTML = d[0].timeline_records;
	document.querySelector('#timeline_size').innerHTML = `${d[0].timeline_size} Bytes`;
	document.querySelector('#number_of_deletes').innerHTML = d[0].number_of_deletes;
	document.querySelector('#number_of_updates').innerHTML = d[0].number_of_updates;
	document.querySelector('#snapshot_number').innerHTML = d[0].snapshot_list.length;

	for (i = 0; i < d[0].snapshot_list.length; i++) {
		var node = document.createElement("LI");
		var textnode = document.createTextNode(d[0].snapshot_list[i]._binaryString);
		node.appendChild(textnode);
		document.querySelector("#snapshot_list").appendChild(node);
	}
});
var viewList = (d=>{
	snapshotDropdown = document.querySelector('#snapshot-list');
	for (var i=0; i<d.length; i++){
		var option = document.createElement("option");
		option.text = d[i].name._binaryString;
		snapshotDropdown.add(option);
	}
});

var snapshot_table = (d=>{
	snapshot_data = d[0].data
	header_title = d[0].keys
	for (var i=0; i<header_title.length;i++){
		var head = document.createElement("TH");
		var textnode = document.createTextNode(header_title[i]._binaryString);
		head.appendChild(textnode);
		document.querySelector('#snapshot_header').appendChild(head);
	}
	for (var i=0; i<snapshot_data.length-1;i++){
		var row = document.createElement("TR")
		for (var j=0; j<header_title.length; j++){
			var node = document.createElement("TD");
			var textnode = document.createTextNode(snapshot_data[i][header_title[j]._binaryString]._binaryString);
			node.appendChild(textnode);
			row.appendChild(node);
		}
		document.querySelector('.snapshot-table').appendChild(row);
	}
	var status = d[0].status._binaryString;
	var snapshotLength = snapshot_data.length;
	var snapshotName = d[0].name;
	document.querySelector('#snapshot-length').innerHTML = snapshotLength-1;
	document.querySelector('#trust-status').innerHTML = status;
	document.querySelector('#snapshot_name').innerHTML = snapshotName;
	if (status === 'Trusted'){
	document.querySelector('#trust-status').style.color = 'Green'
	}
	else{
		document.querySelector('#trust-status').style.color = 'Red'
	}
});

db.collection('info').onSnapshot(res => {
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
	update(data)
});

db.collection('snapshots').onSnapshot(res => {
	res.docChanges().forEach(change => {
		const doc = {...change.doc.data(), id: change.doc.id};

		switch (change.type){
			case 'added':
				snapshots.push(doc);
				break;
			case 'modified':
				const index = snapshots.findIndex(item => item.id == doc.id);
				snapshots[index] = doc;
				break;
			case 'removed':
				snapshots = snapshots.filter(item => item.id !== doc.id);
				break;
			default:
				break;
		}
	});
	viewList(snapshots)
});

db.collection('snapshotQuery').onSnapshot(res => {
	res.docChanges().forEach(change => {
		const doc = {...change.doc.data(), id: change.doc.id};

		switch (change.type){
			case 'added':
				single_snapshot.push(doc);
				break;
			case 'modified':
				const index = single_snapshot.findIndex(item => item.id == doc.id);
				single_snapshot[index] = doc;
				break;
			case 'removed':
				single_snapshot = single_snapshot.filter(item => item.id !== doc.id);
				break;
			default:
				break;
		}
	});
	snapshot_table(single_snapshot);
});

snapshotTable = document.querySelector(".snapshot-view");
chainVerification = document.querySelector(".chain-verification");
recordVerification = document.querySelector(".record-verification");
tabSnap = document.querySelector("#snap-table")
tabChain = document.querySelector("#chain-table")
tabRecord = document.querySelector("#query-table")

function openSnapTable(){
chainVerification.style.display = "none"
recordVerification.style.display = "none"
snapshotTable.style.display = "block"

tabSnap.className +=" active"
tabChain.className ="tablinks"
tabRecord.className = "tablinks"
}

function openChainVerification(){
snapshotTable.style.display = "none"
recordVerification.style.display = "none"
chainVerification.style.display = "block"
tabSnap.className ="tablinks"
tabRecord.className = "tablinks"
tabChain.className +=" active"

}

function openRecordVerification(){
snapshotTable.style.display = "none"
recordVerification.style.display = "block"
chainVerification.style.display = "none"
tabSnap.className ="tablinks"
tabRecord.className += " active"
tabChain.className = "tablinks"

}

const chainTableFill = (d=>{
	Object.keys(d[0]).forEach(key =>{
		if (key !=='id'){
		var row = document.createElement("TR")
		var node1 = document.createElement("TD");
		var node2 = document.createElement("TD");
		var firstTextnode = document.createTextNode(key);
		var secondTextnode = document.createTextNode(d[0][key]._binaryString);

		node1.appendChild(firstTextnode);
		node2.appendChild(secondTextnode);
		row.appendChild(node1)
		row.appendChild(node2)
		document.querySelector('.chain-status-table').appendChild(row)
	}
	});
});

db.collection('chain_check').onSnapshot(res => {
	res.docChanges().forEach(change => {
		const doc = {...change.doc.data(), id: change.doc.id};

		switch (change.type){
			case 'added':
				chain_check.push(doc);
				break;
			case 'modified':
				const index = chain_check.findIndex(item => item.id == doc.id);
				chain_check[index] = doc;
				break;
			case 'removed':
				chain_check = chain_check.filter(item => item.id !== doc.id);
				break;
			default:
				break;
		}
	});
		chainTableFill(chain_check)
});

const recordTableFill = (d=>{
	Object.keys(d[0]).forEach(key =>{
		if (key !=='id'){
		var row = document.createElement("TR")
		var node1 = document.createElement("TD");
		var node2 = document.createElement("TD");
		var firstTextnode = document.createTextNode(key);
		var secondTextnode = document.createTextNode(d[0][key]._binaryString);

		node1.appendChild(firstTextnode);
		node2.appendChild(secondTextnode);
		row.appendChild(node1)
		row.appendChild(node2)
		document.querySelector('.record-status-table').appendChild(row)
	}
	});
	
	var tableData = document.querySelector('.record-status-table');
	var rowData = tableData.querySelectorAll('td')
	rowData.forEach(d=>{
		if (d.innerHTML === 'Untrusted'){
			d.style.color = 'red';
		}
		console.log(d.innerHTML);	
	});
	
});

db.collection('record_signature').onSnapshot(res => {
	res.docChanges().forEach(change => {
		const doc = {...change.doc.data(), id: change.doc.id};

		switch (change.type){
			case 'added':
				record_check.push(doc);
				break;
			case 'modified':
				const index = record_check.findIndex(item => item.id == doc.id);
				record_check[index] = doc;
				break;
			case 'removed':
				record_check = record_check.filter(item => item.id !== doc.id);
				break;
			default:
				break;
		}
	});
		recordTableFill(record_check)
});

