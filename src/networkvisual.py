import os
import networkx as nx
import matplotlib
matplotlib.use('Agg')  # Use matplotlib without a display server.
import matplotlib.pyplot as plt
from source import Source
from article import Article
from keywords import Keyword
from response import Response
from database import Database
from reference import Reference

def draw_graph(imgname, graph, edge_labels = None, labels=None,
               graph_layout='shell', node_size=3300, node_color='blue',
               node_alpha=0.3, node_text_size=12, edge_color='blue',
               edge_alpha=0.3, edge_tickness=1, edge_text_pos=0.3,
               text_font='sans-serif', graph_title=''):
    """(str, dict, dict, list, str, int, str, int, int, str, int, int, int, str)
    -> str
    Generate a network graph based on given edges and nodes(input 'graph'),
    edge labels and other layout settings. Return the name of the graph.
    """
    # Create directed networkx graph.
    G=nx.DiGraph()

    # Add edges to the graph.
    for edge in graph:
        G.add_edge(edge[0], edge[1])

    # Setting the layout.
    if graph_layout == 'spring':
        graph_pos=nx.spring_layout(G)
    elif graph_layout == 'spectral':
        graph_pos=nx.spectral_layout(G)
    elif graph_layout == 'random':
        graph_pos=nx.random_layout(G)
    else:
        graph_pos=nx.shell_layout(G)

    # Draw graph nodes.
    nx.draw_networkx_nodes(G,graph_pos,node_size=node_size,
                           alpha=node_alpha, node_color=node_color)
    # Draw graph edges.
    nx.draw_networkx_edges(G,graph_pos,arrows = True, width=edge_tickness,
                           alpha=edge_alpha,edge_color=edge_color)
    # Draw graph labels(if they are given).
    nx.draw_networkx_labels(G, graph_pos,font_size=node_text_size,
                            font_family=text_font)

    # Draw graph edge-labels(if they are given).
    if edge_labels != None:
        nx.draw_networkx_edge_labels(G, graph_pos, edge_labels=edge_labels,
                                     label_pos=edge_text_pos)

    # Save the image
    plt.axis('off')
    plt.title(graph_title)
    plt.savefig(imgname)
    plt.show()
    plt.close()
    return imgname

def get_references_in_article(database, a_id):
    """(Database, int) -> (dict, str)
    Return the references inside the article as a dictionary with key
    (child_article, parent_source) and value frequency.  Also return the
    name of the article title.
    """
    edges = {}
    name = ""

    # Get the Article information from database
    article = database.get_by_id(Article, a_id)

    if article:

        name = str(article.title)

        # Get all the references of this article.
        references = database.get_references(a_id, None, None).all()
        edges = dict()

        for ref in references:

            # Get the source name as end point of the edge
            refstr = ""
            if ref.source_url:
                refstr += str(ref.source_url)

            # Add edge(child article, parent source) as dictionary key
            # and set proper count.
            try:
                edges[(name, refstr)] += 1
            except KeyError:
                edges[(name, refstr)] = 1

    return edges, name

def draw_references_in_article(database, imgname, a_id):
    """(Database, int) -> None
    Generate a network graph given the database, name of the output file, and
    the id of the article.  If the article is invalid (or there were no
    references for that article, then an empty graph is outputted.
    """
    graph_info = get_references_in_article(database, a_id)
    draw_graph(imgname, graph_info[0],
               graph_title='References inside of %s' % (graph_info[1]))

def get_references_to_source(database, s_id):
    """(Database, int) -> (dict, str)
    Return the references to a source s_id (from other sources) as a dictionary
    with key (child_source, parent_source) and value frequency.  Also return
    the name of the url of the source s_id.
    """

    # Get the source information from the database
    source = database.get_by_id(Source, s_id)
    ref_count = dict()
    s_name = ""

    if source:
        # Update the name of the source
        s_name = str(source.url)

        # Get all the references to the source
        references = database.get_references(None, s_id, None).all()
        for ref in references:
            child_source = ""
            child_article = database.get_by_id(Article, ref.child_id)

            # Get the name of the source of the article
            if child_article.source:
                child_source += str(child_article.source)

            # Add edge(child source, parent source) as dictionary key
            # and set proper count.
            try:
                ref_count[(child_source, s_name)] += 1
            except KeyError:
                ref_count[(child_source, s_name)] = 1

    return ref_count, s_name

def draw_references_to_source(database, imgname, s_id):
    """(Database, int) -> None
    Draw a network graph showing all the references made to a source s_id
    by the sources making the references to it.  Output the image file into
    imgname.
    """
    graph_info = get_references_to_source(database, s_id)
    draw_graph(imgname, graph_info[0], graph_info[0],
               graph_title='References made to %s' % (graph_info[1]))

def get_references_from_source(database, s_id):
    """(Database, int) -> (dict, str)
    Return the references made from articles inside a source s_id to other
    sources as a dictionary with key (child_source, parent_source) and value
    frequency.  Also return the name of the url of the source s_id.
    """

    # Get the source information from the database
    source = database.get_by_id(Source, s_id)
    articles = database.get_articles(source_id=s_id).all()
    ref_count = dict()
    s_name = ""

    if articles:
        # Update the name of the source
        s_name = str(source.url)

        # Get all the references inside every article from source s_id
        for article in articles:
            references = database.get_references(article.id).all()

            # Get all the references to parent_source
            for reference in references:

                parent_source = ""

                # Get the name of the source of the article
                if reference.source_url:
                    parent_source += str(reference.source_url)

                # Add edge(child source, parent source) as dictionary key
                # and set proper count.
                try:
                    ref_count[(s_name, parent_source)] += 1
                except KeyError:
                    ref_count[(s_name, parent_source)] = 1

    return ref_count, s_name

