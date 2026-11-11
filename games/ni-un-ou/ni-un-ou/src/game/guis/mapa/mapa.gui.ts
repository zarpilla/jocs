// Creat per games/ni-un-ou/adapters/benne/joc.ts: el plànol de l'Arenga. No l'editis aquí.
// La lògica és a narrative/mapa.ts i narrative/mapa.script.ts (games/ni-un-ou/adapters/benne/runtime/).
import { tanca, salaSalaRadio, salaPont, salaPal, salaCobertaPopa, salaCuina, salaMenjador, salaInfermeria, salaLaboratori, salaCabinaCapitana, salaPassadis, salaCobertaProa, salaRebost, salaDiposit2, salaSalaMaquines, salaTaller, salaCamarotIri, salaPallol, salaPassadisBaix, salaSalaBombes, salaCaixaCadenes } from './mapa.ids';
import { peuMapa, tancaMapa } from '../../narrative/mapa';
import { viatjaAmbMapa } from '../../narrative/mapa.script';

tanca.onClick(() => tancaMapa())

salaSalaRadio.onClick(() => viatjaAmbMapa('sala_radio'))
salaSalaRadio.onMouseEnter(() => peuMapa('sala_radio'))
salaSalaRadio.onMouseLeave(() => peuMapa(null))

salaPont.onClick(() => viatjaAmbMapa('pont'))
salaPont.onMouseEnter(() => peuMapa('pont'))
salaPont.onMouseLeave(() => peuMapa(null))

salaPal.onClick(() => viatjaAmbMapa('pal'))
salaPal.onMouseEnter(() => peuMapa('pal'))
salaPal.onMouseLeave(() => peuMapa(null))

salaCobertaPopa.onClick(() => viatjaAmbMapa('coberta_popa'))
salaCobertaPopa.onMouseEnter(() => peuMapa('coberta_popa'))
salaCobertaPopa.onMouseLeave(() => peuMapa(null))

salaCuina.onClick(() => viatjaAmbMapa('cuina'))
salaCuina.onMouseEnter(() => peuMapa('cuina'))
salaCuina.onMouseLeave(() => peuMapa(null))

salaMenjador.onClick(() => viatjaAmbMapa('menjador'))
salaMenjador.onMouseEnter(() => peuMapa('menjador'))
salaMenjador.onMouseLeave(() => peuMapa(null))

salaInfermeria.onClick(() => viatjaAmbMapa('infermeria'))
salaInfermeria.onMouseEnter(() => peuMapa('infermeria'))
salaInfermeria.onMouseLeave(() => peuMapa(null))

salaLaboratori.onClick(() => viatjaAmbMapa('laboratori'))
salaLaboratori.onMouseEnter(() => peuMapa('laboratori'))
salaLaboratori.onMouseLeave(() => peuMapa(null))

salaCabinaCapitana.onClick(() => viatjaAmbMapa('cabina_capitana'))
salaCabinaCapitana.onMouseEnter(() => peuMapa('cabina_capitana'))
salaCabinaCapitana.onMouseLeave(() => peuMapa(null))

salaPassadis.onClick(() => viatjaAmbMapa('passadis'))
salaPassadis.onMouseEnter(() => peuMapa('passadis'))
salaPassadis.onMouseLeave(() => peuMapa(null))

salaCobertaProa.onClick(() => viatjaAmbMapa('coberta_proa'))
salaCobertaProa.onMouseEnter(() => peuMapa('coberta_proa'))
salaCobertaProa.onMouseLeave(() => peuMapa(null))

salaRebost.onClick(() => viatjaAmbMapa('rebost'))
salaRebost.onMouseEnter(() => peuMapa('rebost'))
salaRebost.onMouseLeave(() => peuMapa(null))

salaDiposit2.onClick(() => viatjaAmbMapa('diposit2'))
salaDiposit2.onMouseEnter(() => peuMapa('diposit2'))
salaDiposit2.onMouseLeave(() => peuMapa(null))

salaSalaMaquines.onClick(() => viatjaAmbMapa('sala_maquines'))
salaSalaMaquines.onMouseEnter(() => peuMapa('sala_maquines'))
salaSalaMaquines.onMouseLeave(() => peuMapa(null))

salaTaller.onClick(() => viatjaAmbMapa('taller'))
salaTaller.onMouseEnter(() => peuMapa('taller'))
salaTaller.onMouseLeave(() => peuMapa(null))

salaCamarotIri.onClick(() => viatjaAmbMapa('camarot_iri'))
salaCamarotIri.onMouseEnter(() => peuMapa('camarot_iri'))
salaCamarotIri.onMouseLeave(() => peuMapa(null))

salaPallol.onClick(() => viatjaAmbMapa('pallol'))
salaPallol.onMouseEnter(() => peuMapa('pallol'))
salaPallol.onMouseLeave(() => peuMapa(null))

salaPassadisBaix.onClick(() => viatjaAmbMapa('passadis_baix'))
salaPassadisBaix.onMouseEnter(() => peuMapa('passadis_baix'))
salaPassadisBaix.onMouseLeave(() => peuMapa(null))

salaSalaBombes.onClick(() => viatjaAmbMapa('sala_bombes'))
salaSalaBombes.onMouseEnter(() => peuMapa('sala_bombes'))
salaSalaBombes.onMouseLeave(() => peuMapa(null))

salaCaixaCadenes.onClick(() => viatjaAmbMapa('caixa_cadenes'))
salaCaixaCadenes.onMouseEnter(() => peuMapa('caixa_cadenes'))
salaCaixaCadenes.onMouseLeave(() => peuMapa(null))
