import json
import graphviz
import requests
import IPython.display

def generateViz(recs, id_highlight=[]):
    # Visualize the data as a graph
    # Nodes with id in id_ighlight will be outlined in red
    colors = {
        'subsample-of':'green',
        'analysis-of':'blue'
    }
    kinds = {
        'sample':'ellipse',
        'analysis':'diamond',
        'publication':'note',
    }
    g = graphviz.Digraph()
    g.attr('graph', rankdir='BT', size="7")
    for rec in recs:
        _label = f"{rec.get('id')}\n{rec.get('name_t')}"
        _shape = kinds.get(rec.get('is_s',None),'plain')
        _color = "black"
        if rec.get('id') in id_highlight:
            _color='red'
        g.node(rec.get('id'), label=_label, color=_color, shape=_shape)
        for rel in rec.get('edges', {}):
            g.edge(
                rec.get('id'), 
                rel.get('target_s'), 
                label=rel.get('relation_type_s'),
                color=colors.get(rel.get('relation_type_s'),'black')
            )
    return g

class SolrConnection:

    def __init__(self, server="http://localhost:18983", collection="reltest"):
        self.server = server
        self.solr = f"{server}/solr"
        self.collection = collection


    def addField(self, name, ftype="string", indexed="true", stored="true"):
        url = f"{self.solr}/{self.collection}/schema"
        data = {
            "add-field":{
                "name": name,
                "type": ftype,
                "indexed": indexed,
                "stored": stored
            }
        }
        headers = {"Content-Type":"application/json"}
        res = requests.post(url, headers=headers, data=json.dumps(data))
        print(res.text)


    def createCollection(self):
        url = f"{self.solr}/admin/collections"
        params = {
            "action":"CREATE",
            "name":self.collection,
            "numShards":1,
            "collection.configName":"_default",
        }
        res = requests.get(url, params=params)
        print(res.text)


    def deleteCollection(self):
        url = f'{self.server}/api/c/{self.collection}'
        res = requests.delete(url)
        #res = "delete op disabled"
        return res.text


    def addDocument(self, doc):
        url = f"{self.solr}/{self.collection}/update"
        headers = {
            "Content-type":"application/json"
        }
        add_doc = {
            "add":{
                "doc": doc
            }
        }
        data = json.dumps(add_doc, indent=2)
        params = {"commit":"true"}
        res = requests.post(url, headers=headers, data=data, params=params)
        if res.status_code != 200:
            print(res.status_code)
            print(res.text)
            return 0
        return 1
    

    def select(self, q="*:*", fl="*", rows=100):
        url = f"{self.solr}/{self.collection}/select"
        params = {
            "wt":"json",
            "omitHeader": "true",
            "q":q,
            "fl":fl,
            "rows":rows
        }
        headers = {
            "Accept": "application/json"
        }
        res = requests.get(url, params=params, headers=headers)
        return res.json()


    def query(self, data={"q":"*:*"}):
        url = f"{self.solr}/{self.collection}/query"
        headers = {
            "Accept": "application/json"
        }
        res = requests.post(url, data=data, headers=headers)
        return res.json()


    def sendExpr(self, expr):
        url = f'{self.solr}/{self.collection}/stream'
        headers = {
            "Accept": "application/json"
        }
        res = requests.post(url,data={"expr":expr}, headers=headers)
        return res.json()


    def squery(self, q="*:*", fl="*", sort="id ASC", rows=100):
        selection_method = "search"
        params = [
            f'q="{q}"',
            f'fl="{fl}"',
            f'rows={rows}',
        ]
        expr =  f'{selection_method}({self.collection},{",".join(params)},qt="/select")'
        return self.sendExpr(expr)


    def render(self, documents, results, idcol="id", show_docs=False, show_graph=True):
        ids = []
        for _rec in results.get('result-set',{}).get('docs',[]):
            ids.append(_rec.get(idcol))
        if show_docs:
            print(json.dumps(results, indent=2))
        if show_graph:
            IPython.display.display(generateViz(documents, id_highlight=ids))
    
