
import networkx as nx

class AsmGraph(object):

    def __init__(self, sg_file, utg_file, ctg_file):
        self.sg_edges = {}
        self.utg_data = {}
        self.ctg_data ={}
        self.utg_to_ctg = {}
        self.node_to_ctg = {}
        self.node_to_utg = {}

        self.load_sg_data(sg_file)
        self.load_utg_data(utg_file)
        self.load_ctg_data(ctg_file)

        self.build_node_map()

    def load_sg_data(self, sg_file):

        with open(sg_file) as f:
            for l in f:
                l = l.strip().split()
                v, w = l[0:2]
                seq_id, b, e = l[2:5]
                b, e = int(b), int(b)
                score, idt = l[5:7]
                scroe, idt = int(score), float(idt)
                type_ = l[7]
                self.sg_edges[ (v, w) ] = ( (seq_id, b, e), scroe, idt, type_)


    def load_utg_data(self, utg_file):

        with open(utg_file) as f:
            for l in f:
                l = l.strip().split()
                s, v, t = l[0:3]
                type_, length, score = l[3:6]
                length, score = int(length), int(score)
                path_or_edges = l[6]
                self.utg_data[ (s,t,v) ] = ( type_, length, score, path_or_edges)
                

    def load_ctg_data(self, ctg_file):
        with open(ctg_file) as f:
            for l in f:
                l = l.strip().split()
                ctg_id, ctg_type = l[0:2]
                start_edge = l[2]
                end_node = l[3]
                length = int(l[4])
                score = int(l[5])
                path = list( ( e.split("~") for e in l[6].split("|") ) ) 
                self.ctg_data[ ctg_id ] = ( ctg_type, start_edge, end_node,  length, score, path )
                for u in path:
                    s, v, t = u
                    #rint s,v,t
                    type_, length, score, path_or_edges =  self.utg_data[ (s,t,v) ] 
                    if type_ != "compound":
                        self.utg_to_ctg[ (s, t, v) ] = ctg_id
                    else:
                        for svt in path_or_edges.split("|"):
                            s, v, t = svt.split("~")
                            self.utg_to_ctg[ (s, t, v) ] = ctg_id


    def get_sg_for_utg(self, utg_id):
        sg = nx.DiGraph()
        type_, length, score, path_or_edges =  self.utg_data[ utg_id ]
        if type_ == "compound":
            for svt in path_or_edges.split("|"):
                s, v, t = svt.split("~")
                type_, length, score, one_path =  self.utg_data[ (s, t, v) ]
                one_path = one_path.split("~")
                sg.add_path(one_path)
        else:
            one_path = path_or_edges.split("~")
            sg.add_path(one_path)
        return sg


    def get_sg_for_ctg(self, ctg_id):
        sg = nx.DiGraph()
        utgs = []
        path = self.ctg_data[ctg_id][-1]
        for s, v, t in path:
            type_, length, score, path_or_edges =  self.utg_data[ (s, t, v) ]
            utgs.append( (type_, path_or_edges) )

        for t, utg in utgs:
            if t == "simple":
                one_path = utg.split("~")
                sg.add_path(one_path)
            elif t == "compound":
                for svt in utg.split("|"):
                    s, v, t = svt.split("~")
                    type_, length, score, one_path =  self.utg_data[ (s, t, v) ]
                    one_path = one_path.split("~")
                    sg.add_path(one_path)
        
        return sg


    def build_node_map(self):

        for ctg_id in self.ctg_data:
            sg = self.get_sg_for_ctg( ctg_id )
            for n in sg.nodes():
                self.node_to_ctg.setdefault(n, set())
                self.node_to_ctg[n].add(ctg_id)

                
        for u_id in self.utg_data:
            if self.utg_data[u_id][0] == "compound":
                continue
            sg = self.get_sg_for_utg( u_id )
            for n in sg.nodes():
                self.node_to_utg.setdefault(n, set())
                self.node_to_utg[n].add( u_id )
