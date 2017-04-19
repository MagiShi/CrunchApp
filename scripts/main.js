


var reference = firebase.database();
var itemNameField = document.getElementById('itemName');
var barcodeField = document.getElementById('barcode');
var descField = document.getElementById('shortDescription');
var number = 1;

function saveAddItemData() {
    var item = itemNameField.value;
    var id = barcodeField.value;
    var description = descField.value;

    reference.ref('items/' + number++).update(
        {name:item,
            desc:description,
            barcode:id}
    );
}