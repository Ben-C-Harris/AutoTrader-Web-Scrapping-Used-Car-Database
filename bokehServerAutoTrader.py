import pandas as pd
from bokeh.layouts import row, widgetbox
from bokeh.models import Select
from bokeh.palettes import Category20c
from bokeh.plotting import curdoc, figure
from bokeh.models import  HoverTool
from bokeh.models import ColumnDataSource

"""
TO RUN:
bokeh serve --show bokehServerAutoTrader.py

"""
DATA_FILE = "dataFullDatasetAutoTraderPickle.pkl"
SIZES = list(range(10, 30, 3))
COLORS = Category20c[20] + Category20c[20] + Category20c[20]
N_SIZES = len(SIZES)
N_COLORS = len(COLORS)

# Read in data
dfOnline = pd.read_pickle(DATA_FILE)

# Create ordered dict of makes and models for dynamic drop down box
makeModelDict = dfOnline.groupby('Make')['Model'].apply(list).to_dict()
makeModelDictSorted =  {k:sorted(set(j),key=j.index) for k,j in makeModelDict.items()}

# Prep values for plotting
dfOnline.Price = dfOnline.Price.astype(float)
dfOnline.Year = dfOnline.Year.astype(float)
dfOnline.Miles = dfOnline.Miles.astype(float)
dfOnline.BHP = dfOnline.BHP.astype(float)
dfOnline.L = dfOnline.L.astype(float)
columns = sorted(dfOnline.columns)
discrete = [x for x in columns if dfOnline[x].dtype == object]
continuous = [x for x in columns if x not in discrete]

def create_figure():
    # Print to console/CMD what you have requested
    print("X VALUE: " + x.value)
    print("Y VALUE: " + y.value)
    print("Make VALUE: " + make.value)
    print("Model VALUE: " + model.value)

    # Slice df to request
    dfFilteredMake = dfOnline[dfOnline["Make"] == make.value]
    dfFilteredModel = dfFilteredMake[dfFilteredMake["Model"] == model.value]
    
    # Get requested values and names
    xs = dfFilteredModel[x.value].values
    ys = dfFilteredModel[y.value].values
    x_title = x.value.title()
    y_title = y.value.title()

    # Set Hoverover variables 
    argName = dfFilteredModel.Name.values.tolist()
    argPrice = dfFilteredModel.Price.values.tolist()
    argYear = dfFilteredModel.Year.values.tolist()
    argMiles = dfFilteredModel.Miles.values.tolist()
    argBHP = dfFilteredModel.BHP.values.tolist()
    argL = dfFilteredModel.L.values.tolist()
    argTrans = dfFilteredModel.Trans.values.tolist()
       
    # Set XY value and title
    kw = dict()
    if x.value in discrete:
        kw['x_range'] = sorted(set(xs))
    if y.value in discrete:
        kw['y_range'] = sorted(set(ys))
    kw['title'] = "%s vs %s" % (x_title, y_title)

    # Configure plot and labels
    p = figure(plot_height=600, plot_width=800, tools='pan,box_zoom,hover,reset', **kw)
    p.xaxis.axis_label = x_title
    p.yaxis.axis_label = y_title
    
    # Orientate label
    if x.value in discrete:
        p.xaxis.major_label_orientation = pd.np.pi / 4

    # Assign size attribute to plot
    sz = 50
    if size.value != 'None':
        if len(set(dfFilteredModel[size.value])) > N_SIZES:
            groups = pd.qcut(dfFilteredModel[size.value].values, N_SIZES, duplicates='drop')
        else:
            groups = pd.Categorical(dfFilteredModel[size.value])
        sz = [SIZES[xx] for xx in groups.codes]

    # Assign color attribute to plot
    c = "#31AADE"
    if color.value != 'None':
        if len(set(dfFilteredModel[color.value])) > N_SIZES:
            groups = pd.qcut(dfFilteredModel[color.value].values, N_COLORS, duplicates='drop')
        else:
            groups = pd.Categorical(dfFilteredModel[color.value])
        c = [COLORS[xx] for xx in groups.codes]
        
    # Data source including hover over source args
    source = ColumnDataSource(data=dict(x=xs,
                                        y=ys,
                                        color=c,
                                        size=sz,
                                        argName=argName,
                                        argPrice=argPrice,
                                        argYear=argYear,
                                        argMiles=argMiles,
                                        argBHP=argBHP,
                                        argL=argL,
                                        argTrans=argTrans))

    # Plot and set axis format
    p.circle(x='x', y='y', color='color', size='size', source=source, line_color="white", alpha=0.6, hover_color='white', hover_alpha=0.5)
    p.xaxis[0].formatter.use_scientific = False
    p.yaxis[0].formatter.use_scientific = False

    # Define tooltips on hoverover
    hover = p.select(dict(type=HoverTool))
    TOOLTIPS = [("Name", "@argName"),
                ("Price (" + u"\u00a3" +")", "@argPrice"),
                ("Year", "@argYear"),
                ("Miles", "@argMiles"),
                ("BHP", "@argBHP"),
                ("L", "@argL"),
                ("Trans", "@argTrans")]
    hover.tooltips = TOOLTIPS
    hover.mode = "mouse"

    return p


def update(attr, old, new):
    makeVar = make.value
    model.options = makeModelDictSorted[makeVar]
    layout.children[1] = create_figure()


def updateMake(attr, old, new):
    makeVar = make.value
    model.options = makeModelDictSorted[makeVar]
    model.value = model.options[0]
    print("UPDATE-MAKE: " + make.value + " " + model.value)
    layout.children[1] = create_figure()


# Set initial values and then dictate how they react on updates/changes from user     
make = Select(title='Select Car Make', value=sorted(dfOnline['Make'].unique())[0], options= sorted(dfOnline['Make'].unique()))
make.on_change('value', updateMake)

model = Select(title='Select Car Model', value=makeModelDictSorted[sorted(dfOnline['Make'].unique())[0]][0], options= makeModelDictSorted[sorted(dfOnline['Make'].unique())[0]] )
model.on_change('value', update)

x = Select(title='X-Axis', value='Miles', options=columns)
x.on_change('value', update)

y = Select(title='Y-Axis', value='Price', options=columns)
y.on_change('value', update)


size = Select(title='Size', value='BHP', options=['None'] + continuous)
size.on_change('value', update)

color = Select(title='Color', value='Year', options=['None'] + continuous)
color.on_change('value', update)

# Define dynamic drop down box widgets
controls = widgetbox([make, model, x, y, size, color], width=250)

#Set layout
layout = row(controls, create_figure())

curdoc().add_root(layout)
curdoc().title = "Auto-Trader Dynamic Visualization"








