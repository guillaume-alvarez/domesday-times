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
        return (
            <div className="placeBox panel panel-default">
                <div className="panel-heading">
                    <h3 className="panel-title">Selected place</h3>
                </div>
                    <div className="panel-body">
                        <PlaceDesc place={this.state.selected} />
                    </div>
            </div>
        );
    }
});

var PlaceDesc = React.createClass({
    render: function() {
        var place = this.props.place;
        if (!place) {
            return (
                <div className="placeDesc">
                    <p>Select a place on map...</p>
                </div>
            );
        }

        return (
            <div className="placeDesc">
                <p>{place.name}</p>
                <ul>
                    <li>{place.county} County</li>
                    <li>Hundred of {place.hundred}</li>
                </ul>
            </div>
        );
    }
});

ReactDOM.render(
  <PlaceBox />,
  document.getElementById('place')
);