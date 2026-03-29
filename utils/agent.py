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
        template = """
You are a strict medical report analyzer AI.

Your job is to analyze medical prescriptions or reports from OCR text.

IMPORTANT RULES:
1. ONLY use information that is explicitly present in the report.
2. DO NOT assume, guess, or generate new diseases or complications.
3. DO NOT add cardiovascular, respiratory, or psychological issues unless clearly mentioned.
4. DO NOT over-analyze medicines or create risk factors unless directly stated.
5. If something is not present, say "Not mentioned".

OUTPUT FORMAT (STRICT JSON):

{{
  "patient_info": {{
    "age": "",
    "gender": "",
    "date": ""
  }},
  "diagnosis": "",
  "symptoms": [],
  "medicines": [
    {{
      "name": "",
      "dosage": "",
      "duration": ""
    }}
  ],
  "advice": [],
  "summary": "",
  "warnings": []
}}

INSTRUCTIONS:
- Extract name, age, gender exactly as written in the report.
- Extract diagnosis exactly as written.
- Extract symptoms from "Chief Complaints" or "Current Symptoms".
- Extract all medicines with dosage and duration.
- Extract advice exactly as written.
- Summary should be simple and factual (2–3 lines only).
- Warnings should ONLY include:
  * Critical/severe symptoms explicitly mentioned (e.g., "severe chest pain", "sudden fainting", "severe bleeding")
  * Abnormal lab values explicitly noted as abnormal (e.g., "Low Hemoglobin: 11.2 g/dL", "High Blood Pressure: 180/120")
  * Any explicit contraindication or urgent alerts in the report
  * Medication side effects or allergies explicitly mentioned
- Return exact wording from the report for warnings, not your interpretation.
- If no such critical issues are explicitly mentioned, return empty array [].

INPUT TEXT:
{medical_report}
"""
        return PromptTemplate.from_template(template)

    def run(self):
        print(f"Agent {self.role} is running...")
        # Manually format the template to avoid langchain formatting issues
        template_str = self.prompt_template.template
        prompt = template_str.replace("{medical_report}", self.medical_report if self.role != "multi-disciplinary team" else self.extra_info)
        try:
            response = self.model.invoke(prompt)
            content = response.content.strip()
            # Remove markdown code block if present
            if content.startswith("```json"):
                content = content[7:].strip()
            if content.startswith("```"):
                content = content[3:].strip()
            if content.endswith("```"):
                content = content[:-3].strip()
            return content
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

class StrictMedicalAnalyzer(Agents):
    def __init__(self, medical_report):
        super().__init__(medical_report=medical_report, role="strict_analyzer")

    def create_prompt_template(self):
        template = """
You are a medical prescription analyzer and assistant.

Your job is to:
1. Extract exact structured information from the given medical report
2. Provide safe, general health advice for the patient

STRICT RULES:
- Do NOT invent diseases or conditions
- Only extract what is present in the report
- If something is missing, return empty array []
- Advice must be general, safe, and non-harmful
- NEVER give extreme or risky medical suggestions
- ALWAYS include "Consult a doctor" guidance in warnings

For medicines:
- Extract each medicine with its name, dosage, and duration
- If dosage or duration is not specified, use "Not specified"
- Format as array of objects: [{"name": "Medicine Name", "dosage": "100mg", "duration": "7 days"}, ...]

OUTPUT FORMAT (STRICT JSON ONLY):

Output a JSON object with these exact fields:
- name (string)
- age (string)  
- gender (string)
- diagnosis (string)
- symptoms (array of strings)
- medicines (array of objects, each with name, dosage, duration fields)
- report_advice (array of strings)
- ai_advice (array of strings)
- warnings (array of strings)
- summary (string)

IMPORTANT RULES:

1. ai_advice is MANDATORY:
   - Must contain at least 3 points
   - Even if report has no advice, generate helpful general advice

2. ai_advice examples:
   - "Take proper rest"
   - "Drink plenty of water"
   - "Eat a balanced diet"
   - "Avoid oily and spicy foods"
   - "Complete the full course of medicines"

3. IMPORTANT: If the medical report mentions "water intoxication" or "hyponatremia", DO NOT include "Drink plenty of water" in ai_advice.

4. For report_advice and warnings:
   - If no advice or warnings found in the report, include: "it is hard to give advise at this condition please consult your doctor"
   - But for ai_advice, always provide general advice
   - warnings MUST include:
     - When to consult a doctor
     - Mild precautions
     - Example:
       - "Consult a doctor if symptoms worsen"
       - "Seek medical help if fever persists more than 2-3 days"
       - "Do not skip prescribed medication"

4. summary:
   - Short and clear explanation of the report in simple English

INPUT REPORT:
{medical_report}

IMPORTANT ADDITION:
- If giving advice, ALWAYS include a line suggesting:
  "Consult a doctor for proper medical guidance specific to your condition."
"""
        return PromptTemplate.from_template(template)