// For the opening and closing of the left filter menu
function toggleFilterMenu() {
    if (document.getElementById("filter-menu").style.width == "300px") {
        var menuItems = document.getElementById("filter-menu").getElementsByTagName('a');
        for (var i = 1; i < menuItems.length; i++) {
            menuItems[i].style.opacity = 0;
        }
        document.getElementById("filter-menu").style.width = "0";
    } else {
        if (document.getElementById("account-menu").style.width == "300px") {
            toggleAccountMenu();
        }

        var menuItems = document.getElementById("filter-menu").getElementsByTagName('a');
        for (var i = 1; i < menuItems.length; i++) {
            menuItems[i].style.opacity = 1;
        }
        document.getElementById("filter-menu").style.width = "300px";
    }
}

// For the opening and closing of the "accordion panels" within the filter menu
function toggleAccordion(filterButton) {
    var panel = filterButton.nextElementSibling;
    if (panel.style.maxHeight){
      panel.style.maxHeight = null;
    } else {
      panel.style.maxHeight = panel.scrollHeight + "px";
    }
}

// For the opening and closing of the right account menu
function toggleAccountMenu() {
    if (document.getElementById("account-menu").style.width == "250px") {
        var menuItems = document.getElementById("account-menu").getElementsByTagName('a');
        for (var i = 1; i < menuItems.length; i++) {
            menuItems[i].style.opacity = 0;
        }
        document.getElementById("account-menu").style.width = "0";
    } else {
        if (document.getElementById("filter-menu").style.width == "250px") {
            toggleFilterMenu();
        }

        var menuItems = document.getElementById("account-menu").getElementsByTagName('a');
        for (var i = 1; i < menuItems.length; i++) {
            menuItems[i].style.opacity = 1;
        }
        document.getElementById("account-menu").style.width = "250px";
    }
}