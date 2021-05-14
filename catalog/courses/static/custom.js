
function showDetails(elId) {
    let tmp = document.getElementById('card-details-' + elId).hidden;
    document.getElementById('card-details-' + elId).hidden = ! tmp;
}
