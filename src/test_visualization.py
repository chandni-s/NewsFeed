import unittest
import os
import networkx as nx
import matplotlib.pyplot as plt
import rss
import web
from networkvisual import *
from source import Source
from article import Article
from keywords import Keyword
from response import Response
from database import Database
from reference import Reference

    
class TestVisualization(unittest.TestCase):
    global db
    #def setUp(self):
    
    db = Database("testvisuals.db")
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
    
    db.add_source(Source("www.qqc.ca"))
    db.add_keyword(Keyword(7, "QQC"))     
    
    #===CNN==========================================================
    cnn1 = db.add_article(Article("http://www.cnn.com/2014/10/29/us/new-york"
                                  "-murder-suicide/index.html?hpt=ju_c1", 
                                  "CNNTitle1", 
                                  "2010/10/29", 
                                  "CNNAuthor1"))
  
    cnn2 = db.add_article(Article("http://www.cnn.com/2014/10/29/us/new-york"
                                  "-murder-suicide/index.html?hpt=ju_c2", 
                             "CNNTitle2", 
                             "2010/10/29", 
                             "CNNAuthor2"))
    
    cnn3 = db.add_article(Article("http://www.cnn.com/2014/10/29/us/new-york"
                                  "-murder-suicide/index.html?hpt=ju_c3", 
                             "CNNTitle3", 
                             "2011/10/29", 
                             "CNNAuthor3"))    
    
    cnn4 = db.add_article(Article("http://www.cnn.com/2014/10/29/us/new-york"
                                  "-murder-suicide/index.html?hpt=ju_c4", 
                             "CNNTitle4", 
                             "2012/10/29", 
                             "CNNAuthor4"))    
   
    cnn5 = db.add_article(Article("http://www.cnn.com/2014/10/29/us/new-york"
                                  "-murder-suicide/index.html?hpt=ju_c5", 
                             "CNNTitle5", 
                             "2012/10/29", 
                             "CNNAuthor5"))  
    
    #===Others=======================================================

    
    cbc6 = db.add_article(Article("http://www.cbc.ca/2014/10/29/us/new-york-"
                                  "murder-suicide/index.html?hpt=ju_c1", 
                             "CNNTitle1", 
                             "2012/10/29", 
                             "CNNAuthor1"))
    
    wcbs7 = db.add_article(Article("http://www.nytimes.com/2014/10/29/us/new-"
                                   "york-murder-suicide/index.html?hpt=ju_c2", 
                             "CNNTitle2", 
                             "2012/10/29", 
                             "CNNAuthor2"))
    
    nbc8 = db.add_article(Article("http://www.nbcnews.com/2014/10/29/us/new-"
                                  "york-murder-suicide/index.html?hpt=ju_c3", 
                             "CNNTitle3", 
                             "2012/10/29", 
                             "CNNAuthor3"))    
    
    rtl9 = db.add_article(Article("http://www.rtl-longueuil.qc.ca/2014/10/29/"
                                  "us/new-york-murder-suicide/index.html?hpt=ju_c4", 
                             "CNNTitle4", 
                             "2013/10/29", 
                             "CNNAuthor4"))    
   
    cpn10 = db.add_article(Article("http://www.cpn.com/2014/10/29/us/new-york"
                                   "-murder-suicide/index.html?hpt=ju_c5", 
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
        
    #====== get_source_data ====================               
    def test_get_source_data_no_ref(self):
        '''(TestDBSource) -> None
        Test getting source when it does not exit in db
        '''
        edge_dic = get_source_data(db, 22)
        self.assertFalse(edge_dic)
   
    def test_get_source_data_one_ref(self):
        '''(TestDBSource) -> None
        Test getting source data based on id and get only 1 reference 
        associated with it
        '''
        edge_dic = get_source_data(db, 5)[1]
        self.assertTrue(len(edge_dic.keys())==1)
        self.assertTrue(edge_dic['2012']==1)
            
    def test_get_source_data_multi_ref(self):
        '''(TestDBSource) -> None
        Test getting source data based on id and get multiple references
        associated with it
        '''
        edge_dic = get_source_data(db, 2)[1]
        self.assertTrue((edge_dic['2011'])==1)
        self.assertTrue((edge_dic['2010'])==2)
        self.assertTrue((edge_dic['2013'])==2)
        self.assertTrue((edge_dic['2012'])==5)	
        
    #====== visual_arti_ref ====================       
    def test_visual_arti_ref_no_ref(self): 
        '''(TestDBArticle) -> None
        Test getting visual article with no reference in DB
        '''
        edge_dic = visual_arti_ref(db, 11)
        self.assertFalse(edge_dic)
   
    def test_visual_arti_ref_one_ref(self):
        '''(TestDBArticle) -> None
        Test getting only one reference for article based on id
        '''
        edge_dic = visual_arti_ref(db, 6)[1]
        self.assertTrue(len(edge_dic.keys())==1)
        self.assertTrue(edge_dic[('CNNTitle1', 'cbslocal.com')] == 1)
            
    def test_visual_arti_ref_multi_ref(self):
        '''(TestDBArticle) -> None
        Test getting miltiple references for article
        '''
        edge_dic = visual_arti_ref(db, 2)[1]
        self.assertTrue(len(edge_dic.keys())==3)
        self.assertTrue((edge_dic[('CNNTitle2', 'rtl-longueuil.qc.ca')])==1)
        self.assertTrue((edge_dic[('CNNTitle2', 'cbslocal.com')])==1)
        self.assertTrue((edge_dic['CNNTitle2', 'cbc.ca'])==1)
        
    #====== visual_child_source ====================       
    def test_visual_child_source_no_ref(self):
        '''(TestDBSource) -> None
        Test getting source reference without it being in db
        '''
        edge_dic = visual_child_source(db, 7)        
        self.assertFalse(edge_dic)
   
    def test_visual_child_source_one_ref(self):
        '''(TestDBSource) -> None
        Test getting only one child reference for source id given
        '''
        edge_dic = visual_child_source(db, 3)[1]
        self.assertTrue(len(edge_dic.keys())==1)
        self.assertTrue(edge_dic[('nbcnews.com', 'cbslocal.com')] == 1)
            
    def test_visual_child_source_multi_ref(self):
        '''(TestDBSource) -> None
        Test getting multiple child references for source id given
        '''
        edge_dic = visual_child_source(db, 1)[1]
        self.assertTrue(len(edge_dic.keys())==5)
        self.assertTrue((edge_dic[('cnn.com', 'cbc.ca')])==2)
        self.assertTrue((edge_dic[('cnn.com', 'rtl-longueuil.qc.ca')])==3)
        self.assertTrue((edge_dic[('cnn.com', 'cpn.com')])==1) 
        self.assertTrue((edge_dic[('cnn.com', 'cbslocal.com')])==5)
        self.assertTrue((edge_dic[('cnn.com', 'nbcnews.com')])==2)
        
    #====== visual_parent_source ====================       
    def test_visual_parent_source_no_ref(self):
        '''(TestDBSource) -> None
        Test getting parent reference for source id given without it being
        in db
        '''
        edge_dic = visual_parent_source(db, 7)        
        self.assertFalse(edge_dic)
   
    def test_visual_parent_source_one_ref(self):
        '''(TestDBSource) -> None
        Test getting only one parent reference for the source id given
        '''
        edge_dic = visual_parent_source(db, 5)[1]
        self.assertTrue(len(edge_dic.keys())==1)
        self.assertTrue(edge_dic[('cnn.com', 'cpn.com')] == 1)
            
    def test_visual_parent_source_multi_ref(self):
        '''(TestDBSource) -> None
        Test getting multiple parent references for source id given
        '''
        edge_dic = visual_parent_source(db, 2)[1]        
        self.assertTrue(len(edge_dic.keys())==6)
        self.assertTrue((edge_dic[('rtl-longueuil.qc.ca', 'cbslocal.com')])==1)
        self.assertTrue((edge_dic[('nbcnews.com', 'cbslocal.com')])==1)
        self.assertTrue((edge_dic[ ('nytimes.com', 'cbslocal.com')])==1) 
        self.assertTrue((edge_dic[('cpn.com', 'cbslocal.com')])==1)
        self.assertTrue((edge_dic[('cbc.ca', 'cbslocal.com')])==1) 
        self.assertTrue((edge_dic[('cnn.com', 'cbslocal.com')])==5) 
                                       
         
if __name__ == '__main__':
    unittest.main(exit=False)
    db.close()
    os.remove("testvisuals.db")          