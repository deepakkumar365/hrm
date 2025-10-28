/**
 * Export Functionality for HRMS Application
 * Supports CSV, Excel, and PDF export formats
 */

// Export to CSV
function exportToCSV(tableId, filename = 'export.csv') {
    const table = document.getElementById(tableId);
    if (!table) {
        console.error('Table not found:', tableId);
        return;
    }

    let csv = [];
    const rows = table.querySelectorAll('tr');

    for (let i = 0; i < rows.length; i++) {
        const row = [];
        const cols = rows[i].querySelectorAll('td, th');

        for (let j = 0; j < cols.length; j++) {
            // Skip action columns
            if (cols[j].classList.contains('actions-column') || 
                cols[j].textContent.trim() === 'Actions') {
                continue;
            }
            
            // Get text content and clean it
            let data = cols[j].textContent.trim();
            // Escape quotes and wrap in quotes if contains comma
            data = data.replace(/"/g, '""');
            if (data.includes(',') || data.includes('\n')) {
                data = '"' + data + '"';
            }
            row.push(data);
        }
        csv.push(row.join(','));
    }

    // Download CSV file
    downloadFile(csv.join('\n'), filename, 'text/csv');
}

// Export to Excel (using HTML table format)
function exportToExcel(tableId, filename = 'export.xlsx') {
    const table = document.getElementById(tableId);
    if (!table) {
        console.error('Table not found:', tableId);
        return;
    }

    // Clone table and remove action columns
    const clonedTable = table.cloneNode(true);
    const actionCells = clonedTable.querySelectorAll('.actions-column, th:last-child, td:last-child');
    
    // Check if last column is Actions
    const headers = clonedTable.querySelectorAll('th');
    const lastHeader = headers[headers.length - 1];
    if (lastHeader && lastHeader.textContent.trim() === 'Actions') {
        // Remove all action columns
        clonedTable.querySelectorAll('tr').forEach(row => {
            const cells = row.querySelectorAll('th, td');
            if (cells.length > 0) {
                cells[cells.length - 1].remove();
            }
        });
    }

    // Create Excel file content
    const html = clonedTable.outerHTML;
    const blob = new Blob([html], {
        type: 'application/vnd.ms-excel'
    });

    // Download file
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
}

// Export to PDF (using browser print)
function exportToPDF(tableId, filename = 'export.pdf') {
    const table = document.getElementById(tableId);
    if (!table) {
        console.error('Table not found:', tableId);
        return;
    }

    // Create a new window with the table
    const printWindow = window.open('', '', 'height=600,width=800');
    
    // Clone table and remove action columns
    const clonedTable = table.cloneNode(true);
    const headers = clonedTable.querySelectorAll('th');
    const lastHeader = headers[headers.length - 1];
    
    if (lastHeader && lastHeader.textContent.trim() === 'Actions') {
        clonedTable.querySelectorAll('tr').forEach(row => {
            const cells = row.querySelectorAll('th, td');
            if (cells.length > 0) {
                cells[cells.length - 1].remove();
            }
        });
    }

    printWindow.document.write('<html><head><title>' + filename + '</title>');
    printWindow.document.write('<style>');
    printWindow.document.write('body { font-family: Arial, sans-serif; margin: 20px; }');
    printWindow.document.write('table { width: 100%; border-collapse: collapse; }');
    printWindow.document.write('th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }');
    printWindow.document.write('th { background-color: #6C8F91; color: white; }');
    printWindow.document.write('tr:nth-child(even) { background-color: #f2f2f2; }');
    printWindow.document.write('@media print { body { margin: 0; } }');
    printWindow.document.write('</style>');
    printWindow.document.write('</head><body>');
    printWindow.document.write('<h2>' + filename.replace('.pdf', '') + '</h2>');
    printWindow.document.write(clonedTable.outerHTML);
    printWindow.document.write('</body></html>');
    printWindow.document.close();

    // Wait for content to load then print
    printWindow.onload = function() {
        printWindow.print();
        printWindow.close();
    };
}

// Helper function to download file
function downloadFile(content, filename, mimeType) {
    const blob = new Blob([content], { type: mimeType });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
}

// Toggle export dropdown
function toggleExportDropdown(event) {
    event.stopPropagation();
    const dropdown = event.target.closest('.export-dropdown');
    dropdown.classList.toggle('active');
}

// Close dropdown when clicking outside
document.addEventListener('click', function(event) {
    const dropdowns = document.querySelectorAll('.export-dropdown');
    dropdowns.forEach(dropdown => {
        if (!dropdown.contains(event.target)) {
            dropdown.classList.remove('active');
        }
    });
});

// Export current page data (for paginated tables)
function exportCurrentPage(format, tableId, filename) {
    const baseFilename = filename || 'export';
    const fullFilename = `${baseFilename}_${new Date().toISOString().split('T')[0]}`;
    
    switch(format.toLowerCase()) {
        case 'csv':
            exportToCSV(tableId, fullFilename + '.csv');
            break;
        case 'excel':
            exportToExcel(tableId, fullFilename + '.xlsx');
            break;
        case 'pdf':
            exportToPDF(tableId, fullFilename + '.pdf');
            break;
        default:
            console.error('Unknown export format:', format);
    }
}