import streamlit as st
import pandas as pd 

st.write("hello world ")
st.button(label="Generate Isochrone")


# session state example - stores values over reruns which dont get 'reset' 
if 'x' in st.session_state:
    st.session_state.x

df = pd.DataFrame({
    'first column': [1,2,3,4],
    'second column': [10,20,30,40]
})


df 
"you do not need to do st.write to output to streamlit "



st.header("Now an example of formatting the dataframe output with a Pandas Styler object.")

import numpy as np

if 'dataframe' not in st.session_state:
    st.session_state.dataframe = np.random.randn(10,20)

st.dataframe(st.session_state.dataframe)


st.header("improvement with the pandas styler")

st.subheader("Highlight max values in each column")

if 'dataframe2' not in st.session_state:
    st.session_state.dataframe2 = pd.DataFrame(
        np.random.randn(10,20),
        columns = ('col %d' % i for i in range(20))
    )

st.dataframe(st.session_state.dataframe2.style.highlight_max(axis=0))


# static table version
"static table version"

st.table(st.session_state.dataframe)



st.header("DRAW CHARTS AND MAPS ")

st.subheader("line charts example")

chart_data = pd.DataFrame(
    np.random.randn(20,3),
    columns=['a','b','c']
)

st.line_chart(chart_data)

st.subheader("To display data points on a map we use: ")
st.subheader("st.map()")

"generate a sample data to plot on map of San Francisco"
map_data = pd.DataFrame(
    np.random.randn(1000,2) / [50,50] + [37.76, -122.43], # normalisation to san francisco coordinates??
    columns=['lat', 'lon']
)


st.map(map_data)


st.header("WIDGETS")

x = st.slider('x')
st.write(x, 'squared is', x * x)

" store widge key names to access them via "
st.text_input("Your name", key="name")

st.session_state.name

""
"Checkboxes to show/hide data"

if st.checkbox('show dataframe'):
    chart_data


"Select Boxes for options:"
df = pd.DataFrame({
    'first column': [1,2,3,4],
    'second column': [10,20,30,40]
})

option = st.selectbox(
    'Which number do you like the most?',
    df['first column']
)

'you selected: ', option


""
st.header("LAYOUT\n\n")
"steamlit makes it easy to organise widgets in a left panel sidebar with:"
"st.sidebar()"

add_selectbox = st.sidebar.selectbox(
    'How would you like to be contacted?',
    ('Email', 'Home phone', 'Mobile phone')
)

add_slider = st.sidebar.slider(
    'select a range of values',
    0.0, 100.0, (25.0, 75.0)
)



"COLUMNS \n\n\n\n"
"st.columns()"

left_column, right_column = st.columns(2)

left_column.button('Press me!')

with right_column:
    chosen = st.radio(
        'Sorting hat',
        ("Gryffindor", "Ravenclaw", "Hufflepuff", "Slytherin")
    )
    st.write(f"You are in {chosen} house!")

st.selectbox('nothing', [1,2,3,4])

left_column.button('test col after non col') # goes back above the select box into the column when it was defined


left_column.write("expanding section:")

with left_column.expander('image from streamlit examples:'):
    st.image("https://static.streamlit.io/examples/dice.jpg")


st.header("SHOW PROGRESS BAR")
"st.progress() with time.sleep()"

import time 


'starting a long computation'

# add a placeholder
latest_iteration = st.empty()
bar = st.progress(0)

for i in range(100):
    # update the progress bar with each iteration
    latest_iteration.text(f'Iteration {i+1}')
    bar.progress(i+1)
    time.sleep(0.1)

'... and now we\'re done!'


# SESSION STATE 

# EXAMPLE

st.header("Session state example:")

if "counter" not in st.session_state:
    st.session_state.counter = 0

st.session_state.counter += 1

st.header(f"This page has run {st.session_state.counter} times.")
st.button("Run it again")


x

x = 2

x

if 'x' not in st.session_state:
    st.session_state['x'] = 2

