/**
 * Displays the selected place information.
 */
var PlaceBox = React.createClass({
    getInitialState: function() {
        return {selected: PLACES_STORE.selected()};
    },
    componentDidMount: function() {
        PLACES_STORE.addListener(this.placeChanged);
    },
    componentWillUnmount: function() {
        PLACES_STORE.removeListener(this.placeChanged );
    },

    placeChanged: function() {
        this.setState({selected: PLACES_STORE.selected()});
    },

    render: function() {
        if (this.state.selected) {
            return (
                <div className="placeBox">
                    <p>Selected place: {this.state.selected.name}</p>
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