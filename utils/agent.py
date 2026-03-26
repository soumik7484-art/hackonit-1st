from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq

class Agents:
    def __init__(self, medical_report=None, role=None, extra_info=None):
        self.medical_report = medical_report
        self.role = role
        self.extra_info = extra_info
        # Use your actual Groq API Key here
        self.model = ChatGroq(
            api_key="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", 
            model="llama-3.3-70b-versatile",
            temperature=0.0
        )
        self.prompt_template = self.create_prompt_template()

    def create_prompt_template(self):
        if self.role == "multi-disciplinary team":
            template = """
            Act like a multi-disciplinary team of healthcare professionals.
            You will receive medical reports from a Cardiologist, Psychologist, and Pulmonologist.
            Task: Review these reports, analyze them, and provide a list of 3 possible health issues.
            Return bullet points with reasons for each.
            
            Reports: {medical_report}
            """
        else:
            # Templates for individual specialists
            templates = {
                "Cardiologist": "Act like a Cardiologist. Review this report: {medical_report}. Focus on cardiac issues.",
                "Psychologist": "Act like a Psychologist. Review this report: {medical_report}. Focus on mental health/anxiety.",
                "Pulmonologist": "Act like a Pulmonologist. Review this report: {medical_report}. Focus on respiratory signs."
            }
            template = templates.get(self.role, "Analyze this report: {medical_report}")
        
        return PromptTemplate.from_template(template)

    def run(self):
        print(f"Agent {self.role} is running...")
        prompt = self.prompt_template.format(medical_report=self.medical_report if self.role != "multi-disciplinary team" else self.extra_info)
        try:
            response = self.model.invoke(prompt)
            return response.content
        except Exception as e:
            print(f"Error occurred: {e}")
            return None

# Specialized classes for easier inheritance
class Cardiologist(Agents):
    def __init__(self, medical_report):
        super().__init__(medical_report=medical_report, role="Cardiologist")

class Psychologist(Agents):
    def __init__(self, medical_report):
        super().__init__(medical_report=medical_report, role="Psychologist")

class Pulmonologist(Agents):
    def __init__(self, medical_report):
        super().__init__(medical_report=medical_report, role="Pulmonologist")

class MultiDisciplinaryTeam(Agents):
    def __init__(self, cardio_report, psych_report, pulm_report):
        combined_info = f"Cardio: {cardio_report}\nPsych: {psych_report}\nPulm: {pulm_report}"
        super().__init__(role="multi-disciplinary team", extra_info=combined_info)