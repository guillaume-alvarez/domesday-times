/**
 * Displays the selected lord information.
 */
var LordBox = React.createClass({
    getInitialState: function() {
        return {selected: LORDS_STORE.selected()};
    },
    componentDidMount: function() {
        LORDS_STORE.addListener(this.lordChanged);
    },
    componentWillUnmount: function() {
        LORDS_STORE.removeListener(this.lordChanged);
    },

    lordChanged: function() {
        this.setState({selected: LORDS_STORE.selected()});
    },

    render: function() {
        lord = this.state.selected
        if (lord) {
            return (
                <div className="LordBox panel panel-default">
                    <div className="panel-heading">
                        <h3 className="panel-title">{lord.name}</h3>
                    </div>
                    <LordSettlementsList settlements={lord.settlement_set || []}/>
                </div>
            );
        } else {
            return (
                <div className="LordBox panel panel-default">
                    <div className="panel-heading">
                        <h3 className="panel-title">Select a lord in place...</h3>
                    </div>
                </div>
            );
        }
    }
});

var LordSettlementsList = React.createClass({
    render: function() {
        var subs = this.props.settlements.map(function(settlement){
            return (
                <li key={settlement.id} className="list-group-item">
                    <LordSettlement settlement={settlement} />
                </li>
            );
        });
        return (
            <ul className="lordSettlementsList list-group">
                {subs}
            </ul>
        );
    }
});

var LordSettlement = React.createClass({
    render: function() {
        var settlement = this.props.settlement;
        var lord = settlement.lord || settlement.overlord || settlement.head_of_manor;
        return (
            <p className="lordSettlement">
                {settlement.place_name}: {settlement.value}£
                <a target="_blank" href={'http://opendomesday.org/api/1.0/manor/'+settlement.data_id} className="pull-right">
                    <span className="glyphicon glyphicon-link" aria-hidden="true"></span>
                </a>
                <br />{settlement.population} {settlement.population_type.toLowerCase()}
            </p>
        );
    }
});

ReactDOM.render(
  <LordBox />,
  document.getElementById('lord')
);