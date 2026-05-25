document.addEventListener("DOMContentLoaded", function () {
    const itemCards = document.querySelectorAll('.cart-item-card');
    const summaryCol = document.querySelector('.cart-summary-col');
    const layout = document.querySelector('.cart-layout');

    // If there are zero item cards, hide the summary block and make the layout full-width
    if (itemCards.length === 0) {
        if (summaryCol) {
            summaryCol.style.display = 'none';
        }
        if (layout) {
            layout.classList.add('is-empty');
            layout.style.gridTemplateColumns = '1fr';
        }
    }
});
const checkoutBtn = document.querySelector('.cart-checkout-btn');
const shippingModal = document.getElementById('shippingModal');
const closeModalBtn = document.getElementById('closeModalBtn');
const shippingForm = document.getElementById('shippingForm'); 

// when the user clicks the checkout button it pops out a modal 
if(checkoutBtn && shippingModal){
    checkoutBtn.addEventListener("click", function(){
        shippingModal.style.display = 'flex';
        shippingModal.style.alignItems = "center";
        shippingModal.style.justifyContent = "center";
    });

    closeModalBtn.addEventListener("click", function(){
        shippingModal.style.display = "none";
        shippingForm.reset();
    });
}

// when the user clicks the confirm details and pay button it collects all the details and sends it to the django backend 
if (shippingForm) {
    shippingForm.addEventListener("submit", function(event){
        event.preventDefault();
        
        const name = document.getElementById('name-input').value;
        const email = document.getElementById('email-input').value;
        const phone = document.getElementById('phone-input').value;
        const address = document.getElementById('address-input').value; 
        
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value || window.csrfToken;

        fetch('/payments/create-order/', {
            method: 'POST',
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrfToken
            },
            body: JSON.stringify({})
        })
        .then(response => response.json())
        .then(orderData => {
            const options = {
                "key": orderData.key_id,
                "amount": orderData.amount,
                "currency": orderData.currency,
                "name": "Odd Ritual",
                "prefill": {
                    "name": name,
                    "email": email,
                    "contact": phone
                },
                "handler": function(razorpayResponse){
                    const verifyData = new URLSearchParams(); 
                    
                    verifyData.append('payment_id', razorpayResponse.razorpay_payment_id);
                    verifyData.append('razorpay_order_id', razorpayResponse.razorpay_order_id);
                    verifyData.append('razorpay_signature', razorpayResponse.razorpay_signature); 
                    verifyData.append('customer_name', name);
                    verifyData.append('phone', phone);
                    verifyData.append('email', email);
                    verifyData.append('address', address);
                    
                    fetch('/payments/verify-payments/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/x-www-form-urlencoded',
                            'X-CSRFToken': csrfToken
                        },
                        body: verifyData
                    })
                    .then(res => res.json())
                    .then(data => {
                        if(data.status === 'success'){
                            alert('Payment Successful!');
                            window.location.href = '/'; 
                        } else {
                            alert('Payment Failed: ' + data.message);
                        }
                    })
                    .catch(err => {
                        console.error('Verification error:', err);
                    });
                }  
            };
            
            const rzp = new Razorpay(options);
            rzp.open();
        })
        .catch(err => {
            console.error('Order creation error:', err);
        });
    });
}

// Handle quantity updates
const qtyButtons = document.querySelectorAll('.qty-btn');
if (qtyButtons) {
    qtyButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const itemId = this.getAttribute('data-item-id');
            const action = this.classList.contains('plus') ? 'increase' : 'decrease';
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value || window.csrfToken;

            fetch(`/cart/update/${itemId}/`, {
                method: 'POST',
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrfToken
                },
                body: JSON.stringify({ action: action })
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'updated' || data.status === 'deleted') {
                    window.location.reload();
                } else if (data.error) {
                    console.error('Error updating cart:', data.error);
                }
            })
            .catch(err => {
                console.error('Error:', err);
            });
        });
    });
}
