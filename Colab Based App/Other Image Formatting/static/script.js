// Functions

function toggleScale() {
    const graphType = document.getElementById('graphType').value;
    const divScale = document.getElementById('divScale');
    const scaleByIntCheckbox = document.getElementById('scale_by_int');
    const showGridCheckbox = document.getElementById('show_grid');
    const checkGroup = document.getElementById('checkGroup');

    if (!graphType) {
        checkGroup.style.display = 'none';
        divScale.hidden = true;
    }

    else if (graphType === "traditional") {
        divScale.hidden = false;
        checkGroup.style.display = 'flex'
        scaleByIntCheckbox.parentElement.style.display = 'none';
        showGridCheckbox.parentElement.style.display = 'none';

    } 
    
    else if (graphType === "gaussian" || graphType === "non rgb line"){
        divScale.hidden = true;
        showGridCheckbox.parentElement.style.display = 'flex';
        checkGroup.style.display = 'flex'
        scaleByIntCheckbox.parentElement.style.display = 'none';
    }
    
    else {
        divScale.hidden = true;
        scaleByIntCheckbox.parentElement.style.display = 'flex';
        showGridCheckbox.parentElement.style.display = 'flex';
        checkGroup.style.display = 'flex'
    }

}


function labelColours() {
    var peakCheckbox = document.getElementById('show_peak_labels');
    var colourCheckbox = document.getElementById('conditionalCheckbox');
    const graphType = document.getElementById('graphType').value;

    if (graphType === "") {
        colourCheckbox.style.display = 'none';
    }

    else if (peakCheckbox.checked == true && !(graphType === 'traditional')) {
        colourCheckbox.style.display = 'flex';
    }
    else {
        colourCheckbox.style.display = 'none';
    }
}


function sheetForm() {
    const fileUpload = document.getElementById('file');
    const sheet = document.getElementById('sheetSelect');
    var userTitle = document.getElementById('titleGroup');

    if (fileUpload=== "") {
        sheet.hidden = true;
        userTitle.hidden = true;
    }
    else {
        sheet.hidden = false;
        userTitle.hidden = false;
    }
}


