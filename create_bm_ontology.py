from owlready2 import *

bm = get_ontology("file://D:/ontoforce/model/bm_model2.owl").load()

print("Loading DOID ontology")
#doid = get_ontology("http://purl.obolibrary.org/obo/doid/doid-merged.owl").load()
doid = get_ontology("file://D:/ontoforce/model/doid-merged.owl").load()

print("Loading UBERON ontology")
#uberon = get_ontology("http://purl.obolibrary.org/obo/uberon.owl").load()
uberon = get_ontology("file://D:/ontoforce/model/uberon.owl").load()

obo = get_namespace("http://purl.obolibrary.org/obo/")

# Retrieve relevant IDs from ontologies
disease = doid.search_one(label = "disease")
anatomical_entity = uberon.search_one(label = "anatomical entity")

with bm:

    print("Creating classes")
    class Biomarker(Thing):
        pass
    class DiagnosticBM(Biomarker):
        pass
    class PrognosticBM(Biomarker):
        pass
    class PredictiveBM(Biomarker):
        pass
    class RiskBM(Biomarker):
        pass
    class BiomarkerType(Thing):
        pass
    class MolecularBM(BiomarkerType):
        pass
    class PhysiologicBM(BiomarkerType):
        pass
    class RadiographicBM(BiomarkerType):
        pass

    class BMPanel(Thing):
        pass
    
    print("Creating properties")
    # Properties for biomarker minimal information
    class indicatorOf(ObjectProperty):
        domain = [Biomarker]
        range = [disease]
    class hasEvidence(DataProperty): 
        domain = [Biomarker]
        range = [str] # PMID
    class hasEvidenceLevel(DataProperty):
        domain = [Biomarker]
        range = [str] 
    class inPanel(DataProperty):
        domain = [Biomarker]
        range = [bool] # False - single bm, True - a part of a bm panel
    class measuredIn(ObjectProperty):
        domain = [BiomarkerType]
        range = [anatomical_entity] # Source or Lcation
    class assesedBy(DataProperty):
        domain = [BiomarkerType]
        range = [str] # Assay, Experiment, Technology (one or many) - still has to be linked to an existing ontology

    # optional property - additional info
    class hasDescription(DataProperty):
        domain = [Biomarker]
        range = [str]

    # optional property - for biomarkers in clinical trial
    class hasClinicalTrialID(DataProperty):
        domain = [Biomarker]
        range = [str]

    # Properties for MolecularBM
    class hasMolecularType(DataProperty):
        domain = [MolecularBM]
        range = [str] # protein,metabolite,nucleic acid - or gene,variation, 
    class hasMolecularID(DataProperty):
        domain = [MolecularBM]
        range = [str] # Uniprot, HGNC, Ensemble, chembl,...
    
    # Properties for predictiveBM
    class hasTrearment(DataProperty):
        domain = [PredictiveBM]
        range = [str] # name of medicine or other treatment
    class hasResponse(DataProperty):
        domain = [PredictiveBM]
        range = [str] # sensitive / resistant

    # Biomarker panel will be linked to single biomarker instances
    class hasComponent(ObjectProperty):
        domain = [BMPanel]
        range = [Biomarker]


bm.save()
print("Ontology is saved to file")
