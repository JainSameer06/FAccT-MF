import networkx as nx
import matplotlib.pyplot as plt
import csv
import chart_studio.plotly as py
from plotly.graph_objs import *
from plotly.offline import iplot
#from bokeh.io import output_file, show
#from bokeh.models import Range1d, Circle, ColumnDataSource, MultiLine
#from bokeh.plotting import figure, from_networkx


def generate_node(record):
	node_attributes = {}
	node_attributes["id"] = record[1] 


def get_title_dictionary(title_file):
	with open("/home/sameer/Projects/Political-leaning/Data/TXTs/titles.csv") as titlefile:
		reader = csv.reader(titlefile)
		title_dict = {}
		for row in reader:
			title_dict[row[0]] = row[1]
	return title_dict

G = nx.DiGraph()

with open("/home/sameer/Projects/Political-leaning/Data/TXTs/combined-final.csv") as csvfile:	
	title_dict = get_title_dictionary("dummy")
	reader = csv.reader(csvfile)
	for row in reader:
		if row[1] == "Id":
			continue
		source_id = row[1]
		reference_id = row[7]

		if source_id not in G:
			source_filename = row[2]
			source_title = title_dict[source_filename]
			G.add_node(source_id, sourceArticle = source_title)

		if reference_id not in G:
			G.add_node(reference_id, referencedArticle = row[4], authors = row[3], venue = row[5], year = row[6])
			
		G.add_edge(source_id, reference_id)

	pos = nx.fruchterman_reingold_layout(G)		#returns a dictionary of positions keyed by node
	Xv = [pos[k][0] for k in G.nodes()]
	Yv = [pos[k][1] for k in G.nodes()]
	Xed = []
	Yed = []

	reference_articles_titles = [G.nodes[node]['referencedArticle'] if 'referencedArticle' in G.nodes[node] else 'none' for node in G.nodes()]
	reference_articles_authors = [G.nodes[node]['authors'] if 'authors' in G.nodes[node] else 'none' for node in G.nodes()]
	node_text = ['Title: {title}\nAuthors: {author}'.format(title = title, author = author) for title, author in zip(reference_articles_titles, reference_articles_authors)]
	for edge in G.edges():
	    Xed += [pos[edge[0]][0], pos[edge[1]][0], None]
	    Yed += [pos[edge[0]][1], pos[edge[1]][1], None]

	node_adjacencies = []
	
	#for node, adjacencies in enumerate(G.adjacency()):
	    #node_adjacencies.append(len(adjacencies[1]))
	    #node_text.append('# of connections: '+str(len(adjacencies[1])))



	edge_trace = Scatter(x=Xed,
	               y=Yed,
	               mode='lines',
	               line=dict(color='rgb(210,210,210)', width=1),
	               hoverinfo='none'
	               )
	node_trace = Scatter(x=Xv,
	               y=Yv,
	               mode='markers',
	               name='net',

	               marker=dict(symbol='circle-dot',
	                             size=5,
	                             color='#6959CD',
	                             line=dict(color='rgb(50,50,50)', width=0.5)
	                           ),
	               text=node_text,
	               hoverinfo='text'
	               )

	node_trace.marker.size = [in_deg[1] for in_deg in G.in_degree()]
	annot="This networkx.Graph has the Fruchterman-Reingold layout<br>Code:"+\
	"<a href='http://nbviewer.ipython.org/gist/empet/07ea33b2e4e0b84193bd'> [2]</a>"

	data1 = [edge_trace, node_trace]
	fig1 = Figure(data=data1, layout=None)
	#fig1['layout']['annotations'][0]['text']=annot
	iplot(fig1, filename = 'citation-network')



	"""
	d = dict(G.in_degree)

	nx.draw(G, nodelist=list(d.keys()), node_size=[v * 100 for v in d.values()])
	plt.show()

	
	plot = figure(tools="pan, wheel_zoom, save, reset", active_scroll='wheel_zoom',
            x_range=Range1d(-100.1, 100.1), y_range=Range1d(-100.1, 100.1), title="Citation")

	

	#Set node size and color
	degrees = dict(nx.degree(G))
	nx.set_node_attributes(G, name='degree', values = degrees)
	print(degrees)

	number_to_adjust_by = 2
	adjusted_node_size = dict([(node, degree + number_to_adjust_by) for node, degree in nx.degree(G)])
	nx.set_node_attributes(G, name='adjusted_node_size', values = adjusted_node_size)

	network_graph = from_networkx(G, nx.spring_layout, scale=100, center=(0, 0))
	size_by_this_attribute = 'adjusted_node_size'
	#network_graph.node_renderer.data_source.data['index'] = list(reversed(range(len(G))))
	network_graph.node_renderer.glyph = Circle(size=size_by_this_attribute, fill_color='skyblue')

	

	#Set edge opacity and width
	network_graph.edge_renderer.glyph = MultiLine(line_alpha=0.02, line_width=1)

	#Add network graph to the plot
	plot.renderers.append(network_graph)

	show(plot)
	#save(plot, filename=f"{title}.html")
	"""

