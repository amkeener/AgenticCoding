import './style.css'
import { api } from './api/client'

// Global state
let currentResults: QueryResponse | null = null;
let availableTables: TableSchema[] = [];
let isHistoryPanelOpen = false;

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
  initializeQueryInput();
  initializeFileUpload();
  initializeModal();
  initializeQueryHistoryPanel();
  loadDatabaseSchema();
});

// Query Input Functionality
function initializeQueryInput() {
  const queryInput = document.getElementById('query-input') as HTMLTextAreaElement;
  const queryButton = document.getElementById('query-button') as HTMLButtonElement;
  const providerSelect = document.getElementById('llm-provider-select') as HTMLSelectElement;
  
  queryButton.addEventListener('click', async () => {
    const query = queryInput.value.trim();
    if (!query) return;
    
    // Get selected LLM provider
    const selectedProvider = providerSelect.value as "openai" | "anthropic" | "ollama" | "cursor-agent" | "claude";
    
    queryButton.disabled = true;
    queryButton.innerHTML = '<span class="loading"></span>';
    providerSelect.disabled = true;
    
    try {
      const response = await api.processQuery({
        query,
        llm_provider: selectedProvider
      });
      
      displayResults(response, query);
      
      // Clear the input field on success
      queryInput.value = '';
    } catch (error) {
      displayError(error instanceof Error ? error.message : 'Query failed');
    } finally {
      queryButton.disabled = false;
      queryButton.textContent = 'Query';
      providerSelect.disabled = false;
    }
  });
  
  // Allow Cmd+Enter (Mac) or Ctrl+Enter (Windows/Linux) to submit
  queryInput.addEventListener('keydown', (e) => {
    if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') {
      queryButton.click();
    }
  });
}

// File Upload Functionality
function initializeFileUpload() {
  const dropZone = document.getElementById('drop-zone') as HTMLDivElement;
  const fileInput = document.getElementById('file-input') as HTMLInputElement;
  const browseButton = document.getElementById('browse-button') as HTMLButtonElement;
  
  // Browse button click
  browseButton.addEventListener('click', () => fileInput.click());
  
  // File input change
  fileInput.addEventListener('change', (e) => {
    const files = (e.target as HTMLInputElement).files;
    if (files && files.length > 0) {
      handleFileUpload(files[0]);
    }
  });
  
  // Drag and drop
  dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('dragover');
  });
  
  dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('dragover');
  });
  
  dropZone.addEventListener('drop', async (e) => {
    e.preventDefault();
    dropZone.classList.remove('dragover');
    
    const files = e.dataTransfer?.files;
    if (files && files.length > 0) {
      handleFileUpload(files[0]);
    }
  });
}

// Handle file upload
async function handleFileUpload(file: File) {
  try {
    const response = await api.uploadFile(file);
    
    if (response.error) {
      displayError(response.error);
    } else {
      displayUploadSuccess(response);
      await loadDatabaseSchema();
    }
  } catch (error) {
    displayError(error instanceof Error ? error.message : 'Upload failed');
  }
}

// Load database schema
async function loadDatabaseSchema() {
  try {
    const response = await api.getSchema();
    if (!response.error) {
      availableTables = response.tables;
      displayTables(response.tables);
    }
  } catch (error) {
    console.error('Failed to load schema:', error);
  }
}

// Display query results
function displayResults(response: QueryResponse, query: string) {
  currentResults = response;
  
  const resultsSection = document.getElementById('results-section') as HTMLElement;
  const sqlDisplay = document.getElementById('sql-display') as HTMLDivElement;
  const resultsContainer = document.getElementById('results-container') as HTMLDivElement;
  
  resultsSection.style.display = 'block';
  
  // Display natural language query and SQL
  sqlDisplay.innerHTML = `
    <div class="query-display">
      <strong>Query:</strong> ${query}
    </div>
    <div class="sql-query">
      <strong>SQL:</strong> <code>${response.sql}</code>
    </div>
  `;
  
  // Display results table
  if (response.error) {
    resultsContainer.innerHTML = `<div class="error-message">${response.error}</div>`;
  } else if (response.results.length === 0) {
    resultsContainer.innerHTML = '<p>No results found.</p>';
  } else {
    const table = createResultsTable(response.results, response.columns);
    resultsContainer.innerHTML = '';
    resultsContainer.appendChild(table);
  }
  
  // Initialize toggle button
  const toggleButton = document.getElementById('toggle-results') as HTMLButtonElement;
  toggleButton.addEventListener('click', () => {
    resultsContainer.style.display = resultsContainer.style.display === 'none' ? 'block' : 'none';
    toggleButton.textContent = resultsContainer.style.display === 'none' ? 'Show' : 'Hide';
  });
  
  // Refresh history panel if open
  if (isHistoryPanelOpen && !response.error) {
    loadQueryHistory();
  }
}

