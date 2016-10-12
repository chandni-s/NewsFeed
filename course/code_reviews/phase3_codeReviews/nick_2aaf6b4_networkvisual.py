import os
import networkx as nx
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
               text_font='sans-serif'):
    """(str, list, dict, list, str, int, str, int, int, str, int, int, int, str)
    Generate a network graph based on given edges and nodes(input 'graph'), 
    edge lables and other latour setting.
    
    Return the name of the graph. 
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
    nx.draw_networkx_edges(G,graph_pos,arrows = True,width=edge_tickness,
                           alpha=edge_alpha,edge_color=edge_color)
    # Draw graph lables(if they are given).
    nx.draw_networkx_labels(G, graph_pos,font_size=node_text_size,
                            font_family=text_font)
    
    # Draw graph edge-lables(if they are given).
    if edge_labels != None:
        nx.draw_networkx_edge_labels(G, graph_pos, edge_labels=edge_labels, 
                                     label_pos=edge_text_pos)
      
    plt.axis('off') # Do not show axis in the graph.   
    plt.title(imgname) # Set graph title
    plt.savefig(imgname, format="PNG") # Save as png
    plt.show()# Show graph
    return imgname

def visual_arti_ref(db, a_id):
    """(Database, int) -> str
    Generate a network visualization for references of a specific article 
    indicated by a_id.
    
    Return the graph name, and a dictionary with key=reference edges<->value=count.
    """
    # Get the Article information from database by id.
    article = db.get_by_id(Article, a_id)
    
    if article != None:
        # Generate graph name base on article title.
        name = str(article.title)
        imgname = "AritcleVisual: "+name
        # Get all the references of this article. 
        references = db.get_references(a_id, None, None).all()
        edges = dict()
        
        # Loop all the references to generate reference edges.
        for ref in references:
            refstr = ""
            
            # Get the source name as end point
            if ref.source_url:         
                refstr += str(ref.source_url)
            
            # Add edge(child article, parent source) as dictionary key
            # and set proper count.
            if (name,refstr) in edges.keys():  
                edges[(name,refstr)] += 1
            else:
                edges[(name,refstr)] = 1  
        
        # Draw the proper network graph based on edge dictionaay.                 
        draw_graph(imgname, edges.keys())
        return (imgname, edges)
    
    else:
        return "Sorry, no article data founded."



def visual_parent_source(db, s_id):
    """(Database, int) -> png(? or str = image name)
    Generate a network visualization for references relations between a specific 
    source indicated by s_id and the sources that use citation content from that
    source. 
    
    Return the graph name, and a dictionary with key=reference edges<->value=count.
    """   
    # Get the Source information from database by id.
    source = db.get_by_id(Source, s_id)
    
    if source != None:
        # Generate graph name base on source name.
        s_name = str(source.url)
        imgname = "ParentSourceVisual: "+s_name
        ref_count = dict() 
        # Get all the references that made from this source. 
        references = db.get_references(None, s_id, None).all()
        
        # Loop all the references to generate reference edges.
        for ref in references:
            childstr = ""     
            
            # Get the article that made this reference.
            child_a = db.get_by_id(Article, ref.child_id)
            # Get the source name of this article.
            childstr += str(child_a.source)      
            
            # Add edge(child source, parent source) as dictionary key
            # and set proper count.            
            if (childstr, s_name) in ref_count.keys():  
                ref_count[(childstr, s_name)] += 1
            else:
                ref_count[(childstr, s_name)] = 1 
                
        # Draw the proper network graph based on edge dictionary.              
        draw_graph(imgname, ref_count.keys(), ref_count)
        
        return [imgname, ref_count]

    else:
        return "Sorry, no source data founded."
    
    
    
def visual_child_source(db, s_id):
    """(Database, int) -> str
    Generate a network visualization for references relations between a specific 
    source indicated by s_id and the sources that its articles use citation 
    content . 
    
    Return the graph name, and a dictionary with key=reference edges<->value=count.
    """ 
    # Get the Source information from database by id.
    source = db.get_by_id(Source, s_id)
    # Get all the articles of this source.
    articles = db.get_articles(source_id=s_id).all()
    
    if (articles != None) and (source != None):
        # Generate graph name base on source name.
        s_name = str(source.url)
        imgname = "ChildSourceVisual: "+s_name
        ref_count = dict() 
        
        # Loop all the articles for the related references
        for child_a in articles:
            a_refs = db.get_references(child_a.id).all()         
            for ref in a_refs:
                refstr = ""         
                refstr += str(ref.source_url)
                
                if (s_name,refstr) in ref_count.keys():  
                    ref_count[(s_name,refstr)] += 1
                else:
                    ref_count[(s_name,refstr)] = 1
                    
        # Draw the proper network graph based on edge dictionary.             
        draw_graph(imgname, ref_count.keys(), ref_count)
        
        return [imgname, ref_count]
    
    else:
        return "Sorry, no source data founded."        
                              
                 
def get_source_data(db, s_id):
    '''
    Get name of article that user wants to see data of ex: ArticleABC
    Get number of references that are made from this ArticleABC 
    Get Date of each reference made
    '''
    source = db.get_by_id(Source, s_id)
    if source != None:
        s_name = str(source.url)
        imgplot = "SourcePlotVisual: "+s_name
        references = db.get_references(None, s_id, None).all()
        time_count = dict()
        
        for ref in references:
            childtime = ""     
            child_a = db.get_by_id(Article, ref.child_id)
            childtime += str(child_a.date)[0:4] 
            if childtime in  time_count.keys():  
                time_count[childtime] += 1
            else:
                time_count[childtime] = 1 
    
        return [imgplot, time_count]
    else:
        return "Sorry, no source data founded."
   
    
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
    cnn1 = db.add_article(Article("http://www.cnn.com/2014/10/29/us/new-york-murder-suicide/index.html?hpt=ju_c1", 
                             "CNNTitle1", 
                             "2010/10/29", 
                             "CNNAuthor1"))
    
    cnn2 = db.add_article(Article("http://www.cnn.com/2014/10/29/us/new-york-murder-suicide/index.html?hpt=ju_c2", 
                             "CNNTitle2", 
                             "2010/10/29", 
                             "CNNAuthor2"))
    
    cnn3 = db.add_article(Article("http://www.cnn.com/2014/10/29/us/new-york-murder-suicide/index.html?hpt=ju_c3", 
                             "CNNTitle3", 
                             "2011/10/29", 
                             "CNNAuthor3"))    
    
    cnn4 = db.add_article(Article("http://www.cnn.com/2014/10/29/us/new-york-murder-suicide/index.html?hpt=ju_c4", 
                             "CNNTitle4", 
                             "2012/10/29", 
                             "CNNAuthor4"))    
   
    cnn5 = db.add_article(Article("http://www.cnn.com/2014/10/29/us/new-york-murder-suicide/index.html?hpt=ju_c5", 
                             "CNNTitle5", 
                             "2012/10/29", 
                             "CNNAuthor5"))  
    
    #===Others=======================================================

    
    cbc6 = db.add_article(Article("http://www.cbc.ca/2014/10/29/us/new-york-murder-suicide/index.html?hpt=ju_c1", 
                             "CNNTitle1", 
                             "2012/10/29", 
                             "CNNAuthor1"))
    
    wcbs7 = db.add_article(Article("http://www.nytimes.com/2014/10/29/us/new-york-murder-suicide/index.html?hpt=ju_c2", 
                             "CNNTitle2", 
                             "2012/10/29", 
                             "CNNAuthor2"))
    
    nbc8 = db.add_article(Article("http://www.nbcnews.com/2014/10/29/us/new-york-murder-suicide/index.html?hpt=ju_c3", 
                             "CNNTitle3", 
                             "2012/10/29", 
                             "CNNAuthor3"))    
    
    rtl9 = db.add_article(Article("http://www.rtl-longueuil.qc.ca/2014/10/29/us/new-york-murder-suicide/index.html?hpt=ju_c4", 
                             "CNNTitle4", 
                             "2013/10/29", 
                             "CNNAuthor4"))    
   
    cpn10 = db.add_article(Article("http://www.cpn.com/2014/10/29/us/new-york-murder-suicide/index.html?hpt=ju_c5", 
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
    '''
    print "====test_get_source===="
    get_s1 = db.get_by_id(Source, 2)
    print get_s1
    
    print "====plot_test1====="
    
    plot_test1 = get_source_data(db, 2)  
    if len(plot_test1) != 2:
        print plot_test1
    else:
        print plot_test1[0]
        print plot_test1[1]
    
        for i in plot_test1[1].items():
            print i  
           
    print "====art_ref1====="
    art_ref1 = visual_arti_ref(db, 1)
    if len(art_ref1) != 2:
        print art_ref1
    else:
        print art_ref1[0]
        print art_ref1[1]
    
        for i in art_ref1[1].items():
            print i  
            
        #draw_graph(art_ref1[0], art_ref1[1].keys())            
    
    print "====source_ref1====="
    
    source_ref1 = visual_parent_source(db, 2)
    
    if len(source_ref1) != 2:
        print source_ref1
    else:
        print source_ref1[0]
        print source_ref1[1]
    
        for i in source_ref1[1].items():
            print i  
    '''        
      
    
    print "====child_visual1====="
    child_visual1 = visual_child_source(db, 1)
    if len(child_visual1) != 2:
            print child_visual1
    else:
    
        print child_visual1[0]
        print child_visual1[1]
    
        for i in child_visual1[1].items():
            print i
         
    db.close()
    os.remove("testvisual.db")     