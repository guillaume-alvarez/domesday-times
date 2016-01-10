var Actions = {
    ACTION_SELECT_PLACE: "ACTION_SELECT_PLACE",
    ACTION_GET_PLACE: "ACTION_GET_PLACE",

  /**
   * @param  {string} id
   * @param  {object} place
   */
  selectPlace: function(id) {
    AppDispatcher.dispatch({
        actionType: this.ACTION_SELECT_PLACE,
        id: id,
    });
  },

};