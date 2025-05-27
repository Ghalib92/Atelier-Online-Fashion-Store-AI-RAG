document.addEventListener('DOMContentLoaded', function() {
    // Quantity controls
    document.querySelectorAll('.qty-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const input = this.parentElement.querySelector('.qty-input');
            const currentVal = parseInt(input.value);
            
            if (this.classList.contains('qty-decrement') && currentVal > 1) {
                input.value = currentVal - 1;
            } else if (this.classList.contains('qty-increment')) {
                input.value = currentVal + 1;
            }
        });
    });

    // AJAX add to cart
    document.querySelectorAll('.add-to-cart-form').forEach(form => {
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const submitBtn = this.querySelector('button[type="submit"]');
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Adding...';
            
            try {
                const response = await fetch(this.action, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': this.querySelector('[name=csrfmiddlewaretoken]').value,
                        'Accept': 'application/json',
                    },
                    body: new FormData(this)
                });
                
                const data = await response.json();
                
                if (data.success) {
                    // Update all cart count elements
                    document.querySelectorAll('#cart-count, .cart-count').forEach(el => {
                        el.textContent = data.cart_count;
                    });
                    // Show success message (consider using Toast)
                    console.log('Item added to cart');
                } else {
                    console.error(data.error);
                }
            } catch (error) {
                console.error('Error:', error);
            } finally {
                submitBtn.disabled = false;
                submitBtn.innerHTML = '<i class="fas fa-shopping-cart"></i> Add to Cart';
            }
        });
    });
});