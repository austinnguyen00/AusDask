import streamlit as st
import pandas as pd

df = pd.read_excel('output/data/Skill_by_level.xlsx')

chart = st.bar_chart(data=df, x='skill')
