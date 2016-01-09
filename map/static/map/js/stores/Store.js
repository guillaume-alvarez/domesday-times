function Store() {
    this._EE = new EventEmitter();
};

Store.prototype.addListener = function (listener) {
    this._EE.on('change', listener);
};
Store.prototype.removeListener = function (listener) {
    this._EE.on('change', listener);
};
Store.prototype.emitChange = function () {
    this._EE.emit('change');
};

