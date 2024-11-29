import sys
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfpage import PDFTextExtractionNotAllowed
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from io import StringIO
from pdfminer.layout import LAParams
from pdfminer.converter import TextConverter

# TO-DO: figure out how to scrape also languages which are hard to find in text, like C, R, etc.
skills = {'aws':'AWS','gcp':'GCP','azure':'Azure','javascript':'Javascript','typescript':'Typescript','react':'React','docker':'Docker',
        'jenkins':'Jenkins','html':'HTML','css':'CSS','nodejs':'NodeJS','expressjs':'ExpressJS','mongodb':'MongoDB','redis':'Redis','sql':'SQL',
        'nosql':'NoSQL','mysql':'MySQL','graphql':'GraphQL','java':'Java','spring':'Spring','maven':'Maven','hibernate':'Hibernate','python':'Python',
        'flask':'Flask','sap':'SAP', 'abap':'ABAP', 'cloud':'Cloud','rest':'REST','restful':'Restful API','http':'HTTP','tcp':'TCP',
        'udp':'UDP','vmware':'VMWare', 'vmbox':'VMBox', 'k8s':'Kubernetes', 'kubernetes':'Kubernetes','elasticsearch':'ElasticSearch',
        'microservices':'Microservices','mssql':'Microsft SQL', 'c++':'C++', 'c#':'C#','assembly':'Assembly','datastructures':'Data Structures',
        'algorithms':'Algorithms', 'tableau':'Tableau', 'numpy':'NumPy', 'tensorflow':'TensorFlow'}


class MyParser(object):
    def __init__(self, pdf):
        ## Snipped adapted from Yusuke Shinyamas 
        #PDFMiner documentation
        # Create the document model from the file
        parser = PDFParser(open(pdf, 'rb'))
        document = PDFDocument(parser)
        # Try to parse the document
        if not document.is_extractable:
            raise PDFTextExtractionNotAllowed
        # Create a PDF resource manager object 
        # that stores shared resources.
        rsrcmgr = PDFResourceManager()
        # Create a buffer for the parsed text
        retstr = StringIO()
        # Spacing parameters for parsing
        laparams = LAParams()
        codec = 'utf-8'

        # Create a PDF device object
        device = TextConverter(rsrcmgr, retstr, 
                                codec = codec, 
                                laparams = laparams)
        # Create a PDF interpreter object
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        # Process each page contained in the document.
        for page in PDFPage.create_pages(document):
            interpreter.process_page(page)
        
        self.records            = []
        
        lines = retstr.getvalue().splitlines()
        for line in lines:
            self.handle_line(line)
    
    def handle_line(self, line):
        # Customize your line-by-line parser here
        self.records.append(line)

def strip_dots_and_commas(text):
    return ' '.join(text).replace('.',' ').replace(',',' ').replace('   ',' ').replace('  ',' ')

def collect_skills(text):
    lowercase_text = text.lower()
    return list(map(lambda skill_key: skills[skill_key], list(filter(lambda skill: lowercase_text.count(skill)>0, skills))))
    
def collect_education(text):
    # use natural language procession?
    return -1

def collect_experience(text):
    # use natural language procession?
    return -1

if __name__ == '__main__':
    # parse_resume_and_upload_to_db()
    p = MyParser('uploads/Dan_CV.pdf')
    text = strip_dots_and_commas(p.records)
    print(collect_skills(text))