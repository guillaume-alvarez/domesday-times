var Actions = {
    ACTION_SELECT_PLACE: "ACTION_SELECT_PLACE",
    ACTION_LOAD_PLACE: "ACTION_LOAD_PLACE",
    ACTION_LOADED_PLACE: "ACTION_LOADED_PLACE",

  /**
   * @param  {string} id
   * @param  {object} place
   */
  selectPlace: function(id, place) {
    AppDispatcher.dispatch({
        actionType: this.ACTION_SELECT_PLACE,
        id: id,
        place: place,
    });
  },

  /**
   * @param  {string} id
   */
  loadPlace: function(id) {
    AppDispatcher.dispatch({
        actionType: this.ACTION_LOAD_PLACE,
        id: id
    });
  },

  /**
   * @param  {string} id
   * @param  {object} place
   */
  loadedPlace: function(id, place) {
    AppDispatcher.dispatch({
        actionType: ACTION_LOADED_PLACE,
        id: id,
        place: place
    });
  },

};