// Create results table
function createResultsTable(results: Record<string, any>[], columns: string[]): HTMLTableElement {
  const table = document.createElement('table');
  table.className = 'results-table';
  
  // Header
  const thead = document.createElement('thead');
  const headerRow = document.createElement('tr');
  columns.forEach(col => {
    const th = document.createElement('th');
    th.textContent = col;
    headerRow.appendChild(th);
  });
  thead.appendChild(headerRow);
  table.appendChild(thead);
  
  // Body
  const tbody = document.createElement('tbody');
  results.forEach(row => {
    const tr = document.createElement('tr');
    columns.forEach(col => {
      const td = document.createElement('td');
      td.textContent = row[col] !== null ? String(row[col]) : '';
      tr.appendChild(td);
    });
    tbody.appendChild(tr);
  });
  table.appendChild(tbody);
  
  return table;
}

// Display tables
function displayTables(tables: TableSchema[]) {
  const tablesList = document.getElementById('tables-list') as HTMLDivElement;
  
  if (tables.length === 0) {
    tablesList.innerHTML = '<p class="no-tables">No tables loaded. Upload data or use sample data to get started.</p>';
    return;
  }
  
  tablesList.innerHTML = '';
  
  tables.forEach(table => {
    const tableItem = document.createElement('div');
    tableItem.className = 'table-item';
    
    // Header section
    const tableHeader = document.createElement('div');
    tableHeader.className = 'table-header';
    
    const tableLeft = document.createElement('div');
    tableLeft.style.display = 'flex';
    tableLeft.style.alignItems = 'center';
    tableLeft.style.gap = '1rem';
    
    const tableName = document.createElement('div');
    tableName.className = 'table-name';
    tableName.textContent = table.name;
    
    const tableInfo = document.createElement('div');
    tableInfo.className = 'table-info';
    tableInfo.textContent = `${table.row_count} rows, ${table.columns.length} columns`;
    
    tableLeft.appendChild(tableName);
    tableLeft.appendChild(tableInfo);
    
    const removeButton = document.createElement('button');
    removeButton.className = 'remove-table-button';
    removeButton.innerHTML = '&times;';
    removeButton.title = 'Remove table';
    removeButton.onclick = () => removeTable(table.name);
    
    tableHeader.appendChild(tableLeft);
    tableHeader.appendChild(removeButton);
    
    // Columns section
    const tableColumns = document.createElement('div');
    tableColumns.className = 'table-columns';
    
    table.columns.forEach(column => {
      const columnTag = document.createElement('span');
      columnTag.className = 'column-tag';
      
      const columnName = document.createElement('span');
      columnName.className = 'column-name';
      columnName.textContent = column.name;
      
      const columnType = document.createElement('span');
      columnType.className = 'column-type';
      const typeEmoji = getTypeEmoji(column.type);
      columnType.textContent = `${typeEmoji} ${column.type}`;
      
      columnTag.appendChild(columnName);
      columnTag.appendChild(columnType);
      tableColumns.appendChild(columnTag);
    });
    
    tableItem.appendChild(tableHeader);
    tableItem.appendChild(tableColumns);
    tablesList.appendChild(tableItem);
  });
}

