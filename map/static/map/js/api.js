
var TIMEOUT = 10000;

var _pendingRequests = {};

function abortPendingRequests(key) {
    if (_pendingRequests[key]) {
        _pendingRequests[key]._callback = function(){};
        _pendingRequests[key].abort();
        _pendingRequests[key] = null;
    }
}

function dispatch(action, response, params) {
    var payload = {actionType: action, response: response};
    if (params) {
        payload.queryParams = params;
    }
    AppDispatcher.handleRequestAction(payload);
}

// return successful response, else return request Constants
function makeDigestFun(action, params) {
    return function (err, res) {
        if (err && err.timeout === TIMEOUT) {
            dispatch(action, Constants.request.TIMEOUT, params);
        } else if (res.status === 400) {
            UserActions.logout();
        } else if (!res.ok) {
            dispatch(action, Constants.request.ERROR, params);
        } else {
            dispatch(action, res, params);
        }
    };
}

// a simple get request
function get(url) {
    return request
        .get(url)
        .set('Accept', 'application/json')
        .timeout(TIMEOUT)
        .query();
}

var Api = {
    getData: function(url, action, params) {
        abortPendingRequests(url);
        dispatch(action, Constants.request.PENDING, params);
        _pendingRequests[key] = get(url).end(
            makeDigestFun(action, params)
        );
    }
};