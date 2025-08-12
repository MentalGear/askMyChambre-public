import sys
import json
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio

# Set a clean default theme for plots
pio.templates.default = "plotly_white"

# Define a maximum number of points for scatter plots to avoid browser overload
MAX_SCATTER_POINTS = 5000

def nl2plot(df: pd.DataFrame, user_prompt: str) -> go.Figure:
    """
    This is your placeholder for your actual nl2plot function.
    It takes a pandas DataFrame and a user prompt and returns a Plotly Figure.
    """
    try:
        fig = go.Figure()
        
        if df.empty:
            fig.update_layout(title_text="No data available to plot.", showlegend=False)
            return fig

        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        title = ""

        # Simple logic to pick a plot type
        if len(numeric_cols) >= 2:
            x_col, y_col = numeric_cols[0], numeric_cols[1]
            
            # --- OPTIMIZATION: DOWNSAMPLING ---
            # If the dataframe has more points than our defined max, take a random sample.
            if len(df) > MAX_SCATTER_POINTS:
                plot_df = df.sample(n=MAX_SCATTER_POINTS, random_state=1) # random_state for reproducibility
                title += f" (displaying a sample of {MAX_SCATTER_POINTS} points)"
            else:
                plot_df = df

            # --- PERFORMANCE FIX: Use Scattergl for WebGL-based rendering ---
            # This is significantly faster for large datasets than the default SVG-based Scatter.
            fig = go.Figure(data=go.Scattergl(
                x=plot_df[x_col], 
                y=plot_df[y_col], 
                mode='markers', 
                marker=dict(color='#3b82f6', size=5, opacity=0.7) # Smaller, semi-transparent markers look better
            ))
            fig.update_layout(title_text=title, xaxis_title=x_col, yaxis_title=y_col)

        elif len(numeric_cols) == 1 and len(categorical_cols) >= 1:
            x_col, y_col = categorical_cols[0], numeric_cols[0]
            # Aggregation is already a form of downsampling, so this is fine.
            agg_df = df.groupby(x_col)[y_col].sum().reset_index().nlargest(25, y_col)
            fig = go.Figure(data=go.Bar(x=agg_df[x_col], y=agg_df[y_col], marker=dict(color='#3b82f6')))
            fig.update_layout(title_text=title, xaxis_title=x_col, yaxis_title=f"Total {y_col}")
        else:
            fig.update_layout(title_text="Could not determine a suitable plot for the provided data.")
        
        fig.update_layout(font=dict(family="sans-serif"), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        return fig

    except Exception as e:
        fig = go.Figure()
        fig.update_layout(title_text=f"Error during plot generation: {e}")
        return fig

def main():
    if len(sys.argv) < 3:
        print(json.dumps({"error": "Missing arguments. Expecting user_prompt and table_data_json."}), file=sys.stderr)
        sys.exit(1)

    user_prompt = sys.argv[1]
    table_data_json = sys.argv[2]

    try:
        table_data = json.loads(table_data_json)
        df = pd.DataFrame(table_data)
        plotly_fig = nl2plot(df, user_prompt)
        plotly_json_str = pio.to_json(plotly_fig)
        print(plotly_json_str)

    except Exception as e:
        print(json.dumps({"error": f"An unexpected error occurred in Python: {e}"}), file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
