// POS JavaScript with enhanced decimal quantity support
document.addEventListener('DOMContentLoaded', function() {
    // Variables - Use global config if available, fallback to data attributes
    const config = window.POSConfig || {};
    const posDataEl = document.getElementById('pos-data');
    const taxRate = parseFloat(config.taxRate || posDataEl?.dataset.taxRate || "0");
    const currencySymbol = config.currencySymbol || posDataEl?.dataset.currencySymbol || '$';
    let cart = [];
    let selectedPaymentMethod = '';
    
    // DOM Elements
    const productSearch = document.getElementById('product-search');
    const categoryPills = document.querySelectorAll('.category-pill');
    const productCards = document.querySelectorAll('.product-card');
    const cartItemsContainer = document.getElementById('cart-items');
    const subtotalElement = document.getElementById('subtotal');
    const taxElement = document.getElementById('tax');
    const discountInput = document.getElementById('discount-input');
    const totalElement = document.getElementById('total');
    const checkoutBtn = document.getElementById('checkout-btn');
    const clearCartBtn = document.getElementById('clear-cart');
    const cartCustomerSelect = document.getElementById('cart-customer-select');
    const modalCustomerSelect = document.getElementById('modal-customer-select');
    
    // Payment Modal Elements
    const paymentModal = new bootstrap.Modal(document.getElementById('paymentModal'));
    const paymentMethodBtns = document.querySelectorAll('.payment-method-btn');
    const cashDetails = document.getElementById('payment-details-cash');
    const cardDetails = document.getElementById('payment-details-card');
    const mobileDetails = document.getElementById('payment-details-mobile');
    const creditDetails = document.getElementById('payment-details-credit');
    const cashReceived = document.getElementById('cash-received');
    const cashChange = document.getElementById('cash-change');
    const modalTotal = document.getElementById('modal-total');
    const completeSaleBtn = document.getElementById('complete-sale-btn');
    const customerDebtInfo = document.getElementById('customer-debt-info');
    const currentDebtAmount = document.getElementById('current-debt-amount');
    const creditLimitAmount = document.getElementById('credit-limit-amount');
    const availableCreditAmount = document.getElementById('available-credit-amount');
    
    // Receipt Modal Elements
    const receiptModal = new bootstrap.Modal(document.getElementById('receiptModal'));
    const invoiceNumber = document.getElementById('invoice-number');
    const viewReceiptBtn = document.getElementById('view-receipt-btn');
    
    // Event Listeners
    
    // Category selection
    categoryPills.forEach(pill => {
        pill.addEventListener('click', function() {
            // Remove active class from all pills
            categoryPills.forEach(p => p.classList.remove('active'));
            
            // Add active class to clicked pill
            this.classList.add('active');
            
            // Filter products
            const categoryId = this.dataset.categoryId;
            filterProducts(categoryId);
        });
    });
    
    // Product search
    if (productSearch) {
        productSearch.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            filterProductsBySearch(searchTerm);
        });
    }
    
    // Add product to cart
    productCards.forEach(card => {
        card.addEventListener('click', function() {
            const productId = parseInt(this.dataset.productId);
            const productName = this.dataset.productName;
            const productPrice = parseFloat(this.dataset.productPrice);
            const productStock = parseFloat(this.dataset.productStock); // Changed to parseFloat for decimal stock
            
            // Check if product is in stock
            if (productStock <= 0) {
                alert('This product is out of stock');
                return;
            }
            
            addToCart(productId, productName, productPrice, productStock);
        });
    });
    
    // Clear cart
    if (clearCartBtn) {
        clearCartBtn.addEventListener('click', clearCart);
    }
    
    // Discount input
    if (discountInput) {
        discountInput.addEventListener('input', updateTotals);
    }
    
    // Checkout button
    if (checkoutBtn) {
        checkoutBtn.addEventListener('click', function() {
            // Set the total in the modal
            if (modalTotal) {
                modalTotal.textContent = totalElement.textContent;
            }
            
            // Reset payment method selection
            paymentMethodBtns.forEach(btn => btn.classList.remove('selected'));
            selectedPaymentMethod = '';
            
            // Show the payment modal
            paymentModal.show();
        });
    }
    
    // Payment method selection
    paymentMethodBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            // Remove selected class from all buttons
            paymentMethodBtns.forEach(b => b.classList.remove('selected'));
            
            // Add selected class to clicked button
            this.classList.add('selected');
            
            // Store selected payment method
            selectedPaymentMethod = this.dataset.method;
            
            // Show appropriate payment details
            if (cashDetails) cashDetails.classList.add('d-none');
            if (cardDetails) cardDetails.classList.add('d-none');
            if (mobileDetails) mobileDetails.classList.add('d-none');
            if (creditDetails) creditDetails.classList.add('d-none');
            
            if (selectedPaymentMethod === 'cash') {
                if (cashDetails) cashDetails.classList.remove('d-none');
                
                // Set focus to cash received input
                setTimeout(() => {
                    if (cashReceived) {
                        cashReceived.focus();
                        
                        // Set default value to match total
                        const totalValue = parseFloat(totalElement.textContent.replace(currencySymbol, '').trim());
                        cashReceived.value = totalValue.toFixed(2);
                        
                        // Calculate change
                        calculateChange();
                    }
                }, 100);
            } else if (selectedPaymentMethod === 'card') {
                if (cardDetails) cardDetails.classList.remove('d-none');
            } else if (selectedPaymentMethod === 'mobile_payment') {
                if (mobileDetails) mobileDetails.classList.remove('d-none');
            } else if (selectedPaymentMethod === 'credit') {
                if (creditDetails) creditDetails.classList.remove('d-none');
                
                // Check if a real customer is selected (not walk-in)
                const selectedCustomer = modalCustomerSelect?.value;
                const selectedCustomerText = modalCustomerSelect?.options[modalCustomerSelect.selectedIndex]?.text;
                
                if (!selectedCustomer || selectedCustomer === '' || selectedCustomerText === 'Walk-in Customer') {
                    alert('Please select a specific customer for credit transactions. Walk-in customers cannot make credit purchases.');
                    // Reset to cash payment
                    if (paymentMethodBtns[0]) paymentMethodBtns[0].click();
                    return;
                }
                
                // Set default due date (30 days from now)
                const dueDate = new Date();
                dueDate.setDate(dueDate.getDate() + 30);
                const creditDueDateEl = document.getElementById('credit-due-date');
                if (creditDueDateEl) {
                    creditDueDateEl.value = dueDate.toISOString().split('T')[0];
                }
            }
        });
    });
    
    // Synchronize customer selects
    if (cartCustomerSelect && modalCustomerSelect) {
        cartCustomerSelect.addEventListener('change', function() {
            modalCustomerSelect.value = this.value;
        });
    }
    
    // Customer selection change (modal)
    if (modalCustomerSelect) {
        modalCustomerSelect.addEventListener('change', function() {
            // Sync with cart customer select
            if (cartCustomerSelect) {
                cartCustomerSelect.value = this.value;
            }
            
            const selectedOption = this.options[this.selectedIndex];
            
            if (selectedOption.value && selectedOption.text !== 'Walk-in Customer') {
                const creditLimit = parseFloat(selectedOption.dataset.creditLimit || 0);
                const currentDebt = parseFloat(selectedOption.dataset.currentDebt || 0);
                const availableCredit = creditLimit - currentDebt;
                
                // Show customer debt information
                if (customerDebtInfo) {
                    customerDebtInfo.classList.remove('d-none');
                    if (currentDebtAmount) currentDebtAmount.textContent = currencySymbol + currentDebt.toFixed(2);
                    if (creditLimitAmount) creditLimitAmount.textContent = currencySymbol + creditLimit.toFixed(2);
                    if (availableCreditAmount) availableCreditAmount.textContent = currencySymbol + availableCredit.toFixed(2);
                    
                    // Change alert color based on debt status
                    const alertDiv = customerDebtInfo.querySelector('.alert');
                    if (alertDiv) {
                        alertDiv.className = 'alert';
                        
                        if (currentDebt > creditLimit * 0.8) {
                            alertDiv.classList.add('alert-danger');
                        } else if (currentDebt > creditLimit * 0.5) {
                            alertDiv.classList.add('alert-warning');  
                        } else {
                            alertDiv.classList.add('alert-info');
                        }
                    }
                    
                    // If credit payment is selected and customer changes, ensure credit is still available
                    if (selectedPaymentMethod === 'credit' && availableCredit <= 0) {
                        alert('Warning: Selected customer has no available credit. Please choose a different payment method or customer.');
                    }
                }
            } else {
                // Hide customer debt information for walk-in customers
                if (customerDebtInfo) customerDebtInfo.classList.add('d-none');
                
                // If credit payment is selected but walk-in customer is chosen, warn user
                if (selectedPaymentMethod === 'credit') {
                    alert('Credit payment is not available for walk-in customers. Please select a specific customer or choose a different payment method.');
                    // Reset to cash payment
                    if (paymentMethodBtns && paymentMethodBtns[0]) {
                        paymentMethodBtns[0].click();
                    }
                }
            }
        });
    }
    
    // Cash received input
    if (cashReceived) {
        cashReceived.addEventListener('input', calculateChange);
    }
    
    // Complete sale button
    if (completeSaleBtn) {
        completeSaleBtn.addEventListener('click', processSale);
    }
    
    // Functions
    
    // Filter products by category
    function filterProducts(categoryId) {
        productCards.forEach(card => {
            if (categoryId === 'all' || card.dataset.categoryId === categoryId) {
                card.style.display = 'flex';
            } else {
                card.style.display = 'none';
            }
        });
    }
    
    // Filter products by search term
    function filterProductsBySearch(searchTerm) {
        if (searchTerm === '') {
            // If search is cleared, reapply category filter
            const activeCategoryPill = document.querySelector('.category-pill.active');
            if (activeCategoryPill) {
                filterProducts(activeCategoryPill.dataset.categoryId);
            }
            return;
        }
        
        productCards.forEach(card => {
            const productName = card.dataset.productName.toLowerCase();
            if (productName.includes(searchTerm)) {
                card.style.display = 'flex';
            } else {
                card.style.display = 'none';
            }
        });
    }
    
    // Add product to cart with enhanced decimal support
    function addToCart(productId, productName, productPrice, productStock) {
        // Check if product is already in cart
        const existingItemIndex = cart.findIndex(item => item.productId === productId);
        
        if (existingItemIndex !== -1) {
            // If product is already in cart, increment quantity if stock allows
            const newQuantity = parseFloat((cart[existingItemIndex].quantity + 0.5).toFixed(2)); // Default increment of 0.5 for decimals
            if (newQuantity <= productStock) {
                cart[existingItemIndex].quantity = newQuantity;
            } else {
                alert('Cannot add more of this product due to stock limitations');
                return;
            }
        } else {
            // Add new item to cart with default quantity of 0.5
            cart.push({
                productId,
                name: productName,
                price: productPrice,
                quantity: 0.5, // Start with 0.5 instead of 1 for decimal support
                maxStock: productStock
            });
        }
        
        // Update cart display
        renderCart();
        updateTotals();
    }
    
    // Render cart items with enhanced quantity controls
    function renderCart() {
        if (!cartItemsContainer) return;
        
        if (cart.length === 0) {
            cartItemsContainer.innerHTML = `
                <div class="text-center p-4 text-muted">
                    <i class="fas fa-shopping-cart mb-3" style="font-size: 3rem;"></i>
                    <p>No items in cart</p>
                    <p class="small">Select products from the left panel</p>
                </div>
            `;
            if (checkoutBtn) checkoutBtn.disabled = true;
            return;
        }
        
        let cartHTML = '';
        
        cart.forEach((item, index) => {
            const itemTotal = item.price * item.quantity;
            
            cartHTML += `
                <div class="cart-item">
                    <div class="cart-item-details">
                        <div class="cart-item-name">${item.name}</div>
                        <div class="cart-item-price">${currencySymbol} ${item.price.toFixed(2)}</div>
                    </div>
                    <div class="cart-item-controls">
                        <div class="cart-item-quantity">
                            <button class="decrease-qty qty-step-btn" data-index="${index}" data-step="0.25" title="Decrease by 0.25">-¼</button>
                            <button class="decrease-qty-half qty-step-btn" data-index="${index}" data-step="0.5" title="Decrease by 0.5">-½</button>
                            <input type="number" value="${item.quantity}" step="0.01" min="0.01" max="${item.maxStock}" 
                                   class="quantity-input editable" data-index="${index}">
                            <button class="increase-qty-half qty-step-btn" data-index="${index}" data-step="0.5" title="Increase by 0.5">+½</button>
                            <button class="increase-qty qty-step-btn" data-index="${index}" data-step="1" title="Increase by 1">+1</button>
                        </div>
                        <div class="cart-item-subtotal">${currencySymbol} ${itemTotal.toFixed(2)}</div>
                        <button class="btn btn-sm text-danger remove-item" data-index="${index}">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                </div>
            `;
        });
        
        cartItemsContainer.innerHTML = cartHTML;
        if (checkoutBtn) checkoutBtn.disabled = false;
        
        // Add event listeners to cart item controls
        document.querySelectorAll('.decrease-qty').forEach(btn => {
            btn.addEventListener('click', function() {
                const index = parseInt(this.dataset.index);
                const step = parseFloat(this.dataset.step);
                adjustQuantity(index, -step);
            });
        });
        
        document.querySelectorAll('.decrease-qty-half').forEach(btn => {
            btn.addEventListener('click', function() {
                const index = parseInt(this.dataset.index);
                const step = parseFloat(this.dataset.step);
                adjustQuantity(index, -step);
            });
        });
        
        document.querySelectorAll('.increase-qty-half').forEach(btn => {
            btn.addEventListener('click', function() {
                const index = parseInt(this.dataset.index);
                const step = parseFloat(this.dataset.step);
                adjustQuantity(index, step);
            });
        });
        
        document.querySelectorAll('.increase-qty').forEach(btn => {
            btn.addEventListener('click', function() {
                const index = parseInt(this.dataset.index);
                const step = parseFloat(this.dataset.step);
                adjustQuantity(index, step);
            });
        });
        
        // Add event listeners for manual quantity input
        document.querySelectorAll('.quantity-input').forEach(input => {
            input.addEventListener('change', function() {
                const index = parseInt(this.dataset.index);
                const newQuantity = parseFloat(this.value);
                
                if (isNaN(newQuantity) || newQuantity <= 0) {
                    alert('Please enter a valid positive quantity');
                    this.value = cart[index].quantity;
                    return;
                }
                
                if (newQuantity > cart[index].maxStock) {
                    alert(`Cannot exceed stock limit of ${cart[index].maxStock}`);
                    this.value = cart[index].quantity;
                    return;
                }
                
                cart[index].quantity = parseFloat(newQuantity.toFixed(2));
                updateTotals();
                // Re-render to update subtotal
                renderCart();
            });
            
            input.addEventListener('focus', function() {
                this.select(); // Select all text when focused
            });
        });
        
        document.querySelectorAll('.remove-item').forEach(btn => {
            btn.addEventListener('click', function() {
                const index = parseInt(this.dataset.index);
                removeItem(index);
            });
        });
    }
    
    // Enhanced quantity adjustment with decimal support
    function adjustQuantity(index, step) {
        const newQuantity = parseFloat((cart[index].quantity + step).toFixed(2));
        
        if (newQuantity <= 0) {
            removeItem(index);
            return;
        }
        
        if (newQuantity > cart[index].maxStock) {
            alert('Cannot add more of this product due to stock limitations');
            return;
        }
        
        cart[index].quantity = newQuantity;
        renderCart();
        updateTotals();
    }
    
    // Remove item from cart
    function removeItem(index) {
        cart.splice(index, 1);
        renderCart();
        updateTotals();
    }
    
    // Clear cart
    function clearCart() {
        if (cart.length === 0) return;
        
        if (confirm('Are you sure you want to clear the cart?')) {
            cart = [];
            renderCart();
            updateTotals();
        }
    }
    
    // Update totals
    function updateTotals() {
        // Calculate subtotal
        const subtotal = cart.reduce((total, item) => total + (item.price * item.quantity), 0);
        
        // Get discount
        const discount = parseFloat(discountInput?.value || 0);
        
        // Calculate tax
        const taxableAmount = subtotal - discount;
        const tax = taxableAmount * (taxRate / 100);
        
        // Calculate total
        const total = taxableAmount + tax;
        
        // Update display
        if (subtotalElement) subtotalElement.textContent = `${currencySymbol} ${subtotal.toFixed(2)}`;
        if (taxElement) taxElement.textContent = `${currencySymbol} ${tax.toFixed(2)}`;
        if (totalElement) totalElement.textContent = `${currencySymbol} ${total.toFixed(2)}`;
    }
    
    // Calculate change
    function calculateChange() {
        if (!totalElement || !cashReceived || !cashChange) return;
        
        const totalValue = parseFloat(totalElement.textContent.replace(currencySymbol, '').trim());
        const received = parseFloat(cashReceived.value) || 0;
        const change = received - totalValue;
        
        if (change >= 0) {
            cashChange.value = change.toFixed(2);
            cashChange.classList.remove('is-invalid');
            cashChange.classList.add('is-valid');
        } else {
            cashChange.value = '0.00';
            cashChange.classList.remove('is-valid');
            cashChange.classList.add('is-invalid');
        }
    }
    
    // Process sale
    function processSale() {
        // Validate cart
        if (cart.length === 0) {
            alert('Please add items to the cart before checkout');
            return;
        }
        
        // Validate payment method
        if (!selectedPaymentMethod) {
            alert('Please select a payment method');
            return;
        }
        
        // Validate cash payment
        if (selectedPaymentMethod === 'cash') {
            const totalValue = parseFloat(totalElement.textContent.replace(currencySymbol, '').trim());
            const received = parseFloat(cashReceived?.value || 0);
            
            if (received < totalValue) {
                alert('Cash received must be at least equal to the total amount');
                return;
            }
        }
        
        // Validate credit payment
        if (selectedPaymentMethod === 'credit') {
            const selectedCustomerValue = modalCustomerSelect?.value;
            const selectedCustomerText = modalCustomerSelect?.options[modalCustomerSelect.selectedIndex]?.text;
            
            // Ensure a real customer is selected (not walk-in or empty)
            if (!selectedCustomerValue || selectedCustomerValue === '' || selectedCustomerText === 'Walk-in Customer') {
                alert('Please select a specific customer for credit transactions. Walk-in customers cannot make credit purchases.');
                return;
            }
            
            const selectedOption = modalCustomerSelect.options[modalCustomerSelect.selectedIndex];
            const creditLimit = parseFloat(selectedOption.dataset.creditLimit || 0);
            const currentDebt = parseFloat(selectedOption.dataset.currentDebt || 0);
            const totalValue = parseFloat(totalElement.textContent.replace(currencySymbol, '').trim());
            
            if (currentDebt + totalValue > creditLimit) {
                const exceeded = (currentDebt + totalValue) - creditLimit;
                if (!confirm(`This transaction will exceed the customer's credit limit by ${currencySymbol}${exceeded.toFixed(2)}. Continue anyway?`)) {
                    return;
                }
            }
        }
        
        // Calculate totals with proper validation
        const subtotal = cart.reduce((total, item) => total + (item.price * item.quantity), 0);
        const discount = parseFloat(discountInput?.value || 0);
        const taxableAmount = subtotal - discount;
        const tax = taxableAmount * (taxRate / 100);
        const total = taxableAmount + tax;
        
        // Prepare sale data
        const saleData = {
            customer_id: modalCustomerSelect?.value || null,
            subtotal: subtotal,
            tax_amount: tax,
            discount_amount: discount,
            total_amount: total,
            payment_method: selectedPaymentMethod,
            payment_reference: '',
            notes: document.getElementById('payment-notes')?.value || '',
            items: cart.map(item => ({
                product_id: item.productId,
                quantity: item.quantity,
                unit_price: item.price
            }))
        };
        
        console.log('Sale data:', saleData); // Debug log
        
        // Add payment reference based on payment method
        if (selectedPaymentMethod === 'card') {
            const cardRefEl = document.getElementById('card-reference');
            if (cardRefEl) saleData.payment_reference = cardRefEl.value;
        } else if (selectedPaymentMethod === 'mobile_payment') {
            const mobileRefEl = document.getElementById('mobile-reference');
            if (mobileRefEl) saleData.payment_reference = mobileRefEl.value;
        } else if (selectedPaymentMethod === 'credit') {
            const creditDueDateEl = document.getElementById('credit-due-date');
            const creditNotesEl = document.getElementById('credit-notes');
            if (creditDueDateEl) saleData.credit_due_date = creditDueDateEl.value;
            if (creditNotesEl) saleData.credit_notes = creditNotesEl.value;
        }
        
        // Get CSRF token
        const csrfToken = getCookie('csrftoken');
        if (!csrfToken) {
            alert('Security token not found. Please refresh the page and try again.');
            return;
        }
        
        // Get the process sale URL from global config or data attribute
        const processSaleUrl = config.processSaleUrl || posDataEl?.dataset.processSaleUrl || '/pos/process-sale/';
        
        // Debug: Log the URL being used
        console.log('Using process sale URL:', processSaleUrl);
        
        // Send sale data to server
        fetch(processSaleUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify(saleData)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                // Close payment modal
                paymentModal.hide();
                
                // Set receipt details
                if (invoiceNumber) invoiceNumber.textContent = data.invoice_number;
                if (viewReceiptBtn) viewReceiptBtn.href = `/pos/receipt/${data.sale_id}/`;
                
                // Show receipt modal
                receiptModal.show();
                
                // Clear cart
                cart = [];
                renderCart();
                updateTotals();
                
                // Reset form fields
                if (discountInput) discountInput.value = 0;
                if (cartCustomerSelect) cartCustomerSelect.value = '';
                if (modalCustomerSelect) modalCustomerSelect.value = '';
            } else {
                alert('Error: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while processing the sale. Please try again.');
        });
    }
    
    // Get CSRF token from cookies
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    
    // Initialize
    renderCart();
    updateTotals();
});