

document.addEventListener('DOMContentLoaded', () => {
    let cartButtons = document.querySelectorAll('.update-cart')
    
    for(let i = 0; i < cartButtons.length; i++){
        cartButtons[i].addEventListener('click', function() {
            const action = this.dataset.action
            const item_id = this.dataset.item_id
            url = '/update_cart'
            
            fetch(url, {
                method: "POST",
                headers: {
                    'X-CSRFToken': csrftoken
                },
                body: JSON.stringify({
                    'item_id': item_id,
                    'action': action
                })
            })
            .then(response => response.json())
            .then(data => {
                let total = 0;
                let total_cart_quantity = 0;
                let total_cart_price = 0;
                let formatter = new Intl.NumberFormat('en-US', {
                    style: 'currency',
                    currency: 'USD',
                })
                data.forEach(d => {

                    total += d.quantity
                    total_cart_price += d.price_per_item

                    // Update the prices and quantity of each item
                    document.querySelectorAll('.update-single-item-quantity').forEach(item => {
                        document.querySelectorAll('.update-total-item-price').forEach(price => {
                            if(item.dataset.item_id == d.product.id && price.dataset.item_id == d.product.id){
                                item.innerHTML = d.quantity
                                price.innerHTML = formatter.format(d.price_per_item)
                            }
                        })
                    })
                    // Remove row if quantity is 0 or less
                    document.querySelectorAll('.remove-table-row').forEach(row => {
                        if(parseInt(row.dataset.item_id) === d.product.id){
                            if(d.quantity <= 0){
                                row.remove()
                            }
                        }
                    })
                })
                // Update the total prices and quantity
                document.querySelector('.cart-item-total span').innerHTML = total
                document.querySelector('.update-total-cart-price').innerHTML = formatter.format(total_cart_price)
                if(total <= 0){
                    document.querySelector('#checkout-btn').style.display = 'none'
                    document.querySelector('#table-foot').style.display = 'none'
                }
            })
            .catch(error => console.log("ERROR", error))
        })
    }
})