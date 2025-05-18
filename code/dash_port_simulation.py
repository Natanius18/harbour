import dash
from dash import html, dcc, Output, Input, State
import plotly.graph_objs as go
import pandas as pd
import random
from enum import Enum
import math


class ShipClass(Enum):
    SMALL = {'name': 'Small', 'priority': 1, 'size_multiplier': 0.7}
    MEDIUM = {'name': 'Medium', 'priority': 2, 'size_multiplier': 1.0}
    LARGE = {'name': 'Large', 'priority': 3, 'size_multiplier': 1.3}

    @classmethod
    def get_properties(cls, class_name):
        return cls[class_name].value


app = dash.Dash(__name__)

# Initial simulation parameters
app.layout = html.Div([
    html.H2("Port System Model", style={'textAlign': 'center', 'marginTop': '10', 'marginBottom': '10px'}),
    html.Div([
        html.Div([
            html.Div([
                html.Label("Ship arrival rate (ships per hour):", style={'display': 'inline-block', 'width': '300px'}),
                dcc.Input(id='arrival_rate', type='number', min=1, max=100, step=1, value=20,
                          style={'width': '60px', 'display': 'inline-block'}),
            ], style={'marginBottom': '10px'}),
            html.Div([
                html.Label("Containers for small ships:", style={'display': 'inline-block', 'width': '300px'}),
                dcc.Input(id='containers_small', type='number', min=1, max=1000, step=1, value=500,
                          style={'width': '60px', 'display': 'inline-block'}),
            ], style={'marginBottom': '10px'}),
            html.Div([
                html.Label("Containers for medium ships:", style={'display': 'inline-block', 'width': '300px'}),
                dcc.Input(id='containers_medium', type='number', min=1, max=2000, step=1, value=2000,
                          style={'width': '60px', 'display': 'inline-block'}),
            ], style={'marginBottom': '10px'}),
            html.Div([
                html.Label("Containers for large ships:", style={'display': 'inline-block', 'width': '300px'}),
                dcc.Input(id='containers_large', type='number', min=1, max=30000, step=1, value=5000,
                          style={'width': '60px', 'display': 'inline-block'}),
            ], style={'marginBottom': '10px'}),
            html.Div([
                html.Label("Income per container ($):", style={'display': 'inline-block', 'width': '300px'}),
                dcc.Input(id='income_per_container', type='number', min=0.1, max=1000, step=0.1, value=10.0,
                          style={'width': '60px', 'display': 'inline-block'}),
            ], style={'marginBottom': '10px'}),
            html.Div([
                html.Label("Cost per container ($):", style={'display': 'inline-block', 'width': '300px'}),
                dcc.Input(id='cost_per_container', type='number', min=0, max=1000, step=0.1, value=2.0,
                          style={'width': '60px', 'display': 'inline-block'}),
            ], style={'marginBottom': '10px'}),
            html.Div([
                html.Label("Monthly maintenance cost ($):", style={'display': 'inline-block', 'width': '300px'}),
                dcc.Input(id='maintenance_cost', type='number', min=0, max=1000000, step=100, value=50000,
                          style={'width': '60px', 'display': 'inline-block'}),
            ], style={'marginBottom': '10px'}),
            html.Div([
                html.Label("Berth productivity (containers/hour):",
                           style={'display': 'inline-block', 'width': '300px'}),
                dcc.Input(id='berth_productivity', type='number', min=1, max=100000, step=1, value=3000,
                          style={'width': '60px', 'display': 'inline-block'}),
            ], style={'marginBottom': '10px'}),
            html.Div([
                html.Label("Pilotage time (minutes):", style={'display': 'inline-block', 'width': '300px'}),
                dcc.Input(id='pilotage_time', type='number', min=1, max=240, step=1, value=30,
                          style={'width': '60px', 'display': 'inline-block'}),
            ], style={'marginBottom': '10px'}),
            html.Div([
                html.Label("Mooring/Unmooring time (minutes):", style={'display': 'inline-block', 'width': '300px'}),
                dcc.Input(id='mooring_time', type='number', min=1, max=60, step=1, value=5,
                          style={'width': '60px', 'display': 'inline-block'}),
            ], style={'marginBottom': '10px'}),
            html.Div([
                html.Label("Number of berths:", style={'display': 'inline-block', 'width': '300px'}),
                dcc.Input(id='num_berths', type='number', min=1, max=60, step=1, value=3,
                          style={'width': '60px', 'display': 'inline-block'}),
            ], style={'marginBottom': '10px'}),
            html.Div([
                html.H4("Weather Conditions", style={'marginBottom': '7px', 'color': '#333'}),
                html.Div([
                    html.Div([
                        html.Label("Bad weather probability:",
                                   style={'display': 'inline-block', 'width': '200px', 'color': '#333'}),
                        dcc.Slider(
                            id='bad_weather_slider',
                            min=0,
                            max=100,
                            step=1,
                            value=10,
                            marks={i: f'{i}%' for i in range(0, 101, 10)},
                            tooltip={"placement": "bottom", "always_visible": True}
                        )
                    ], style={'marginBottom': '15px'}),
                    html.Div([
                        html.Label("Weather duration range (minutes):",
                                   style={'display': 'inline-block', 'color': '#333'}),
                        dcc.RangeSlider(
                            id='weather_duration_range',
                            min=10,
                            max=600,
                            step=10,
                            value=[10, 50],
                            marks={i: f'{i}' for i in range(0, 601, 60)},
                            tooltip={"placement": "bottom", "always_visible": True}
                        )
                    ], style={'marginBottom': '15px'}),
                ], style={'marginBottom': '15px'}),
            ], style={'marginBottom': '15px', 'backgroundColor': '#f5f6f7', 'borderRadius': '8px'}),
            html.Div([
                html.H4("Ship Class Distribution", style={'marginBottom': '7px', 'color': '#333'}),
                html.Div([
                    html.Div([
                        html.Label("Small Ships:",
                                   style={'display': 'inline-block', 'width': '100px', 'color': '#333'}),
                        dcc.Slider(
                            id='small_ships_slider',
                            min=0,
                            max=100,
                            step=1,
                            value=50,
                            marks={i: f'{i}%' for i in range(0, 101, 10)},
                            tooltip={"placement": "bottom", "always_visible": True}
                        )
                    ], style={'marginBottom': '15px'}),
                    html.Div([
                        html.Label("Medium Ships:",
                                   style={'display': 'inline-block', 'width': '100px', 'color': '#333'}),
                        dcc.Slider(
                            id='medium_ships_slider',
                            min=0,
                            max=100,
                            step=1,
                            value=30,
                            marks={i: f'{i}%' for i in range(0, 101, 10)},
                            tooltip={"placement": "bottom", "always_visible": True}
                        )
                    ], style={'marginBottom': '15px'}),
                    html.Div([
                        html.Label("Large Ships:",
                                   style={'display': 'inline-block', 'width': '100px', 'color': '#333'}),
                        dcc.Slider(
                            id='large_ships_slider',
                            min=0,
                            max=100,
                            step=1,
                            value=20,
                            marks={i: f'{i}%' for i in range(0, 101, 10)},
                            tooltip={"placement": "bottom", "always_visible": True}
                        )
                    ], style={'marginBottom': '15px'}),
                    html.Div(id='distribution_sum',
                             style={'textAlign': 'center', 'fontWeight': 'bold', 'marginTop': '10px'})
                ], style={'padding': '5px', 'backgroundColor': '#f5f6f7', 'borderRadius': '8px'})
            ], style={'marginBottom': '20px'}),
            html.Div([
                html.Label([
                    "Use ship class priority:",
                    dcc.Checklist(
                        id='use_priority',
                        options=[{'label': '', 'value': 'on'}],
                        value=['on'],
                        style={'display': 'inline-block'}
                    ),
                    html.Span("?", style={
                        'display': 'inline-block',
                        'marginLeft': '5px',
                        'cursor': 'pointer',
                        'backgroundColor': '#ccc',
                        'color': '#fff',
                        'borderRadius': '50%',
                        'width': '16px',
                        'height': '16px',
                        'textAlign': 'center',
                        'lineHeight': '16px',
                        'fontSize': '12px'
                    }, title="When enabled, larger ships are served first, followed by medium, and then small ships."),
                ], style={'display': 'inline-block', 'marginRight': '10px'}),
            ], style={'marginBottom': '10px'}),
            html.Div([
                html.Label("Simulation speed:", style={'display': 'block', 'marginBottom': '5px'}),
                dcc.Slider(id='sim_speed', min=1, max=10, step=1, value=1, marks={1: 'x1', 2: 'x2', 5: 'x5', 10: 'x10'},
                           tooltip={"placement": "bottom", "always_visible": False}, updatemode='drag'),
            ], style={'marginBottom': '10px'}),
            html.Div([
                html.Button('Start simulation', id='start_btn', n_clicks=0,
                            style={
                                'marginRight': '10px',
                                'backgroundColor': '#4CAF50',
                                'color': 'white',
                                'border': 'none',
                                'padding': '8px 16px',
                                'borderRadius': '4px',
                                'cursor': 'pointer',
                                'fontWeight': 'bold',
                                'boxShadow': '0 2px 4px rgba(0,0,0,0.2)',
                                'transition': 'all 0.3s ease'
                            }),
                html.Button('Stop simulation', id='stop_btn', n_clicks=0,
                            style={
                                'backgroundColor': '#f44336',
                                'color': 'white',
                                'border': 'none',
                                'padding': '8px 16px',
                                'borderRadius': '4px',
                                'cursor': 'pointer',
                                'fontWeight': 'bold',
                                'boxShadow': '0 2px 4px rgba(0,0,0,0.2)',
                                'transition': 'all 0.3s ease'
                            }),
            ], style={'textAlign': 'center', 'marginTop': '10px'}),
        ], style={
            'width': '400px',
            'boxShadow': '0 2px 8px rgba(0,0,0,0.08)',
            'padding': '10px',
            'borderRadius': '12px',
            'background': '#fafbfc',
            'marginRight': '30px',
            'flexShrink': 0,
        }),
        html.Div([
            dcc.Graph(id='port-graph', style={'height': '340px', 'margin': '0 auto'}),
            dcc.Graph(id='queue-graph', style={'height': '250px', 'margin': '0 auto'}),
            dcc.Graph(id='wait-time-graph', style={'height': '250px', 'margin': '0 auto'}),
            dcc.Graph(id='utilization-graph', style={'height': '250px', 'margin': '0 auto'}),
            dcc.Graph(id='income-graph', style={'height': '250px', 'margin': '0 auto'}),
            dcc.Interval(id='interval', interval=100, n_intervals=0, disabled=False),
            html.Div(id='status-text', style={'textAlign': 'center', 'marginTop': '100px', 'fontWeight': 'bold'}),
        ], style={
            'width': '1000px',
            'boxShadow': '0 2px 8px rgba(0,0,0,0.08)',
            'padding': '30px',
            'borderRadius': '12px',
            'background': '#fff',
        }),
    ], style={
        'display': 'flex',
        'flexDirection': 'row',
        'justifyContent': 'center',
        'alignItems': 'flex-start',
        'margin': '20px 0 0 0',
        'width': '100%',
    }),
], style={'background': '#f0f2f5', 'minHeight': '100vh', 'margin': '0', 'padding': '0'})


