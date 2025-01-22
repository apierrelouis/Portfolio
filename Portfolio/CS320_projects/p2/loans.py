import json
import zipfile
import csv
from io import TextIOWrapper

race_lookup = {
    "1": "American Indian or Alaska Native",
    "2": "Asian",
    "3": "Black or African American",
    "4": "Native Hawaiian or Other Pacific Islander",
    "5": "White",
    "21": "Asian Indian",
    "22": "Chinese",
    "23": "Filipino",
    "24": "Japanese",
    "25": "Korean",
    "26": "Vietnamese",
    "27": "Other Asian",
    "41": "Native Hawaiian",
    "42": "Guamanian or Chamorro",
    "43": "Samoan",
    "44": "Other Pacific Islander"
}

class Applicant:
    def __init__(self, age, race):
        self.age = age
        self.race = set()
        for r in race:
            if str(r) in race_lookup:
                self.race.add(race_lookup[str(r)])
    
    def __repr__(self):
        return f"Applicant('{self.age}', {sorted(self.race)})"
        #return f"Applicant('{self.age}', [{', '.join(str(s) for s in self.race)}])"
    
    def lower_age(self):
        if "-" in self.age:
            return float(self.age[:self.age.find("-")])
        elif ">" in self.age:
            return float(self.age[1:])
        elif "<" in self.age:
            return float(self.age[1:])
    
    def __lt__(self, other):
        if isinstance(other, Applicant):
            return int(self.lower_age()) < int(other.lower_age())
        else:
            raise TypeError(f"Expected type Applicant for comparison but got type {type(other)}")
            

class Loan:
    def __init__(self, values):
        #strings like "NA" and "Exempt" that represent missing values can be -1 when you convert to floats
        '''
        if values["loan_amount"] == "NA" or values["loan_amount"] == "Exempt":
            self.loan_amount = float(values["loan_amount"])
        else:
            self.loan_amount = -1
        if values["property_value"] == "NA" or values["property_value"] == "Exempt":
            self.property_value = float(values["property_value"])
        else:
            self.property_value = -1
        if values["interest_rate"] == "NA" or values["interest_rate"] == "Exempt":
            self.interest_rate = float(values["interest_rate"])
        else:
            self.interest_rate = -1
        '''
        try:
            self.loan_amount = float(values["loan_amount"])
        except ValueError:
            self.loan_amount = -1
        try:
            self.property_value = float(values["property_value"])
        except ValueError:
            self.property_value = -1
        try:
            self.interest_rate = float(values["interest_rate"])
        except ValueError:
            self.interest_rate = -1
        
        self.applicants = []
        r1 = set()
        for v in values:
            if "applicant_race-" in v:
                if "co-" not in v:
                    r1.add(values[v])
        self.applicants.append(Applicant(values["applicant_age"], r1))
        if values["co-applicant_age"] != "9999":
            r2 = set()
            for v in values:
                if "co-applicant_race-" in v:
                    r2.add(values[v])
            self.applicants.append(Applicant(values["co-applicant_age"], r2))
        
        
    def __str__(self):
        return f"<Loan: {self.interest_rate}% on ${self.property_value} with {len(self.applicants)} applicant(s)>"
        
    def __repr__(self):
        return f"<Loan: {self.interest_rate}% on ${self.property_value} with {len(self.applicants)} applicant(s)>"
    
    
    def yearly_amounts(self, yearly_payment):
        # TODO: assert interest and amount are positive
        assert self.interest_rate > 0, "Interest rate is negative or NA"
        assert self.loan_amount > 0, "Loan amount is negative or NA"
        
        amt = self.loan_amount

        while amt > 0:
            yield amt
            # TODO: add interest rate multiplied by amt to amt
            amt += self.interest_rate * amt / 100
            # TODO: subtract yearly payment from amt
            amt -= yearly_payment
    
    
class Bank:
    def __init__(self, name):
        self.name = None
        self.lei = None
        self.loans = []
        with open("banks.json", 'r') as b:
            banks = json.load(b)
            for bank in banks:
                if bank['name'] == name:
                    self.name = name
                    self.lei = bank['lei']
        
        with zipfile.ZipFile('wi.zip', 'r') as zf:
            with zf.open('wi.csv') as wi:
                rdr = csv.DictReader(TextIOWrapper(wi))
                for loan in rdr:
                    if loan['lei'] == self.lei:
                        self.loans.append(Loan(loan))
        
        
    def __getitem__(self, idx):
        return self.loans[idx]
    
    def __len__(self):
        return len(self.loans)
        
#%load_ext autoreload
#%autoreload 2