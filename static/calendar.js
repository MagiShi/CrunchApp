// hold the values of the dates in all the input boxes
var calendarValues = [];
var itemIds = [];

function initialize_calendar_setting() {
    $('input[name="daterange"]').daterangepicker({
        "linkedCalendars": false,
        "autoUpdateInput": false,
        "showCustomRangeLabel": false,
        beforeShow: function(){$('input').blur();}
    });
    
    // store original values of the calendars
    $('.calendar-picker-input').each(function() {
        calendarValues.push($(this).val());
    });
}

// Function called when the Apply button is clicked
$(document).on('click','#my-reservations-page-body .daterangepicker .applyBtn',function(){
    console.log("Old calendar values: ");
    for (i = 0; i < calendarValues.length; i++) {
        console.log(i + ": " + calendarValues[i]);
    }
    
    // calendarDivIndex is the index regarding body as a parent
    // CURRENTLY the calendars are the 8th, 9th, 10th, ... children of <body>, so if we want the first (index 0) calendar, we would do calendarDivIndex - 8. This means the next line is hardcoded and a bit ridiculous
    // (Sorry, I couldn't figure out how to get which number Apply Button was clicked)
    var calendarDivIndex = $(this).parent().parent().parent().index() - 8;
    
    // Next line selects the calendar value of that number calendar
    var calendarResult = $('.calendar-picker-input').eq(calendarDivIndex).val();

    prev_start= calendarValues [calendarDivIndex];
    // Update the array of calendar values
    calendarValues[calendarDivIndex] = calendarResult;
    
    console.log("New calendar values: ");
    for (i = 0; i < calendarValues.length; i++) {
        console.log(i + ": " + calendarValues[i]);
    }

    // alert(itemIds);
    // alert(calendarResult);
    // alert(prev_start);
    // alert("/editReservation?daterange=" + calendarResult);
    var nospace = calendarResult.replace(/\s/g, '');
    // return [itemIds[calendarDivIndex], calendarResult, prev_start];
    var jsonobj= JSON.stringify({itemId: itemIds[calendarDivIndex], calendarResult: calendarResult, prev_start: prev_start});
    // alert(jsonobj);
    var strJSON = encodeURIComponent(jsonobj);
    // alert(strJSON)


    window.location.replace("/editReservation/"+strJSON);
});


function greyout_taken_dates_in_my_reservations(all) {
    // 'all' array: [[0:email, 1:item_id, 2:start, 3:end, 4:status_enum: current,past,future], 5:item name]
    var today = moment().format('MM/DD/YYYY');
    $('#upcoming-reservations input[name="daterange"]').each(function(index, input) {
        var item_id = $(input).attr('class');
        itemIds.push(item_id);
        var current_reserved_time = $(input).val();
        var takenDateRanges = [];
        $(input).daterangepicker({
            isInvalidDate: function(date) {
                takenDateRanges = [];
                all.forEach(function(reservation) {
                    if (item_id === reservation[1]) {
                        if (moment(reservation[2]).format('MM/DD/YYYY') !== current_reserved_time.substring(0,10)) {
                            takenDateRanges.push({"start": reservation[2], "end": reservation[3]});
                        }
                    }
                });
                return takenDateRanges.reduce(function(bool, range) {
                    return bool || (date >= moment(range.start) && date <= moment(range.end));
                }, false);
            },
            "minDate": today
        });
    });
}

function greyout_taken_dates_in_new_reservation(all) {
    // 'all' array: [[0:email, 1:item_id, 2:start, 3:end, 4:status_enum: current,past,future]]
    var today = moment().format('MM/DD/YYYY');
    $('input[name="daterange"]').each(function(index, input) {
        var takenDateRanges = [];
        $(input).daterangepicker({
            isInvalidDate: function(date) {
                all.forEach(function(reservation) {
                    takenDateRanges.push({"start": reservation[2], "end": reservation[3]});
                });
                return takenDateRanges.reduce(function(bool, range) {
                    return bool || (date >= moment(range.start) && date <= moment(range.end));
                }, false);
            },
            "minDate": today
        });
    });
}

function set_default_start_end(date) {
    $('input[name="daterange"]').daterangepicker({
        "linkedCalendars": false,
        "autoUpdateInput": false,
        "showCustomRangeLabel": false,
        "startDate": date,
        "endDate": date
    });
}
