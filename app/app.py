import os
import json
import subprocess
import streamlit as st
import pathlib

import pandas as pd

from ladybug.datacollection import HourlyContinuousCollection, \
    MonthlyCollection, DailyCollection
from ladybug.sql import SQLiteResult

from ladybug_charts.to_figure import heat_map


def serialize_data(data_dicts):
    """Reserialize a list of collection dictionaries."""
    if len(data_dicts) == 0:
        return []
    elif data_dicts[0]['type'] == 'HourlyContinuous':
        return [HourlyContinuousCollection.from_dict(data) for data in data_dicts]
    elif data_dicts[0]['type'] == 'Monthly':
        return [MonthlyCollection.from_dict(data) for data in data_dicts]
    elif data_dicts[0]['type'] == 'Daily':
        return [DailyCollection.from_dict(data) for data in data_dicts]


# upload sqlite file
sqlit_file = st.file_uploader(
    label='SQL output from EnergyPlus.', type='sql'
)

output_name = st.selectbox(
    'EnergyPlus Outputs',
    options=pathlib.Path(__file__).parent.joinpath('outputs.txt').read_text().splitlines()
)

if not sqlit_file:
    sqlit_file = pathlib.Path(__file__).parent.parent.joinpath('sample_data', 'output', 'eplusout.sql').as_posix()

# parse the output
if os.name == 'nt':  # we are on windows; use IronPython like usual
    sql_obj = SQLiteResult(sqlit_file)  # create the SQL result parsing object
    results = sql_obj.data_collections_by_output_name(output_name)

else:  # we are on Mac; sqlite3 module doesn't work in Mac IronPython
    # Execute the honybee CLI to obtain the results via CPython
    cmds = [folders.python_exe_path, '-m', 'honeybee_energy', 'result',
            'data-by-outputs', sqlit_file, output_name]
    process = subprocess.Popen(cmds, stdout=subprocess.PIPE)
    stdout = process.communicate()
    data_dicts = json.loads(stdout[0])
    results = serialize_data(data_dicts[0])

if not results:
    st.warning(f'Results for "{output_name}" is not available. Try a different output.')
    st.stop()

# generate a dataframe
# There will be a dataset for every zone from the type HourlyContinuousCollection
# I just run it for the first 3 to keep the app faster. We can add a dropdown to 
# filter the rooms that user is interested to visualize
for result in results[:3]:
    # print(result.header.metadata)
    try:
        # a system result
        st.write(result.header.metadata['System'])
    except KeyError:
        # this is a zone result
        st.write(result.header.metadata['Zone'])

    df = pd.DataFrame(result)
    
    # pass it to Andy!
    # Here is an example of using ladybug_charts
    fig = heat_map(result)
    st.plotly_chart(fig)
    # and here is another one using streamlit
    st.line_chart(df)

