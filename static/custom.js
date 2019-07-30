function showGroups(val, nam) {
    /* Creating AJAX-request */

	var xhttp, params;
	var nextid, previd;

	// в случае если объект пустой
	if (val == '') {
		return;
	}

    // define next necessary element
	switch(nam) {
	    case 'trtype':
	        nextid = 'oprGroup';
	        previd = 'oprSubGroup';
	        break;
	    case 'group':
	        nextid = 'oprSubGroup'
	        previd = undefined;
	        break;
	}

	// создать объект XMLHttpRequest
	xhttp = new XMLHttpRequest
	xhttp.onreadystatechange = function() {
		if(this.readyState == 4 && this.status == 200) {
		    try {
			    var itms = JSON.parse(this.responseText);
			} catch(e) {
			    alert('Некорректный ответ')
			}
			showItems(itms, nextid, previd);
		}
	};

	// собрать имя формы и значение
	params = nam.concat('=',val);
	console.log(params);

	// отправить форму
	xhttp.open("GET", "/show?".concat(params));
	xhttp.send();
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
