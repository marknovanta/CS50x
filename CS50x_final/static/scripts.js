let priceTag = document.querySelector("#priceTag");
let priceInput = document.querySelector("#priceBuy");
let sizeInput = document.querySelector("#sizeBuy");

const formatter = new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
});

priceInput.addEventListener("input", function() {
    priceTag.innerHTML = "Total cost: " + formatter.format((sizeInput.value * priceInput.value));
});

sizeInput.addEventListener("input", function() {
    priceTag.innerHTML = "Total cost: " + formatter.format((sizeInput.value * priceInput.value));
});

