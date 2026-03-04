// RMOS Sprint 1 Frontend Application

class RMOSApp {
    constructor() {
        this.apiBaseUrl = '/api';
        this.menuItems = [];
        this.categories = [];
        this.currentOrder = [];
        this.currentCategory = null;
        this.tableNumber = 1;
        
        this.init();
    }
    
    async init() {
        this.cacheElements();
        this.attachEventListeners();
        await this.checkConnection();
        await this.loadCategories();
        await this.loadMenuItems();
        this.updateOrderDisplay();
    }
    
    cacheElements() {
        // Cache DOM elements
        this.elements = {
            connectionStatus: document.getElementById('connection-status'),
            statusIndicator: document.querySelector('.status-indicator'),
            statusText: document.getElementById('status-text'),
            categoryNav: document.getElementById('category-nav'),
            currentCategory: document.getElementById('current-category'),
            menuGrid: document.getElementById('menu-grid'),
            orderItems: document.getElementById('order-items'),
            orderTotal: document.getElementById('order-total'),
            tableNumber: document.getElementById('table-number'),
            orderTable: document.getElementById('order-table'),
            clearOrderBtn: document.getElementById('clear-order'),
            placeOrderBtn: document.getElementById('place-order'),
            callWaiterBtn: document.getElementById('call-waiter'),
            orderModal: document.getElementById('order-modal'),
            waiterModal: document.getElementById('waiter-modal'),
            orderSummary: document.getElementById('order-summary'),
            closeModalBtn: document.getElementById('close-modal'),
            closeWaiterModal: document.getElementById('close-waiter-modal')
        };
    }
    
    attachEventListeners() {
        // Table selection
        this.elements.tableNumber.addEventListener('change', (e) => {
            this.tableNumber = parseInt(e.target.value);
            this.elements.orderTable.textContent = `Table ${this.tableNumber}`;
        });
        
        // Order actions
        this.elements.clearOrderBtn.addEventListener('click', () => this.clearOrder());
        this.elements.placeOrderBtn.addEventListener('click', () => this.placeOrder());
        this.elements.callWaiterBtn.addEventListener('click', () => this.callWaiter());
        
        // Modal close buttons
        this.elements.closeModalBtn.addEventListener('click', () => {
            this.elements.orderModal.classList.remove('active');
        });
        
        this.elements.closeWaiterModal.addEventListener('click', () => {
            this.elements.waiterModal.classList.remove('active');
        });
        
        // Close modals on outside click
        window.addEventListener('click', (e) => {
            if (e.target === this.elements.orderModal) {
                this.elements.orderModal.classList.remove('active');
            }
            if (e.target === this.elements.waiterModal) {
                this.elements.waiterModal.classList.remove('active');
            }
        });
    }
    
    async checkConnection() {
        try {
            const response = await fetch('/health');
            if (response.ok) {
                this.setConnectionStatus(true);
            } else {
                this.setConnectionStatus(false);
            }
        } catch (error) {
            console.error('Connection check failed:', error);
            this.setConnectionStatus(false);
        }
    }
    
    setConnectionStatus(connected) {
        const { statusIndicator, statusText } = this.elements;
        
        if (connected) {
            statusIndicator.className = 'status-indicator connected';
            statusText.textContent = 'Connected';
        } else {
            statusIndicator.className = 'status-indicator disconnected';
            statusText.textContent = 'Disconnected';
        }
    }
    
