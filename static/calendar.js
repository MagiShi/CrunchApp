function initialize_calendar_setting() {
    $('input[name="daterange"]').daterangepicker({
    "linkedCalendars": false,
    "autoUpdateInput": false,
    "showCustomRangeLabel": false
    });
}

function greyout_taken_dates_in_my_reservations(all) {
    // 'all' array: [[0:email, 1:item_id, 2:start, 3:end, 4:status_enum: current,past,future]]
    var today = moment().format('MM/DD/YYYY');
    $('#upcoming-reservations input[name="daterange"]').each(function(index, input) {
        var item_id = $(input).attr('class');
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
