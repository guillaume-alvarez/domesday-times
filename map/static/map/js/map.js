/**
 * Embed and initialize the map created using pixi.
 */
var MapBox = React.createClass({
    componentDidMount: function() {
        map = new Map(this.refs.gameCanvas, 1366, 768);
    },
    render: function() {
        return (
            <div className="map-canvas-container" ref="gameCanvas">
            </div>
        );
    },
});
ReactDOM.render(
  <MapBox />,
  document.getElementById('map')
);