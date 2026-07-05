from datetime import datetime

class Case:
    def __init__(self, case_id, investigator, description, evidence_path):
        self.case_id = case_id
        self.investigator = investigator
        self.description = description
        self.evidence_path = evidence_path
        self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        #forensic data to be filled later
        self.hashes={}
        self.metadata=[]
        self.timeline=[]
        self.recovered_files=[]

    #converting the case object to dictionary
    #since custom write onto JSON not possible

    def to_dict(self):                          
            return {
            "case_id":self.case_id,
            "investigator":self.investigator,
            "description":self.description,
            "evidence_path":self.evidence_path,
            "created_at":self.created_at,

    }