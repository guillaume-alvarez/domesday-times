var Actions = {
    ACTION_SELECT_PLACE: "ACTION_SELECT_PLACE",
    ACTION_GET_PLACE: "ACTION_GET_PLACE",
    ACTION_SELECT_LORD: "ACTION_SELECT_LORD",
    ACTION_GET_LORD: "ACTION_GET_LORD",

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

  /**
   * @param  {string} id
   * @param  {object} lord
   */
  selectLord: function(id) {
    AppDispatcher.dispatch({
        actionType: this.ACTION_SELECT_LORD,
        id: id,
    });
  },

};