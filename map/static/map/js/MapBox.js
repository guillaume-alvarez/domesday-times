/**
 * Embed and initialize the map created using pixi.
 */
var MapBox = React.createClass({
    componentDidMount: function() {
        AppDispatcher.register(this.handleEvent);
        this.setState({
            map: new PixiMap(this.refs.gameCanvas, 1366, 768),
        });
    },

    handleEvent: function(event) {
        switch(event.actionType) {
            case Actions.ACTION_SELECT_SETTLEMENT:
                this.state.map.selectPlace(event.settlement.place_name);
                return true;
            default:
                return true;
        }
    },
    handleSubmit: function(e) {
        e.preventDefault();
        place = this.state.map.selectPlace($("#searchPlaceText").val());
        if (place) {
            Actions.selectPlace(place.id);
        }
        return false;
    },
    render: function() {
        return (
            <div className="panel panel-default">
                <SearchTown onSubmit={this.handleSubmit} />
                <div className="map-canvas-container" ref="gameCanvas">
                </div>
            </div>
        );
    },
});

var SearchTown = React.createClass({
    componentDidMount: function() {
        $(function() {
            $("#searchPlaceText").autocomplete({
                source: "/api/search_places/",
                minLength: 3,
            });
        });
    },
    render: function() {
        return (
            <form id="searchPlace" onSubmit={this.props.onSubmit}>
                <div className="form-group">
                    <div className="input-group col-md-12">
                        <input id="searchPlaceText" type="text" className=" search-query form-control" placeholder="Search place..." />
                        <span className="input-group-btn">
                            <button className="btn btn-danger" type="submit">
                                <span className="glyphicon glyphicon-search"></span>
                            </button>
                        </span>
                    </div>
                </div>
            </form>
        );
    }
});

ReactDOM.render(
  <MapBox />,
  document.getElementById('map')
);