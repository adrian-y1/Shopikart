



document.addEventListener('DOMContentLoaded', () => {

    // ------------------- EDIT ITEM CODE -------------------
    let modalDescription = document.querySelector('#edit-item-form-description')
    let modalTitle = document.querySelector('#edit-item-form-title')
    let modalPrice = document.querySelector('#edit-item-form-price')
    let modalQauntity = document.querySelector('#edit-item-form-quantity')

    let updateDescription = document.querySelector('#update-item-description')
    let updateTitle = document.querySelector('#update-item-title')
    let updatePrice = document.querySelector('#update-item-price')
    let updateQuantity = document.querySelector('#update-item-quantity')

    let formatter = new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
    })

    form = document.querySelector('#edit-item-form')

    if(form != null){
        form.onsubmit = (e) => {
            e.preventDefault();
            
            url = `/edit_item/${e.target.dataset.item_id}`
            
            fetch(url, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken
                },
                body: JSON.stringify({
                    'description': modalDescription.value,
                    'title': modalTitle.value,
                    'price': modalPrice.value,
                    'quantity': modalQauntity.value
                })
            })
            .then(response => response.json())
            .then(data => {
                updateDescription.innerHTML = data.description
                updateTitle.innerHTML = data.name
                updatePrice.innerHTML = formatter.format(data.price)
                updateQuantity.innerHTML = data.quantity
                if(parseInt(data.quantity) > 0){
                    document.querySelector('.item-view-stock').style.display = 'none'
                }
            })
            .catch(error => console.log("ERROR", error))
        }
    }
    // ------------------- UPDATE CART CODE -------------------

    document.querySelectorAll('#add-to-cart-item-view-form').forEach(form => {
        form.onsubmit = (e) => {
            e.preventDefault();
            
            const itemAdded = document.createElement('div')
            const capacityReached = document.createElement('div')
            const maxReached = document.createElement('div')

            const row = document.getElementById('item-view-wrapper-row')
            itemAdded.className = 'item-has-been-added alert text-center alert-primary'
            capacityReached.className = 'item-has-been-added alert text-center alert-danger'
            maxReached.className = 'item-has-been-added alert text-center alert-danger'

            capacityReached.style.display = 'none'
            maxReached.style.display = 'none'
            itemAdded.style.display = 'none'
            
            url = '/update_cart'
            
            fetch(url, {
                method: "POST",
                headers: {
                    'X-CSRFToken': csrftoken
                },
                body: JSON.stringify({
                    'item_id': e.target.dataset.item_id,
                    'action': e.target.dataset.action,
                    'quantity': document.querySelector('#quantity-number-input').value
                })
            })
            .then(respons => respons.json())
            .then(data => {
                let total = 0;
                let quanNumVal = document.querySelector('#quantity-number-input').value

                if('amount_exceeding' in data){
                    // if user's quantity input is greather than whats available ...
                    let parseAmount = JSON.parse(data.amount_exceeding)

                    maxReached.innerHTML = `You cannot buy more than the available quantity for this item.`
                    maxReached.style.display = 'block'
                    maxReached.classList.add('fade-out')
                    setTimeout(() => {
                        maxReached.style.display = 'none'
                    }, 5000)
                    itemAdded.style.display = 'none'
                    capacityReached.style.display = 'none'
                    row.prepend(maxReached)
                    document.querySelector('.cart-item-total span').innerHTML = parseInt(parseAmount.total)

                } else if('amount_exceeded' in data) {
                    // If user has reached max quantity in cart ...
                    let parseAmount = JSON.parse(data.amount_exceeded)
                    capacityReached.innerHTML = 'Item capacity has been reached!'
                    capacityReached.style.display = 'block'
                    capacityReached.classList.add('fade-out')
                    setTimeout(() => {
                        capacityReached.style.display = 'none'
                    }, 5000)
                    itemAdded.style.display = 'none'
                    maxReached.style.display = 'none'
                    row.prepend(capacityReached)
                    document.querySelector('.cart-item-total span').innerHTML = parseInt(parseAmount.total)

                } else {
                    // If order quantity is > the product's quantity and the order quantity + user's quantity input is < product quantity ...
                    data.forEach(d => {
                        total += d.quantity
                        if(d.quantity <= d.product.quantity){
                            itemAdded.innerHTML = `Added x${quanNumVal} to cart!`
                            itemAdded.style.display = 'block'
                            itemAdded.classList.add('fade-out')
                            setTimeout(() => {
                                itemAdded.style.display = 'none'
                            }, 5000)
                            capacityReached.style.display = 'none'
                            maxReached.style.display = 'none'
                            row.prepend(itemAdded)
    
                        }
                    })
                    document.querySelector('.cart-item-total span').innerHTML = total
                }
            })
            .catch(error => console.log('ERROR', error))
        }

    })

    // ------------------- UPDATE WISHLIST CODE -------------------
    let wishlistBtn = document.querySelectorAll('.update-wishlist')
    for(let i = 0; i <  wishlistBtn.length; i++){
        wishlistBtn[i].addEventListener('click', function() {
            const wishlistAction = this.dataset.action
            const wishlistItemId = this.dataset.item_id
            url =  '/update_wishlist'

            fetch(url, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken
                },
                body: JSON.stringify({
                    'action': wishlistAction,
                    'item_id': wishlistItemId
                })
            })
            .then(response => response.json())
            .then(data => {
                document.querySelector('.wishlist-number').innerHTML = data.length
            })
            .catch(error => console.log("ERROR", error))
            if(this.value === 'add'){
                this.value = 'remove'
                this.innerHTML = 'Remove from Wishlist'
                this.dataset.action = 'remove'
                this.className = 'update-wishlist-remove'
                const el = document.createElement('i')
                el.className = 'bi bi-dash fa-lg ms-1'
                this.appendChild(el)

            } else if(this.value === 'remove'){
                this.value = 'add'
                this.innerHTML = 'Add to Wishlist'
                this.dataset.action = 'add'
                this.className = 'update-wishlist-add'
                const el = document.createElement('i')
                el.className = 'bi bi-plus fa-lg ms-1'
                this.appendChild(el)
            } 
        })
    }

    // ------------------- CALCULATE STAR RATING CODE -------------------
    const numberOfRating = document.querySelectorAll('.number-of-rating')
    let ratings = {};
    numberOfRating.forEach(number => {
        ratings[number.dataset.review_id] = parseFloat(number.value)
    })
    const starTotal = 5;

    for(const rating in ratings){
        const starPercentage = (ratings[rating] / starTotal) * 100;
        const starPercentageRounded = `${(Math.round(starPercentage / 10) * 10)}%`

        document.querySelectorAll('.stars-inner').forEach(star => {
            if(star.dataset.review_id === rating){
                star.style.width = starPercentageRounded;
            }
        })
    }
    const averageRating = document.querySelectorAll('.average-rating-number-item-view')
    let items = {};
    averageRating.forEach(number => {
        items[number.dataset.item_id] = parseFloat(number.value)
    })
    const starTotalItemView = 5;

    for(const item in items){
        const starPercentage = (items[item] / starTotalItemView) * 100;
        document.querySelectorAll('.stars-inner-item-view').forEach(star => {
            if(star.dataset.item_id === item){
                star.style.width = `${starPercentage}%`;
            }
        })
    }
})