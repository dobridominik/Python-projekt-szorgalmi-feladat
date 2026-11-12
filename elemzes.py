import pandas as pd
import numpy as np
import plotly.express as px


# beolvasas
adatok = pd.read_csv("diabetes_binary_health_indicators_BRFSS2015.csv")


# jovedelmet meg a kort at kellett irnom normalisan hasznalható range-be
korcsoport_mop = {
    1: '18-24', 2: '25-29', 3: '30-34', 4: '35-39', 5: '40-44',
    6: '45-49', 7: '50-54', 8: '55-59', 9: '60-64', 10: '65-69',
    11: '70-74', 12: '75-79', 13: '80+'
}

jovedelem_map = {
    1: '<$10k', 2: '$10k-15k', 3: '$15k-20k', 4: '$20k-25k',
    5: '$25k-35k', 6: '$35k-50k', 7: '$50k-75k', 8: '>$75k'
}

allapot_map = {
    1: 'Kiváló',
    2: 'Nagyon jó',
    3: 'Jó',
    4: 'Elfogadható',
    5: 'Rossz'
}


# append a koros listahoz
korcsoport_lista = []

for k in adatok['Age']:
    korcsoport = korcsoport_mop[k]
    korcsoport_lista.append(korcsoport)

adatok['Korcsoport_Cimke'] = korcsoport_lista


# Incomeos append
jovedelem_lista = []

for j in adatok['Income']:
    jovedelem = jovedelem_map[j]
    jovedelem_lista.append(jovedelem)

adatok['Jovedelem_Cimke'] = jovedelem_lista


# 1. Hogyan valtozik a cukorbetegseg aranya kor és bmi szerint?

# Ide kellett numpy
bmi_feltetelek = [
    adatok['BMI'] < 18.5,
    (adatok['BMI'] >= 18.5) & (adatok['BMI'] < 25),
    (adatok['BMI'] >= 25) & (adatok['BMI'] < 30),
    adatok['BMI'] >= 30
]

bmi_kategoriak = [
    'Sovány',
    'Normál',
    'Túlsúlyos',
    'Elhízott'
]

adatok['BMI_Kategoria'] = np.select(
    bmi_feltetelek,
    bmi_kategoriak,
    default='Ismeretlen'
)


# A Diabetes_binary átlaga átlag mert 0 1 | csoportositas utána vissza rendes oszloppá
kerdes1_adat = adatok.groupby(
    ['Age', 'Korcsoport_Cimke', 'BMI_Kategoria']
)['Diabetes_binary'].mean().reset_index() # atlag + vissza


# arany szazalekba
kerdes1_adat['Arany_Szazalek'] = kerdes1_adat['Diabetes_binary'] * 100


# 1. diagram
diagram1 = px.line(
    kerdes1_adat,
    x='Korcsoport_Cimke',
    y='Arany_Szazalek',
    color='BMI_Kategoria',
    title='1. Kérdés: Cukorbetegek aránya korcsoportok és BMI kategóriák szerint',
    labels={
        'Korcsoport_Cimke': 'Korcsoport',
        'Arany_Szazalek': 'Cukorbetegek aránya (%)',
        'BMI_Kategoria': 'BMI kategória'
    }
).update_xaxes(tickangle=-45)

diagram1.write_image("kepek/1_kerdes.png")


# 2. Hogyan alakul a cukorbetegseg aranya bmi kategoria és fizikai aktivitas szerint?

# ugyanugy csoportositas atlag vissza csak itt bmi és fizikai aktivitas szerint
kerdes2_adat = adatok.groupby(
    ['BMI_Kategoria', 'PhysActivity']
)['Diabetes_binary'].mean().reset_index()


# szazalek
kerdes2_adat['Arany_Szazalek'] = kerdes2_adat['Diabetes_binary'] * 100


# szovegkent jobb mint 0 és 1 
aktivitas_lista = []

for p in kerdes2_adat['PhysActivity']:
    if p == 1:
        aktivitas_lista.append('Aktív')
    else:
        aktivitas_lista.append('Inaktív')

kerdes2_adat['Fizikai_Aktivitas'] = aktivitas_lista


# 2. diagram
diagram2 = px.bar(
    kerdes2_adat,
    x='BMI_Kategoria',
    y='Arany_Szazalek',
    color='Fizikai_Aktivitas',
    barmode='group',
    title='2. Kérdés: Fizikai aktivitás és BMI hatása a cukorbetegek arányára',
    labels={
        'BMI_Kategoria': 'BMI kategória',
        'Arany_Szazalek': 'Cukorbetegek aránya (%)',
        'Fizikai_Aktivitas': 'Aktivitás'
    }
)

