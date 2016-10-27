from response import Response
from reference import Reference
from database import Database
from source import Source
from article import Article
from keywords import Keyword
from datetime import datetime
import os
import matplotlib
matplotlib.use('Agg')  # Use matplotlib without a display server.
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from random import randint

colors = ["b", "g", "c", "m", "y", "k"]
styles = ["+", "--", "-.", "o", "+", "*", "p", "s", "D", "h"]


def plot_bars(database, imgname, sources):
    """(Database, name, list) -> None
    Draw the bars of the number of references made to a source contained inside
    info, which contains the references made per year.
    """
    graph_info = get_graph_information(database, sources)
    print ("PRINT GRAPH INFO BELOW ============")
    print (sources)

    print (graph_info)

    # Format the years to be integers
    years = []
    for year in graph_info[0]:
        years.append(int(year))

    # Choose an combination of line style
    color = 0
    style = 0

    # Set up the img file where the graph will be outputted
    fig = plt.figure()
    fig.set_size_inches([18.5, 10.5])

    # Set the labels on the x-axis
    ax = fig.add_subplot(111)

    # Determine the width of each bar depending on the number of sources
    width = 0.9 * (1.0 / len(graph_info[1]))
    
    #years = [2011, 2012, 2013, 2014, 2015, 2016] * len(sources)
    #Graph a line for each source in sources
    for i in range(len(sources)):

        # Find where to place bars depending on width and number of sources

        new_years = [year + width * i for year in years]
        
        print new_years
        print ("============")

        for j in years:
            print (graph_info[1][i][i])
            print (graph_info[2][i])
            ax.bar(new_years[j], graph_info[1][i][i], width=width, color=colors[color],label=graph_info[2][i])

        # x-axis, y-axis, width, color, label
        
        # Choose different colors and styles for lines
        color += 1
        if color > len(colors):
            color = 0
    # for i in range(len(sources)):
    #     # Find where to place bars depending on width and number of sources
    #     new_years = [year + width * i for year in years]
    #     ax.bar(new_years[i],randint(1,20),width=width,color=colors[color],label=graph_info[2][i])

    #     color += 1
    #     if color > len(colors):
    #         color = 0

    # Set up the labels on the graph
    plt.title("Number of references made to sources by year")
    plt.xlabel("Year")
    plt.ylabel("Number of times referenced by articles")

    # Set up the legend of the graph
    plt.legend()

    # Set up the labels on the x-axis
    ax.xaxis.set_major_formatter(mdates.ticker.FormatStrFormatter('%d'))

    # Save the image and output it into the file
    fig.savefig(imgname, dpi=100)

    plt.close()


def plot_lines(database, imgname, sources):
    """(Database, name, list) -> None
    Draw the line of the number of references made to a source contained inside
    info, which contains the references made per year.
    """
    graph_info = get_graph_information(database, sources)
    # Format the years to be integers
    years = []
    for year in graph_info[0]:
        years.append(int(year))

    # Choose an combination of line style
    color = 0
    style = 0

    # Set up the img file where the graph will be outputted
    fig = plt.figure()
    fig.set_size_inches([18.5, 10.5])

    # Set the labels on the x-axis
    ax = fig.add_subplot(111)

    # Graph a line for each source in sources
    for i in range(0, len(graph_info[1])):
        ax.plot(years, graph_info[1][i], color=colors[color],
                label=graph_info[2][i], linewidth=4)

        # Choose different colors and styles for lines
        color += 1
        if color > len(colors):
            color = 0

            # Choose a different style for the next line
            style += 1
            if style > len(styles):
                # Reset to the initial color and style
                style = 0

    # Set up the labels on the graph
    plt.title("Number of references made to sources by year")
    plt.xlabel("Year")
    plt.ylabel("Number of times referenced by articles")

    # Set up the legend of the graph
    leg = ax.legend(loc='best')
    for l in leg.legendHandles:
        l.set_linewidth(10)

    # Set up the labels on the x-axis
    ax.xaxis.set_major_formatter(mdates.ticker.FormatStrFormatter('%d'))

    # Save the image and output it into the file
    fig.savefig(imgname, dpi=100)

    plt.close()


def get_references_to_source(database, s_id):
    """(Database, int) -> dict
    Given a source, return a dictionary that contains the information:
    url -> s_id.url
    references -> {YEAR -> Number of references}
    """

    # Get the source and get the references made to the source
    source = database.get_by_id(Source, s_id)

    if source is None:
        return None

    info = {"name": source.url}
    

    # Get the references to the source per year
    references = {}
    for ref in database.get_references(None, s_id).all():
        print ref
        # Update the number of refs made at the year the article was made
        article = database.get_by_id(Article, ref.child_id)
        if article.date:
            year = datetime.strptime(article.date, '%Y-%m-%d').year
            print year
            try:
                references[year] += 1
            except KeyError:
                references[year] = 1

    info["references"] = references
    
    return info


def get_graph_information(database, sources):
    """(Database, sources) -> tuple([str], [str], [str])
    Return the years that references are made to specified sources and the
    number of references made to each source in each year.
    """
    source_information = []

    # Get all of the information related to each source in sources:
    for s_id in sources:
        info = get_references_to_source(database, s_id)
        if info is not None:
            source_information.append(info)

    years = []
    names = []
    # Get all the years for all references made and names of sources
    for info in source_information:
        names.append(info["name"])

        # Update the years list with all possible years
        for year in info["references"].keys():
            if year not in years:
                years.append(year)

    years.sort()

    graphs = []

    # Get the number of references made to each source and update it in graphs
    for info in source_information:

        refs_made = []

        # Get the number of references per year
        for year in years:
            try:
                # There are references made to the source in year
                refs_made.append(info["references"][year])
            except KeyError:
                # There were not references made to the source in year
                refs_made.append(0)

        graphs.append(refs_made)

    return years, graphs, names