def get_initial_state():
    return {
        'minute': 0,
        'queue': [],
        'berths': [None] * 3,
        'moving_ships': [],
        'leaving_ships': [],
        'ship_id_counter': 1,
        'time_series': [],
        'queue_series': [],
        'wait_time_series': [],
        'berth_utilization': [],
        'total_income': 0,
        'income_series': [],
        'total_cost': 0,
        'cost_series': [],
        'profit_series': [],
        'financial_time_series': [],
        'running': False,
        'params': (2.0, 200, 500, 1000, 3000, 3, 30, 5, 10.0, 2.0),  # Added cost_per_container as last param
        # Updated: arrival_rate, containers_small, containers_medium, containers_large, 
        # berth_productivity, num_berths, pilotage_time, mooring_time, income_per_container, cost_per_container
        'class_distribution': {'SMALL': 0.5, 'MEDIUM': 0.3, 'LARGE': 0.2},
        'use_priority': True,
        'bad_weather_probability': 0.1,
        'is_bad_weather': False,
        'weather_duration': 0,
        'min_weather_duration': 10,
        'max_weather_duration': 50,
        'monthly_maintenance_cost': 50000.0,
        'last_maintenance_update': 0
    }


app.layout.children.append(dcc.Store(id='sim-state', data=get_initial_state()))