// Display upload success
function displayUploadSuccess(response: FileUploadResponse) {
  // Close modal
  const modal = document.getElementById('upload-modal') as HTMLElement;
  modal.style.display = 'none';
  
  // Show success message
  const successDiv = document.createElement('div');
  successDiv.className = 'success-message';
  successDiv.textContent = `Table "${response.table_name}" created successfully with ${response.row_count} rows!`;
  successDiv.style.cssText = `
    background: rgba(40, 167, 69, 0.1);
    border: 1px solid var(--success-color);
    color: var(--success-color);
    padding: 1rem;
    border-radius: 8px;
    margin-bottom: 1rem;
  `;
  
  const tablesSection = document.getElementById('tables-section') as HTMLElement;
  tablesSection.insertBefore(successDiv, tablesSection.firstChild);
  
  // Remove success message after 3 seconds
  setTimeout(() => {
    successDiv.remove();
  }, 3000);
}

// Display error
function displayError(message: string) {
  const errorDiv = document.createElement('div');
  errorDiv.className = 'error-message';
  errorDiv.textContent = message;
  
  const resultsContainer = document.getElementById('results-container') as HTMLDivElement;
  resultsContainer.innerHTML = '';
  resultsContainer.appendChild(errorDiv);
  
  const resultsSection = document.getElementById('results-section') as HTMLElement;
  resultsSection.style.display = 'block';
}

// Initialize modal
function initializeModal() {
  const uploadButton = document.getElementById('upload-data-button') as HTMLButtonElement;
  const modal = document.getElementById('upload-modal') as HTMLElement;
  const closeButton = modal.querySelector('.close-modal') as HTMLButtonElement;
  
  // Open modal
  uploadButton.addEventListener('click', () => {
    modal.style.display = 'flex';
  });
  
  // Close modal
  closeButton.addEventListener('click', () => {
    modal.style.display = 'none';
  });
  
  // Close on background click
  modal.addEventListener('click', (e) => {
    if (e.target === modal) {
      modal.style.display = 'none';
    }
  });
  
  // Initialize sample data buttons
  const sampleButtons = modal.querySelectorAll('.sample-button');
  sampleButtons.forEach(button => {
    button.addEventListener('click', async (e) => {
      const sampleType = (e.currentTarget as HTMLElement).dataset.sample;
      await loadSampleData(sampleType!);
    });
  });
}

// Remove table
async function removeTable(tableName: string) {
  if (!confirm(`Are you sure you want to remove the table "${tableName}"?`)) {
    return;
  }
  
  try {
    const response = await fetch(`/api/table/${tableName}`, {
      method: 'DELETE'
    });
    
    if (!response.ok) {
      throw new Error('Failed to remove table');
    }
    
    // Reload schema
    await loadDatabaseSchema();
    
    // Show success message
    const successDiv = document.createElement('div');
    successDiv.className = 'success-message';
    successDiv.textContent = `Table "${tableName}" removed successfully!`;
    successDiv.style.cssText = `
      background: rgba(40, 167, 69, 0.1);
      border: 1px solid var(--success-color);
      color: var(--success-color);
      padding: 1rem;
      border-radius: 8px;
      margin-bottom: 1rem;
    `;
    
    const tablesSection = document.getElementById('tables-section') as HTMLElement;
    tablesSection.insertBefore(successDiv, tablesSection.firstChild);
    
    setTimeout(() => {
      successDiv.remove();
    }, 3000);
  } catch (error) {
    displayError(error instanceof Error ? error.message : 'Failed to remove table');
  }
}

// Get emoji for data type
function getTypeEmoji(type: string): string {
  const upperType = type.toUpperCase();
  
  // SQLite types
  if (upperType.includes('INT')) return '🔢';
  if (upperType.includes('REAL') || upperType.includes('FLOAT') || upperType.includes('DOUBLE')) return '💯';
  if (upperType.includes('TEXT') || upperType.includes('CHAR') || upperType.includes('STRING')) return '📝';
  if (upperType.includes('DATE') || upperType.includes('TIME')) return '📅';
  if (upperType.includes('BOOL')) return '✓';
  if (upperType.includes('BLOB')) return '📦';
  
  // Default
  return '📊';
}

// Load sample data
async function loadSampleData(sampleType: string) {
  try {
    const filename = sampleType === 'users' ? 'users.json' : 'products.csv';
    const response = await fetch(`/sample-data/${filename}`);
    
    if (!response.ok) {
      throw new Error('Failed to load sample data');
    }
    
    const blob = await response.blob();
    const file = new File([blob], filename, { type: blob.type });
    
    // Upload the file
    await handleFileUpload(file);
  } catch (error) {
    displayError(error instanceof Error ? error.message : 'Failed to load sample data');
  }
}

