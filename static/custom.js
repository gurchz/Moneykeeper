$(function () {
    $('#currentParametersIcon').popover({
        container: 'body',
        title: 'Общие параметры',
        content: $('#forPopover').html(),
        trigger: 'focus',
        placement: 'bottom',
        html: true
    })
});

function creatingXMLHttpReq(cmd, obj, meth="GET", formName="", toJSON=false) {
    // If cmd is array call function from cycle
    var arrYes = false;
    if (Array.isArray(cmd)) {
        arrYes = true;
        cmd.forEach(function(c) {
            creatingXMLHttpReq(c, obj);
        })
    }
    if (arrYes) {return;}

    /* Creating AJAX-request */
    var xhttp, params, resUrl;
    
	// создать объект XMLHttpRequest
	xhttp = new XMLHttpRequest
	xhttp.onreadystatechange = function() {
		if(this.readyState == 4 && this.status == 200) {
		    try {
		        alert(this.responseText);
			    var itms = JSON.parse(this.responseText);
			} catch(e) {
			    alert('Некорректный ответ')
			}
			switch(cmd) {
			    case 'show_groups':
			        showGroups(itms, obj.value, obj.name);
			        break;
			    case 'show_trns':
                    showTrns(itms, 'trnTable');
                    $('#dailyTrnModal').modal('show'); // show modal
			        break;
			    case 'show_last_months':
			        crCostMonthDiagr(itms);
			        break;
			    case 'show_accounts':
			        showAccounts(itms, obj);
			        break;
			    case 'show_users':
			        showAccounts(itms, obj, 'userInModal');
			        break;
			    case 'update_balances':
                    showBalanceAndSberUpd(itms);
			        break;
			    case 'send_sber_data':
                    addMsgToContainer(itms);
                    updBalances();
                    $('#sberManage').modal('hide');
                    break;
                case 'month_year':
                    newDateInInput([itms.year, itms.month]);
                    break;
                case 'show_planning':
                    formCreating(itms, 'modalContentPlanning', 'planningModal');
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
            var btn = document.getElementById('btnAddFromTrnModal');
            btn.addEventListener('click', () => {newDateInInput('oprDate', d);showModalByHiding('#dailyTrnModal', '#addTrnModal');enabledBtnInCal();})
	        document.getElementById('trnDate').innerHTML = d.concat(' ', m.toLowerCase(), ' ', y);
	        break;
	    case 'show_last_months':
	        params='show_months=true';
	        break;
	    case 'show_accounts':
	    case 'show_users':
        case 'month_year':
            params = cmd + '=true'
            break;
        case 'show_planning':
            params = cmd + '=true&planning_group=' + obj;
            break;
	    case 'update_balances':
	        params = 'upd_sber_data=true';
            break;
	};
	console.log(params);
	switch(meth) {
	    case 'GET':
	        resUrl = '/show?'.concat(params);
	        break;  
	    case 'POST':
            resUrl = '/submit/';
            switch(cmd) {
                case 'planningSave':
                    resUrl += 'planning';
                    try {
                        dataForSend = mineFormData(formName);
                    } catch(NoData) {
                        msgForAlert = 'Нет данных';
                        alert(msgForAlert);
                        return 0;
                    };
                    break;
                default:
                    resUrl += 'default';
                    dataForSend = new FormData(document.forms[formName]);
            }
	}

	// отправить форму
	xhttp.open(meth, resUrl);
	if (meth == 'GET') {
	    xhttp.send();
	} else {
        if (toJSON) {
            dataForSend = JSON.stringify(dataForSend);
        }
	    xhttp.send(dataForSend);
	}
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


function enabledBtnInCal(els_ids = ['oprType', 'oprGroup', 'oprSubGroup', 'oprOwner', 'oprSum', 'oprDate'],
                         btnId='addTrnBtn') {
    /* Check when submit button should be enabled */

    var btn = document.getElementById(btnId);
    var valStatus = true;

    try {
        var NoValidation = {};
        els_ids.forEach(function(el_id) {
            var el_val = document.getElementById(el_id).value;
            if (el_val == '' || el_val == 'Выбор...') {
                throw NoValidation;
            }
        });
    } catch(e) {
        if (e !== NoValidation) {
            throw e
        } else {
            valStatus = false;
        }
    }

    if (valStatus) {
        btn.disabled = false;
    } else {
        btn.disabled = true;
    };
}

function showTrns(itms, tableId) {
    var tbl = document.getElementById(tableId);

    // let's clear table
    tbl.innerText = '';

    // lets create tbody
    var tbd = document.createElement('tbody');

    // let's create tr
    itms.forEach(function(r){
        var rbr = document.createElement('tr');
        // let's create td
        for (var c in r) {
            var rbc = document.createElement('td');
            rbc.innerText = r[c];
            rbr.appendChild(rbc);
        };
        tbd.appendChild(rbr);
    });

    // insert data into table
    tbl.appendChild(tbd);
};

function showModalByHiding(id_for_hide, id_for_show) {
    $(id_for_hide).modal('hide');
    $(id_for_show).modal('show');
}

function showAccounts(itms, modalId, selId='accountsInModal') {
    // detect option and clear it
    var sel = document.getElementById(selId);
    sel.innerHTML = '';

    // creating default element
    var opt_def = document.createElement('option');
    opt_def.innerHTML = 'Выбор...';
    sel.add(opt_def);
    opt_def = undefined;

    // getting data from db and adding it to select
    itms.forEach(function(itm) {
        var opt = document.createElement('option');
        opt.value = itm[0];
        opt.text = itm[1];
        sel.add(opt);
    });

    // show modal
    $(modalId).modal('show');
}

function updBalances() {
    creatingXMLHttpReq('update_balances');
}

function showBalanceAndSberUpd(itms) {
    var b = document.getElementById('balTotal');
    var sber_b = document.getElementById('balSber');
    var b_nav = document.getElementById('navBal');
    var sber_b_nav = document.getElementById('navSberBal');

    b.innerHTML = itms.bal;
    sber_b.innerText = itms.sber_bal;

    b_nav.innerHTML = itms.bal;
    sber_b_nav.innerText = itms.sber_bal;

    showTrns(itms.sber_tbl, 'tblSber');
}

function addMsgToContainer(content, msgContainerId='msg-container', msgId="serverMsg") {
    // Getting msg-contaiener
    var msgContObj = document.getElementById(msgContainerId);
    var newMsg = document.createElement('div');
    
    // Defining attrinbutes of msg-div and adding it to container
    newMsg.setAttribute('id', msgId)
    newMsg.setAttribute('class', 'fade show alert '.concat('alert-', content.class));
    newMsg.setAttribute('role', 'alert');
    newMsg.innerText = content.txt;
    msgContObj.appendChild(newMsg);
    $('#'.concat(msgId)).alert();
    
    // Removing it after a little pause
    setTimeout(() => $('#'.concat(msgId)).alert('close'), 5000);
}

function checkSumData(inpId='val') {
    /* for checking integer values */
    var resVal = '';
    var tmpVal;
    var sumVal = document.getElementById(inpId).value;
    for (let i in sumVal) {
        let itrVal = sumVal[i];
        if (itrVal !== '.' && itrVal !== ',') {
            tmpVal = parseInt(itrVal);
            if (isNaN(tmpVal)) {
                continue;
            }
        } else {
            tmpVal = itrVal; 
        }            
        resVal = resVal.concat(tmpVal);
    }
    document.getElementById(inpId).value = resVal;    
}

function newDateInInput(inpId, newDay) {
    /* for changing date in form by clicking button from another modal */
    WrongDay = {};
    var inp = document.getElementById(inpId);
    try {
        newDay = addingZeros(newDay);
    } catch(WrongSymLength) {
        newDay = '01';
    };
    oldDateArr = inp.value.split('-');
    oldDateArr[2] = newDay;
    inp.value = oldDateArr.join('-');
}

function addingZeros(strForAdding, maxSymbols=2) {
    /* Adding leading zeros */
    var WrongSymLength = new Object();
    var zeros = new String();
    if (typeof(strForAdding) !== 'string') {strForAdding += '';};
    var nessZeros = maxSymbols - strForAdding.length;
    if (nessZeros >= maxSymbols || nessZeros < 0) {
        throw WrongSymLength;
    } else if (nessZeros < maxSymbols && nessZeros > 0 ) {
        for (i=0; i < nessZeros; i++) {
            zeros += '0';
        }
    }
    return zeros + strForAdding;
}

function addingEventListenerForPl() {
    /* Adding event listeners for planning editing buttons */

    var plBtns = document.getElementsByClassName('edit-plan');
    for (let i=0; i < plBtns.length; i++) {
        let plBtn = plBtns[i];
        plBtn.addEventListener('click', () => {showPlanningGroup(plBtn.id)});
    };

    var saveBtn = document.getElementById('planningSave');
    const METH = 'POST';
    const FORM_NAME = 'planningForm';
    saveBtn.addEventListener('click', () => {creatingXMLHttpReq(saveBtn.id, saveBtn, METH, FORM_NAME, true)});
}

function showPlanningGroup(btnId) {
    /* Matching operations according to planning-edit button */
    var planningGroup;
    switch(btnId) {
        case 'btnEditIncome':
            planningGroup = 'INC';
            break;
        case 'btnEditOpt':
            planningGroup = 'OPT';
            break;
        case 'btnEditMan':
            planningGroup = 'MAN';
            break;
        case 'btnEditOut':
            planningGroup = 'OUT';
            break;
    }
    if (planningGroup !== undefined) {
        creatingXMLHttpReq('show_planning', planningGroup);
    }
}

function formCreating(itms, containerIdForCreating, modalIdForShow) {
    /* Creating form elements */
    var containerForCr = document.getElementById(containerIdForCreating);
    var formData = itms.data;
    var formKeys = itms.keys;

    // Cleaniing modal
    containerForCr.innerHTML = '';

    // Checking data length
    if (formData.length !== 0) {
        // Create form if data doesnt equal zero
        var formObj = document.createElement('form');
        formObj.setAttribute('method', 'POST');
        formObj.setAttribute('id', 'planningForm');
        formData.forEach(function(r) {
            // For each data row create new div element
            var divObj = document.createElement('div');
            divObj.setAttribute('class', 'row p-2');
            for (let i=0; i < formKeys.length; i++) {
                // Create html-tag that was specified in JSON
                var inpObj = document.createElement(formKeys[i].tag);
                inpObj.setAttribute('name', formKeys[i].name);

                var valCreated = false; // Default value - val not created
                
                // When tag is input we should specify a type element
                if (formKeys[i].tag == 'input') { 
                    inpObj.setAttribute('type', formKeys[i].attr);
                } else if (formKeys[i].tag == 'select') {
                    var optObj = document.createElement('option');
                    optObj.innerText = r[formKeys[i].name];
                    if (formKeys[i].ref !== null) {
                        optObj.setAttribute('value', r[formKeys[i].ref]);
                    }
                    valCreated = true // val is created now and we shouldnt add it again
                    inpObj.appendChild(optObj);
                };
                
                // If value wasnt created we should do it
                if (!valCreated) {
                    inpObj.setAttribute('value', r[formKeys[i].name]);
                }

                // If in JSON file edition is not allowed
                if (!formKeys[i].edit) {
                    inpObj.disabled = true;
                };
                inpObj.setAttribute('class', 'form-control col-md m-2');
                divObj.appendChild(inpObj);
            }
        formObj.appendChild(divObj);
        });
    } else {
        var formObj = document.createElement('p');
        formObj.innerText = 'Нет данных';
        formObj.setAttribute('class', 'col-12 text-center');
        btnVisible('fromPrevMonth', true);
    };
    containerForCr.appendChild(formObj);
    modalShow(modalIdForShow);
}

function modalShow(modalId) {
    $('#' + modalId).modal('show');
}

function crBtn(value, id, cls="btn", type="button") {
    /* Creating btn */
    var newBtn = document.createElement('button');
    newBtn.setAttribute('type', type);
    newBtn.setAttribute('class', cls);
    newBtn.setAttribute('id', id);
    newBtn.innerText = value;
    return newBtn;
}

function btnVisible(btnId, vis) {
    /* Changing visibility of button */
    var btn = document.getElementById(btnId);
    var visVal;
    if (vis) {
        visVal = 'inline-block';
    } else {
        visVal = 'none';
    }
    btn.style.display = visVal;
}

function mineFormData(formId) {
    /* Mine form data by form id */
    
    var NoData = {}
    // Getting form object
    try {
        var formObjElements = document.getElementById(formId).elements;
    } catch(e) {
        throw NoData;
    }

    if (formObjElements.length == 0) {throw NoData};
    
    // Creating object
    var fData = [], iterObj = {};
    for (let i=0; i < formObjElements.length; i++) {
        iterObj['name'] = formObjElements[i].name;
        iterObj['value'] = formObjElements[i].value;
        fData.push(iterObj);
        iterObj = {};
    }
    return fData;
}