if __name__ == '__main__':
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

    # ===CNN==========================================================
    cnn1 = db.add_article(Article(
        "http://www.cnn.com/2014/10/29/us/"
        "new-york-murder-suicide/index.html?hpt=ju_c1",
        "CNNTitle1",
        "2005-10-29",
        "CNNAuthor1"))

    cnn2 = db.add_article(Article(
        "http://www.cnn.com/2014/10/29/us/"
        "new-york-murder-suicide/index.html?hpt=ju_c2",
        "CNNTitle2",
        "2006-10-29",
        "CNNAuthor2"))

    cnn3 = db.add_article(Article(
        "http://www.cnn.com/2014/10/29/us/"
        "new-york-murder-suicide/index.html?hpt=ju_c3",
        "CNNTitle3",
        "2007-10-29",
        "CNNAuthor3"))

    cnn4 = db.add_article(Article(
        "http://www.cnn.com/2014/10/29/us/"
        "new-york-murder-suicide/index.html?hpt=ju_c4",
        "CNNTitle4",
        "2010-10-30",
        "CNNAuthor4"))

    cnn5 = db.add_article(Article(
        "http://www.cnn.com/2014/10/29/us/"
        "new-york-murder-suicide/index.html?hpt=ju_c5",
        "CNNTitle5",
        "2010-10-23",
        "CNNAuthor5"))

    # ===Others=======================================================

    cbc6 = db.add_article(Article(
        "http://www.cbc.ca/2014/10/29/us/"
        "new-york-murder-suicide/index.html?hpt=ju_c1",
        "CNNTitle1",
        "2011-10-21",
        "CNNAuthor1"))

    wcbs7 = db.add_article(Article(
        "http://www.nytimes.com/2014/10/29/us/"
        "new-york-murder-suicide/index.html?hpt=ju_c2",
        "CNNTitle2",
        "2012-10-24",
        "CNNAuthor2"))

    nbc8 = db.add_article(Article(
        "http://www.nbcnews.com/2014/10/29/us/"
        "new-york-murder-suicide/index.html?hpt=ju_c3",
        "CNNTitle3",
        "2012-10-22",
        "CNNAuthor3"))

    rtl9 = db.add_article(Article(
        "http://www.rtl-longueuil.qc.ca/2014/10/29/us/"
        "new-york-murder-suicide/index.html?hpt=ju_c4",
        "CNNTitle4",
        "2013-10-26",
        "CNNAuthor4"))

    cpn10 = db.add_article(Article(
        "http://www.cpn.com/2014/10/29/us/"
        "new-york-murder-suicide/index.html?hpt=ju_c5",
        "CNNTitle5",
        "2013-10-15",
        "CNNAuthor5"))

    # CNN CBS NBC RTL CPN CBC
    print ("GETTING ALL THE SOURCES FROM DB:")
    print(db.get_sources().all())
    db.add_reference(Reference(1, 1, None))
    db.add_reference(Reference(1, 2, None))
    db.add_reference(Reference(1, 3, None))
    db.add_reference(Reference(1, 4, None))
    db.add_reference(Reference(2, 2, None))
    db.add_reference(Reference(2, 4, None))
    db.add_reference(Reference(2, 5, None))
    db.add_reference(Reference(2, 6, None))
    db.add_reference(Reference(3, 1, None))
    db.add_reference(Reference(3, 2, None))
    db.add_reference(Reference(3, 4, None))
    db.add_reference(Reference(4, 2, None))
    db.add_reference(Reference(4, 6, None))
    db.add_reference(Reference(5, 1, None))
    db.add_reference(Reference(5, 2, None))
    db.add_reference(Reference(5, 3, None))
    db.add_reference(Reference(5, 4, None))
    db.add_reference(Reference(5, 5, None))
    db.add_reference(Reference(5, 6, None))
    db.add_reference(Reference(6, 1, None))
    db.add_reference(Reference(6, 2, None))
    db.add_reference(Reference(6, 4, None))
    db.add_reference(Reference(6, 6, None))
    db.add_reference(Reference(7, 2, None))
    db.add_reference(Reference(7, 4, None))
    db.add_reference(Reference(8, 2, None))
    db.add_reference(Reference(8, 3, None))
    db.add_reference(Reference(9, 1, None))
    db.add_reference(Reference(9, 2, None))
    db.add_reference(Reference(9, 5, None))
    db.add_reference(Reference(9, 6, None))
    db.add_reference(Reference(10, 2, None))
    db.add_reference(Reference(10, 4, None))
    db.add_reference(Reference(10, 6, None))

    print ("Getting all the references from DB: ")
    #print (db.get_references().all()) 

    print "====plot_test1====="
    #plot_lines(db, "Source 1.png", [1])
    #plot_lines(db, "Source 2.png", [2])

    print "====PLOT ALL LINES===="
    #plot_lines(db, "TESTETAIOSTHT.png", [1, 2, 3, 4, 5, 6])

    print "====BARS===="
    sources = db.get_sources().all()
    s_list = []
    for s in sources:
        s_list.append(s.id)

    plot_bars(db, "bars", s_list)

    print "====MAYBE FEWER===="
    plot_bars(db, "bars", [1, 5, 6])

    db.close()
    os.remove("testvisual.db")