def get_random_ship_class(state):
    r = random.random()
    cumulative = 0
    for class_name, probability in state['class_distribution'].items():
        cumulative += probability
        if r <= cumulative:
            return class_name
    return 'MEDIUM'


@app.callback(
    Output('distribution_sum', 'children'),
    Output('distribution_sum', 'style'),
    Input('small_ships_slider', 'value'),
    Input('medium_ships_slider', 'value'),
    Input('large_ships_slider', 'value')
)
def update_distribution(small, medium, large):
    total = small + medium + large
    if total != 100:
        style = {'textAlign': 'center', 'fontWeight': 'bold', 'marginTop': '10px', 'color': '#f44336'}
        sum_text = f"Total: {total}% (should be 100%)"
    else:
        style = {'textAlign': 'center', 'fontWeight': 'bold', 'marginTop': '10px', 'color': '#4CAF50'}
        sum_text = f"Total: {total}%"
    return sum_text, style


@app.callback(
    Output('interval', 'disabled'),
    Output('sim-state', 'data'),
    Input('start_btn', 'n_clicks'),
    Input('stop_btn', 'n_clicks'),
    Input('arrival_rate', 'value'),
    Input('containers_small', 'value'),
    Input('containers_medium', 'value'),
    Input('containers_large', 'value'),
    Input('berth_productivity', 'value'),
    Input('pilotage_time', 'value'),
    Input('mooring_time', 'value'),
    Input('num_berths', 'value'),
    Input('sim_speed', 'value'),
    Input('use_priority', 'value'),
    Input('small_ships_slider', 'value'),
    Input('medium_ships_slider', 'value'),
    Input('large_ships_slider', 'value'),
    Input('bad_weather_slider', 'value'),
    Input('weather_duration_range', 'value'),
    Input('interval', 'n_intervals'),
    State('sim-state', 'data'),
    State('income_per_container', 'value'),
    State('cost_per_container', 'value'),
    prevent_initial_call=False
)
def control_and_step_simulation(n_clicks_start, n_clicks_stop, arrival_rate, containers_small, containers_medium,
                                containers_large, berth_productivity, pilotage_time, mooring_time, num_berths,
                                sim_speed, use_priority, small_percent, medium_percent, large_percent, bad_weather_prob,
                                weather_duration_range, n_intervals, state, income_per_container, cost_per_container):
    ctx = dash.callback_context
    if not ctx.triggered:
        return True, state

    trigger = ctx.triggered[0]['prop_id'].split('.')[0]

    if trigger == 'stop_btn':
        state['running'] = False
        return True, state

    if trigger == 'start_btn':
        state = get_initial_state()
        state['params'] = (
            arrival_rate, containers_small, containers_medium, containers_large, berth_productivity, num_berths,
            pilotage_time, mooring_time, income_per_container, cost_per_container)
        state['berths'] = [None] * int(num_berths)
        state['use_priority'] = bool(use_priority)
        state['class_distribution'] = {
            'SMALL': small_percent / 100,
            'MEDIUM': medium_percent / 100,
            'LARGE': large_percent / 100
        }
        state['bad_weather_probability'] = bad_weather_prob / 100
        state['min_weather_duration'] = weather_duration_range[0]
        state['max_weather_duration'] = weather_duration_range[1]
        state['running'] = True
        return False, state

    if (arrival_rate, containers_small, containers_medium, containers_large, berth_productivity, num_berths,
        pilotage_time, mooring_time, income_per_container, cost_per_container) != tuple(state['params']) or \
            state['use_priority'] != bool(use_priority) or \
            state['class_distribution'] != {'SMALL': small_percent / 100, 'MEDIUM': medium_percent / 100,
                                            'LARGE': large_percent / 100} or \
            state['bad_weather_probability'] != bad_weather_prob / 100 or \
            state['min_weather_duration'] != weather_duration_range[0] or \
            state['max_weather_duration'] != weather_duration_range[1]:
        state = get_initial_state()
        state['params'] = (
            arrival_rate, containers_small, containers_medium, containers_large, berth_productivity, num_berths,
            pilotage_time, mooring_time, income_per_container, cost_per_container)
        state['berths'] = [None] * int(num_berths)
        state['use_priority'] = bool(use_priority)
        state['class_distribution'] = {
            'SMALL': small_percent / 100,
            'MEDIUM': medium_percent / 100,
            'LARGE': large_percent / 100
        }
        state['bad_weather_probability'] = bad_weather_prob / 100
        state['min_weather_duration'] = weather_duration_range[0]
        state['max_weather_duration'] = weather_duration_range[1]
        state['running'] = False
        return True, state

    if trigger == 'interval' and state.get('running', False):
        t = state['minute']
        queue = state['queue']
        berths = state['berths']
        moving_ships = state.get('moving_ships', [])
        leaving_ships = state.get('leaving_ships', [])
        ship_id_counter = state['ship_id_counter']
        arrival_prob = arrival_rate / 60

        for _ in range(sim_speed):
            # Weather simulation
            if state['weather_duration'] <= 0:
                if random.random() < state['bad_weather_probability']:
                    state['is_bad_weather'] = True
                    state['weather_duration'] = random.randint(state['min_weather_duration'],
                                                               state['max_weather_duration'])
                else:
                    state['is_bad_weather'] = False
                    state['weather_duration'] = random.randint(state['min_weather_duration'],
                                                               state['max_weather_duration'])
            else:
                state['weather_duration'] -= 1

            # Ship arrival
            if random.random() < arrival_prob:
                ship_class = get_random_ship_class(state)
                queue.append({
                    'id': ship_id_counter,
                    'class': ship_class,
                    'arrival_time': t
                })
                ship_id_counter += 1

            # Animate moving ships (to berth) with pilotage
            new_moving_ships = []
            for mship in moving_ships:
                if mship['state'] == 'pilotage':
                    mship['time_left'] -= 1
                    if mship['time_left'] > 0:
                        mship['progress'] = 1.0 - (mship['time_left'] / pilotage_time)
                        new_moving_ships.append(mship)
                    else:
                        idx = mship['target_berth']
                        berths[idx] = {
                            'id': mship['id'],
                            'state': 'mooring',
                            'time_left': mooring_time,
                            'class': mship['class']
                        }
            moving_ships = new_moving_ships

            # Animate leaving ships
            new_leaving_ships = []
            for lship in leaving_ships:
                lship['progress'] += 0.12
                if lship['progress'] < 1.0:
                    new_leaving_ships.append(lship)
            leaving_ships = new_leaving_ships

            # Process berths
            for i in range(int(num_berths)):
                if berths[i] is not None and not state['is_bad_weather']:
                    berths[i]['time_left'] -= 1
                    if berths[i]['time_left'] <= 0:
                        if berths[i]['state'] == 'mooring':
                            berths[i]['state'] = 'service'
                            # Calculate service time based on containers and berth productivity
                            containers = {
                                'SMALL': containers_small,
                                'MEDIUM': containers_medium,
                                'LARGE': containers_large
                            }[berths[i]['class']]
                            total_processing_time = (containers / berth_productivity) * 60  # Convert hours to minutes
                            berths[i]['time_left'] = total_processing_time
                            berths[i]['containers_processed'] = 0
                            berths[i]['total_containers'] = containers
                            berths[i]['containers_per_minute'] = containers / total_processing_time
                            berths[i]['last_income_update'] = 0
                        elif berths[i]['state'] == 'service':
                            # Calculate continuous income during service
                            current_minute = state['minute']
                            if 'last_income_update' in berths[i]:
                                time_since_last_update = current_minute - berths[i]['last_income_update']
                                if time_since_last_update > 0:
                                    containers_processed = time_since_last_update * berths[i]['containers_per_minute']
                                    containers_processed = min(containers_processed, berths[i]['total_containers'] - berths[i]['containers_processed'])
                                    if containers_processed > 0:
                                        # Calculate income and cost for processed containers
                                        income = containers_processed * income_per_container
                                        cost = containers_processed * cost_per_container
                                        state['total_income'] = state.get('total_income', 0) + income
                                        state['total_cost'] = state.get('total_cost', 0) + cost
                                        berths[i]['containers_processed'] += containers_processed
                                        berths[i]['last_income_update'] = current_minute
                            berths[i]['state'] = 'unmooring'
                            berths[i]['time_left'] = mooring_time
                        elif berths[i]['state'] == 'unmooring':
                            ship = berths[i]
                            from_x = (int(num_berths) - 1 - i) * 2 + 0.25
                            to_x = from_x + 4.0
                            from_y = 1.25
                            to_y = 1.25 + 2.5
                            leaving_ships.append({
                                'id': ship['id'],
                                'from_x': from_x,
                                'to_x': to_x,
                                'from_y': from_y,
                                'to_y': to_y,
                                'progress': 0.0,
                                'class': ship['class']
                            })
                            berths[i] = None

                # Move ships from queue to free berths with pilotage
                if (berths[i] is None and not any(m['target_berth'] == i for m in moving_ships)) and queue and not \
                        state['is_bad_weather']:
                    if state['use_priority']:
                        queue.sort(key=lambda x: ShipClass.get_properties(x['class'])['priority'], reverse=True)
                    ship = queue.pop(0)
                    from_x = -1.5
                    to_x = (int(num_berths) - 1 - i) * 2 + 0.25
                    moving_ships.append({
                        'id': ship['id'],
                        'from_x': from_x,
                        'to_x': to_x,
                        'progress': 0.0,
                        'target_berth': i,
                        'class': ship['class'],
                        'state': 'pilotage',
                        'time_left': pilotage_time
                    })

        # Update metrics
        if 'time_series' not in state:
            state['time_series'] = []
            state['queue_series'] = []
            state['wait_time_series'] = []
            state['berth_utilization'] = []

        avg_wait = sum(t - ship['arrival_time'] for ship in queue) / len(queue) if queue else 0
        occupied_berths = sum(1 for b in berths if b is not None)
        utilization = occupied_berths / len(berths)

        state['time_series'].append(t)
        state['queue_series'].append(len(queue))
        state['wait_time_series'].append(avg_wait)
        state['berth_utilization'].append(utilization)
        # Initialize financial series if they don't exist
        if 'income_series' not in state:
            state['income_series'] = []
            state['cost_series'] = []
            state['profit_series'] = []
            state['financial_time_series'] = []
        
        # Always update financial metrics at each time step for accurate time tracking
        current_income = state.get('total_income', 0)
        current_cost = state.get('total_cost', 0)
        
        # Add maintenance cost every 60 minutes
        if state['minute'] - state.get('last_maintenance_update', 0) >= 60:
            maintenance_cost = state.get('monthly_maintenance_cost', 50000.0)
            maintenance_per_minute = maintenance_cost / 60  # Monthly cost divided by 60*24*30 minutes
            state['total_cost'] += maintenance_per_minute * 60  # Add cost for last hour
            state['last_maintenance_update'] = state['minute']
            current_cost = state.get('total_cost', 0)
        
        current_profit = current_income - current_cost
        
        # Always append new data point with current time
        state['financial_time_series'].append(t)
        state['income_series'].append(current_income)
        state['cost_series'].append(current_cost)
        state['profit_series'].append(current_profit)
        state['minute'] = t + sim_speed
        state['queue'] = queue
        state['berths'] = berths
        state['moving_ships'] = moving_ships
        state['leaving_ships'] = leaving_ships
        state['ship_id_counter'] = ship_id_counter

        if state['minute'] >= 500:
            state['running'] = False
            return True, state

        return False, state

    return state.get('running', False), state