// Initialize query history panel
function initializeQueryHistoryPanel() {
  const showButton = document.getElementById('show-history-button') as HTMLButtonElement;
  const panel = document.getElementById('query-history-panel') as HTMLElement;
  const closeButton = document.getElementById('close-history-panel') as HTMLButtonElement;
  
  showButton.addEventListener('click', () => {
    isHistoryPanelOpen = !isHistoryPanelOpen;
    if (isHistoryPanelOpen) {
      panel.classList.add('open');
      showButton.textContent = 'Hide Panel';
      loadQueryHistory();
    } else {
      panel.classList.remove('open');
      showButton.textContent = 'Show Panel';
    }
  });
  
  closeButton.addEventListener('click', () => {
    isHistoryPanelOpen = false;
    panel.classList.remove('open');
    showButton.textContent = 'Show Panel';
  });
}

// Load query history
async function loadQueryHistory() {
  const historyList = document.getElementById('query-history-list') as HTMLDivElement;
  
  try {
    const response = await api.getQueryHistory();
    
    if (response.error) {
      historyList.innerHTML = `<p class="no-queries">Error loading history: ${response.error}</p>`;
      return;
    }
    
    if (response.queries.length === 0) {
      historyList.innerHTML = '<p class="no-queries">No queries yet. Execute a query to see it here.</p>';
      return;
    }
    
    historyList.innerHTML = '';
    response.queries.forEach(item => {
      const itemElement = displayQueryHistoryItem(item);
      historyList.appendChild(itemElement);
    });
  } catch (error) {
    historyList.innerHTML = `<p class="no-queries">Error loading history: ${error instanceof Error ? error.message : 'Unknown error'}</p>`;
  }
}

// Display a query history item
function displayQueryHistoryItem(item: QueryHistoryItem): HTMLDivElement {
  const itemDiv = document.createElement('div');
  itemDiv.className = 'query-history-item';
  
  const nameDiv = document.createElement('div');
  nameDiv.className = 'query-history-item-name';
  nameDiv.textContent = item.display_name;
  
  const metaDiv = document.createElement('div');
  metaDiv.className = 'query-history-item-meta';
  
  const timeDiv = document.createElement('div');
  timeDiv.className = 'query-history-item-time';
  const date = new Date(item.created_at);
  timeDiv.textContent = date.toLocaleString();
  
  const rowsDiv = document.createElement('div');
  rowsDiv.className = 'query-history-item-rows';
  rowsDiv.textContent = `${item.row_count} rows`;
  
  metaDiv.appendChild(timeDiv);
  metaDiv.appendChild(rowsDiv);
  
  itemDiv.appendChild(nameDiv);
  itemDiv.appendChild(metaDiv);
  
  itemDiv.addEventListener('click', () => {
    refocusQuery(item.id);
  });
  
  return itemDiv;
}

// Refocus on a query from history
async function refocusQuery(queryId: number) {
  try {
    const queryDetail = await api.getQueryHistoryById(queryId);
    
    if (queryDetail.error) {
      displayError(queryDetail.error);
      return;
    }
    
    // Set query input
    const queryInput = document.getElementById('query-input') as HTMLTextAreaElement;
    queryInput.value = queryDetail.query_text;
    
    // Create QueryResponse from history
    const response: QueryResponse = {
      sql: queryDetail.sql,
      results: queryDetail.results,
      columns: queryDetail.columns,
      row_count: queryDetail.row_count,
      execution_time_ms: queryDetail.execution_time_ms
    };
    
    // Display results
    displayResults(response, queryDetail.query_text);
    
    // Scroll to results section
    const resultsSection = document.getElementById('results-section') as HTMLElement;
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    
    // Optionally close panel (or keep it open)
    // Uncomment to close panel after refocusing:
    // const panel = document.getElementById('query-history-panel') as HTMLElement;
    // const showButton = document.getElementById('show-history-button') as HTMLButtonElement;
    // isHistoryPanelOpen = false;
    // panel.classList.remove('open');
    // showButton.textContent = 'Show Panel';
  } catch (error) {
    displayError(error instanceof Error ? error.message : 'Failed to load query');
  }
}
