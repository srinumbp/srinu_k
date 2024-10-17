from flask import Flask, request, jsonify
import math
import uuid




def calculate_sip(monthly_investment, expected_return, time_period, inflation_rate, tax_rate):
    monthly_rate = (expected_return / 12) / 100
    inflation_adjusted_return = (1 + expected_return/100) / (1 + inflation_rate/100) - 1
    monthly_inflation_adjusted_rate = inflation_adjusted_return / 12
    
    future_value = monthly_investment * ((math.pow(1 + monthly_rate, time_period * 12) - 1) / monthly_rate) * (1 + monthly_rate)
    inflation_adjusted_value = monthly_investment * ((math.pow(1 + monthly_inflation_adjusted_rate, time_period * 12) - 1) / monthly_inflation_adjusted_rate) * (1 + monthly_inflation_adjusted_rate)
    
    total_investment = monthly_investment * time_period * 12
    total_gain = future_value - total_investment
    tax_on_gain = total_gain * (tax_rate / 100)
    after_tax_future_value = future_value - tax_on_gain
    
    return {
        "future_value": round(future_value, 2),
        "inflation_adjusted_value": round(inflation_adjusted_value, 2),
        "total_investment": round(total_investment, 2),
        "total_gain": round(total_gain, 2),
        "after_tax_future_value": round(after_tax_future_value, 2)
    }

def calculate_swp(initial_investment, monthly_withdrawal, expected_return, time_period, inflation_rate, tax_rate):
    monthly_rate = (expected_return / 12) / 100
    inflation_adjusted_withdrawal = monthly_withdrawal * math.pow(1 + inflation_rate/100, time_period)
    
    remaining_balance = initial_investment
    total_withdrawal = 0
    months = 0
    
    while remaining_balance > 0 and months < time_period * 12:
        interest = remaining_balance * monthly_rate
        tax_on_interest = interest * (tax_rate / 100)
        remaining_balance += interest - tax_on_interest - monthly_withdrawal
        total_withdrawal += monthly_withdrawal
        months += 1
    
    return {
        "months_lasted": months,
        "total_withdrawal": round(total_withdrawal, 2),
        "remaining_balance": round(max(0, remaining_balance), 2),
        "inflation_adjusted_final_withdrawal": round(inflation_adjusted_withdrawal, 2)
    }

# In-memory storage for investment scenarios
scenarios = {}

def calculate_investment(principal, monthly_contribution, years, interest_rate, inflation_rate, tax_rate):
    monthly_rate = (interest_rate / 12) / 100
    inflation_adjusted_return = (1 + interest_rate/100) / (1 + inflation_rate/100) - 1
    monthly_inflation_adjusted_rate = inflation_adjusted_return / 12
    
    future_value = principal * (1 + monthly_rate) ** (years * 12)
    future_value += monthly_contribution * ((math.pow(1 + monthly_rate, years * 12) - 1) / monthly_rate) * (1 + monthly_rate)
    
    inflation_adjusted_value = principal * (1 + monthly_inflation_adjusted_rate) ** (years * 12)
    inflation_adjusted_value += monthly_contribution * ((math.pow(1 + monthly_inflation_adjusted_rate, years * 12) - 1) / monthly_inflation_adjusted_rate) * (1 + monthly_inflation_adjusted_rate)
    
    total_contributions = principal + (monthly_contribution * years * 12)
    total_gain = future_value - total_contributions
    tax_on_gain = total_gain * (tax_rate / 100)
    after_tax_future_value = future_value - tax_on_gain
    
    return {
        "future_value": round(future_value, 2),
        "inflation_adjusted_value": round(inflation_adjusted_value, 2),
        "total_contributions": round(total_contributions, 2),
        "total_gain": round(total_gain, 2),
        "after_tax_future_value": round(after_tax_future_value, 2)
    }



#---------------------------------------------------------------------------------------------------------------
@app.route('/sip', methods=['POST']) 
def sip():
    data = request.json
    result = calculate_sip(
        data['monthly_investment'],
        data['expected_return'],
        data['time_period'],
        data['inflation_rate'],
        data['tax_rate']
    )
    return jsonify(result) 

@app.route('/swp', methods=['POST'])
def swp():
    data = request.json
    result = calculate_swp(
        data['initial_investment'],
        data['monthly_withdrawal'],
        data['expected_return'],
        data['time_period'],
        data['inflation_rate'],
        data['tax_rate']
    )
    return jsonify(result)

@app.route('/investment', methods=['GET'])
def get_all_scenarios():
    return jsonify(scenarios)

@app.route('/investment/<scenario_id>', methods=['GET'])
def get_scenario(scenario_id):
    scenario = scenarios.get(scenario_id)
    if scenario:
        return jsonify(scenario)
    return jsonify({"error": "Scenario not found"}), 404

@app.route('/investment', methods=['PUT'])
def create_or_update_scenario():
    data = request.json
    scenario_id = data.get('id', str(uuid.uuid4()))
    
    result = calculate_investment(
        data['principal'],
        data['monthly_contribution'],
        data['years'],
        data['interest_rate'],
        data['inflation_rate'],
        data['tax_rate']
    )
    
    scenarios[scenario_id] = {
        "id": scenario_id,
        "inputs": data,
        "results": result
    }
    
    return jsonify(scenarios[scenario_id]), 201

@app.route('/investment/<scenario_id>', methods=['DELETE'])
def delete_scenario(scenario_id):
    if scenario_id in scenarios:
        del scenarios[scenario_id]
        return jsonify({"message": f"Scenario {scenario_id} deleted successfully"}), 200
    return jsonify({"error": "Scenario not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)