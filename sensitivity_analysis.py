def run_sensitivity_analysis(ref_values, original_results):
    deviations = [i * 0.02 for i in range(-5, 6)]  # -10% bis +10%
    sensitivity_results = {
        'kapitalwert': {},
        'gesamtgewinn': {},
        'amortisationsjahr':{},
        'interner_zinsfuss': {},
        'lcoe':{}
    }
    from Wirtschaftlichkeit import wirtschaftlichkeitsberechnung

    from Energiesystem1 import Energiesystem
    for param_name, ref_value in ref_values.items():
        for deviation in deviations:
            modified_values = ref_values.copy()
            modified_values[param_name] = ref_value * (1 + deviation)
            kwh_haus, kwh_netz = Energiesystem(**modified_values)

            modified_values['kwh_haus'] = kwh_haus
            modified_values['kwh_netz'] = kwh_netz
            modified_results = wirtschaftlichkeitsberechnung(**modified_values)
            for metric in sensitivity_results.keys():
                original_value = original_results[metric]
                modified_value = modified_results[metric]
                try:
                    original_value = float(original_value)
                    modified_value = float(modified_value)
                except ValueError:
                    raise ValueError(f"Ein Wert, der für die Berechnung verwendet wird, ist kein gültiger Float. Original: {original_value}, Modifiziert: {modified_value}")
                if metric == 'amortisationsjahr' and (original_value == 999 or modified_value == 999):
                    if original_value == 999 and modified_value == 999:
                        change_percent = 0 
                    elif original_value == 999:
                        change_percent = -100 
                    else:
                        change_percent = 100 
                else:
                    change_percent = ((modified_value - original_value) / original_value) * 100 if original_value else 0

                sensitivity_key = f"{deviation * 100:.1f}%"
                if sensitivity_key not in sensitivity_results[metric]:
                    sensitivity_results[metric][sensitivity_key] = {}
                sensitivity_results[metric][sensitivity_key][param_name] = change_percent

    return sensitivity_results