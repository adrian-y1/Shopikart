


document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('#add-to-cart-form').forEach(form => {
        form.onsubmit = (e) => {
            e.preventDefault();
            url = '/update_cart'

            fetch(url, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken
                },
                body: JSON.stringify({
                    'item_id': e.target.dataset.item_id,
                    'action':e.target.dataset.action
                })
            })
            .then(response => response.json())
            .then(data => {
                let total = 0;
                data.forEach(d => {
                    total += d.quantity
                })
                document.querySelector('.cart-item-total').innerHTML = total
            })
            .catch(error => console.log("Error:",error))
        }
    })
    const averageRating = document.querySelectorAll('.average-rating-number')
    let items = {};
    averageRating.forEach(number => {
        items[number.dataset.item_id] = parseFloat(number.value)
    })
    const stars = 5;

    for(const item in items){
        const starPercentage = (items[item] / stars) * 100;
        document.querySelectorAll('.stars-inner-index').forEach(star => {
            if(star.dataset.item_id === item){
                star.style.width = `${starPercentage}%`;
            }
        })
    }
})