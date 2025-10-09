let currentView = 'overview';
let tasks = [];
let stats = {};

document.addEventListener('DOMContentLoaded', function() {
    console.log('Dashboard loaded');
    initializeNavigation();
    loadDashboardData();
    setInterval(loadDashboardData, 30000);
});

function initializeNavigation() {
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
            this.classList.add('active');
            switchView(this.dataset.view);
        });
    });
    
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            renderTasks();
        });
    });
}

function switchView(view) {
    currentView = view;
    document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
    document.getElementById('view-' + view).classList.add('active');
    
    const titles = {
        'overview': 'Dashboard Overview',
        'tasks': 'Research Queue',
        'documents': 'Documents',
        'search': 'Search'
    };
    document.getElementById('page-title').textContent = titles[view];
    
    if (view === 'tasks') {
        loadTasks();
    } else if (view === 'documents') {
        loadDocuments();
    }
}

async function loadDashboardData() {
    try {
        const statsResponse = await fetch('/api/stats');
        stats = await statsResponse.json();
        renderStats();
        
        const recentResponse = await fetch('/api/recent?limit=10');
        const recentData = await recentResponse.json();
        renderRecentDocuments(recentData.documents);
        
        await loadTasks();
    } catch (error) {
        console.error('Error loading data:', error);
    }
}

function renderStats() {
    const statTotal = document.getElementById('stat-total');
    const statSize = document.getElementById('stat-size');
    const statCompleted = document.getElementById('stat-completed');
    const statPending = document.getElementById('stat-pending');
    const pendingCount = document.getElementById('pending-count');
    
    if (statTotal) statTotal.textContent = stats.total_documents || 0;
    if (statSize) statSize.textContent = (stats.total_size_kb || 0) + ' KB';
    
    const completed = tasks.filter(t => t.status === 'completed').length;
    const pending = tasks.filter(t => t.status === 'pending').length;
    
    if (statCompleted) statCompleted.textContent = completed;
    if (statPending) statPending.textContent = pending;
    if (pendingCount) pendingCount.textContent = pending;
    
    renderCategories();
}

function renderCategories() {
    const container = document.getElementById('categories');
    if (!container) return;
    
    if (!stats.categories) {
        container.innerHTML = '<p style="color: var(--text-secondary);">No categories yet</p>';
        return;
    }
    
    let html = '';
    for (const name in stats.categories) {
        const data = stats.categories[name];
        const percentage = stats.total_documents > 0 ? (data.count / stats.total_documents * 100).toFixed(1) : 0;
        
        html += `<div class="category-item">
                <div class="category-info">
                <strong>${name}</strong>
                <span class="category-count">${data.count} docs</span>
                </div>
                <div class="progress-bar">
                <div class="progress-fill" style="width: ${percentage}%"></div>
                </div>
                </div>`;
    }
    container.innerHTML = html;
}

function renderRecentDocuments(documents) {
    const container = document.getElementById('recent-documents');
    if (!container) return;
    
    if (!documents || documents.length === 0) {
        container.innerHTML = '<p style="color: var(--text-secondary); padding: 1rem;">No documents yet</p>';
        return;
    }
    
    const errorDocs = documents.filter(doc => doc.name.toLowerCase().includes('error'));
    let html = '';
    if (errorDocs.length > 0) {
        html = `<button class="btn btn-danger btn-sm" onclick="cleanupErrors()" style="margin-bottom: 1rem;">
                <i class="fas fa-trash"></i> Cleanup ${errorDocs.length} Error Document(s)
                </button>`;
    }
    
    documents.forEach(doc => {
        const date = new Date(doc.modified * 1000).toLocaleDateString();
        const size = (doc.size / 1024).toFixed(1);
        const isError = doc.name.toLowerCase().includes('error');
        
        html += `<div class="document-item${isError ? ' error-document' : ''}">
                <div class="document-icon${isError ? ' error' : ''}">
                <i class="fas fa-${isError ? 'exclamation-triangle' : 'file-alt'}"></i>
                </div>
                <div class="document-info" onclick="viewDocument('${doc.relative_path}')" style="flex: 1; cursor: pointer;">
                <div class="document-name">${doc.name}</div>
                <div class="document-meta">${date} • ${size} KB</div>
                </div>
                </div>`;
    });
    container.innerHTML = html;
}

