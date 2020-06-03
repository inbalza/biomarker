# Biomarker
Traineeship project - creation of a knowledge graph for biomarker-disease associations

## Description
Biomarkers, or biological markers, refer to a broad subcategory of medical signs. They are objective and quantifiable characteristics of biological processes. Though already used in clinical trials, biomarker data vary widely between different resources.
The aim of this project is to help unifying biomarker information by creating a light ontology (OWL) model and applying it on data from different resources.

## Usage

*create_bm_ontology.py* creates the owl ontology using Owlready2 package, can be installed by :
```
pip install owlready2
```

*harmonize.py* and *resource_ext.py* extract data sources and add instances to ontology
*query_graph.py* uses SPARQL to query instances created in ontology

Owl ontology models can be visualized with Protégé 
https://protege.stanford.edu/products.php#desktop-protege
VOWL plugin for visualization: http://vowl.visualdataweb.org/protegevowl.html
