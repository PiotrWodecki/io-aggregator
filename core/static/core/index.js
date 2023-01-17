function increaseValue(id) {
    let value = parseInt(document.getElementById("number" + id).value, 10);
    value = isNaN(value) ? 1 : value;
    value > 9 ? value = 9 : '';
    value < 1 ? value = 1 : '';
    value++;
    document.getElementById("number" + id).value = value;
}

function decreaseValue(id) {
    let value = parseInt(document.getElementById("number" + id).value, 10);
    value = isNaN(value) ? 1 : value;
    value < 1 ? value = 2 : '';
    value--;
    document.getElementById("number" + id).value = value;
}

function getValue(id){
    let value = parseInt(document.getElementById("number" + id).value, 10);
    document.getElementById("amount" + id).value = value;
}