def draw_references_from_source(database, imgname, s_id):
    """(Database, int) -> None
    Draw a network graph showing all the references inside articles from source
    s_id to other sources.
    """
    graph_info = get_references_from_source(database, s_id)
    draw_graph(imgname, graph_info[0], graph_info[0],
               graph_title='References made in articles from %s' % (graph_info[1]))

if __name__ == "__main__":
    db = Database("testvisual.db")
    db.create_tables()
    db.add_source(Source("www.cnn.com"))
    db.add_keyword(Keyword(1, "CNN"))

    db.add_source(Source("http://newyork.cbslocal.com/"))
    db.add_keyword(Keyword(2, "WCBS"))

    db.add_source(Source("http://www.nbcnews.com/"))
    db.add_keyword(Keyword(3, "NBC"))

    db.add_source(Source("http://www.rtl-longueuil.qc.ca/"))
    db.add_keyword(Keyword(4, "RTL"))

    db.add_source(Source("http://www.cpn.com"))
    db.add_keyword(Keyword(5, "N"))

    db.add_source(Source("www.cbc.ca"))
    db.add_keyword(Keyword(6, "CBC"))

    #===CNN==========================================================
    cnn1 = db.add_article(Article("http://www.cnn.com/2014/10/29/us/"
                                  "new-york-murder-suicide/index.html?hpt=ju_c1",
                             "CNNTitle1",
                             "2010/10/29",
                             "CNNAuthor1"))

    cnn2 = db.add_article(Article("http://www.cnn.com/2014/10/29/us/"
                                  "new-york-murder-suicide/index.html?hpt=ju_c2",
                             "CNNTitle2",
                             "2010/10/29",
                             "CNNAuthor2"))

    cnn3 = db.add_article(Article("http://www.cnn.com/2014/10/29/us/"
                                  "new-york-murder-suicide/index.html?hpt=ju_c3",
                             "CNNTitle3",
                             "2011/10/29",
                             "CNNAuthor3"))

    cnn4 = db.add_article(Article("http://www.cnn.com/2014/10/29/us/"
                                  "new-york-murder-suicide/index.html?hpt=ju_c4",
                             "CNNTitle4",
                             "2012/10/29",
                             "CNNAuthor4"))

    cnn5 = db.add_article(Article("http://www.cnn.com/2014/10/29/us/"
                                  "new-york-murder-suicide/index.html?hpt=ju_c5",
                             "CNNTitle5",
                             "2012/10/29",
                             "CNNAuthor5"))

    #===Others=======================================================


    cbc6 = db.add_article(Article("http://www.cbc.ca/2014/10/29/us/"
                                  "new-york-murder-suicide/index.html?hpt=ju_c1",
                             "CNNTitle1",
                             "2012/10/29",
                             "CNNAuthor1"))

    wcbs7 = db.add_article(Article("http://www.nytimes.com/2014/10/29/us/"
                                   "new-york-murder-suicide/index.html?hpt=ju_c2",
                             "CNNTitle2",
                             "2012/10/29",
                             "CNNAuthor2"))

    nbc8 = db.add_article(Article("http://www.nbcnews.com/2014/10/29/us/"
                                  "new-york-murder-suicide/index.html?hpt=ju_c3",
                             "CNNTitle3",
                             "2012/10/29",
                             "CNNAuthor3"))

    rtl9 = db.add_article(Article("http://www.rtl-longueuil.qc.ca/2014/10/29/us/"
                                  "new-york-murder-suicide/index.html?hpt=ju_c4",
                             "CNNTitle4",
                             "2013/10/29",
                             "CNNAuthor4"))

    cpn10 = db.add_article(Article("http://www.cpn.com/2014/10/29/us/"
                                   "new-york-murder-suicide/index.html?hpt=ju_c5",
                             "CNNTitle5",
                             "2013/10/29",
                             "CNNAuthor5"))



    db.add_reference(Reference(1, 1, None))
    db.add_reference(Reference(1, 2, None))
    db.add_reference(Reference(1, 3, None))
    db.add_reference(Reference(1, 4, None))
    db.add_reference(Reference(2, 2, None))
    db.add_reference(Reference(2, 4, None))
    db.add_reference(Reference(2, 6, None))
    db.add_reference(Reference(3, 1, None))
    db.add_reference(Reference(3, 2, None))
    db.add_reference(Reference(4, 2, None))
    db.add_reference(Reference(5, 1, None))
    db.add_reference(Reference(5, 2, None))
    db.add_reference(Reference(5, 3, None))
    db.add_reference(Reference(5, 4, None))
    db.add_reference(Reference(5, 5, None))
    db.add_reference(Reference(5, 6, None))
    db.add_reference(Reference(6, 2, None))
    db.add_reference(Reference(7, 2, None))
    db.add_reference(Reference(8, 2, None))
    db.add_reference(Reference(9, 2, None))
    db.add_reference(Reference(10, 2, None))

    print "====Article Visual====="
    a = get_references_in_article(db, 1)
    for edge in a[0]:
        print(edge)

    print "====Cited Source Test====="
    a = get_references_to_source(db, 2)
    for edge in a[0]:
        print(edge)

    print "====Target Source Test====="
    a = get_references_from_source(db,1)
    for edge in a[0]:
        print(edge)

    print "====See graphs====="
    draw_references_in_article(db, "refs_in_article.png", 2)
    draw_references_to_source(db, "refs_to_source.png", 2)
    draw_references_from_source(db, "refs_from_source.png", 1)

    db.close()
    os.remove("testvisual.db")