import dash
import base64
import json
import dash_core_components as dcc
from dash.dependencies import Output, Input, State
import dash_html_components as html
import dash_bootstrap_components as dbc
import numpy as np


class DataStorage:
    def __init__(self):
        with open('result_default.json', 'r') as f:
            self.data = json.load(f)


SEP = '-|||-'
NONSENSE = 'NONSENSE'
ds = DataStorage()
HARDCODED_CLUSTERS = ['Company / Brand',
                      'App experience',
                      'Logistics',
                      'Buying Experience',
                      'Support',
                      'Attributes',
                      'Value',
                      'Post-purchase',
                      'Payment',
                      'Account',
                      'Software issue / Bugs']

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css',
                        dbc.themes.BOOTSTRAP]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = 'Anecdote Labelling'

app.layout = dbc.Container([dbc.Row([dbc.Col([html.Img(src='/assets/logo.png', height='50px', style={'margin-top': '15px'})],
                                             md=3),
                                     dbc.Col(html.Div(id='error_line', style={'color': 'red', 'font-size': '12px',
                                                                              'margin-top': '15px', 'text-align': 'center'}),
                                             md=6),
                                     dbc.Col(dbc.Row(
                                             [dcc.Upload(id='file_upload',
                                                         children=[html.A('Select a File')],
                                                         style={'width': '100%', 'height': '38px', 'lineHeight': '38px',
                                                                'borderWidth': '1px', 'borderStyle': 'dashed',
                                                                'padding-left': '7px', 'padding-right': '7px',
                                                                'borderRadius': '5px', 'margin-top': '15px',
                                                                'textAlign': 'center'}),
                                             dbc.Button(id='save_btn',
                                                        children='Save',
                                                        style={'margin': '15px', 'float': 'right',
                                                               'background-color': 'white',
                                                               'color': '#6c757d'}),
                                              dcc.Download(id="download_text")
                                              ]),
                                             md=3)]),
                            html.Hr(),
                            dbc.Row([
                                    dbc.Col([dbc.Row(html.H5("Topic title", style={'margin-top': '15px'})),
                                             dbc.Row([dcc.Input(id='topic_name_input',
                                                                placeholder='Topic Name', type='text', value=ds.data[0]['title'],
                                                                style={'width': '35%'}),
                                                      html.Div(dcc.RadioItems(id='topic_name_candidates_ri',
                                                                              labelStyle={'display': 'block'}),
                                                               style={'width': '25%', 'margin-left': '15px'}),
                                                      html.Div(dcc.Dropdown(id='existing_topic_name_dd',
                                                                            style={'margin-left': '15px'},
                                                                            placeholder="Pick from existing"),
                                                               style={"width": "30%",
                                                                      "margin-left": '15px'}),
                                                      ]),
                                             html.Hr(),
                                             dbc.Row(html.H5("Cluster", style={'margin-top': '15px'})),
                                             dbc.Row([dcc.Input(id='cluster_name_input',
                                                                placeholder='Cluster Name',
                                                                type='text',
                                                                value='',
                                                                style={'width': '35%'}),
                                                      html.Div(dcc.Dropdown(id='existing_cluster_name_dd',
                                                                            style={'margin-left': '15px'},
                                                                            placeholder="Pick from existing"),
                                                               style={"width": "30%",
                                                                      "margin-left": '15px'}),
                                                      ]),
                                             html.Hr(),
                                             dbc.Row([html.Div([dcc.Dropdown(id='topic_id_dd',
                                                                             options=[{'label': i, 'value': i} for i in
                                                                                      range(len(ds.data))],
                                                                             value=0,
                                                                             placeholder="Topic #",
                                                                             style={'margin': '15px'})]),
                                                      dbc.Button(id='nonsense_btn', children='Nonsense', style={'margin': '15px'}),
                                                      dbc.Button(id='skip_btn', children='Skip', style={'margin': '15px'}),
                                                      dbc.Button(id='confirm_btn', children='Confirm & Next', style={'margin': '15px'}),
                                                      ],
                                                     style={'float': 'right'})
                                             ],
                                            md=8),
                                    dbc.Col(dcc.Checklist(id='message_examples_cl',
                                                          labelStyle={'display': 'block'}),
                                            style={'overflow-y': 'scroll',
                                                   'height': '850px'},
                                            md=4),
                                    ]),
                            html.Div(id='placeholder_1')
                            ])


@app.callback(Output(component_id='topic_id_dd', component_property='options'),
              Output(component_id='topic_id_dd', component_property='value'),
              Output(component_id='error_line', component_property='children'),
              Input('confirm_btn', 'n_clicks'),
              Input('nonsense_btn', 'n_clicks'),
              Input('skip_btn', 'n_clicks'),
              Input('file_upload', 'contents'),
              State(component_id='topic_id_dd', component_property='options'),
              State(component_id='topic_id_dd', component_property='value'),
              State('topic_name_input', 'value'),
              State('cluster_name_input', 'value'),
              State('message_examples_cl', 'value'),
              prevent_initial_call=True)
