/**
 * Displays the selected place information.
 */
var PlaceBox = React.createClass({
    getInitialState: function() {
        return PLACES_STORE.selected();
    },
    componentDidMount: function() {
        PLACES_STORE.addListener(this.placeChanged);
    },
    componentWillUnmount: function() {
        PLACES_STORE.removeListener(this.placeChanged );
    },

    placeChanged: function() {
        this.setState(PLACES_STORE.selected());
    },

    render: function() {
        var selected = this.state;
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