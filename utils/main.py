import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from utils.agent import Cardiologist, Psychologist, Pulmonologist, MultiDisciplinaryTeam

# 1. Load the medical report
with open("medical_report.txt", "r") as file:
    medical_report = file.read()

# 2. Initialize the Specialized Agents
agents = {
    "Cardiologist": Cardiologist(medical_report),
    "Psychologist": Psychologist(medical_report),
    "Pulmonologist": Pulmonologist(medical_report)
}

# 3. Helper function to get response from an agent
def get_response(name, agent):
    print(f"{name} is analyzing...")
    response = agent.run()
    return name, response

# 4. Run agents concurrently (at the same time) to save time
responses = {}
with ThreadPoolExecutor() as executor:
    futures = [executor.submit(get_response, name, agent) for name, agent in agents.items()]
    for future in as_completed(futures):
        name, response = future.result()
        responses[name] = response

# 5. Pass individual reports to the Multi-Disciplinary Team for final review
team_agent = MultiDisciplinaryTeam(
    cardio_report=responses.get("Cardiologist"),
    psych_report=responses.get("Psychologist"),
            pulm_report=responses.get("Pulmonologist")
)

final_diagnosis = team_agent.run()

# 6. Save the final output
if not os.path.exists("results"):
    os.makedirs("results")

with open("results/final_diagnosis.txt", "w") as f:
    f.write(final_diagnosis)

print("\n--- Final Diagnosis Saved to results/final_diagnosis.txt ---")
print(final_diagnosis)