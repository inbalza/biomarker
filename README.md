# Biomarker
Traineeship project - creation of a knowledge graph for biomarker-disease associations

## Description
Biomarkers, or biological markers, refer to a broad subcategory of biomedical indicators. They are supposed to be objective and quantifiable characteristics of biological processes, states or conditions and are intended to be used in biomedical research and clinical decision making. Though biomarkers are often discussed in the scientific literature, the level of detail and the quality of their descriptions and annotations vary widely between different sources. The absence of a minimum information standard and a harmonized data model to clearly describe the concept of a biomarker poses a challenge to verify, integrate and analyze available biomarker information. <br>The aim of this project is to develop a semantic model applicable to capture the essential minimal information to clearly identify and describe biomarkers as meaningful data. In a next step, the model is applied to assess the quality of the provided biomarker data from selected data sources and to integrate this data into a large knowledge graph. This enables the re-use and interoperability of harmonized biomarker data in a research or clinical setting. 

## Tools

Owlready2 package for creating and editing owl files :
```
pip install owlready2
```
Protégé for editing and visualizing owl files: <br>
https://protege.stanford.edu/products.php#desktop-protege <br>
VOWL plugin for visualization: http://vowl.visualdataweb.org/protegevowl.html

## Content
- <b>BM Minimal info</b> defines the requirements for biomarker information <br>
- <b>bm_model.owl</b> is the semantic model to represent biomarker data<br>
- <b>resource_ext.py</b> and <b>harmonize.py</b> are Python scripts used to extract data from sources and use it in the onotlogy model<br>
- <b>SPARQL_queries.ipynb</b> is a Jupyter Notebook containing examples for querying the RDF graph with SPARQL 

Under 'results' folder:<br>
- CSV and json files with processed data from different sources
- <b>merged.xlsx</b> contains harmonized data in one table
- <b>bm_db.owl</b> is the RDF graph database, containing individuals
