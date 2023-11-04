import numpy_financial as npf
import numpy as np
import pandas as pd

def wirtschaftlichkeitsberechnung(preis_pro_kw, anlagen_groesse,stromverbrauch, stromkosten, verteuerungsrate, kredit_zinsen, npv_zinsen, kwh_netz, kwh_haus, eeg_verguetung, Batterie, batterie_costs_kwh):
    
    if Batterie >0: 
        batterie_costs = Batterie*(batterie_costs_kwh)
        print('cost_battery', batterie_costs)
    else:
        batterie_costs = 0
    initial_investment = preis_pro_kw * anlagen_groesse + batterie_costs
    if kredit_zinsen == 0:
        annuitaet = initial_investment / 20
    else:
        annuitaet = initial_investment * (kredit_zinsen * (1 + kredit_zinsen)**20) / ((1 + kredit_zinsen)**20 - 1)

    einnahmen = [0]
    zinskosten_liste = [0]
    gewinn_liste = [-initial_investment]  
    verbleibender_kredit_liste = [initial_investment]
    cashflows = [-initial_investment] 
    verbleibender_kredit = initial_investment
    stromproduktion_liste = []
    annuitaet_liste =[]
    stromproduktion = (kwh_netz + kwh_haus)

    for i in range(1, 21): 
        jaehrliche_einnahme = (stromkosten * (1 + verteuerungsrate)**i * kwh_haus) + (eeg_verguetung * kwh_netz)
        einnahmen.append(jaehrliche_einnahme)

        zinskosten = verbleibender_kredit * kredit_zinsen
        zinskosten_liste.append(zinskosten)

        jaehrlicher_gewinn = jaehrliche_einnahme - zinskosten
        gewinn_liste.append(jaehrlicher_gewinn)

        cashflows.append(jaehrlicher_gewinn)

        verbleibender_kredit -= (annuitaet - zinskosten)
        verbleibender_kredit_liste.append(verbleibender_kredit)
        stromproduktion_liste.append(stromproduktion)
        annuitaet_liste.append(annuitaet)
    npv = npf.npv(npv_zinsen, cashflows)
    irr = npf.irr(cashflows)
    
    abgezinste_kosten = npf.npv(npv_zinsen, annuitaet_liste)
    abgezinste_stromproduktion = npf.npv(npv_zinsen,stromproduktion_liste)

    lcoe = abgezinste_kosten / abgezinste_stromproduktion
    kumulative_gewinne = np.cumsum(gewinn_liste)
    amortisationsjahr = next((i for i, value in enumerate(kumulative_gewinne) if value >= 0), 999)

    ergebnisse = {
        'gesamtgewinn': sum(gewinn_liste),
        'amortisationsjahr': amortisationsjahr,
        'interner_zinsfuss': irr * 100, 
        'kapitalwert': npv,
        'cashflows': cashflows,  
        'kumulative_gewinne': kumulative_gewinne.tolist(), 
        'lcoe': lcoe
    }

    return ergebnisse