async function cleanupErrors() {
    if (!confirm('Delete ALL error documents?')) return;
    
    try {
        const response = await fetch('/api/recent?limit=200');
        const data = await response.json();
        const errorDocs = data.documents.filter(doc => doc.name.toLowerCase().includes('error'));
        
        if (errorDocs.length === 0) {
            alert('No error documents found');
            return;
        }
        
        const paths = errorDocs.map(doc => doc.relative_path);
        const deleteResponse = await fetch('/api/documents/bulk-delete', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ paths: paths })
        });
        
        const result = await deleteResponse.json();
        if (deleteResponse.ok) {
            alert(result.message);
            await loadDashboardData();
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

async function loadTasks() {
    try {
        const response = await fetch('/api/tasks');
        const data = await response.json();
        tasks = data.tasks;
        renderTasks();
    } catch (error) {
        console.error('Error loading tasks:', error);
    }
}

function renderTasks() {
    const container = document.getElementById('tasks-container');
    if (!container) return;
    
    if (tasks.length === 0) {
        container.innerHTML = `<div class="empty-state">
                              <i class="fas fa-inbox"></i>
                              <p>No tasks yet. Click "New Task" to create one!</p>
                              </div>`;
        return;
    }
    
    let html = '';
    tasks.forEach(task => {
        const date = new Date(task.created_at).toLocaleString();
        html += `<div class="task-item">
                <div class="task-header">
                <div>
                <div class="task-title">${task.topic}</div>
                <div class="task-meta">${date}</div>
                </div>
                <span class="status-badge status-${task.status}">${task.status}</span>
                </div>
                ${task.context ? `<p class="task-context">${task.context}</p>` : ''}
                <div class="task-actions">
                ${task.status === 'pending' ? `
                <button class="btn btn-success btn-sm" onclick="approveTask(${task.id})">Approve</button>
                <button class="btn btn-danger btn-sm" onclick="denyTask(${task.id})">Deny</button>
                ` : ''}
                ${task.status !== 'processing' ? `
                <button class="btn btn-secondary btn-sm" onclick="deleteTask(${task.id})">Delete</button>
                ` : ''}
                </div>
                </div>`;
    });
    container.innerHTML = html;
}

async function approveTask(taskId) {
    const response = await fetch(`/api/tasks/${taskId}/approve`, { method: 'POST' });
    if (response.ok) await loadTasks();
}

async function denyTask(taskId) {
    const response = await fetch(`/api/tasks/${taskId}/deny`, { method: 'POST' });
    if (response.ok) await loadTasks();
}

async function deleteTask(taskId) {
    if (!confirm('Delete this task?')) return;
    const response = await fetch(`/api/tasks/${taskId}`, { method: 'DELETE' });
    if (response.ok) await loadTasks();
}

function showNewTaskModal() {
    document.getElementById('new-task-modal').classList.add('active');
}

function closeModal() {
    document.getElementById('new-task-modal').classList.remove('active');
}

async function createTask() {
    const topic = document.getElementById('task-topic').value;
    if (!topic) return alert('Please enter a topic');
    
    const response = await fetch('/api/tasks', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            topic: topic,
            context: document.getElementById('task-context').value,
            source_type: document.getElementById('task-source-type').value,
            source_url: document.getElementById('task-source-url').value
        })
    });
    
    if (response.ok) {
        closeModal();
        document.getElementById('task-topic').value = '';
        document.getElementById('task-context').value = '';
        document.getElementById('task-source-url').value = '';
        await loadTasks();
        await loadDashboardData();
    }
}

async function viewDocument(path) {
    const response = await fetch('/api/document/' + encodeURIComponent(path));
    const data = await response.json();
    document.getElementById('doc-title').textContent = path.split('/').pop();
    document.getElementById('doc-content').innerHTML = data.html;
    document.getElementById('document-modal').classList.add('active');
}

function closeDocumentModal() {
    document.getElementById('document-modal').classList.remove('active');
}

async function loadDocuments() {
    const container = document.getElementById('documents-container');
    if (!container) return;
    
    const category = document.getElementById('category-filter')?.value || '';
    const limit = parseInt(document.getElementById('limit-input')?.value) || 50;
    
    const url = '/api/recent?' + (category ? 'category=' + category + '&' : '') + 'limit=' + limit;
    const response = await fetch(url);
    const data = await response.json();
    
    if (!data.documents || data.documents.length === 0) {
        container.innerHTML = '<div class="empty-documents"><i class="fas fa-folder-open"></i><p>No documents found</p></div>';
        return;
    }
    
    let html = '';
    data.documents.forEach(doc => {
        const date = new Date(doc.modified * 1000).toLocaleDateString();
        const size = (doc.size / 1024).toFixed(1);
        const category = doc.relative_path.split('/')[0];
        
        html += `<div class="document-card" onclick="viewDocument('${doc.relative_path}')">
                <div class="document-card-header">
                <div class="document-card-icon"><i class="fas fa-file-alt"></i></div>
                </div>
                <div class="document-card-title">${doc.name}</div>
                <div class="document-card-meta">
                <span><i class="fas fa-calendar"></i> ${date}</span>
                <span><i class="fas fa-database"></i> ${size} KB</span>
                </div>
                <span class="document-card-category">${category}</span>
                </div>`;
    });
    container.innerHTML = html;
}

function refreshData() {
    loadDashboardData();
}
