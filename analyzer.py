import operator
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from typing import Union, Tuple, Dict, List
from community import community_louvain
import numpy as np
from scipy.optimize import curve_fit
from PIL import Image
import requests
from io import BytesIO
from transliterate import translit
import matplotlib.image as mpimg
from delete_file import delete_file
from custom_logger import logger

def preprocessing_graph(g: nx.Graph, info: dict) -> Tuple[nx.Graph, dict, int, int]:
    n_deactivated = 0
    for i in list(info.keys()):
        if info[i].get('deactivated'):
            del info[i]
            if g.has_node(i):
                g.remove_node(i)
            n_deactivated += 1
    n_isolated = 0
    for i in list(nx.connected_components(g)):
        if len(i) == 1:
            index = i.pop()
            if g.has_node(index):
                g.remove_node(index)
            del info[index]
            n_isolated += 1
    return g, info, n_deactivated, n_isolated
    

def powlaw(x: float, a: float, b: float) -> float:
    return a * np.power(x, b)


def linlaw(x: float, a: float, b: float) -> float:
    return a + x * b


def curve_fit_log(xdata: set, ydata: list) -> np.array:
    """Fit data to a power law with weights according to a log scale"""
    x_log = np.log10(xdata)
    y_log = np.log10(ydata)
    popt_log, _ = curve_fit(linlaw, x_log, y_log)
    ydatafit_log = np.power(10, linlaw(x_log, *popt_log))
    return ydatafit_log


def create_digree_distrbution(g: nx.Graph, info_id: int) -> str:
    degree = dict(g.degree())
    degree_values = sorted(set(degree.values()))
    hist = [list(degree.values()).count(x) for x in degree_values]
    deg = tuple(degree_values)
    fig, ax = plt.subplots(figsize=(8,8))
    plt.bar(deg, hist, width=0.80, color="g")

    plt.title("Degree distribution", size=20)
    plt.ylabel("Number of nodes", size=15)
    plt.xlabel("Degree", size=15)
    ax.set_xticks(list(range(0, max(deg), 5)))
    ax.set_xticklabels(list(range(0, max(deg), 5)))
    y_fit = curve_fit_log(degree_values, hist)
    plt.plot(degree_values[1:], y_fit[1:], linewidth = 4, color = "r", label="Law degree")
    
    picture_name = f'generated_docs/degree_distribution_{info_id}.png'
    plt.legend(fontsize=15);
    plt.savefig(picture_name, transparent=True);
    plt.close()
    return picture_name


def return_photo_vk(userid: int, info: str) -> Image:
    url = info[userid]['photo']
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    return img

def take_top_metrics(x: dict, n: int) -> list:
    """
    x: ("id": number)
    @return: [("id": metric)] - list of biggest n metrics with "id"
    """
    sorted_x = sorted(x.items(), key=operator.itemgetter(1))[::-1]
    return sorted_x[:n]

def return_name(id_user: int, info: dict, type_graph: str) -> str:
    """Concatenate name for vk or facebook"""
    if type_graph == 'vk':
        first_name = translit(info[id_user]['first_name'], "ru", reversed=True)
        first_name = first_name.encode('latin-1', 'ignore').decode("latin-1")
        last_name = translit(info[id_user]['last_name'], "ru", reversed=True)
        last_name = last_name.encode('latin-1', 'ignore').decode("latin-1")
        return first_name + " " + last_name
    elif type_graph == 'facebook':
        name = translit(info[id_user]['name'], "ru", reversed=True)
        return name

def make_column_for_one_metric(metrics, info: dict, n: int, type_graph: str) -> list:
    top_metrics = take_top_metrics(metrics, n)
    return [return_name(idd[0], info, type_graph) for idd in top_metrics]
    
    
def make_metrics_for_table(g: nx.Graph, info: dict, n: int, type_graph: str ='vk') -> Tuple[List[str], list]:
    """
    info: information about users
    n: number of top metrics
    return: column_names, rows
    """
    column_names = ["Betweenness", "Closeness", "Pagerank", "Degree"]
    rows = [[], [], [], []]
    metrics = nx.algorithms.centrality.betweenness_centrality(g)
    rows[0] = make_column_for_one_metric(metrics, info, n, type_graph)
    metrics = nx.algorithms.centrality.closeness_centrality(g)
    rows[1] = make_column_for_one_metric(metrics, info, n, type_graph)
    metrics = nx.algorithms.link_analysis.pagerank_alg.pagerank(g)
    rows[2] = make_column_for_one_metric(metrics, info, n, type_graph)
    metrics = nx.algorithms.centrality.degree_centrality(g)
    rows[3] = make_column_for_one_metric(metrics, info, n, type_graph)
    return column_names, np.array(rows).T.tolist()

def create_picture_social_network(g: nx.Graph, info: dict, user_id: int, type_graph: str) -> Tuple[list, str]:
    part = community_louvain.best_partition(g)
    values = [part.get(node) for node in g.nodes()]
    # pos = nx.spring_layout(g, scale=1, iterations=100, threshold=1e-6)
    pos = nx.nx_agraph.graphviz_layout(g)
    g_pagerank = nx.algorithms.link_analysis.pagerank_alg.pagerank(g)
    df = pd.DataFrame.from_dict(part, orient='index', columns=['group'])
    df['pagerank'] = df.index.map(g_pagerank)
    clusters = df['group'].unique()
    index_img = []
    for i in clusters:
        rank = df['pagerank'].where(df['group'] == i ).idxmax()
        index_img.append(rank)
    names = [return_name(i, info, type_graph) for i in index_img]
    
    ax = plt.gca()
    fig = plt.gcf()
    trans = ax.transData.transform
    trans2 = fig.transFigure.inverted().transform
    plt.rcParams['figure.figsize'] = [10, 10]

    nx.draw_networkx(g, pos = pos, cmap = plt.get_cmap('tab10'),
                     node_color = values,
                     node_size=40, width=0.3, edge_color='grey', with_labels=False)
    limits = plt.axis('off')
    imsize = 0.06
    img_name = f"generated_docs/graph_mini_pic{user_id}.png"
    for index in index_img:
        x, y = pos[index]
        xx, yy = trans((x,y)) # figure coordinates
        xa, ya = trans2((xx,yy)) # axes coordinates

        a = plt.axes([xa - imsize / 2.0, ya - imsize / 2.0, imsize, imsize ])
        current_img = return_photo_vk(index, info)
        
        current_img.save(img_name)
        current_img = mpimg.imread(img_name)
        a.imshow(current_img)
        a.axis('off');
    graph_name = f"generated_docs/graph_picture_{user_id}.png"
    plt.savefig(fname=graph_name, dpi=300, transparent=True)
    delete_file(img_name)
    plt.close()
    return names, graph_name