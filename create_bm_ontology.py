from owlready2 import *

biomarker = get_ontology("file://D:/ontoforce/model/bm_model.owl").load()

with biomarker:

    print("Creating classes")
    class Biomarker(Thing):
        pass
    class BiomarkerType(Biomarker):
        pass
    class BiomarkerUsage(Biomarker):
        pass
    class DiagnosticBM(BiomarkerUsage):
        pass
    class PrognosticBM(BiomarkerUsage):
        pass
    class PredictiveBM(BiomarkerUsage):
        pass
    class ResponseBM(BiomarkerUsage):
        pass
    class RiskBM(BiomarkerUsage):
        pass
    class MolecularBM(BiomarkerType):
        pass
    class PhysiologicBM(BiomarkerType):
        pass
    class RadiographicBM(BiomarkerType):
        pass

    class ComplexBM(Thing):
        pass
    class Disease(Thing):
        pass
    class AnatomicalEntity(Thing):
        pass
    class AssayTest(Thing):
        pass
    class Treatment(Thing):
        pass
    class Publication(Thing):
        pass

    print("Creating properties")
    # Properties for biomarker minimal information
    class indicatorOf(ObjectProperty):
        domain = [Biomarker]
        range = [Disease]
    class hasIndicator(ObjectProperty):
        domain = [Disease]
        range = [Biomarker]
        inverse_property = indicatorOf
    class hasEvidenceLevel(DataProperty):
        domain = [Biomarker]
        range = [str]
    class hasEvidence(ObjectProperty): 
        domain = [Biomarker]
        range = [Publication]
    class measuredIn(ObjectProperty):
        domain = [Biomarker]
        range = [AnatomicalEntity] # Source or Location
    class measuredBy(ObjectProperty):
        domain = [Biomarker]
        range = [AssayTest] # Assay, Experiment, Technology (one or many) 

    # optional property - additional info
    class hasDescription(DataProperty):
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
    class hasTrearment(ObjectProperty):
        domain = [PredictiveBM | ResponseBM]
        range = [Treatment] # name of medicine or other treatment
    
    # Biomarker panel will be linked to single biomarker instances
    class hasComponent(ObjectProperty):
        domain = [ComplexBM]
        range = [Biomarker]


biomarker.save()
print("Ontology is saved to file")
