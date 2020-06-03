from owlready2 import *

###############################
#   Query graph with SPARQL   #
###############################

my_world = World()
onto = my_world.get_ontology("file://D:/ontoforce/model/model_with_instances.owl").load()
graph = my_world.as_rdflib_graph()

bm_list = list(graph.query("""SELECT ?s WHERE {
  ?s <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <file://D:/ONTOFORCE/model/bm.owl#MolecularBM>.
}"""))
print("Molecular Biomarkers:")
for bm in bm_list: print(bm)

bm_list = list(graph.query("""SELECT ?s WHERE {
  ?s <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <file://D:/ONTOFORCE/model/bm.owl#PrognosticBM>.
}"""))
print("Prognostic Biomarkers:")
for bm in bm_list: print(bm)

bm_list = list(graph.query("""SELECT ?s WHERE {
  ?s <file://D:/ONTOFORCE/model/bm.owl#hasEvidenceLevel> 'clinical use'.
}"""))
print("Biomarkers in clinical use:")
for bm in bm_list: print(bm)

bm_list = list(graph.query("""SELECT ?s1 WHERE {
  ?s1 ?p1 ?o1 .
  ?o1 ?p2 <file://D:/ONTOFORCE/model/bm.owl#measuredIn> .
  ?o1 ?p3 <http://purl.obolibrary.org/obo/UBERON_0001836> .
}"""))
print("Biomarkers measured in saliva:")
for bm in bm_list: print(bm)

bm_list = list(graph.query("""SELECT ?s1 WHERE {
  ?s1 ?p1 ?o1 .
  ?o1 ?p2 <file://D:/ONTOFORCE/model/bm.owl#indicatorOf> .
  ?o1 ?p3 <http://purl.obolibrary.org/obo/DOID_1612> .
}"""))
print("Biomarkers that are indicators of breast cancer:")
for bm in bm_list: print(bm)

bm_list = list(graph.query("""SELECT ?s1 WHERE {
  ?s1 <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <file://D:/ONTOFORCE/model/bm.owl#PrognosticBM> .
  ?s1 ?p1 ?o1 .
  ?o1 ?p2 <file://D:/ONTOFORCE/model/bm.owl#indicatorOf> .
  ?o1 ?p3 <http://purl.obolibrary.org/obo/DOID_1612> .
}"""))
print("Prognostic biomarkers of breast cancer:")
for bm in bm_list: print(bm)

bm_list = list(graph.query("""SELECT ?s1 WHERE {
  ?s1 <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <file://D:/ONTOFORCE/model/bm.owl#RiskBM> .
  ?s1 ?p1 ?o1 .
  ?o1 ?p2 <file://D:/ONTOFORCE/model/bm.owl#indicatorOf> .
  ?o1 ?p3 <http://purl.obolibrary.org/obo/DOID_1612> .
  ?s1 ?p1 ?o2 .
  ?o2 ?p2 <file://D:/ONTOFORCE/model/bm.owl#measuredIn> .
  ?o2 ?p3 <http://purl.obolibrary.org/obo/UBERON_0001836> .
}"""))
print("Risk biomarkers of breast cancer measured in saliva:")
for bm in bm_list: print(bm)
