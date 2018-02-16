function toggleFilterMenu() {
    if (document.getElementById("filterMenu").style.width == "250px") {
        var menuItems = document.getElementById("filterMenu").getElementsByTagName('a');
        for (var i = 1; i < menuItems.length; i++) {
            menuItems[i].style.opacity = 0;
        }
        document.getElementById("filterMenu").style.width = "0";
    } else {
        if (document.getElementById("accountMenu").style.width == "250px") {
            toggleAccountMenu();
        }

        var menuItems = document.getElementById("filterMenu").getElementsByTagName('a');
        for (var i = 1; i < menuItems.length; i++) {
            menuItems[i].style.opacity = 1;
        }
        document.getElementById("filterMenu").style.width = "250px";
    }
}


function toggleAccountMenu() {
    if (document.getElementById("accountMenu").style.width == "250px") {
        var menuItems = document.getElementById("accountMenu").getElementsByTagName('a');
        for (var i = 1; i < menuItems.length; i++) {
            menuItems[i].style.opacity = 0;
        }
        document.getElementById("accountMenu").style.width = "0";
    } else {
        if (document.getElementById("filterMenu").style.width == "250px") {
            toggleFilterMenu();
        }

        var menuItems = document.getElementById("accountMenu").getElementsByTagName('a');
        for (var i = 1; i < menuItems.length; i++) {
            menuItems[i].style.opacity = 1;
        }
        document.getElementById("accountMenu").style.width = "250px";
    }
}