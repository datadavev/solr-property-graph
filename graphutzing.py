import json
import graphviz
import requests
import IPython.display

def generateViz(recs, id_highlight=[],labels={}):
    # Visualize the data as a graph
    # Nodes with id in id_ighlight will be outlined in red
    # entries in labels will be added to the node labels
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
        rec_id = rec.get('id')
        _label = f"{rec_id}\n{rec.get('name_t')}\n{labels.get(rec_id,'')}".strip()
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
        self._relation_target = "relation_target"
        self._relation_type = "relation_type"


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


    def render(self, documents, results, idcol="id", show_docs=False, show_graph=True, add_label=None):
        ids = []
        labels = {}
        for _rec in results.get('result-set',{}).get('docs',[]):
            rec_id = _rec.get(idcol)
            ids.append(rec_id)
            if add_label is not None:
                labels[rec_id] = _rec.get(add_label, "")
        if show_docs:
            print(json.dumps(results, indent=2))
        if show_graph:
            IPython.display.display(generateViz(documents, id_highlight=ids, labels=labels))
    
    def ancestors(self, node_id, fl="*", rows=1000):
        expr = '''search(''' + self.collection + ''',
            q="{!join 
                    from='''+self._relation_target+''' 
                    to=id
                }{!graph 
                    from=_nest_parent_ 
                    to='''+self._relation_target+'''
                }({!child 
                    of='*:* -_nest_path_:*'
                }id:''' + node_id + ''')",
            fl="''' + fl + '''",
            rows=''' + str(rows) + '''
        )'''
        res = self.sendExpr(expr)
        return res

    def descendants(self, node_id, fl="*", rows=1000):
        expr = '''search(''' + self.collection + ''',
           q="{!parent which='*:* -_nest_path_:*'}({!graph 
            to=_nest_parent_ 
            from='''+self._relation_target+'''
        }'''+self._relation_target+''':'''+node_id + ''')",
        fl="'''+fl+'''",
        rows='''+str(rows)+'''
        )'''
        res = self.sendExpr(expr)
        return res

    def progenitors(self, rows=1000):
        incoming ='''select(
                    facet(''' + self.collection + ''',
                        q="'''+self._relation_target+''':*",
                        buckets="'''+self._relation_target+'''",
                        rows=100,
                        count(*)
                    ),
                    '''+self._relation_target+''' as id,
                    count(*) as cnt
                )'''
        outgoing = '''select(
                    rollup(
                        search(
                            ''' + self.collection + ''',
                            q="'''+self._relation_target+''':*",
                            fl="*",
                            rows=100
                        ),
                        over="_nest_parent_",
                        count(*)
                    ),
                    _nest_parent_ as id,
                    count(*) as cnt
                )'''
        expr = f'''complement(
            sort(
                {incoming}, 
                by="id asc"
            ),
            sort(
                {outgoing}, 
                by="id asc"
            ),
            on="id"
        )
        '''
        