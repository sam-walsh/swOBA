import pandas as pd
import numpy
import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder
from st_aggrid.shared import GridUpdateMode

spray_xwoba = pd.read_csv("spray_xwoba.csv")
spray_xwoba = spray_xwoba.round(3)

def aggrid_interactive_table(df: pd.DataFrame):
    """Creates an st-aggrid interactive table based on a dataframe.

    Args:
        df (pd.DataFrame]): Source dataframe

    Returns:
        dict: The selected row
    """
    options = GridOptionsBuilder.from_dataframe(
        df, enableRowGroup=True, enableValue=True, enablePivot=True
    )

    options.configure_side_bar()

    options.configure_selection("single")
    selection = AgGrid(
        df,
        enable_enterprise_modules=True,
        gridOptions=options.build(),
        theme="light",
        update_mode=GridUpdateMode.MODEL_CHANGED,
        allow_unsafe_jscode=True,
    )

    return selection


spray_xwoba = pd.read_csv("spray_xwoba.csv")
spray_xwoba['spray xwoba percentile'] = spray_xwoba['spray xwoba'].rank(pct=True).mul(100).round(1)
spray_xwoba = spray_xwoba.round(3)

selection = aggrid_interactive_table(df=spray_xwoba)

if selection:
    st.write("You selected:")
    st.json(selection["selected_rows"])