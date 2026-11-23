"""
El segon muntatge (cinemàtica, gairebé al final): l'Iri ho reparteix tot a parts iguals pel compte de les nòmines, i a
les dotze en punt cobra tothom. És la mateixa sala de control que el primer muntatge (muntatge.py), amb les mateixes
sis pantalles, però cadascuna amb el seu «després»: tothom té 12.195,12 € (100 bilions d'euros ÷ 8.200 milions de
persones), al rellotge són les 12:00, i al mapa els diners corren al revés, del compte de les nòmines cap a tothom.
  - Mònaco: el milionari i el mariner que frega la coberta, amb el mateix al mòbil;
  - Nova York: la gràfica, després de caure, és una ratlla plana («FONS = BECARI»);
  - Ginebra: l'home de la corbata i la secretària, empatats de debò;
  - el bar La Propina: la persiana amunt, gent a la barra i en Tomàs a la porta («OBERT»);
  - el caixer: l'àvia i el cambrer, que ara sí que cobra;
  - el mapa: del compte 0001 cap a totes les ciutats.

Es carrega una còpia pròpia de muntatge.py (amb les seves memòries cau) i s'hi posa `REPARTIT = True`: tot el dibuix
és el d'aquell fitxer.
"""
import importlib.util
from pathlib import Path

import hd640  # noqa: F401  (abans que cap hd.rooms: posa la llibreria a 640×360)

_spec = importlib.util.spec_from_file_location('hd640.rooms._muntatge_repartit', Path(__file__).with_name('muntatge.py'))
M = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(M)
M.REPARTIT = True
M.QUANT = M.QUANT_R

LIGHT = M.LIGHT
bg = M.bg
PROPS = M.PROPS
ANIMS = M.ANIMS
GEOMETRIA = M.GEOMETRIA
