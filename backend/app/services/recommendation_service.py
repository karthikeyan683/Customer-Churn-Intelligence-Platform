def generate_recommendations(customer, churn_probability, risk_level):
    recommendations = []

    # 1. Satisfaction
    if customer.satisfaction_score is not None:
        if customer.satisfaction_score <= 5:
            recommendations.append({
                "priority": "High",
                "category": "Customer Experience",
                "action": "Contact the customer to understand dissatisfaction and resolve major concerns."
            })

        elif customer.satisfaction_score <= 7:
            recommendations.append({
                "priority": "Medium",
                "category": "Customer Experience",
                "action": "Schedule a customer experience follow-up."
            })

    # 2. Support tickets
    if customer.support_tickets >= 5:
        recommendations.append({
            "priority": "High",
            "category": "Support",
            "action": "Assign priority support and proactively resolve recurring issues."
        })

    elif customer.support_tickets >= 3:
        recommendations.append({
            "priority": "Medium",
            "category": "Support",
            "action": "Review recent support tickets and follow up with the customer."
        })

    # 3. Contract
    if customer.contract_type == "Month-to-month":
        recommendations.append({
            "priority": "High",
            "category": "Retention",
            "action": "Offer an annual or long-term contract with a suitable retention benefit."
        })

    # 4. Monthly charges
    if customer.monthly_charges >= 90:
        recommendations.append({
            "priority": "Medium",
            "category": "Pricing",
            "action": "Review pricing and consider a personalized retention offer."
        })

    # 5. Tenure
    if customer.tenure_months <= 6:
        recommendations.append({
            "priority": "Medium",
            "category": "Onboarding",
            "action": "Provide onboarding assistance and early-stage customer engagement."
        })

    # 6. Internet service
    if customer.internet_service == "Fiber optic":
        recommendations.append({
            "priority": "Medium",
            "category": "Service Quality",
            "action": "Check service quality and investigate any connectivity-related issues."
        })

    # 7. Overall risk
    if risk_level == "High":
        recommendations.append({
            "priority": "Critical",
            "category": "Churn Prevention",
            "action": "Initiate an immediate retention campaign for this customer."
        })

    elif risk_level == "Medium":
        recommendations.append({
            "priority": "Medium",
            "category": "Churn Prevention",
            "action": "Add the customer to a proactive retention monitoring list."
        })

    else:
        recommendations.append({
            "priority": "Low",
            "category": "Customer Engagement",
            "action": "Continue regular engagement and monitor future risk changes."
        })

    return recommendations
