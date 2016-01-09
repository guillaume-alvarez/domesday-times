/**
 * Contains the places known to the system.
 */
function PlacesStore () {
    Store.call(this);
    this._places = {};
    this._selectedId = '';
};
PlacesStore.prototype = Object.create(Store.prototype);
PlacesStore.prototype.constructor = PlacesStore;

PlacesStore.prototype.selected = function () {
    if (this._selectedId) {
        return this._places[this._selectedId];
    } else {
        return null;
    }
};

PlacesStore.prototype.handle = function (event) {
    switch(event.actionType) {
        case Actions.ACTION_SELECT_PLACE:
            PLACES_STORE._selectedId = event.id;
            if (!(PLACES_STORE._selectedId in PLACES_STORE._places)) {
                PLACES_STORE._places[event.id] = event.place;
            }
            break;
        case Actions.ACTION_LOADED_PLACE:
            PLACES_STORE._places[event.id] = event.place;
            break;
        default:
            return true;
    }
    PLACES_STORE.emitChange();
    return true;
};

var PLACES_STORE = new PlacesStore();
AppDispatcher.register(PLACES_STORE.handle);