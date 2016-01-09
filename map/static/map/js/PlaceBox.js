/**
 * Displays the selected place information.
 */
var PlaceBox = React.createClass({
    componentDidMount: function() {
        PLACES_STORE.addListener(this.placeChanged);
    },
    componentWillUnmount: function() {
        PLACES_STORE.removeListener(this.placeChanged );
    },
    placeChanged: function() {
        // Since the places changed, trigger a new render.
        this.forceUpdate();
    },

    render: function() {
        var selected = PLACES_STORE.selected();
        if (selected) {
            return (
                <div className="placeBox">
                    <p>Selected place: {selected.fields.name}</p>
                </div>
            );
        } else {
            return (
                <div className="placeBox">
                    <p>Select a place on map...</p>
                </div>
            );
        }
    }
});
ReactDOM.render(
  <PlaceBox />,
  document.getElementById('place')
);