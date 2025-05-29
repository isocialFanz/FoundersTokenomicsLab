import pandas as pd
import numpy as np

def run_simulation(parameters: dict) -> pd.DataFrame:
    """
    Simulates tokenomics based on provided parameters over a specified duration.

    Args:
        parameters (dict): A dictionary containing all simulation parameters.

    Returns:
        pd.DataFrame: A DataFrame with monthly data for various tokenomics metrics.
    """

    # --- 1. Extract Core Parameters ---
    total_supply = parameters.get('total_supply')
    initial_circulating_supply = parameters.get('initial_circulating_supply')
    simulation_duration_months = parameters.get('simulation_duration_months') # e.g., 60 months

    # --- 2. Allocation Percentages ---
    team_allocation_pct = parameters.get('team_allocation_pct')
    private_sale_pct = parameters.get('private_sale_pct')
    public_sale_pct = parameters.get('public_sale_pct')
    treasury_pct = parameters.get('treasury_pct')
    community_rewards_pct = parameters.get('community_rewards_pct')
    liquidity_mining_pct = parameters.get('liquidity_mining_pct')

    # --- 3. Vesting Schedules (in months) ---
    team_cliff_months = parameters.get('team_cliff_months')
    team_vesting_linear_months = parameters.get('team_vesting_linear_months') # Duration after cliff
    private_sale_cliff_months = parameters.get('private_sale_cliff_months')
    private_sale_vesting_linear_months = parameters.get('private_sale_vesting_linear_months') # Duration after cliff

    # --- 4. Emission & Burn Mechanisms ---
    monthly_emission_tokens = parameters.get('monthly_emission_tokens')
    transaction_fee_burn_pct = parameters.get('transaction_fee_burn_pct') # e.g., 0.005 for 0.5%
    # Placeholder for simulated transactions for now
    monthly_simulated_transactions = parameters.get('monthly_simulated_transactions', 1000000) # Default value for simulation

    # --- Initialize Data Structures for Simulation Results ---
    data = []

    # Calculate initial locked allocations
    initial_team_locked = total_supply * team_allocation_pct
    initial_private_sale_locked = total_supply * private_sale_pct

    # Current state variables
    current_circulating_supply = initial_circulating_supply
    current_total_supply = total_supply # Total supply might increase with emissions beyond initial_supply

    current_team_locked = initial_team_locked
    current_private_sale_locked = initial_private_sale_locked

    # Calculate monthly unlock amounts after cliff
    # Note: If vesting_linear_months is 0 or less, it implies immediate unlock after cliff.
    team_monthly_unlock_amount = 0
    if team_vesting_linear_months > 0:
        team_monthly_unlock_amount = initial_team_locked / team_vesting_linear_months

    private_sale_monthly_unlock_amount = 0
    if private_sale_vesting_linear_months > 0:
        private_sale_monthly_unlock_amount = initial_private_sale_locked / private_sale_vesting_linear_months

    # --- Simulation Loop ---
    for month in range(1, simulation_duration_months + 1):
        unlocked_team_this_month = 0
        unlocked_private_sale_this_month = 0
        minted_tokens_this_month = monthly_emission_tokens
        burned_tokens_this_month = 0 # Will be calculated based on simulated transactions

        # Apply vesting unlocks
        if month > team_cliff_months and current_team_locked > 0:
            unlocked_team_this_month = min(team_monthly_unlock_amount, current_team_locked)
            current_team_locked -= unlocked_team_this_month

        if month > private_sale_cliff_months and current_private_sale_locked > 0:
            unlocked_private_sale_this_month = min(private_sale_monthly_unlock_amount, current_private_sale_locked)
            current_private_sale_locked -= unlocked_private_sale_this_month

        # Calculate burned tokens
        # For simplicity, we assume 'transactions' are volume in tokens, and a % of that is burned.
        # In a real scenario, this would be more complex (e.g., fees in stablecoins, then used to buy & burn).
        burned_tokens_this_month = monthly_simulated_transactions * transaction_fee_burn_pct

        # Update supplies
        current_total_supply += minted_tokens_this_month - burned_tokens_this_month
        current_circulating_supply += (
            unlocked_team_this_month +
            unlocked_private_sale_this_month +
            minted_tokens_this_month -
            burned_tokens_this_month
        )

        # Store current month's data
        data.append({
            'month': month,
            'total_supply': current_total_supply,
            'circulating_supply': current_circulating_supply,
            'unlocked_team': unlocked_team_this_month,
            'unlocked_private_sale': unlocked_private_sale_this_month,
            'minted_tokens': minted_tokens_this_month,
            'burned_tokens': burned_tokens_this_month,
            'current_team_locked': current_team_locked,
            'current_private_sale_locked': current_private_sale_locked,
        })

    return pd.DataFrame(data)

# --- Example Usage (for testing the simulation engine) ---
if __name__ == "__main__":
    # Define some default parameters for a sample simulation
    sample_params = {
        'total_supply': 1_000_000_000, # 1 Billion tokens
        'initial_circulating_supply': 150_000_000, # 150 Million at launch
        'simulation_duration_months': 60, # 5 years

        'team_allocation_pct': 0.20, # 20%
        'private_sale_pct': 0.15, # 15%
        'public_sale_pct': 0.10, # 10% (assumed fully circulating at launch or with very short lockup)
        'treasury_pct': 0.30, # 30%
        'community_rewards_pct': 0.15, # 15%
        'liquidity_mining_pct': 0.10, # 10%

        'team_cliff_months': 12, # 1-year cliff
        'team_vesting_linear_months': 36, # 3 years linear vesting after cliff

        'private_sale_cliff_months': 6, # 6-month cliff
        'private_sale_vesting_linear_months': 24, # 2 years linear vesting after cliff

        'monthly_emission_tokens': 5_000_000, # 5 Million new tokens per month
        'transaction_fee_burn_pct': 0.001, # 0.1% of transactions burned
        'monthly_simulated_transactions': 500_000_000 # 500 Million tokens volume per month
    }

    print("Running tokenomics simulation with sample parameters...")
    simulation_results = run_simulation(sample_params)

    print("\n--- Simulation Results (First 5 Months) ---")
    print(simulation_results.head())

    print("\n--- Simulation Results (Last 5 Months) ---")
    print(simulation_results.tail())

    print(f"\nSimulation completed for {simulation_results['month'].max()} months.")
    print(f"Final Circulating Supply: {simulation_results['circulating_supply'].iloc[-1]:,.0f}")
    print(f"Final Total Supply: {simulation_results['total_supply'].iloc[-1]:,.0f}")
