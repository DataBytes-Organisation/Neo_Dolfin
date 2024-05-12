import pandas as pd
import plotly.graph_objects as go


#DolFin colour scheme for reference
dark_grey = '#343a40'
dark_blue = '#0077bb'
grey_1 = '#d9d9d9'
grey_2 = '#fafafe'
grey_3 = '#abb5be'

#import csv transaction data 
file_path = 'neo_dolfin/ai/generated_data/fake_bank_account_transactions2.csv'
data = pd.read_csv(file_path)
#data = data[data['Category 2'] != 'Income']

#ensure Debit is number so it can be added up 
data['Debit'] = pd.to_numeric(data['Debit'], errors='coerce').fillna(0)  # Convert Debit to numeric and fill NaNs

#group by categories and sum Debits
category_sums = data.groupby(['Category 1', 'Category 2'])['Debit'].sum().reset_index()

#Initialize lists
labels = []
sources = []
targets = []
values = []


label_dict = {}  # Dictionary to map labels to indices

#color_palette = ['#e6194b', '#3cb44b', '#ffe119', '#4363d8', '#f58231', '#911eb4', '#46f0f0', '#f032e6', '#bcf60c', '#fabebe', '#008080', '#e6beff', '#9a6324', '#fffac8', '#800000', '#aaffc3', '#808000', '#ffd8b1', '#000075', '#808080']

#link_colors = [color_palette[src % len(color_palette)] for src in sources]

#create sankey diagram
def get_label_index(label):
    if label not in label_dict:
        label_dict[label] = len(label_dict)
        labels.append(label)
    return label_dict[label]

for idx, row in category_sums.iterrows():
    cat1_idx = get_label_index(row['Category 1'])
    cat2_idx = get_label_index(row['Category 2'])

    sources.append(cat1_idx)
    targets.append(cat2_idx)
    values.append(row['Debit'])

sankey_fig = go.Figure(go.Sankey(
    node=dict(
        pad=15,
        thickness=20,
        line=dict(color='#fafafe', width=0.5),
        label=labels,
        color='#343a40'
    ),
    link=dict(
        source=sources,
        target=targets,
        value=values,
        color='#0077bb'
    )
))

sankey_fig.update_layout(title_text="Transaction Flows", font_size=12)
sankey_fig.show()
