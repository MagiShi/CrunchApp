function toggleAccordion(clickedButton) {
    var panel = clickedButton.nextElementSibling;
    if (panel.style.maxHeight){
      panel.style.maxHeight = null;
    } else {
      panel.style.maxHeight = panel.scrollHeight + "px";
    }
}


var current_renamed_folder;

$(document).ready(function() {
    $('#delete-confirmed').click(function() {
        location.href = 'folders';
    });

    $('#create-folder-button').click(function() {
        //Reset the error message to empty string
        $( '.error-message' ).text('');
    });

    $('#save-name-button').click(function() {
        //remove trailing space and tab from the beginning and end of the name string
        var name_input = $('#input-new-foldername').val().trim();
        $('#input-new-foldername').val(name_input);

        //Check if input is empty or contains just white spaces only
        if ( name_input.length === 0) {
            $('#save-name-button').prop('type', 'button');
            $( '.error-message' ).text("* The name either is empty or contains only white spaces. Please input the eligible name for the folder. Example: Folder number 12");
            return;
        //Check if the name is unchanged. It just closes the modal.
        } else if (name_input === current_renamed_folder) {
            $('#save-name-button').prop('type', 'button');
            $('#rename-modal').modal('hide');
            return;
        } else {
            check_duplicate_folder_name("#save-name-button", name_input);
        }
    });

    $('#add-folder-button').click(function() {
        //Reset current renamed folder to pass the first if statement and take all folders into account.
        current_renamed_folder = '';

        //remove trailing space and tab from the beginning and end of the name string
        var name_input = $('#input-new-folder').val().trim();
        $('#input-new-folder').val(name_input);

        if ( name_input.length === 0) {
            $('#add-folder-button').prop('type', 'button');
            $( '.error-message' ).text("* The name either is empty or contains only white spaces. Please input the eligible name for the folder. Example: Folder number 12");
            return;
        } else {
            check_duplicate_folder_name("#add-folder-button", name_input);
        }
    });

    // Tooltip for the icon buttons
    $('[data-tooltip="tooltip"]').tooltip({trigger: "hover"});
});

function activate_rename_field(folder_name) {
    $('#rename-modal').on('show.bs.modal', function(e) {
        $(this).find("input").val(folder_name);
        $(this).find("#save-name-button").val(folder_name);
        current_renamed_folder =  folder_name;
        //Reset the error message to empty string
        $( '.error-message' ).text('');
    });
}

function get_delete_name(folder_name) {
    $('#delete-modal').on('show.bs.modal', function(e) {
        $(this).find("input").val(folder_name);
        $(this).find("#delete-confirmed").val(folder_name);
    });
}

function check_duplicate_folder_name(button_id, name_input) {
    var is_duplicate = false;

    // Check if the input name is duplicate with any existing folders (not deleted-pending)
    $( '.list-group-item' ).each(function() {
        var foldername = $(this).attr('id').split("_")[1];
        if (foldername !== current_renamed_folder) {
            if (foldername === name_input) {
                $( '.error-message' ).text("* There is an existing folder with that name. Please use the different name for the folder.");
                $(button_id).prop('type', 'button');
                is_duplicate = true;
            }
        }
    });

    // Check if the input name is duplicate with any deleted-pending folders
    var deleted_folders = {{ deletedfolders|safe }};
    deleted_folders.forEach(function(e) {
        if (e === name_input) {
            $( '.error-message' ).text("* There is a pending deleted folder with that name. Please use the different name for the folder.");
            $(button_id).prop('type', 'button');
            is_duplicate = true;
        }
    });

    if (!is_duplicate) {
        $(button_id).prop('type', 'submit');
    }
}