diagram2.write_image("kepek/2_kerdes.png")


# 3. Hogyan fugg ossze a jovedelem es az orvosi ellatas koltseg miatti kihagyasa a cukorbetegseggel?

# csoportositas megint
kerdes3_adat = adatok.groupby(
    ['Income', 'Jovedelem_Cimke', 'NoDocbcCost'] # azért kell mind a kettő hogy sorba lehessen rendezni de a grafikon szép legyen
)['Diabetes_binary'].mean().reset_index() # atlag + oszlopba vissza


# %
kerdes3_adat['Arany_Szazalek'] = kerdes3_adat['Diabetes_binary'] * 100


# Az orvosi ellátás szoveg convert
ellatas_lista = []

for n in kerdes3_adat['NoDocbcCost']:
    if n == 1:
        ellatas_lista.append('Költség miatt kihagyva')
    else:
        ellatas_lista.append('Nem volt akadály')

kerdes3_adat['Ellatas_Kihagyva'] = ellatas_lista


# 3. diagram
diagram3 = px.bar(
    kerdes3_adat,
    x='Jovedelem_Cimke',
    y='Arany_Szazalek',
    color='Ellatas_Kihagyva',
    barmode='group',
    title='3. Kérdés: Jövedelem, egészségügyi ellátás költségkorlátja és a cukorbetegség',
    labels={
        'Jovedelem_Cimke': 'Jövedelmi sáv',
        'Arany_Szazalek': 'Cukorbetegek aránya (%)',
        'Ellatas_Kihagyva': 'Ellátási státusz'
    }
)

diagram3.write_image("kepek/3_kerdes.png")


# 4. Magas vérnyomás és magas koleszterin kockázata

# fuggveny a kockazati csoportokhoz
def kockazati_csoport(vernyomas, koleszterin):
    if vernyomas == 1 and koleszterin == 1:
        return 'Mindkettő magas'
    elif vernyomas == 1:
        return 'Csak magas vérnyomás'
    elif koleszterin == 1:
        return 'Csak magas koleszterin'
    else:
        return 'Egyik sem'


# soronkent vegigmegyunk és mindenkit berakunk egy csoportba 
kockazati_lista = []

for i in range(len(adatok)):
    vernyomas = adatok['HighBP'].iloc[i] # itt a vernyomas alapjan megyunk integerlocate
    koleszterin = adatok['HighChol'].iloc[i] # itt pedig a koleszterin alapjan

    csoport = kockazati_csoport(vernyomas, koleszterin)
    kockazati_lista.append(csoport)

adatok['Kockazati_Csoport'] = kockazati_lista


# csoportositas a kockazati csoportok szerint
kerdes4_adat = adatok.groupby(
    'Kockazati_Csoport'
)['Diabetes_binary'].mean().reset_index()


# %
kerdes4_adat['Arany_Szazalek'] = kerdes4_adat['Diabetes_binary'] * 100


# 4. diagram
diagram4 = px.bar(
    kerdes4_adat,
    x='Kockazati_Csoport',
    y='Arany_Szazalek',
    color='Kockazati_Csoport',
    title='4. Kérdés: Magas vérnyomás és koleszterin hatása a cukorbetegség kockázatára',
    labels={
        'Kockazati_Csoport': 'Kockázati csoport',
        'Arany_Szazalek': 'Cukorbetegek aránya (%)'
    }
)

diagram4.write_image("kepek/4_kerdes.png")


# 5. A cukorbetegek hogyan oszlanak meg az általános egészségi állapot szerint

# csak a cukorbetegeket szurjuk ki
cukorbetegek = adatok[adatok['Diabetes_binary'] == 1]


# Groupby a genhealth szerint és itt mar alapbol csak a cukorbetegekkel nezzuk nem az egesz adathalmazzal
kerdes5_adat = cukorbetegek.groupby(
    'GenHlth'
)['Diabetes_binary'].sum().reset_index()


# atirjuk szovegge a szamokat a Genhealthbol
allapot_lista = []

for g in kerdes5_adat['GenHlth']:
    allapot = allapot_map[g]
    allapot_lista.append(allapot)

kerdes5_adat['Allapot'] = allapot_lista


# pie diagram
diagram5 = px.pie(
    kerdes5_adat,
    names='Allapot',
    values='Diabetes_binary',
    title='5. Kérdés: A cukorbetegek megoszlása az általános egészségi állapot szerint'
)

diagram5.write_image("kepek/5_kerdes.png")
# vége
print("Kész, mind az 5 kép lementve.")