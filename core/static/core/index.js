function increaseValue(id) {
    let value = parseInt(document.getElementById("number" + id).value, 10);
    if(isNaN(value)) {value=1}
    else {
        value++;
        if(value>10) {value=10;}
        if(value<1) {value=1;}
    }
    document.getElementById("number" + id).value = value;
}

function decreaseValue(id) {
    let value = parseInt(document.getElementById("number" + id).value, 10);
    if(isNaN(value)) {value=1}
    else {
        value--;
        if(value>10) {value=10;}
        if(value<1) {value=1;}
    }
    document.getElementById("number" + id).value = value;
}

function getValue(id){
    let value = parseInt(document.getElementById("number" + id).value, 10);
    if(isNaN(value)) {value=1}
    document.getElementById("amount" + id).value = value;
}