var Actions = {
    ACTION_SELECT_PLACE: "ACTION_SELECT_PLACE",
    ACTION_GET_PLACE: "ACTION_GET_PLACE",
    ACTION_SELECT_LORD: "ACTION_SELECT_LORD",
    ACTION_GET_LORD: "ACTION_GET_LORD",
    ACTION_SELECT_SETTLEMENT: "ACTION_SELECT_SETTLEMENT",

  /**
   * @param  {string} id
   */
  selectPlace: function(id) {
    AppDispatcher.dispatch({
        actionType: this.ACTION_SELECT_PLACE,
        id: id,
    });
  },

  /**
   * @param  {string} id
   */
  selectLord: function(id) {
    AppDispatcher.dispatch({
        actionType: this.ACTION_SELECT_LORD,
        id: id,
    });
  },

  /**
   * @param  {object} settlement
   */
  selectSettlement: function(settlement) {
    console.log('Selected settlement ' + JSON.stringify(settlement, null, 4))
    AppDispatcher.dispatch({
        actionType: this.ACTION_SELECT_SETTLEMENT,
        settlement: settlement,
    });
  },

};