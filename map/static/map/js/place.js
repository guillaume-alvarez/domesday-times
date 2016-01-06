/**
 * Displays the selected place information.
 */
var PlaceBox = React.createClass({
  render: function() {
    return (
      <div className="placeBox">
        <p>Selected place:</p>
      </div>
    );
  }
});
ReactDOM.render(
  <PlaceBox />,
  document.getElementById('place')
);