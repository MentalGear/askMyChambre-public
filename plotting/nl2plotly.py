import pandas as pd
import plotly.express as px

df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/2014_apple_stock.csv')

fig = px.line(df, x = 'AAPL_x', y = 'AAPL_y', title='Apple Share Prices over time (2014)')
fig.show()


user_prompt = """ Plot this table in a bar chart. """

system_prompt = """ You are a python plotly expert. Your goal is to display data in a plot usnig plotly python package. """

system_prompt2 = """Provide python code to build a plot. Provide it is a way that"""

prompt = system_prompt + user_prompt + system_prompt2