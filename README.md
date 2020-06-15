# Biomarker
Traineeship project - creation of a knowledge graph for biomarker-disease associations

## Description
Biomarkers, or biological markers, refer to a broad subcategory of medical signs. They are objective and quantifiable characteristics of biological processes. Though already used in clinical trials, biomarker data vary widely between different resources.
The aim of this project is to help unifying biomarker information by creating a light ontology (OWL) model and applying it on data from different sources.

## Tools

Owlready2 package for creating and editing owl files :
```
pip install owlready2
```
Protégé for editing and visualizing owl files: <br>
https://protege.stanford.edu/products.php#desktop-protege <br>
VOWL plugin for visualization: http://vowl.visualdataweb.org/protegevowl.html

## Content
- <b>BM Minimal</b> info defines the requirements for biomarker information <br>
- <b>bm_model.owl</b> is the semantic model to represent biomarker data<br>
- <b>resource_ext.py</b> and <b>harmonize.py</b> are Python scripts used to extract data from sources and use it in the onotlogy model<br>

Under 'results' folder:<br>
- CSV and json files with processed data from different sources
- <b>merged.xlsx</b> contains harmonized data in one table
- <b>bm_db.owl</b> is the RDF graph database, containing individuals
- <b>SPARQL_queries.ipynb</b> notebook contains examples for querying the graph with SPARQL 
