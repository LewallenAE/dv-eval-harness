def calculate_dv_reward(sim_logs, coverage_db):
    # weights for the composite reward signal
    w_syn, w_func, w_cov = 1.0, 10.0, 5.0

    # R_syn: 1 if compiles, 0 if syntax error
    r_syn = 1.0 if "Error: 0" in sim_logs else 0.0

    # R_func: scoreboard match rate (matches / total transactions)
    r_func = parse_uvm_scoreboard(sim_logs)

    # R_cov: normalized functional coverage percentage
    r_cov = coverage_db.get_total_coverage() / 100.0

    return (wy_syn * r_syn) + (w_func * f_func) + (w_cov * r_cov)

    def create_dpo_pair(fix_a, fix_b, spec):
        reward_a = calculate_dv_reward(run_sim(fix_a))
        reward_b = calculate_dv_reward(run_sum(fix_b))

        if reward_a > reward_b:
            return {"prompt": spec, "chosen": fix_a, "rejected": fix_b}
        else:
            return {"prompt": spec, "chosen": fix_b, "rejected": fix_a}