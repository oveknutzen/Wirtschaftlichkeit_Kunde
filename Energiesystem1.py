import pypsa
import pandas as pd
import numpy as np

def Energiesystem(preis_pro_kw, eeg_verguetung, stromkosten,verteuerungsrate,kredit_zinsen,npv_zinsen, anlagen_groesse, stromverbrauch, Batterie, batterie_costs_kwh):
    df_wetterdaten = pd.read_csv("ninja_weather_51_9.csv", sep = ",") # Wetterdaten von renewables.ninja; irradiation in W/m2; wind_speed in m/s
    
    invest_pv = preis_pro_kw #Investitionskosten für PV in €/kW
    infeed_rate_pv = eeg_verguetung #Einspeisevergütung PV in €/kWh. Im Netzwerk auf 0 gesetzt, da es für die Berechnung unrelevant ist.
    lifetime_pv = 19.5 #Lebensdauer PV in Jahren 
    Nutzungsgrad = 0.86
    # Installierte Leistung in kWp
    p_nom_pv_south = anlagen_groesse                           

    # Jahresprofil als DF in %
    df_pv_gesamt = pd.DataFrame(data = {"pv_south_100": (df_wetterdaten["irradiation"]/1000*Nutzungsgrad)})
    #Werte für Li-Ion Batterie - Quartierspeichergröße
    invest_el_storage = (532.31+44.56)*1.17 #Investitionskosten für Speicher in €/kWh
    standing_loss_el_storage = 0 #Speicherverluste über Zeit
    lifetime_el_storage = 20 #Lebensdauer des Speichers 
    efficiency_el_storage = 1 #Ein- und Ausspeichereffizienz liegt bei 100 %.
    #Haushalte
    anzahl_H3 = 1 #Mehrpersonenhaushalte
    verbrauch_H3 = stromverbrauch #kWh Jahresverbrauch je HH

    df_household_csv = pd.read_csv('Haushaltslastprofile.csv', sep = ';', decimal = '.')
    df_household = df_household_csv.drop(columns=['date']).astype(float)

    # Multiplikation der großen Lastprofile mit der Anzahl der Haushalte
    # Die Spalte H1, H2 und H3 sind die Lastprofile der Haushaltstypen für das ganze Dorf.

    df_household['H3'] = df_household['H3'] * anzahl_H3/4959*verbrauch_H3


    # Speichern der Lastprofile in einer csv

    p_set_HH = df_household['H3']
    # df_load_profil.head(5)
    network = pypsa.Network()
    network.set_snapshots(range(8760))

    #Buses
    network.add('Bus', name = 'pv_bus')
    network.add('Bus', name = 'electricity_bus')
    network.add('Generator', name = 'netz', bus = 'electricity_bus', marginal_cost = 0.4,
                p_nom_extendable = True) 

    #PV-Anlage - nicht extendable
    network.add('Generator', name = 'pv_south', bus = 'pv_bus', capital_cost = invest_pv/lifetime_pv, 
                p_nom = p_nom_pv_south, p_max_pu = df_pv_gesamt["pv_south_100"], p_min_pu = df_pv_gesamt["pv_south_100"]) 
    network.add("Generator", name = "grid_infeed_pv", bus = "pv_bus", marginal_cost = 0, sign = -1, 
                p_nom = p_nom_pv_south)
    network.add('Link', name = 'pv_link', bus0 = 'pv_bus', bus1 = 'electricity_bus', 
                p_nom = p_nom_pv_south)

    print("Batteriewert:", Batterie)
    #Stromspeicher
    if Batterie >0:
        network.add("Bus", name="el_storage_bus")
        network.add("Link", name = "el_storage_charge", bus0 = "electricity_bus", bus1 = "el_storage_bus", 
           efficiency = np.sqrt(efficiency_el_storage), p_nom=100000)
        network.add("Link", name = "el_storage_discharge", bus0 = "el_storage_bus", bus1 = "electricity_bus", 
           efficiency = np.sqrt(efficiency_el_storage), p_nom=100000)
        print("Buses im Netzwerk:", network.buses)
        network.add("Store", name = "el_storage", bus = "el_storage_bus", standing_loss = standing_loss_el_storage, e_cyclic = True,
        e_nom = Batterie, capital_cost = invest_el_storage/lifetime_el_storage)
   
    #Lastkurven
    network.add("Load", name = "load_HH", bus = 'electricity_bus', p_set = p_set_HH)
    network.lopf(pyomo = False, solver_name = 'cbc')
    print(network.links_t.p0['pv_link'].sum())
    print(network.generators_t.p['pv_south'].sum())
    print(network.links_t.p0['pv_link'].sum()/network.generators_t.p['pv_south'].sum())
    print(network.loads_t.p.sum())
    kwh_netz = network.generators_t.p['pv_south'].sum()-network.links_t.p0['pv_link'].sum()
    kwh_haus = network.links_t.p0['pv_link'].sum()
    return kwh_haus, kwh_netz