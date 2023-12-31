import streamlit as st
import pypsa
import numpy_financial as npf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from Wirtschaftlichkeit import wirtschaftlichkeitsberechnung
from sensitivity_analysis import run_sensitivity_analysis
from Energiesystem1 import Energiesystem
# Streamlit App

st.title('Wirtschaftlichkeitsanalyse für Solaranlagen')

# Eingabefelder
preis_pro_kw = st.number_input('Preis pro kW (€)', value=1000.0)
anlagen_groesse = st.number_input('Größe der Anlage (kW)', value=10.0)
stromverbrauch = st.number_input('Stromverbrauch (kWh)', value=4000.0)
stromkosten = st.number_input('Stromkosten pro kWh (€)', value=0.30, format="%.4f")
verteuerungsrate = st.number_input('Stromverteuerungsrate (%)', value=3.0) / 100
kredit_zinsen = st.number_input('Zinsen für Kredit (%)', value=1.0) / 100
npv_zinsen = st.number_input('Diskontsatz für NPV (%)', value=3.0) / 100
eeg_verguetung = st.number_input('EEG Vergütung pro kWh (€)', value=0.10, format="%.4f")
batterie_costs_kwh = st.number_input('Batteriekosten pro kWh (€)', value=(532.31+44.56)*1.17)
Batterie = st.checkbox('Batteriespeicher')
if st.button("Berechnen"):

    
    if Batterie:
        Batterie = 7
        print('Bat', Batterie)
    ref_values = {
        'preis_pro_kw': preis_pro_kw,
        'anlagen_groesse': anlagen_groesse,
        'stromverbrauch': stromverbrauch,
        'stromkosten': stromkosten,
        'verteuerungsrate': verteuerungsrate,
        'kredit_zinsen': kredit_zinsen,
        'npv_zinsen': npv_zinsen,
        'eeg_verguetung': eeg_verguetung,
        'Batterie':Batterie,
        'batterie_costs_kwh':batterie_costs_kwh
    }
    kwh_haus, kwh_netz = Energiesystem(preis_pro_kw, eeg_verguetung, stromkosten, verteuerungsrate, kredit_zinsen,npv_zinsen,anlagen_groesse, stromverbrauch, Batterie, batterie_costs_kwh)  # Beachten Sie das Argument "stromkosten"
    ergebnisse = wirtschaftlichkeitsberechnung(**ref_values, kwh_haus = kwh_haus, kwh_netz=kwh_netz)
    sensitivity_results = run_sensitivity_analysis(ref_values, ergebnisse)

    # Ergebnisse anzeigen
    st.subheader('Ergebnisse')
    st.write(f'Gesamtgewinn nach 20 Jahren: {ergebnisse["gesamtgewinn"]:.2f} €')
    st.write(f'Die Anlage amortisiert sich im Jahr: {ergebnisse["amortisationsjahr"]}')
    st.write(f'Interner Zinsfuß: {ergebnisse["interner_zinsfuss"]:.2f} %')
    st.write(f'Kapitalwert (NPV) zum Zeitpunkt t0: {ergebnisse["kapitalwert"]:.2f} €')
    st.write(f'Stromeinspeisung ins Netz: {kwh_netz} kWh')
    st.write(f'Eigenverbrauch PV-Strom: {kwh_haus} kWh')
    st.write(f'Eigenverbrauchsquote: {kwh_haus/(kwh_netz+kwh_haus)} ')    
    st.write(f'Autarkiequote: {kwh_haus/stromverbrauch} ')
    st.write(f'LCOE:{ergebnisse["lcoe"]}')


    jahre = list(range(21))  
    df = pd.DataFrame({
        'Jahr': jahre,
        'Einnahmen (€)': [0] + ergebnisse['cashflows'][1:],  
        'Kumulative Gewinne (€)': ergebnisse['kumulative_gewinne']
    })

    st.subheader('Jährliche Finanzübersicht')
    st.table(df.style.format("{:.2f}", subset=['Einnahmen (€)', 'Kumulative Gewinne (€)']))

    st.subheader('Kumulative Gewinne über 20 Jahre')
    fig, ax = plt.subplots()
    ax.plot(jahre, ergebnisse['kumulative_gewinne'], '-o', color='b', label='Kumulative Gewinne')
    ax.axhline(0, color='grey', linestyle='--')
    ax.set_xlabel('Jahr')
    ax.set_ylabel('€')
    ax.set_title('Kumulative Gewinne über 20 Jahre')
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)
    st.subheader('Sensitivitätsanalyse Ergebnisse')
    st.subheader('Sensitivitätsanalyse: Prozentuale Änderung der Ausgabewerte')

    st.subheader('Sensitivitätsanalyse: Prozentuale Änderung der Ausgabewerte')

    for metric, deviations_dict in sensitivity_results.items():
        fig, ax = plt.subplots()

        plt.rcParams["font.family"] = "Times New Roman"

        plot_data = {}  
    lesbare_namen = {
    'preis_pro_kw': 'Preis pro kW',
    'anlagen_groesse': 'Anlagengröße',
    'stromverbrauch': 'Stromverbrauch',
    'stromkosten': 'Stromkosten',
    'verteuerungsrate': 'Verteuerungsrate',
    'kredit_zinsen': 'Kreditzinsen',
    'npv_zinsen': 'Diskontsatz',
    'kwh_netz': 'Netzeinspeisung',
    'kwh_haus': 'Eigenverbrauch',
    'eeg_verguetung': 'EEG-Vergütung',
    'Batterie': 'Batteriekapazität',
    'batterie_costs_kwh': 'Batteriekosten pro kWh'
}

    titel_anpassungen = {
    'kapitalwert': 'Sensitivitätsanalyse für die Änderung des Kapitalwerts',
    'interner_zinsfuss': 'Sensitivitätsanalyse für die Änderung des internen Zinsfußes',
    'gesamtgewinn': 'Sensitivitätsanalyse für die Änderung des Gesamtgewinns',
    'lcoe': 'Levelized cost of Energy'
}


    st.subheader('Sensitivitätsanalyse: Prozentuale Änderung der Ausgabewerte')

    for metric, deviations_dict in sensitivity_results.items():
        fig, ax = plt.subplots()

        plt.rcParams["font.family"] = "Times New Roman"

        plot_data = {}  

        for deviation, param_changes in deviations_dict.items():
            deviation_value = float(deviation.replace('%', ''))  
            for param_name, change_percent in param_changes.items():
                if param_name not in plot_data:
                    plot_data[param_name] = ([], [])  
                plot_data[param_name][0].append(deviation_value)
                plot_data[param_name][1].append(change_percent)

        for param_name, (deviations, changes) in plot_data.items():
            lesbare_param_name = lesbare_namen.get(param_name, param_name)  
            ax.plot(deviations, changes, label=lesbare_param_name)  
        angepasster_titel = titel_anpassungen.get(metric, metric)
        ax.set_title(angepasster_titel)
        ax.set_xlabel('Prozentuale Änderung der Eingabe (%)')
        ax.set_ylabel('Prozentuale Änderung der Ausgabe (%)')
        ax.grid(True)

        ax.set_xlim(-10, 10) 

        ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), fancybox=True, shadow=True, ncol=5)

        st.pyplot(fig)

    ten_percent_change = {}
    for metric, changes_dict in sensitivity_results.items():
        ten_percent_change[metric] = {}
        for param_name, changes in changes_dict.items():
            if "10.0%" in changes:
                ten_percent_change[metric][param_name] = changes["10.0%"]
            else:
                ten_percent_change[metric][param_name] = None  

    for metric, sensitivity_data in sensitivity_results.items():
        st.write(f'Änderungen für {metric}:')
        st.write(pd.DataFrame(sensitivity_data))