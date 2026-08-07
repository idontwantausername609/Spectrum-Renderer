// Predefined Variables/Constants

//Fullscreen preview modal logic
const previewModal = document.getElementById('previewModal');
const modalChartContainer = document.getElementById('modalPlotlyChart');
const modalClose = document.getElementById('modalClose');
const modalBackdrop = document.getElementById('modalBackdrop');
const mainChart = document.getElementById('mainPlotlyChart');

// File upload and sheet loading
const fileInput = document.getElementById('file');
const sheetSelect = document.getElementById('sheet');
const renderForm = document.getElementById('renderForm');
const resultDiv = document.getElementById('result');
const renderAllCheckbox = document.getElementById('render_all_sheets');
let availableSheets = [];

const graphType = document.getElementById('graphType').value;

// Global data states
let globalHeaders = [];
let intHeaders = [];
let nmHeaders = [];
let globalRows = [];
let rawParsedData = [];

let globalChartData = null; 


// Functions

function toggleScale() {
    const divScale = document.getElementById('divScale');
    const scaleByIntCheckbox = document.getElementById('scale_by_int');
    const showGridCheckbox = document.getElementById('show_grid');
    const checkGroup = document.getElementById('checkGroup');
    const revCheckbox = document.getElementById('reverse_x');
    const graphType = document.getElementById('graphType').value;

    if (!graphType) {
        checkGroup.style.display = 'none';
        divScale.hidden = true;
    }
    else if (graphType === "traditional") {
        divScale.hidden = false;
        checkGroup.style.display = 'flex'
        scaleByIntCheckbox.parentElement.style.display = 'none';
        showGridCheckbox.parentElement.style.display = 'none';
        revCheckbox.parentElement.style.display = 'none'
    }
    else if (graphType === "gaussian" || graphType === "non rgb line") {
        divScale.hidden = true;
        showGridCheckbox.parentElement.style.display = 'flex';
        checkGroup.style.display = 'flex'
        scaleByIntCheckbox.parentElement.style.display = 'none';
        revCheckbox.parentElement.style.display = 'flex'
    }
    else {
        divScale.hidden = true;
        scaleByIntCheckbox.parentElement.style.display = 'flex';
        showGridCheckbox.parentElement.style.display = 'flex';
        checkGroup.style.display = 'flex'
        revCheckbox.parentElement.style.display = 'flex'
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

function selectHeaders() {
    var detectCheckbox = document.getElementById('detect_header_rows');
    var colGroup = document.getElementById('selector-section');

    if (detectCheckbox.checked == true) {
        colGroup.hidden = false;
    }
    else {
        colGroup.hidden = true;
    }
}

function sheetForm() {
    const fileUpload = document.getElementById('file');
    const sheet = document.getElementById('sheetSelect');
    var userTitle = document.getElementById('titleGroup');

    if (fileUpload === "") {
        sheet.hidden = true;
        userTitle.hidden = true;
    }
    else {
        sheet.hidden = false;
        userTitle.hidden = false;
    }
}


function tableToggle() {
    const dataPreview = document.getElementById('preview-section');
    var dataPreviewButton = document.getElementById('data-preview-button');
    const table = document.getElementById('table-container');

    table.classList.toggle('hidden');

}



function loadSheetJS(callback) {
    if (typeof XLSX !== "undefined") {
        callback();
        return;
    }
    const script = document.createElement("script");
    script.src =
        "https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js";
    script.onload = () => {
        console.log("SheetJS loaded successfully.");
        callback();
    };
    script.onerror = () => {

        const fallbackScript = document.createElement("script");
        fallbackScript.src = "https://sheetjs.com";
        fallbackScript.onload = callback;
        document.head.appendChild(fallbackScript);
    };
    document.head.appendChild(script);
}

function parseCSVTo2DArray(text) {
    const lines = text.split(/\r?\n/).filter((line) => line.trim().length > 0);
    return lines.map((line) => {
        const result = [];
        let current = "";
        let inQuotes = false;
        for (let i = 0; i < line.length; i++) {
            let char = line[i];
            if (char === '"') inQuotes = !inQuotes;
            else if (char === "," && !inQuotes) {
                result.push(current.trim());
                current = "";
            } else current += char;
        }
        result.push(current.trim());
        return result;
    });
}

function processRawData(dataGrid) {
    if (!dataGrid || dataGrid.length === 0) return;
    const hasHeaders = document.getElementById("has-headers").checked;
    const maxCols = Math.max(...dataGrid.map((row) => (row ? row.length : 0)));
    if (maxCols === 0) return;

    if (hasHeaders) {
        const firstRow = dataGrid[0] || [];
        globalHeaders = [...firstRow];
        globalRows = dataGrid.slice(1);

        for (let i = 0; i < maxCols; i++) {
            if (!globalHeaders[i] || globalHeaders[i].toString().trim() === "") {
                globalHeaders[i] = `Column ${i + 1}`;
            }
        }
    } else {
        globalHeaders = Array.from({ length: maxCols }, (_, i) => `Column ${i + 1}`);
        globalRows = dataGrid;
    }

    const selectorSection = document.getElementById("selector-section");
    if (selectorSection) selectorSection.classList.remove("hidden");
    const previewSec = document.getElementById("preview-section");
    if (previewSec) previewSec.classList.remove("hidden");
    updateTablePreview();
    setupColumnSelector();
}

function setupColumnSelector() {
    const intContainer = document.getElementById("int-selection");
    const nmContainer = document.getElementById("nm-selection");
    const prevIntSelected = document.querySelector('input[name="intensity-column"]:checked')?.value;
    const prevNmSelected = document.querySelector('input[name="wavelength-column"]:checked')?.value;

    intContainer.innerHTML = "";
    nmContainer.innerHTML = "";

    globalHeaders.forEach((header, index) => {
        const intLabel = document.createElement("label");
        intLabel.className = "radio-label";
        const intRadio = document.createElement("input");
        intRadio.type = "radio";
        intRadio.name = "intensity-column";
        intRadio.value = index + 1;
        intRadio.checked = prevIntSelected ? (parseInt(prevIntSelected, 10) === index + 1) : (index === 0);
        intRadio.addEventListener("change", updateTablePreview);
        intLabel.appendChild(intRadio);
        intLabel.appendChild(document.createTextNode(` ${header}`));
        intContainer.appendChild(intLabel);

        // Generate Wavelength Column Radios
        const nmLabel = document.createElement("label");
        nmLabel.className = "radio-label";
        const nmRadio = document.createElement("input");
        nmRadio.type = "radio";
        nmRadio.name = "wavelength-column";
        nmRadio.value = index + 1;
        nmRadio.checked = prevNmSelected ? (parseInt(prevNmSelected, 10) === index + 1) : (index === 1);
        nmRadio.addEventListener("change", updateTablePreview);
        nmLabel.appendChild(nmRadio);
        nmLabel.appendChild(document.createTextNode(` ${header}`));
        nmContainer.appendChild(nmLabel);
    });
    updateTablePreview();
}

function updateTablePreview() {
    if (!globalHeaders || globalHeaders.length === 0) return;
    const activeIndexes = globalHeaders.map((_, index) => index);
    const thead = document.getElementById("table-head");
    thead.innerHTML = "";
    const trHead = document.createElement("tr");

    activeIndexes.forEach((idx) => {
        const th = document.createElement("th");
        th.textContent = globalHeaders[idx];
        trHead.appendChild(th);
    });
    thead.appendChild(trHead);
    const tbody = document.getElementById("table-body");
    tbody.innerHTML = "";

    if (!globalRows || globalRows.length === 0) return;

    globalRows.slice(0, 5).forEach((row) => {
        if (!row) return;
        const tr = document.createElement("tr");

        activeIndexes.forEach((idx) => {
            const td = document.createElement("td");
            td.textContent = row[idx] !== undefined ? row[idx] : "";
            tr.appendChild(td);
        });
        tbody.appendChild(tr);
    });
}

document.getElementById("has-headers").addEventListener("change", () => {
    if (globalRows && globalRows.length > 0) {
        const hasHeaders = document.getElementById("has-headers").checked;
        let fallbackGrid = [];

        if (hasHeaders) {
            fallbackGrid = [globalHeaders, ...globalRows];
        } else {
            const isGeneric = globalHeaders[0] === "Column 1";
            fallbackGrid = isGeneric ? [...globalRows] : [globalHeaders, ...globalRows];
        }

        processRawData(fallbackGrid);
    }
});

// Script
loadSheetJS(() => {
    document
        .getElementById("has-headers")
        .addEventListener("change", function () {
            if (rawParsedData && rawParsedData.length > 0) {
                processRawData(rawParsedData);
            }
        });

    document
        .getElementById("file")
        .addEventListener("change", function (e) {
            const files = e.target.files;
            if (!files || files.length === 0) return;

            const file = files[0];
            const reader = new FileReader();
            const extension = file.name.split(".").pop().toLowerCase();

            if (extension === "csv") {
                reader.onload = function (evt) {
                    rawParsedData = parseCSVTo2DArray(evt.target.result);
                    processRawData(rawParsedData);
                };
                reader.readAsText(file);
            } else if (extension === "xlsx" || extension === "xls") {
                reader.onload = function (evt) {
                    try {
                        const data = new Uint8Array(evt.target.result);
                        const workbook = XLSX.read(data, { type: "array" });
                        const sheetName = workbook.SheetNames[0];
                        const worksheet = workbook.Sheets[sheetName];

                        // Convert spreadsheet to 2D array grid [[row1], [row2]]
                        rawParsedData = XLSX.utils.sheet_to_json(worksheet, {
                            header: 1,
                            defval: ""
                        });
                        processRawData(rawParsedData);
                    } catch (err) {
                        console.error("Parsing engine crash: ", err);
                        alert("Error parsing file structure.");
                    }
                };
                reader.readAsArrayBuffer(file);
            }
        });
});

// File upload and sheet loading
fileInput.addEventListener('change', async (e) => {
    e.preventDefault();
    resultDiv.innerHTML = '';
    document.getElementById('detect_header_rows').checked = false;
    document.getElementById('has-headers').checked = true;
    selectHeaders();

    const file = document.getElementById('file').files[0];
    if (!file) return;
    document.getElementById('graphType').selectedIndex = 0;
    toggleScale();

    const formData = new FormData();
    formData.append('file', file);
    formData.append('detect_columns', document.getElementById('detect_header_rows').checked ? 'true' : 'false');
    const checkedInt = document.querySelector('input[name="intensity-column"]:checked')?.value;
    const checkedNm = document.querySelector('input[name="wavelength-column"]:checked')?.value;
    let intCol = "";
    let nmCol = "";

    if (document.getElementById('detect_header_rows').checked === true) {
        intCol = checkedInt || "";
        nmCol = checkedNm || "";
    } else {
        intCol = "auto";
        nmCol = "auto";
    }

    formData.append('int_col', intCol);
    formData.append('nm_col', nmCol);
    formData.append('graph_type', document.getElementById('graphType').value);
    formData.append('show_grid', document.getElementById('show_grid').value);
    if (document.getElementById('reverse_x').checked) formData.append('reverse_x', 'on');
    if (document.getElementById('graphType').value === 'traditional') {
        formData.append('scale_mode', document.getElementById('scaleMode').value);
    }
    try {
        const response = await fetch('/api/nistCheck', { method: 'POST', body: formData });
        const data = await response.json();

        if (data.needs_manual_selection) {
            resultDiv.innerHTML = '<div class="error">Could not auto-detect column headers. Please manually select the wavelength and intensity columns below.</div>';
            document.getElementById('selector-section').hidden = false;
            document.getElementById('graphSelection').hidden = false;
            document.getElementById('detect_header_rows').checked = true;
            selectHeaders();

            var nistPlots = document.getElementById('nistPlots');
            var allPlots = document.getElementById('allPlots');
            var select = document.getElementById('graphType');
            if (nistPlots) select.removeChild(nistPlots);
            if (!allPlots) {
                allPlots = document.createElement('optgroup');
                allPlots.id = 'allPlots';
                allPlots.label = '';
                allPlots.innerHTML = '<option value="">--Choose Graph Type--</option>' +
                    '<option value="traditional">Traditional Plot</option>' +
                    '<option value="line">Line Plot</option>' +
                    '<option value="filled line">Filled Line Plot</option>' +
                    '<option value="non rgb line">Non-RGB Line Plot</option>' +
                    '<option value="bar">Bar Chart</option>' +
                    '<option value="scatter">Scatter Plot</option>' +
                    '<option value="gaussian">Gaussian Plot</option>';
                select.appendChild(allPlots);
            }

            // Load sheets
            const sheetResponse = await fetch('/api/sheets', { method: 'POST', body: formData });
            const sheetData = await sheetResponse.json();
            availableSheets = sheetData.sheets || [];
            sheetSelect.innerHTML = '<option value="">Auto-detect (no selection)</option>';
            availableSheets.forEach(sheet => {
                const option = document.createElement('option');
                option.value = sheet;
                option.textContent = sheet;
                sheetSelect.appendChild(option);
            });
            if (renderAllCheckbox) renderAllCheckbox.checked = false;
            return;
        }

        document.getElementById('graphSelection').hidden = true;

        if (data.is_nist) {
            document.getElementById('graphSelection').hidden = false;
            var nistPlots = document.getElementById('nistPlots');
            var allPlots = document.getElementById('allPlots');
            var select = document.getElementById('graphType');
            if (allPlots) select.removeChild(allPlots);
            if (!nistPlots) {
                nistPlots = document.createElement('optgroup');
                nistPlots.id = 'nistPlots';
                nistPlots.label = '';
                nistPlots.innerHTML = '<option value="">--Choose Graph Type--</option>' +
                    '<option value="traditional">Traditional Plot</option>' +
                    '<option value="gaussian">Gaussian Plot</option>';
                select.appendChild(nistPlots);
            }
            console.log("NIST rendering");
        } else {
            document.getElementById('graphSelection').hidden = false;
            var nistPlots = document.getElementById('nistPlots');
            var allPlots = document.getElementById('allPlots');
            var select = document.getElementById('graphType');
            if (nistPlots) select.removeChild(nistPlots);
            if (!allPlots) {
                allPlots = document.createElement('optgroup');
                allPlots.id = 'allPlots';
                allPlots.label = '';
                allPlots.innerHTML = '<option value="">--Choose Graph Type--</option>' +
                    '<option value="traditional">Traditional Plot</option>' +
                    '<option value="line">Line Plot</option>' +
                    '<option value="filled line">Filled Line Plot</option>' +
                    '<option value="non rgb line">Non-RGB Line Plot</option>' +
                    '<option value="bar">Bar Chart</option>' +
                    '<option value="scatter">Scatter Plot</option>' +
                    '<option value="gaussian">Gaussian Plot</option>';
                select.appendChild(allPlots);
            }
            console.log("generic rendering");
        }

        const sheetResponse = await fetch('/api/sheets', { method: 'POST', body: formData });
        const sheetData = await sheetResponse.json();

        availableSheets = sheetData.sheets || [];
        sheetSelect.innerHTML = '<option value="">Auto-detect (no selection)</option>';
        availableSheets.forEach(sheet => {
            const option = document.createElement('option');
            option.value = sheet;
            option.textContent = sheet;
            sheetSelect.appendChild(option);
        });

        if (renderAllCheckbox) renderAllCheckbox.checked = false;
    } catch (error) {
        resultDiv.innerHTML = `<div class="error">Error loading sheets: ${error.message}</div>`;
    }
});

// Form submission
renderForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const file = fileInput.files[0];
    if (!file) {
        resultDiv.innerHTML = '<div class="error">Please select a file</div>';
        return;
    }
    resultDiv.innerHTML = '<div class="loading"><div class="spinner"></div>Rendering...</div>';
    try {
        const title = document.getElementById('title').value;
        const randomTitle = document.getElementById('random_title').checked;
        let selectedSheets = [];
        if (renderAllCheckbox && renderAllCheckbox.checked) {
            selectedSheets = availableSheets.slice();
        } else {
            selectedSheets = Array.from(sheetSelect.selectedOptions).map(o => o.value).filter(v => v !== '');
        }
        if (!selectedSheets || selectedSheets.length === 0) {
            selectedSheets = [null];
        }

        let html = '';
        for (const sheetName of selectedSheets) {
            const labelSheet = sheetName || 'Auto-detected sheet';
            const formData = new FormData();
            formData.append('file', file);
            formData.append('detect_columns', document.getElementById('detect_header_rows').checked ? 'true' : 'false');

            const checkedInt = document.querySelector('input[name="intensity-column"]:checked')?.value;
            const checkedNm = document.querySelector('input[name="wavelength-column"]:checked')?.value;

            let intCol = "";
            let nmCol = "";

            if (document.getElementById('detect_header_rows').checked === true) {

                intCol = checkedInt || "";
                nmCol = checkedNm || "";
            } else {
                intCol = "auto";
                nmCol = "auto";
            }

            formData.append('int_col', intCol);
            formData.append('nm_col', nmCol);
            if (sheetName) formData.append('sheet', sheetName);
            formData.append('title', title);
            formData.append('graph_type', document.getElementById('graphType').value);  
            formData.append('scale_mode', document.getElementById('scaleMode').value);
            if (randomTitle) formData.append('random_title', 'on');
            if (document.getElementById('show_peak_labels').checked) formData.append('show_peak_labels', 'on');
            if (document.getElementById('reverse_x').checked) formData.append('reverse_x', 'on');
            if (document.getElementById('show_label_colour').checked) formData.append('show_label_colour', 'on');
            if (document.getElementById('show_grid').checked) formData.append('show_grid', 'on');       
            if (document.getElementById('scale_by_int').checked) formData.append('scale_by_int', 'on');       

            const response = await fetch('/api/render', { method: 'POST', body: formData });
            const contentType = response.headers.get('content-type');

            if (contentType && contentType.includes('application/json')) {
                const data = await response.json();

                if (data.needs_manual_selection) {
                    resultDiv.innerHTML = '<div class="error">Could not auto-detect column headers. Please manually select the wavelength and intensity columns below.</div>';
                    document.getElementById('selector-section').hidden = false;
                    document.getElementById('detect_header_rows').checked = true;
                    selectHeaders();
                    return;
                }
                
                if (data.error) {
                    throw new Error(data.error);
                }

                globalChartData = data;

                html += '<div class="image-container">' +
                        '<div class="image-label">' + labelSheet + '</div>' +
                        '<div id="mainPlotlyChart" style="width:100%;">' + '<button id="preview-button" type="button" title="Expand to Preview"><i class="fa fa-search-plus"></i></button>' + '</div>' + 
                        '</div>';

            } else {
                const blob = await response.blob();
                const url = URL.createObjectURL(blob);
                html += '<div class="image-container"><div class="image-label">' + labelSheet + ' </div><img src="' + url + '" alt="Spectrum"></div>';
            }
        }

        resultDiv.innerHTML = html;
        if (globalChartData && document.getElementById('mainPlotlyChart')) {
            // Unpack your backend configurations cleanly
            const chartData   = Array.isArray(globalChartData.data) ? globalChartData.data : [globalChartData.data];
            const chartLayout = Object.assign({}, globalChartData.layout);
            const chartConfig = Object.assign({}, globalChartData.config);
            Plotly.newPlot('mainPlotlyChart', chartData, chartLayout, chartConfig);
        }

        var gType = document.getElementById('graphType').value;
            if (gType === 'traditional') {
            modalChartContainer.style.maxHeight = '100%';
            previewModal.style.maxHeight = '100%';
        }
        else {
            modalChartContainer.style.maxHeight = '100vh';
            previewModal.style.maxHeight = '100vh';
        }

        const previewButton = document.getElementById('preview-button');
           if (gType === 'traditional') {
            previewButton.style.position = 'relative';
            previewButton.style.marginTop = '10px';
            previewButton.style.marginBottom = '-5px';
            previewButton.style.left = '98%';
        }
        else {
            previewButton.style.position = 'absolute';
            previewButton.style.right = '0.5%';
        }

    } catch (error) {
        resultDiv.innerHTML = `<div class="error">Error: ${error.message}</div>`;
    }
});

