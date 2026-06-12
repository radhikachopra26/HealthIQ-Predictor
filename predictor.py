import os
import requests
from dotenv import load_dotenv

load_dotenv()


def calculate_health_score(glucose, haemoglobin, cholesterol):
    score = 100

    if glucose < 70:
        score -= 22
    elif 100 <= glucose <= 125:
        score -= 12
    elif glucose > 125:
        score -= 25

    if haemoglobin < 12:
        score -= 20
    elif haemoglobin > 16:
        score -= 15

    if cholesterol < 125:
        score -= 12
    elif cholesterol > 200:
        score -= 22

    if score >= 80:
        return score, "Low Risk"
    if score >= 60:
        return score, "Moderate Risk"
    return score, "High Risk"


def fallback_prediction(glucose, haemoglobin, cholesterol):
    score, risk_level = calculate_health_score(glucose, haemoglobin, cholesterol)
    findings = []
    actions = []

    if glucose < 70:
        findings.append("Low sugar level detected")
        actions.append("Maintain timely meals and avoid long fasting gaps")
        actions.append("Monitor dizziness, sweating, weakness or sudden fatigue")
    elif 70 <= glucose <= 99:
        findings.append("Glucose level appears within the normal range")
    elif 100 <= glucose <= 125:
        findings.append("Slightly elevated glucose level detected")
        actions.append("Reduce refined sugar and sugary beverages")
        actions.append("Include daily walking or light exercise")
        actions.append("Monitor fasting glucose regularly")
    else:
        findings.append("High sugar level detected")
        actions.append("Limit sugary foods and processed carbohydrates")
        actions.append("Follow a balanced meal plan")
        actions.append("Consult a doctor for diabetes screening")

    if haemoglobin < 12:
        findings.append("Low haemoglobin detected")
        actions.append("Include iron-rich foods such as leafy vegetables, pulses and dates")
        actions.append("Monitor tiredness, weakness or breathlessness")
    elif 12 <= haemoglobin <= 16:
        findings.append("Haemoglobin level appears within the normal range")
    else:
        findings.append("High haemoglobin level detected")
        actions.append("Maintain hydration and seek medical review if symptoms continue")

    if cholesterol < 125:
        findings.append("Low cholesterol level detected")
        actions.append("Review nutrition quality and maintain a balanced diet")
    elif 125 <= cholesterol <= 200:
        findings.append("Cholesterol level appears within the normal range")
    else:
        findings.append("High cholesterol level detected")
        actions.append("Reduce fried and oily food intake")
        actions.append("Increase fibre-rich foods such as oats, fruits and vegetables")
        actions.append("Exercise regularly and monitor lipid profile")

    if glucose < 70 or haemoglobin < 12:
        findings.append("Weakness or low BP-like symptoms may occur, but blood pressure cannot be confirmed without BP readings")

    if not actions:
        actions.append("Continue regular checkups, balanced diet, hydration and physical activity")

    return (
        f"Risk Level: {risk_level}\n\n"
        f"Health Score: {score}/100\n\n"
        f"Findings:\n• " + "\n• ".join(findings) + "\n\n"
        f"Suggested Actions:\n• " + "\n• ".join(actions) + "\n\n"
        f"Medical Advice:\nConsult a qualified doctor before taking medicines or supplements."
    )


def call_external_ai_api(glucose, haemoglobin, cholesterol):
    api_key = os.getenv("HUGGINGFACE_API_KEY")

    if not api_key:
        return None

    url = "https://api-inference.huggingface.co/models/google/flan-t5-base"

    prompt = (
        f"Generate a short patient-friendly health risk remark based on these values: "
        f"Glucose {glucose}, Haemoglobin {haemoglobin}, Cholesterol {cholesterol}. "
        f"Include risk level, findings, lifestyle suggestions and doctor consultation advice."
    )

    headers = {"Authorization": f"Bearer {api_key}"}
    payload = {"inputs": prompt, "parameters": {"max_new_tokens": 180}}

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=20)

        if response.status_code == 200:
            result = response.json()

            if isinstance(result, list) and result:
                generated_text = result[0].get("generated_text", "").strip()

                if generated_text:
                    score, risk_level = calculate_health_score(glucose, haemoglobin, cholesterol)
                    return (
                        f"Risk Level: {risk_level}\n\n"
                        f"Health Score: {score}/100\n\n"
                        f"AI Health Remarks:\n{generated_text}\n\n"
                        f"Medical Advice:\nConsult a qualified doctor before taking medicines or supplements."
                    )

        return None

    except requests.RequestException:
        return None


def generate_health_remark(glucose, haemoglobin, cholesterol):
    ai_result = call_external_ai_api(glucose, haemoglobin, cholesterol)

    if ai_result:
        return ai_result

    return fallback_prediction(glucose, haemoglobin, cholesterol)