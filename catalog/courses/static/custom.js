
function showDetails(elId) {
    let tmp = document.getElementById('card-details-' + elId).hidden;
    document.getElementById('card-details-' + elId).hidden = ! tmp;
}

function showExtraSearchOptions() {
    let state = document.getElementById('extra-search-options').hidden;
    document.getElementById('extra-search-options').hidden = ! state;
}

function runFilter() {
    document.getElementById('filter-form').submit();
}