@app.callback(
    Output('port-graph', 'figure'),
    Output('queue-graph', 'figure'),
    Output('wait-time-graph', 'figure'),
    Output('utilization-graph', 'figure'),
    Output('income-graph', 'figure'),
    Output('status-text', 'children'),
    Input('sim-state', 'data'),
    State('num_berths', 'value'),
    State('containers_small', 'value'),
    State('containers_medium', 'value'),
    State('containers_large', 'value'),
    State('berth_productivity', 'value'),
    State('income_per_container', 'value'),
    State('cost_per_container', 'value')
)
def update_graphs(state, num_berths, containers_small, containers_medium, containers_large, berth_productivity, income_per_container, cost_per_container):
    queue = state['queue']
    berths = state['berths']
    moving_ships = state.get('moving_ships', [])
    leaving_ships = state.get('leaving_ships', [])
    ship_width = 1.0
    ship_height = 0.8
    berth_width = 1.5
    berth_height = 1.2
    max_queue_in_row = 8
    port_shapes = []
    port_annotations = []

    water_y0 = 0
    water_y1 = 2.7 + 1.2
    water_x0 = -max_queue_in_row * 1.5 - 2
    water_x1 = int(num_berths) * 2 + 7

    port_shapes.append(
        dict(type='rect', x0=water_x0, y0=water_y0, x1=water_x1, y1=water_y1, fillcolor='#4fc3f7', line=dict(width=0)))
    port_shapes.append(
        dict(type='rect', x0=water_x0 - 0.5, y0=0.15 - 0.5, x1=water_x1 + 0.5, y1=0.15 + 0.5, fillcolor='#ffe0b2',
             line=dict(width=0), layer='below'))
    for i in range(8):
        y = water_y0 + (water_y1 - water_y0) * (i + 1) / 10
        port_shapes.append(dict(type='line', x0=water_x0 + 0.5, y0=y, x1=water_x1 - 0.5, y1=y,
                                line=dict(color='#81d4fa', width=1, dash='dot')))

    def add_ship_shape(port_shapes, x, y, ship_class_name, ship_id=None, state='queue'):
        ship_props = ShipClass.get_properties(ship_class_name)
        size_multiplier = ship_props['size_multiplier']
        color = {'queue': 'red', 'berth': 'orange', 'leaving': 'green'}.get(state, 'blue')
        ship_width = 1.0 * size_multiplier
        ship_height = 0.8 * size_multiplier
        x_offset = (1.0 - ship_width) / 2
        y_offset = (0.8 - ship_height) / 2

        hull_points = [
            [x + x_offset + 0.15 * size_multiplier, y + y_offset + 0.45 * size_multiplier],
            [x + x_offset + 0.25 * size_multiplier, y + y_offset + 0.25 * size_multiplier],
            [x + x_offset + 0.75 * size_multiplier, y + y_offset + 0.25 * size_multiplier],
            [x + x_offset + 0.85 * size_multiplier, y + y_offset + 0.45 * size_multiplier],
            [x + x_offset + 0.7 * size_multiplier, y + y_offset + 0.65 * size_multiplier],
            [x + x_offset + 0.3 * size_multiplier, y + y_offset + 0.65 * size_multiplier],
        ]
        bow_arc = f'M {x + x_offset + 0.25 * size_multiplier},{y + y_offset + 0.25 * size_multiplier} Q {x + x_offset + 0.5 * size_multiplier},{y + y_offset + 0.1 * size_multiplier} {x + x_offset + 0.75 * size_multiplier},{y + y_offset + 0.25 * size_multiplier}'
        hull_path = 'M ' + ' L '.join(f'{px},{py}' for px, py in hull_points) + ' Z ' + bow_arc
        port_shapes.append(
            dict(type='path', path=hull_path, fillcolor=color, line=dict(width=1, color='#222'), layer='above'))

        port_shapes.append(
            dict(type='rect', x0=x + x_offset + 0.38 * size_multiplier, y0=y + y_offset + 0.5 * size_multiplier,
                 x1=x + x_offset + 0.62 * size_multiplier, y1=y + y_offset + 0.62 * size_multiplier, fillcolor='white',
                 line=dict(width=0), layer='above'))
        port_shapes.append(
            dict(type='line', x0=x + x_offset + 0.5 * size_multiplier, y0=y + y_offset + 0.62 * size_multiplier,
                 x1=x + x_offset + 0.5 * size_multiplier, y1=y + y_offset + 0.8 * size_multiplier,
                 line=dict(color='#ffd600', width=2), layer='above'))
        port_shapes.append(dict(type='circle', xref='x', yref='y', x0=x + x_offset + 0.58 * size_multiplier,
                                y0=y + y_offset + 0.54 * size_multiplier,
                                x1=x + x_offset + 0.62 * size_multiplier, y1=y + y_offset + 0.58 * size_multiplier,
                                fillcolor='#1976d2', line=dict(width=0), layer='above'))

    for idx, ship in enumerate(queue):
        row = idx // max_queue_in_row
        col = idx % max_queue_in_row
        x0 = -(col + 1) * 1.5
        y0 = 1.25 + row * 1.1
        add_ship_shape(port_shapes, x0, y0, ship['class'], ship_id=ship['id'], state='queue')
        port_annotations.append(dict(x=x0 + 0.5, y=y0 + 0.4, text=str(ship['id']), showarrow=False,
                                     font=dict(color='white', size=12, family='Arial Black')))

    for i in range(int(num_berths)):
        x = (int(num_berths) - 1 - i) * 2
        port_shapes.append(dict(type='rect', x0=x, y0=0, x1=x + berth_width, y1=berth_height, fillcolor='#b0bec5',
                                line=dict(width=2, color='#78909c'), layer='above'))
        port_shapes.append(
            dict(type='rect', x0=x, y0=berth_height - 0.15, x1=x + berth_width, y1=berth_height, fillcolor='#78909c',
                 line=dict(width=0), layer='above'))

        if berths[i] is None:
            port_shapes.append(
                dict(type='rect', x0=x, y0=0, x1=x + berth_width, y1=berth_height, fillcolor='rgba(200, 200, 200, 0.3)',
                     line=dict(width=0), layer='above'))
            port_annotations.append(dict(x=x + berth_width / 2, y=berth_height / 2, text="FREE", showarrow=False,
                                         font=dict(size=12, color='red', family='Arial', weight='bold')))

    for i in range(int(num_berths)):
        x = (int(num_berths) - 1 - i) * 2
        ship = berths[i]
        if ship is not None:
            add_ship_shape(port_shapes, x + (berth_width - ship_width) / 2, 1.25, ship['class'], ship_id=ship['id'],
                           state='berth')
            port_annotations.append(dict(x=x + berth_width / 2, y=1.25 + 0.4, text=str(ship['id']), showarrow=False,
                                         font=dict(color='white', size=12, family='Arial Black')))

            operation_text = {'mooring': 'Mooring', 'service': 'Service', 'unmooring': 'Unmooring'}.get(ship['state'],
                                                                                                        '')
            port_annotations.append(
                dict(x=x + berth_width / 2, y=berth_height / 2, text=operation_text, showarrow=False,
                     font=dict(size=10, color='#000', family='Arial', weight='bold')))

            # Calculate total time dynamically for progress bar
            total_time = {
                'mooring': state['params'][6],  # mooring_time
                'service': ({
                                'SMALL': containers_small,
                                'MEDIUM': containers_medium,
                                'LARGE': containers_large
                            }[ship['class']] / berth_productivity) * 60,  # service time in minutes
                'unmooring': state['params'][6]  # mooring_time
            }[ship['state']]
            progress = 1.0 - (ship['time_left'] / total_time)
            bar_x0 = x + (berth_width - ship_width) / 2
            bar_x1 = bar_x0 + ship_width
            bar_y0 = 0.05
            bar_y1 = 0.2
            port_shapes.append(
                dict(type='rect', x0=bar_x0, y0=bar_y0, x1=bar_x1, y1=bar_y1, fillcolor='#e0e0e0', line=dict(width=0),
                     layer='above'))
            port_shapes.append(dict(type='rect', x0=bar_x0, y0=bar_y0, x1=bar_x0 + progress * ship_width, y1=bar_y1,
                                    fillcolor='#26d104', line=dict(width=0), layer='above'))

    for mship in moving_ships:
        x = mship['from_x'] + (mship['to_x'] - mship['from_x']) * min(1.0, mship['progress'])
        y = 1.25
        add_ship_shape(port_shapes, x, y, mship['class'], ship_id=mship['id'], state='berth')
        port_annotations.append(dict(x=x + 0.5, y=y + 0.4, text=str(mship['id']), showarrow=False,
                                     font=dict(color='white', size=12, family='Arial Black')))
        if mship['state'] == 'pilotage':
            port_annotations.append(dict(x=x + 0.5, y=y + 1.0, text="Pilotage", showarrow=False,
                                         font=dict(size=10, color='#000', family='Arial', weight='bold')))

    for lship in leaving_ships:
        x = lship['from_x'] + (lship['to_x'] - lship['from_x']) * min(1.0, lship['progress'])
        y = lship.get('from_y', 1.25) + (lship.get('to_y', 1.25) - lship.get('from_y', 1.25)) * min(1.0,
                                                                                                    lship['progress'])
        add_ship_shape(port_shapes, x, y, lship['class'], ship_id=lship['id'], state='leaving')
        port_annotations.append(dict(x=x + 0.5, y=y + 0.4, text=str(lship['id']), showarrow=False,
                                     font=dict(color='white', size=12, family='Arial Black')))

    if state.get('is_bad_weather', False):
        def generate_cloud_path(x0, y0, x1, y1, steps=8):
            width = x1 - x0
            height = y1 - y0
            step = width / steps
            mid_y = (y0 + y1) / 2
            amp = height * 0.2
            points_bottom = []
            for i in range(steps + 1):
                x = x0 + i * step
                y = mid_y + (amp if i % 2 == 0 else -amp)
                points_bottom.append(f"Q{x - step / 2},{y} {x},{mid_y}")
            path_bottom = " ".join(points_bottom)
            path = f"M{x0},{mid_y} {path_bottom} L{x1},{y0} L{x0},{y0} Z"
            return path

        port_shapes.append(dict(type="path", path=generate_cloud_path(water_x0, water_y0, water_x1, water_y1),
                                fillcolor='rgba(255, 255, 255, 0.5)', line=dict(width=0), layer='above'))
        warning_x = int(num_berths) * 2 + 2
        warning_y = 3.5
        opacity = (1.01 + math.sin(state['minute'])) / 2
        port_shapes.append(dict(type='path',
                                path=f'M {warning_x},{warning_y + 1.5} L {warning_x + 1.5},{warning_y} L {warning_x - 1.5},{warning_y} Z',
                                fillcolor=f'rgba(255, 152, 0, {opacity})',
                                line=dict(width=3, color=f'rgba(0, 0, 0, {opacity})'), layer='above'))
        port_annotations.append(dict(x=warning_x, y=warning_y + 0.5, text="!", showarrow=False,
                                     font=dict(size=30, color=f'rgba(255, 255, 255, {opacity})', family='Arial Black')))
        port_annotations.append(dict(x=warning_x, y=warning_y - 0.5, text="Bad Weather", showarrow=False,
                                     font=dict(size=20, color=f'rgba(255, 0, 0, {opacity})', family='Arial')))

    port_fig = go.Figure()
    port_fig.update_layout(
        shapes=port_shapes,
        annotations=port_annotations,
        xaxis=dict(range=[-max_queue_in_row * 1.5 - 1, int(num_berths) * 2 + 6], showgrid=False, zeroline=False,
                   visible=False, showline=False),
        yaxis=dict(range=[-1.5, 5], showgrid=False, zeroline=False, visible=False, showline=False),
        height=440,
        margin=dict(l=10, r=10, t=10, b=10),
        plot_bgcolor='#4fc3f7',
        paper_bgcolor='#4fc3f7',
    )

    # Ensure all series have the same length for queue DataFrame
    min_length = min(len(state['time_series']), len(state['queue_series']))
    time_series = state['time_series'][:min_length]
    queue_series = state['queue_series'][:min_length]
    
    df = pd.DataFrame({
        'Time (minutes)': time_series,
        'Queue length': queue_series
    })
    queue_fig = go.Figure(data=[
        go.Scatter(x=df['Time (minutes)'], y=df['Queue length'], mode='lines', name='Queue length')
    ])
    queue_fig.update_layout(
        title='Queue Length Over Time',
        xaxis_title='Time (minutes)',
        yaxis_title='Number of ships',
        height=250,
        margin=dict(l=40, r=40, t=40, b=40),
        plot_bgcolor='white',
    )

    # Ensure all series have the same length for metrics DataFrame
    min_metrics_length = min(
        len(state['time_series']), 
        len(state['wait_time_series']), 
        len(state['berth_utilization'])
    )
    time_metrics = state['time_series'][:min_metrics_length]
    wait_times = state['wait_time_series'][:min_metrics_length]
    utilizations = state['berth_utilization'][:min_metrics_length]
    
    metrics_df = pd.DataFrame({
        'Time (minutes)': time_metrics,
        'Average Wait Time': wait_times,
        'Berth Utilization': utilizations
    })

    wait_time_fig = go.Figure(data=[
        go.Scatter(x=metrics_df['Time (minutes)'], y=metrics_df['Average Wait Time'], mode='lines',
                   name='Avg Wait Time', line=dict(color='#ff6b6b', width=2))
    ])
    wait_time_fig.update_layout(
        title='Average Wait Time',
        xaxis_title='Time (minutes)',
        yaxis_title='Wait Time (minutes)',
        height=250,
        margin=dict(l=40, r=40, t=40, b=40),
        plot_bgcolor='white',
    )

    utilization_fig = go.Figure(data=[
        go.Scatter(x=metrics_df['Time (minutes)'], y=metrics_df['Berth Utilization'], mode='lines',
                   name='Berth Utilization', line=dict(color='#4CAF50', width=2))
    ])
    utilization_fig.update_layout(
        title='Berth Utilization',
        xaxis_title='Time (minutes)',
        yaxis_title='Utilization',
        height=250,
        margin=dict(l=40, r=40, t=40, b=40),
        plot_bgcolor='white',
        yaxis=dict(range=[0, 1], tickformat='.0%')
    )

    # Get current queue and berths
    queue = state.get('queue', [])
    berths = state.get('berths', [None] * 3)
    
    # Calculate common metrics
    max_queue = max(state['queue_series']) if state['queue_series'] else 0
    avg_queue = sum(state['queue_series']) / len(state['queue_series']) if state['queue_series'] else 0
    avg_wait = sum(state['wait_time_series']) / len(state['wait_time_series']) if state['wait_time_series'] else 0
    avg_util = sum(state['berth_utilization']) / len(state['berth_utilization']) if state['berth_utilization'] else 0
    total_income = state.get('total_income', 0)
    total_cost = state.get('total_cost', 0)
    total_profit = total_income - total_cost
    profit_margin = (total_profit / total_income * 100) if total_income > 0 else 0
    
    if state['minute'] >= 500 or not state.get('running', True):
        # Show detailed statistics when simulation is finished
        status = [
            html.Div([
                html.H4("Simulation Results (500 minutes)", style={'color': '#1976D2', 'margin-bottom': '10px'}),
                html.Div([
                    html.Div([
                        html.Div("Queue Statistics:", style={'font-weight': 'bold'}),
                        html.Div(f"• Maximum queue length: {max_queue} ships"),
                        html.Div(f"• Average queue length: {avg_queue:.1f} ships"),
                        html.Div(f"• Average waiting time: {avg_wait:.1f} minutes"),
                    ], style={'margin-bottom': '15px'}),
                    
                    html.Div([
                        html.Div("Berth Utilization:", style={'font-weight': 'bold'}),
                        html.Div(f"• Average utilization: {avg_util:.1%}"),
                    ], style={'margin-bottom': '15px'}),
                    
                    html.Div([
                        html.Div("Financial Summary:", style={'font-weight': 'bold'}),
                        html.Div(f"• Total Income: ${total_income:,.2f}"),
                        html.Div(f"• Container Costs: ${total_cost - state.get('monthly_maintenance_cost', 0):,.2f}"),
                        html.Div(f"• Maintenance Costs: ${state.get('monthly_maintenance_cost', 0):,.2f}"),
                        html.Div([
                            "• ",
                            html.Span(f"Profit: ${total_profit:,.2f} ({profit_margin:+.1f}%)", 
                                    style={'color': 'green' if total_profit >= 0 else 'red', 
                                          'font-weight': 'bold'})
                        ]),
                    ]),
                ], style={'background-color': '#f5f5f5', 'padding': '15px', 'border-radius': '5px'})
            ])
        ]
    else:
        # Show running status during simulation
        current_queue = len(queue)
        occupied_berths = sum(1 for b in berths if b is not None)
        status = [
            html.Div([
                html.H4(f"Time: {state['minute']} min | " \
                f"Queue: {current_queue} ship{'s' if current_queue != 1 else ''} | " \
                f"Occupied berths: {occupied_berths}/{len(berths)} | " \
                f"Profit: ${total_profit:,.2f} ({profit_margin:+.1f}%)", style={'color': '#1976D2', 'margin-bottom': '10px'})
            ])
        ]

    # Create financial metrics graph
    # Use the dedicated financial time series for financial metrics
    min_length = min(
        len(state.get('financial_time_series', [])), 
        len(state.get('income_series', [])), 
        len(state.get('cost_series', [])),
        len(state.get('profit_series', []))
    )
    time_series = state.get('financial_time_series', [])[:min_length]
    income_series = state.get('income_series', [])[:min_length]
    cost_series = state.get('cost_series', [])[:min_length]
    profit_series = state.get('profit_series', [])[:min_length]
    
    financial_df = pd.DataFrame({
        'Time (minutes)': time_series,
        'Income ($)': income_series,
        'Costs ($)': cost_series,
        'Profit ($)': profit_series
    })
    
    financial_fig = go.Figure()
    
    # Add income trace
    financial_fig.add_trace(go.Scatter(
        x=financial_df['Time (minutes)'],
        y=financial_df['Income ($)'],
        mode='lines',
        name='Income',
        line=dict(color='#4CAF50', width=2)  # Green for income
    ))
    
    # Add costs trace
    financial_fig.add_trace(go.Scatter(
        x=financial_df['Time (minutes)'],
        y=financial_df['Costs ($)'],
        mode='lines',
        name='Costs',
        line=dict(color='#F44336', width=2)  # Red for costs
    ))
    
    # Add profit trace
    financial_fig.add_trace(go.Scatter(
        x=financial_df['Time (minutes)'],
        y=financial_df['Profit ($)'],
        mode='lines',
        name='Profit',
        line=dict(color='#2196F3', width=3, dash='dash')  # Blue dashed for profit
    ))
    
    financial_fig.update_layout(
        title='Financial Metrics Over Time',
        xaxis_title='Time (minutes)',
        yaxis_title='Amount ($)',
        height=300,
        margin=dict(l=40, r=40, t=40, b=40),
        plot_bgcolor='white',
        yaxis=dict(tickprefix='$', tickformat=',.0f'),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
    )

    return port_fig, queue_fig, wait_time_fig, utilization_fig, financial_fig, status


@app.callback(
    Output('start_btn', 'disabled'),
    Output('start_btn', 'style'),
    Input('small_ships_slider', 'value'),
    Input('medium_ships_slider', 'value'),
    Input('large_ships_slider', 'value')
)
def update_start_button(small, medium, large):
    total = small + medium + large
    if total != 100:
        style = {
            'marginRight': '10px',
            'backgroundColor': '#cccccc',
            'color': '#666666',
            'border': 'none',
            'padding': '8px 16px',
            'borderRadius': '4px',
            'cursor': 'not-allowed',
            'fontWeight': 'bold',
            'boxShadow': '0 2px 4px rgba(0,0,0,0.2)',
            'transition': 'all 0.3s ease'
        }
        return True, style
    else:
        style = {
            'marginRight': '10px',
            'backgroundColor': '#4CAF50',
            'color': 'white',
            'border': 'none',
            'padding': '8px 16px',
            'borderRadius': '4px',
            'cursor': 'pointer',
            'fontWeight': 'bold',
            'boxShadow': '0 2px 4px rgba(0,0,0,0.2)',
            'transition': 'all 0.3s ease'
        }
        return False, style


if __name__ == '__main__':
    app.run(debug=True)
