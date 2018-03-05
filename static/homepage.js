function homepageFilterMenuSetup() {
    updateCurrentFilters();
    var allFilters = document.getElementByClassName("panel");
    
    for (var i = 0; i < allFilters.length; i++) {
        allFilters.onclick = updateCurrentFilters();
    }
}

var prop = "(all prop types)";
var costume = "(all costume types)";
var timePeriod = "(all time periods)";
var region = "(all regions)";
var sex = "(all sexes)";
var color = "(all)"

function updateCurrentFilters() {
    var filtersList = document.getElementById("current-filters");
    var appliedFilters = "Filter by: ";
    var allFilters = document.getElementsByClassName("panel");
    
    for (var i = 0; i < allFilters.length; i++) {
        var count = 0;
        var currFilters = "";
        var currType = document.getElementById(allFilters[i].id).getElementsByTagName('input');
        
        var allFiltersString;
        switch (i) {
            case 0:
                allFiltersString = "(all prop types)";
                break;
            case 1:
                allFiltersString = "(all costume types)";
                break;
            case 2: 
                allFiltersString = "(all time periods)";
                break;
            case 3:
                allFiltersString = "(all regions)";
                break;
            case 4:
                allFiltersString = "(all sexes)";
                break;
            case 5:
                allFiltersString = "(all colors)";
                break;
            case 6:
                allFiltersString = "(all sizes)";
                break;
            case 7:
                allFiltersString = "(all conditions)";
                break;
            case 8:
                allFiltersString = "(all availabilities)";
                break;
        }
        
        
        for (var j = 0; j < currType.length; j++) {
            if (currType[j].checked) {
                if (count == 0) {
                    currFilters += currType[j].nextSibling.nodeValue.trim();
                } else {
                    currFilters += ", " + currType[j].nextSibling.nodeValue.trim();
                }
                count++;
            }
        }
        if (count != 0) {
            if (count == currType.length) {
                appliedFilters += allFiltersString;
            } else {
                appliedFilters += currFilters;
            }
            appliedFilters += "; ";
        }
        filtersList.innerHTML = appliedFilters;
    }
}