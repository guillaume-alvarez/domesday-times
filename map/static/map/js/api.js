var API_URL = '/api/';
var TIMEOUT = 10000;

var _pendingRequests = {};

function abortPendingRequests(key) {
    if (_pendingRequests[key]) {
        _pendingRequests[key]._callback = function(){};
        _pendingRequests[key].abort();
        _pendingRequests[key] = null;
    }
}

function makeUrl(type, id) {
    var url = API_URL + type;
    if (id) url += '/' + id + '/';
    return url;
}

function dispatch(action, response, params) {
    var payload = {actionType: action, response: response.body};
    if (params) payload.queryParams = params;
    AppDispatcher.dispatch(payload);
}

// return successful response, else return request Constants
function makeDigestFun(action, params) {
    return function (err, res) {
        if (err && err.timeout === TIMEOUT) {
            dispatch(action, 'TIMEOUT', params);
        } else if (res.status === 400) {
            dispatch(action, 'LOGOUT', params);
        } else if (!res.ok) {
            dispatch(action, 'ERROR', params);
        } else {
            dispatch(action, res, params);
        }
    };
}

// a simple get request
function get(url) {
    return superagent
        .get(url)
        .set('Accept', 'application/json')
        .set('Accept-Encoding', 'gzip, deflate')
        .timeout(TIMEOUT)
        .query();
}

var Api = {
    getData: function(type, id, action, params) {
        var url = makeUrl(type, id);
        abortPendingRequests(url);
        _pendingRequests[url] = get(url).end(
            makeDigestFun(action, params)
        );
    }
};