// Fullscreen preview modal logic

let hintTimeout;

function showExitHint() {
  const hint = document.querySelector('.preview-exit-hint');
  if (!hint) return;

  clearTimeout(hintTimeout);
  hint.classList.add('show');
  hintTimeout = setTimeout(() => {
    hint.classList.remove('show');
  }, 3000);
}

resultDiv.addEventListener('click', (ev) => {
    const t = ev.target;
    if (!t) return;

    const previewBtn = t.closest('#preview-button');
    if (previewBtn) {
        console.log('Preview button clicked successfully!'); // Debug log
        
        const chartExists = document.getElementById('mainPlotlyChart');
        if (chartExists) {
            openPlotlyPreview('spectrum.png');
        } else {
            console.error('Error: #mainPlotlyChart element not found in DOM.');
        }
        return; 
    }

    const imgElement = t.closest('img');
    if (imgElement) {
        openPreview(imgElement.src, imgElement.alt || 'spectrum.png');
        return;
    }
});

function openPlotlyPreview(filename) {
    if (!globalChartData) return;
    const template = document.getElementById('exit-preview-hint-template');
    if (template && !document.querySelector('.preview-exit-hint')) {
      const clone = template.content.cloneNode(true);
      document.body.appendChild(clone);
    }

    previewModal.classList.add('open');
    previewModal.style.display = 'flex'; 
    previewModal.setAttribute('aria-hidden', 'false');
    modalChartContainer.style.display = 'block';

    showExitHint();

    const chartData = Array.isArray(globalChartData.data) ? globalChartData.data : [globalChartData.data];
    const chartLayout = Object.assign({}, globalChartData.layout);
    const chartConfig = globalChartData.config || {};
    chartLayout.width = null;
    chartLayout.height = null;
    chartLayout.autosize = true;

    Plotly.newPlot('modalPlotlyChart', chartData, chartLayout, chartConfig);
    Plotly.Plots.resize('modalPlotlyChart');
}

