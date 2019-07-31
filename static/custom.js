function creatingXMLHttpReq(cmd, obj) {
    /* Creating AJAX-request */

	var xhttp, params;

	// создать объект XMLHttpRequest
	xhttp = new XMLHttpRequest
	xhttp.onreadystatechange = function() {
		if(this.readyState == 4 && this.status == 200) {
		    try {
			    var itms = JSON.parse(this.responseText);
			} catch(e) {
			    alert('Некорректный ответ')
			}
			switch(cmd) {
			    case 'show_groups':
			        showGroups(itms, obj.value, obj.name);
			        break;
			    case 'show_trns':
			        showTrns(itms);
			        break;
			}
		}
	};

	// собрать имя формы и значение
	switch(cmd) {
	    case 'show_groups':
	        if (obj.value == "") {return;};
	        params = obj.name.concat('=', obj.value);
	        break;
	    case 'show_trns':
	        var d = obj.firstElementChild.innerText,
	            m = document.getElementById('trn_month').innerText,
	            y = document.getElementById('trn_year').innerText;
	        params = 'trn_day='.concat(d);
	        var idsOfEls = ['trn_month', 'trn_year'];
	        idsOfEls.forEach(function(idOfEl) {
	            var objById = document.getElementById(idOfEl);
	            params = params.concat('&', objById.id, '=', objById.innerText);
	        });
	        document.getElementById('trnDate').innerHTML = d.concat(' ', m.toLowerCase(), ' ', y);
	        break;
	};
	console.log(params);

	// отправить форму
	xhttp.open("GET", "/show?".concat(params));
	xhttp.send();
}

function showGroups(items, val, nam) {
	var nextid, previd;

    // define next necessary element
	switch(nam) {
	    case 'trtype':
	        nextid = 'oprGroup';
	        previd = 'oprSubGroup';
	        break;
	    case 'group':
	        nextid = 'oprSubGroup';
	        previd = undefined;
	        break;
	}
	showItems(items, nextid, previd);
}

function showItems(arr, sel_id, prev_id) {
    /* Returns AJAX-request when on trn-adding-form */

    // detecting necessary select-tag by its id
    var selectObj = document.getElementById(sel_id);

    // clear all items
    selectObj.innerHTML = '';
    if (prev_id !== undefined) {
        var selectPrevObj = document.getElementById(prev_id);
        selectPrevObj.innerHTML = '';
    }

    // loop for returned array
    arr.forEach(function(itm) {
        var optionObj = document.createElement('option')
        optionObj.setAttribute('value', itm[0]);
        optionObj.text = itm[1];
        selectObj.appendChild(optionObj);
    });
    optionObj = document.createElement('option');
    optionObj.text = 'Выбор...'
    optionObj.setAttribute('selected', 'selected')
    selectObj.insertBefore(optionObj, selectObj.firstElementChild);
}


function enabledBtnInCal() {
    /* Check when submit button should be enabled */

    var btn = document.getElementById('addTrnBtn');
    var valStatus = false;

    els_ids = ['oprType', 'oprGroup', 'oprSubGroup', 'oprOwner', 'oprSum', 'oprDate'];

    els_ids.forEach(function(el_id) {
        if (document.getElementById(el_id).value == '') {
            valStatus = false;
            return;
        }
        valStatus = true;
    });

    if (valStatus) {
        btn.disabled = false;
    } else {
        btn.disabled = true;
    };
}

function showTrns(itms) {
    var tbl = document.getElementById('trnTable');

    // let's clear table
    tbl.innerText = '';

    // lets create tbody
    var tbd = document.createElement('tbody');

    // let's create tr
    itms.forEach(function(r){
        var rbr = document.createElement('tr');
        // let's create td
        r.forEach (function(c) {
            var rbc = document.createElement('td');
            rbc.innerText = c;
            rbr.appendChild(rbc);
        });
        tbd.appendChild(rbr);
    });

    // insert data into table
    tbl.appendChild(tbd);

    // show modal
    $('#dailyTrnModal').modal('show');
};