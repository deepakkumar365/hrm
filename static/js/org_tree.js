document.addEventListener('DOMContentLoaded', function () {
    const container = document.getElementById('orgTreeContainer');
    const companySelect = document.getElementById('companySelect');
    let draggedNodeId = null;
    let draggedNodeName = null;

    if (companySelect) {
        loadTree(companySelect.value);
        companySelect.addEventListener('change', function () {
            loadTree(this.value);
        });
    }

    function loadTree(companyId) {
        container.innerHTML = '<div class="text-center py-5"><div class="spinner-border text-primary"></div></div>';

        fetch(`/org-structure/api/tree/${companyId}`)
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    container.innerHTML = `<div class="alert alert-danger">${data.error}</div>`;
                    return;
                }
                if (data.length === 0) {
                    container.innerHTML = '<div class="alert alert-info">No employees found for this company.</div>';
                    return;
                }

                renderTree(data);
            })
            .catch(err => {
                console.error(err);
                container.innerHTML = '<div class="alert alert-danger">Failed to load organization tree.</div>';
            });
    }

    function renderTree(data) {
        const treeRoot = document.createElement('div');
        treeRoot.className = 'org-tree';

        const ul = document.createElement('ul');
        data.forEach(node => {
            ul.appendChild(createNodeElement(node));
        });

        treeRoot.appendChild(ul);
        container.innerHTML = '';
        container.appendChild(treeRoot);
    }

    function createNodeElement(node) {
        const li = document.createElement('li');

        // Node Card
        const card = document.createElement('div');
        card.className = 'org-node';
        if (node.children && node.children.length > 0) {
            card.classList.add('has-children');
        }
        card.setAttribute('draggable', 'true');
        card.dataset.id = node.id;
        card.dataset.name = node.name;

        // Content
        const imgPath = node.image ? `/static/${node.image}` : '/static/img/default_avatar.png'; // Make sure default exists or handle error
        // Fallback for image
        let imgHtml = `<img src="${imgPath}" class="org-node-img" onerror="this.src='https://ui-avatars.com/api/?name=${encodeURIComponent(node.name)}&background=random'">`;

        card.innerHTML = `
            ${imgHtml}
            <span class="org-node-name">${node.name}</span>
            <span class="org-node-title">${node.title}</span>
        `;

        // Expand/Collapse Toggle
        if (node.children && node.children.length > 0) {
            const toggle = document.createElement('span');
            toggle.className = 'toggle-btn fas fa-minus';
            toggle.onclick = function (e) {
                e.preventDefault();
                e.stopPropagation(); // Prevent drag start
                const parentLi = this.closest('li');
                parentLi.classList.toggle('collapsed');
                this.classList.toggle('fa-minus');
                this.classList.toggle('fa-plus');
            };
            card.appendChild(toggle);
        }

        // Drag Events
        card.addEventListener('dragstart', handleDragStart);
        card.addEventListener('dragover', handleDragOver);
        card.addEventListener('dragleave', handleDragLeave);
        card.addEventListener('drop', handleDrop);
        card.addEventListener('dragend', handleDragEnd);

        li.appendChild(card);

        // Children
        if (node.children && node.children.length > 0) {
            const childrenUl = document.createElement('ul');
            node.children.forEach(child => {
                childrenUl.appendChild(createNodeElement(child));
            });
            li.appendChild(childrenUl);
        }

        return li;
    }

    // --- Drag and Drop Handlers ---

    function handleDragStart(e) {
        draggedNodeId = this.dataset.id;
        draggedNodeName = this.dataset.name;
        this.classList.add('dragging');
        e.dataTransfer.effectAllowed = 'move';
        e.dataTransfer.setData('text/plain', draggedNodeId);
    }

    function handleDragOver(e) {
        e.preventDefault(); // Necessary to allow dropping
        e.dataTransfer.dropEffect = 'move';
        if (this.dataset.id !== draggedNodeId) {
            this.classList.add('drag-over');
        }
    }

    function handleDragLeave(e) {
        this.classList.remove('drag-over');
    }

    function handleDragEnd(e) {
        this.classList.remove('dragging');
        document.querySelectorAll('.drag-over').forEach(el => el.classList.remove('drag-over'));
    }

    function handleDrop(e) {
        e.stopPropagation();
        this.classList.remove('drag-over');

        const targetId = this.dataset.id;
        const targetName = this.dataset.name;

        if (draggedNodeId === targetId) return; // Dropped on self

        // Confirm Move
        const modal = new bootstrap.Modal(document.getElementById('confirmMoveModal'));
        document.getElementById('employeeName').textContent = draggedNodeName;
        document.getElementById('newManagerName').textContent = targetName;

        const confirmBtn = document.getElementById('confirmMoveBtn');
        // Remove old listeners to prevent stacking
        const newBtn = confirmBtn.cloneNode(true);
        confirmBtn.parentNode.replaceChild(newBtn, confirmBtn);

        newBtn.addEventListener('click', function () {
            updateManager(draggedNodeId, targetId, modal);
        });

        modal.show();
    }

    function updateManager(employeeId, newManagerId, modalInstance) {
        modalInstance.hide();

        // optimistic UI update or just reload? Reload is safer for integrity.

        fetch('/org-structure/api/update', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrf_token') // Ensure CSRF if enabled, though flask-wtf usually handles form inputs. Assume session auth ok for JSON for now or need token.
            },
            body: JSON.stringify({
                employee_id: employeeId,
                new_manager_id: newManagerId
            })
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Show success toast (using global toast if avail or alert)
                    // Reload tree
                    loadTree(companySelect.value);
                } else {
                    alert('Error: ' + data.error);
                }
            })
            .catch(err => {
                console.error(err);
                alert('Failed to update reporting line.');
            });
    }

    // Cookie helper for CSRF if needed (standard Flask-WTF pattern usually puts token in meta tag, but here assuming basic auth session)
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});