function closePreview() {
    previewModal.classList.remove('open');
    previewModal.style.display = 'none';
    previewModal.setAttribute('aria-hidden', 'true');
    Plotly.purge('modalPlotlyChart');

    const hint = document.querySelector('.preview-exit-hint');
    if (hint) {
      clearTimeout(hintTimeout);
      hint.remove();
    }
}

document.addEventListener('mousemove', (ev) => {
    if (previewModal && previewModal.classList.contains('open')) {
      const windowCenterX = window.innerWidth / 2;
      const horizontalSensitivity = 200; 
      const verticalSensitivity = 60;
      const isNearTopEdge = ev.clientY <= verticalSensitivity;
      const isCenteredHorizontally = Math.abs(ev.clientX - windowCenterX) <= horizontalSensitivity;
      if (isNearTopEdge && isCenteredHorizontally) {
        showExitHint();
      }
    }
  });

modalBackdrop.addEventListener('click', closePreview);
document.addEventListener('keydown', (ev) => {
    if (ev.key === 'Escape' && previewModal.classList.contains('open')) {
        closePreview();
    }
});

document.addEventListener('DOMContentLoaded', () => {
    const template = document.getElementById('modebar-toggle-template');
    const observer = new MutationObserver(() => {
      const charts = document.querySelectorAll('.js-plotly-plot:not(.has-toggle-btn)');
      charts.forEach(chart => {
        if (!chart.layout || !template) return;
        chart.classList.add('has-toggle-btn');
        const layoutStyle = (chart.layout && chart.layout.meta && chart.layout.meta.modebar_style) || 'shifted';
        const modebar = chart.querySelector('.modebar');
        if (layoutStyle === 'vertical') {
          chart.classList.add('style-vertical-modebar');
        }
        const templateContent = template.content.cloneNode(true);
        const toggleBtn = templateContent.querySelector('.modebar-toggle');
        toggleBtn.addEventListener('click', (e) => {
          e.stopPropagation();
          chart.classList.toggle('modebar-expanded');
          const isOpen = chart.classList.contains('modebar-expanded');
        });
        chart.style.position = 'relative';
        chart.appendChild(toggleBtn);
      });
    });
    observer.observe(document.body, { childList: true, subtree: true });
  });




const dataPreviewButton = document.getElementById('data-preview-button');
dataPreviewButton.addEventListener('click', function() {
    if (this.textContent === '▲') {
        this.textContent = '▼';
    } else {
        this.textContent = '▲'
    }
});