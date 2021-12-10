from fpdf import FPDF
import numpy as np
import networkx as nx
from transliterate import translit
from delete_file import delete_file
from vk_graph import VkGraph
from config import access_token
from analyzer import preprocessing_graph, create_degree_distrbution, make_metrics_for_table, create_picture_social_network
from custom_logger import logger

class PDF(FPDF):
    """
    A wrapper class on a FPDF with customized table
    """
    def footer(self):
        # Position cursor at 1.5 cm from bottom:
        self.set_y(-15)
        # Setting font: helvetica italic 8
        self.set_font("helvetica", "I", 8)
        # Printing page number:
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", 0, 0, "C")
        
    def colored_table(self, headings, rows, col_widths=(45, 50, 50, 45)):
        # Colors, line width and bold font:
        self.set_fill_color(255, 100, 0)
        self.set_text_color(255)
        self.set_draw_color(255, 0, 0)
        self.set_line_width(0.6)
        self.set_font(style="B", size=15)
        for col_width, heading in zip(col_widths, headings):
            self.cell(col_width, 12, heading, 1, 0, "C", True)
        self.ln()
        # Color and font restoration:
        self.set_fill_color(224, 235, 255)
        self.set_text_color(0)
        self.set_font(size=10)
        fill = False
        for row in rows:
            self.cell(col_widths[0], 10, row[0], "LR", 0, "C", fill)
            self.cell(col_widths[1], 10, row[1], "LR", 0, "C", fill)
            self.cell(col_widths[2], 10, row[2], "LR", 0, "C", fill)
            self.cell(col_widths[3], 10, row[3], "LR", 0, "C", fill)
            self.ln()
            fill = not fill
        self.cell(sum(col_widths), 0, "", "T")


def generate_vk_pdf(name_pdf: str, user_id: int, user_name: str, option_downloading_vk: str) -> None:
    user_name = translit(user_name, "ru", reversed=True)
    type_graph = "vk"
    background_name = 'generated_docs/a4_color.png'  # 'blue_colored.png'
    vk = VkGraph(access_token=access_token, user_id=int(user_id))
    g, info = vk.make_graph(option_downloading_vk)
    if g is None or info is None:
        logger.error("Error in vk.make_graph")
        return
    g, info, n_deactivated, n_isolated = preprocessing_graph(g, info)
    
    pdf = PDF()
    pdf.alias_nb_pages()

    #######################################################
    pdf.add_page()
    pdf.image(background_name, x = 0, y = 0, w = 210, h = 297, type = '', link = '')


    pdf.set_font(family="helvetica", style="B", size=24)
    pdf.cell(w=None, h=None, txt="VK analysis", center=True, border=0, ln=1)

    pdf.set_font(family="helvetica", style="B", size=12)
    pdf.set_y(20)
    pdf.cell(w=None, h=None, txt=user_name, center=True, border=0, ln=1)
    pdf.line(x1=0, y1=30, x2=250, y2=30)
    pdf.set_font(family="helvetica", style="B", size=20)
    pdf.set_y(33)
    pdf.cell(w=None, h=None, txt="Network summary", center=True, border=0, ln=1)

    # statistics
    pdf.set_font("Times", size=12)
    we=0
    he=10
    pdf.cell(we, he, f"Number of nodes: {len(g)}", border=0, ln=1, center=False)
    pdf.cell(we, he, f"Number of isolated friends: {n_isolated}", border=0, ln=1, center=False)
    pdf.cell(we, he, f"Number of deactivated accounts: {n_deactivated}", border=0, ln=1, center=False)
    pdf.cell(we, he, f"Average degree: {sum([i[1] for i in g.degree()])/len(g.nodes()):.4}", 
            border=0, ln=1, center=False)
    pdf.cell(we, he, f"Graph's density: {len(g.edges())*2/(len(g.nodes())*(len(g.nodes())-1)):.2}"
            , border=0, ln=1, center=False)
    pdf.cell(we, he, f"Number of connected components: {nx.number_connected_components(g)}", 
            border=0, ln=1, center=False)
    pdf.cell(we, he, f"Average clustering coefficient: {nx.average_clustering(g):.2}", border=0, ln=1, center=False)

    subgraphs = [g.subgraph(c).copy() for c in nx.connected_components(g)]
    average_distance = np.mean([nx.average_shortest_path_length(i) for i in subgraphs])
    
    pdf.cell(we, he, f"Average shortest path length: {average_distance:.2}", border=0, ln=1, center=False)
    average_diam = np.mean([nx.diameter(c) for c in subgraphs])
    pdf.cell(we, he, f"Graph's diameter: {average_diam}", border=0, ln=1, center=False)

    # add histogramm
    picture_name = create_degree_distrbution(g, user_id);
    pdf.image(picture_name, x=100, y=36, w=100, h=0);
    delete_file(picture_name)
    # structural analysis
    pdf.set_font(family="helvetica", style="B", size=20)
    pdf.set_y(140)
    pdf.cell(w=None, h=None, txt="Structural Analysis", center=True, border=0, ln=1)
    pdf.set_y(150)

    col_names, rows = make_metrics_for_table(g, info, 5, type_graph)
    pdf.colored_table(col_names, rows)
    pdf.set_y(220)
    pdf.set_font("helvetica", style="B",size=13)
    pdf.cell(we, he, f"Probably, your best friend is {rows[0][2]}!", border=0, ln=1, center=False)

    #######################################################
    pdf.add_page()
    pdf.image(background_name, x = 0, y = 0, w = 210, h = 297, type = '', link = '')
    pdf.set_font("Times", size=12)
    we=0
    he=10
    picture_names, graph_vizualization_name = create_picture_social_network(g, info, user_id, type_graph)
    pdf.cell(we, he, f"Main nodes in each of {len(picture_names)} clusters: ", border=0, ln=1, center=False)
    
    for n in picture_names:
        pdf.cell(we, he, n, border=0, ln=1, center=False)

    pdf.set_y(300)
    pdf.image(graph_vizualization_name, x=0, y=50, w=200, h=0)
    delete_file(graph_vizualization_name)
    pdf.output(name_pdf)
