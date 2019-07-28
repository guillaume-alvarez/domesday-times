/**
 * Contains the lords known to the system.
 */
function LordsStore () {
    Store.call(this);
    this._lords = {};
    this._selectedId = '';
};
LordsStore.prototype = Object.create(Store.prototype);
LordsStore.prototype.constructor = LordsStore;

LordsStore.prototype.selected = function () {
    if (this._selectedId) {
        return this._lords[this._selectedId];
    } else {
        return null;
    }
};

LordsStore.prototype.handle = function (event) {
    switch(event.actionType) {
        case Actions.ACTION_SELECT_LORD:
            LORDS_STORE._selectedId = event.id;
            if (!(LORDS_STORE._selectedId in LORDS_STORE._lords)) {
                Api.getData('lords', event.id, Actions.ACTION_GET_LORD, {});
                return true;
            }
            break;
        case Actions.ACTION_GET_LORD:
            console.log('Loaded lord ' + JSON.stringify(event.response, null, 4));
            LORDS_STORE._lords[event.response.id] = event.response;
            break;
        case Actions.ACTION_SELECT_PLACE:
            // do not apply for 'SELECT_SETTLEMENT': keeps the same lord
            LORDS_STORE._selectedId = undefined;
            break;
        default:
            return true;
    }
    LORDS_STORE.emitChange();
    return true;
};

var LORDS_STORE = new LordsStore();
AppDispatcher.register(LORDS_STORE.handle);