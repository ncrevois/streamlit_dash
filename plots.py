import matplotlib.pyplot as plt  
import pandas as pd
from typing import Literal
from io import BytesIO
import seaborn as sns

def generate_plots(results_df, type: Literal['sum', 'count', 'co2']): 
    # Group and calculate data for the plots
    if type == 'sum':
        grouped_data = results_df.groupby(["matching_type"]).device_instances.sum()
        metric = "Total Device assets"

    if type == 'count': 
        grouped_data = results_df.groupby(["matching_type"]).device_instances.count()
        metric = "Distinct Device Models"

    if type == 'co2': 
        results_df['total_co2_kg'] = results_df['co2'] * results_df['device_instances'] / 1000
        grouped_data = results_df.groupby(["matching_type"]).total_co2_kg.sum()
        metric = "CO2 emitted by all devices [kgCO2eq]"

    total = grouped_data.sum()
    percentage_data = (grouped_data / total) * 100

    # Use the default color palette for bars and pie chart
    colors = sns.color_palette("Set2", len(grouped_data))

    # Set the plot style and theme
    plt.style.use('dark_background')
    plt.rcParams['axes.facecolor'] = '#2C2C2C'          # Dark grey for axes background
    plt.rcParams['figure.facecolor'] = '#2C2C2C'        # Dark grey for figure background
    plt.rcParams['text.color'] = '#E8E8E8'              # Light grey for text color
    plt.rcParams['axes.labelcolor'] = '#E8E8E8'         # Light grey for axis labels
    plt.rcParams['xtick.color'] = '#E8E8E8'             # Light grey for x-ticks
    plt.rcParams['ytick.color'] = '#E8E8E8'             # Light grey for y-ticks
    plt.rcParams['font.size'] = 12                      # General font size
    plt.rcParams['axes.titlesize'] = 16                 # Title font size
    plt.rcParams['axes.labelsize'] = 14                 # Label font size
    plt.rcParams['legend.fontsize'] = 12                # Legend font size

    # Create a figure with 2 subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Plotting the bar chart on the first subplot
    bars = ax1.bar(grouped_data.index, grouped_data, color=colors)
    ax1.set_title(f"Sum of {metric}")
    ax1.set_xlabel("Matching Type")
    ax1.set_ylabel(f"Sum of {metric}")

    # Adding the numbers on each bar with light grey text color
    for bar in bars:
        yval = bar.get_height()
        ax1.text(
            bar.get_x() + bar.get_width() / 2,
            yval,
            int(yval),
            va='bottom',
            ha='center',
            color='#E8E8E8',  # Light grey for numbers on the bar chart
            fontsize=12       # Font size for numbers on bars
        )

    # Plotting the pie chart on the second subplot with black text color for percentages
    wedges, texts, autotexts = ax2.pie(
        percentage_data, 
        labels=percentage_data.index, 
        autopct='%1.1f%%', 
        colors=colors,
        textprops={'color': '#E8E8E8', 'fontsize': 12}  # Light grey for labels
    )
    for autotext in autotexts:
        autotext.set_fontsize(12)  # Set font size for percentage text
        autotext.set_color('#000000')  # Black for percentages on the pie chart

    ax2.set_title(f"Percentage of {metric}")

    # Save the figure to a BytesIO object
    buf = BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format='png', facecolor=fig.get_facecolor())  # Ensures background is dark when saving
    buf.seek(0)  # Rewind the buffer to the beginning so it can be read
    plt.close()

    return buf