def update_dataset(_0, _1, _2, content, topics_id_options, topic_id_value, topic_name, cluster_name, selected_messages):
    trigger_id = dash.callback_context.triggered[0]["prop_id"].split(".")[0]
    selected_messages = [sm.split(SEP)[0] for sm in selected_messages]
    if trigger_id == 'file_upload':
        try:
            content_type, content_string = content.split(',')
            ds.data = json.loads(base64.b64decode(content_string))
            topics_id_options = [{'label': i, 'value': i} for i in range(len(ds.data))]
            return topics_id_options, 0, ''
        except Exception as e:
            print(str(e))
            return topics_id_options, topic_id_value, 'error while reading file'
    elif trigger_id == 'confirm_btn':
        ds.data[topic_id_value]['title'] = topic_name
        ds.data[topic_id_value]['cluster_name'] = cluster_name if cluster_name else ''
        ds.data[topic_id_value]['is_nonsense'] = 0
        for i in range(len(ds.data[topic_id_value]['messages'])):
            if ds.data[topic_id_value]['messages'][i] in selected_messages:
                ds.data[topic_id_value]['message_flags'][i] = 1
            else:
                ds.data[topic_id_value]['message_flags'][i] = 0

        return topics_id_options, (topic_id_value + 1) % len(ds.data), ''
    elif trigger_id == 'nonsense_btn':
        ds.data[topic_id_value]['cluster_name'] = NONSENSE
        ds.data[topic_id_value]['title'] = NONSENSE
        ds.data[topic_id_value]['is_nonsense'] = 1
        for i in range(len(ds.data[topic_id_value]['messages'])):
            ds.data[topic_id_value]['message_flags'][i] = 0
        return topics_id_options, (topic_id_value + 1) % len(ds.data), ''
    elif trigger_id == 'skip_btn':
        return topics_id_options, (topic_id_value + 1) % len(ds.data), ''

    return topics_id_options, topic_id_value, ''

@app.callback(
    Output("download_text", "data"),
    Input("save_btn", "n_clicks"),
    prevent_initial_call=True,
)
def save_data(_):
    from datetime import datetime
    name = datetime.now().strftime("%Y%m%d_%H%M%S")
    return dict(content=json.dumps(ds.data), filename=name + ".json")


@app.callback(Output(component_id='topic_name_input', component_property='value'),
              Output(component_id='topic_name_candidates_ri', component_property='options'),
              Output(component_id='topic_name_candidates_ri', component_property='value'),
              Output(component_id='existing_topic_name_dd', component_property='options'),
              Output(component_id='existing_topic_name_dd', component_property='value'),
              Output(component_id='message_examples_cl', component_property='options'),
              Output(component_id='message_examples_cl', component_property='value'),
              Output(component_id='cluster_name_input', component_property='value'),
              Output(component_id='existing_cluster_name_dd', component_property='options'),
              Output(component_id='existing_cluster_name_dd', component_property='value'),
              Input(component_id='topic_id_dd', component_property='value'),
              Input(component_id='topic_name_candidates_ri', component_property='value'),
              Input(component_id='existing_topic_name_dd', component_property='value'),
              Input(component_id='existing_cluster_name_dd', component_property='value'),
              State(component_id='topic_id_dd', component_property='value'),
              State(component_id='topic_name_input', component_property='value'),
              State(component_id='cluster_name_input', component_property='value'),
              )
def update_page(_, input_ri_value, existing_topic_name_value, existing_cluster_name, topic_id, current_topic_name, current_cluster_name):
    trigger_id = dash.callback_context.triggered[0]["prop_id"].split(".")[0]
    if topic_id is None:
        topic_id = 0
    all_topic_names = sorted(list(set([t['title'] for t in ds.data])))
    all_cluster_names = [t['cluster_name'] for t in ds.data if t != NONSENSE] + HARDCODED_CLUSTERS
    all_cluster_names = sorted(list(set(all_cluster_names)))
    candidates = ds.data[topic_id]['title_candidates']
    message_examples, message_checked = [], []
    for message, checked in zip(ds.data[topic_id]['original_messages'],
                                ds.data[topic_id]['message_flags']):
        r = str(np.random.rand())
        checked = bool(checked)
        message_examples.append({'label': message, 'value': message + SEP + r})
        if checked:
            message_checked.append(message + SEP + r)

    if trigger_id == 'topic_name_candidates_ri':
        title = input_ri_value
        cluster_name = existing_cluster_name
    elif trigger_id == 'existing_topic_name_dd':
        title = existing_topic_name_value
        cluster_name = current_cluster_name
    elif trigger_id == 'existing_cluster_name_dd':
        title = current_topic_name
        cluster_name = existing_cluster_name
    else: # trigger_id == 'topic_id_dd':
        title = ds.data[topic_id]['title']
        cluster_name = ds.data[topic_id]['cluster_name']

    return title, \
           [{'label': c, 'value': c} for c in candidates], None,\
           [{'label': c, 'value': c} for c in all_topic_names], [],\
           message_examples, message_checked,\
           cluster_name,\
           [{'label': c, 'value': c} for c in all_cluster_names], None#ds.data[topic_id]['cluster_name']


if __name__ == '__main__':
    app.run_server(host='0.0.0.0',
                   debug=True,
                   port=8765)