    async loadCategories() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/categories`);
            if (!response.ok) throw new Error('Failed to load categories');
            
            this.categories = await response.json();
            this.renderCategories();
        } catch (error) {
            console.error('Error loading categories:', error);
            this.showError('Failed to load menu categories');
        }
    }
    
    renderCategories() {
        const nav = this.elements.categoryNav;
        nav.innerHTML = '';
        
        // Add "All" category
        const allCategory = document.createElement('div');
        allCategory.className = `category-item ${this.currentCategory === null ? 'active' : ''}`;
        allCategory.textContent = 'All Items';
        allCategory.dataset.category = 'all';
        allCategory.addEventListener('click', () => this.filterByCategory(null));
        nav.appendChild(allCategory);
        
        // Add actual categories
        this.categories.forEach(category => {
            const item = document.createElement('div');
            item.className = `category-item ${this.currentCategory === category.id ? 'active' : ''}`;
            item.textContent = category.name;
            item.dataset.category = category.id;
            item.addEventListener('click', () => this.filterByCategory(category.id));
            nav.appendChild(item);
        });
    }
    
    async loadMenuItems() {
        this.elements.menuGrid.innerHTML = '<div class="loading">Loading menu...</div>';
        
        try {
            let url = `${this.apiBaseUrl}/menu-items?limit=100`;
            if (this.currentCategory) {
                url += `&category_id=${this.currentCategory}`;
            }
            
            const response = await fetch(url);
            if (!response.ok) throw new Error('Failed to load menu items');
            
            this.menuItems = await response.json();
            this.renderMenuItems();
        } catch (error) {
            console.error('Error loading menu items:', error);
            this.elements.menuGrid.innerHTML = '<div class="error">Failed to load menu. Please refresh.</div>';
        }
    }
    
    renderMenuItems() {
        const grid = this.elements.menuGrid;
        grid.innerHTML = '';
        
        if (this.menuItems.length === 0) {
            grid.innerHTML = '<div class="empty-state">No menu items available</div>';
            return;
        }
        
        this.menuItems.forEach(item => {
            const card = document.createElement('div');
            card.className = `menu-item ${!item.is_available ? 'unavailable' : ''}`;
            card.dataset.id = item.id;
            
            card.innerHTML = `
                <h3>${this.escapeHtml(item.name)}</h3>
                <div class="description">${this.escapeHtml(item.description || '')}</div>
                <div class="price">$${item.price.toFixed(2)}</div>
                ${item.preparation_time ? `<div class="prep-time">🕒 ${item.preparation_time} min</div>` : ''}
            `;
            
            if (item.is_available) {
                card.addEventListener('click', () => this.addToOrder(item));
            }
            
            grid.appendChild(card);
        });
    }
    
    filterByCategory(categoryId) {
        this.currentCategory = categoryId;
        
        // Update active category in nav
        document.querySelectorAll('.category-item').forEach(item => {
            const catId = item.dataset.category === 'all' ? null : parseInt(item.dataset.category);
            item.classList.toggle('active', catId === categoryId);
        });
        
        // Update category title
        if (categoryId === null) {
            this.elements.currentCategory.textContent = 'All Items';
        } else {
            const category = this.categories.find(c => c.id === categoryId);
            this.elements.currentCategory.textContent = category ? category.name : 'Menu';
        }
        
        this.loadMenuItems();
    }
    
    addToOrder(item) {
        if (!item.is_available) return;
        
        const existingItem = this.currentOrder.find(i => i.id === item.id);
        
        if (existingItem) {
            existingItem.quantity += 1;
        } else {
            this.currentOrder.push({
                id: item.id,
                name: item.name,
                price: item.price,
                quantity: 1
            });
        }
        
        this.updateOrderDisplay();
        this.animateAddToOrder();
    }
    
    updateOrderDisplay() {
        const container = this.elements.orderItems;
        const total = this.currentOrder.reduce((sum, item) => sum + (item.price * item.quantity), 0);
        
        if (this.currentOrder.length === 0) {
            container.innerHTML = `
                <div class="empty-order">
                    <p>Your order is empty</p>
                    <small>Tap items on the menu to add</small>
                </div>
            `;
        } else {
            container.innerHTML = this.currentOrder.map(item => `
                <div class="order-item" data-id="${item.id}">
                    <div class="order-item-info">
                        <div class="order-item-name">${this.escapeHtml(item.name)}</div>
                        <div class="order-item-price">$${(item.price * item.quantity).toFixed(2)}</div>
                    </div>
                    <div class="order-item-controls">
                        <button class="quantity-btn" onclick="app.updateQuantity(${item.id}, -1)">−</button>
                        <span class="order-item-quantity">${item.quantity}</span>
                        <button class="quantity-btn" onclick="app.updateQuantity(${item.id}, 1)">+</button>
                        <span class="remove-item" onclick="app.removeFromOrder(${item.id})">✕</span>
                    </div>
                </div>
            `).join('');
        }
        
        this.elements.orderTotal.textContent = `$${total.toFixed(2)}`;
        this.elements.clearOrderBtn.disabled = this.currentOrder.length === 0;
        this.elements.placeOrderBtn.disabled = this.currentOrder.length === 0;
    }
    
    updateQuantity(itemId, delta) {
        const item = this.currentOrder.find(i => i.id === itemId);
        if (item) {
            item.quantity += delta;
            if (item.quantity <= 0) {
                this.removeFromOrder(itemId);
            } else {
                this.updateOrderDisplay();
            }
        }
    }
    
    removeFromOrder(itemId) {
        this.currentOrder = this.currentOrder.filter(i => i.id !== itemId);
        this.updateOrderDisplay();
    }
    
    clearOrder() {
        if (confirm('Clear your entire order?')) {
            this.currentOrder = [];
            this.updateOrderDisplay();
        }
    }
    
    async placeOrder() {
        if (this.currentOrder.length === 0) return;
        
        this.elements.placeOrderBtn.disabled = true;
        this.elements.placeOrderBtn.textContent = 'Placing...';
        
        try {
            const orderData = {
                table_number: this.tableNumber,
                customer_name: 'Guest', // Could add name input in future
                items: this.currentOrder.map(item => ({
                    menu_item_id: item.id,
                    quantity: item.quantity,
                    notes: ''
                }))
            };
            
            const response = await fetch(`${this.apiBaseUrl}/orders`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(orderData)
            });
            
            if (!response.ok) throw new Error('Failed to place order');
            
            const order = await response.json();
            this.showOrderConfirmation(order);
            this.currentOrder = [];
            this.updateOrderDisplay();
        } catch (error) {
            console.error('Error placing order:', error);
            alert('Failed to place order. Please try again.');
        } finally {
            this.elements.placeOrderBtn.disabled = false;
            this.elements.placeOrderBtn.textContent = 'Place Order';
        }
    }
    
    callWaiter() {
        this.elements.waiterModal.classList.add('active');
        
        // In a real implementation, this would call an API endpoint
        console.log(`Waiter called for Table ${this.tableNumber}`);
    }
    
    showOrderConfirmation(order) {
        const summary = this.elements.orderSummary;
        summary.innerHTML = `
            <p><strong>Order #${order.id}</strong></p>
            <p>Table: ${order.table_number}</p>
            <p>Total: $${order.total_amount.toFixed(2)}</p>
            <p>Status: ${order.status}</p>
        `;
        
        this.elements.orderModal.classList.add('active');
    }
    
    animateAddToOrder() {
        // Visual feedback for adding items
        const sidebar = this.elements.orderSidebar;
        sidebar.style.transform = 'scale(1.02)';
        setTimeout(() => {
            sidebar.style.transform = 'scale(1)';
        }, 200);
    }
    
    showError(message) {
        // Simple error handling - could be enhanced
        console.error(message);
        alert(message);
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize app when DOM is loaded
let app;
document.addEventListener('DOMContentLoaded', () => {
    app = new RMOSApp();
    window.app = app; // For debugging and inline event handlers
});