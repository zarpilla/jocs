// GENERAT per adapters/benne/sync.ts. No l'editis aquí.
import { dialog, options } from './teclat.ids';
import { chooseNarrativeOption, startNarrativeDialog } from '../../narrative/narrative.script';

dialog.onStart(() => {
  startNarrativeDialog('teclat', dialog)
})

options.inici__tecleja.onChoose(() => {
  chooseNarrativeOption('teclat', dialog, 'inici', 'tecleja')
})

options.inici__deixa.onChoose(() => {
  chooseNarrativeOption('teclat', dialog, 'inici', 'deixa')
})

options.casella1__c1_m.onChoose(() => {
  chooseNarrativeOption('teclat', dialog, 'casella1', 'c1_m')
})

options.casella1__c1_v.onChoose(() => {
  chooseNarrativeOption('teclat', dialog, 'casella1', 'c1_v')
})

options.casella1__c1_t.onChoose(() => {
  chooseNarrativeOption('teclat', dialog, 'casella1', 'c1_t')
})

options.casella1__c1_b.onChoose(() => {
  chooseNarrativeOption('teclat', dialog, 'casella1', 'c1_b')
})

options.casella2__c2_a.onChoose(() => {
  chooseNarrativeOption('teclat', dialog, 'casella2', 'c2_a')
})

options.casella2__c2_e.onChoose(() => {
  chooseNarrativeOption('teclat', dialog, 'casella2', 'c2_e')
})

options.casella2__c2_i.onChoose(() => {
  chooseNarrativeOption('teclat', dialog, 'casella2', 'c2_i')
})

options.casella2__c2_o.onChoose(() => {
  chooseNarrativeOption('teclat', dialog, 'casella2', 'c2_o')
})

options.casella3__c3_r.onChoose(() => {
  chooseNarrativeOption('teclat', dialog, 'casella3', 'c3_r')
})

options.casella3__c3_t.onChoose(() => {
  chooseNarrativeOption('teclat', dialog, 'casella3', 'c3_t')
})

options.casella3__c3_n.onChoose(() => {
  chooseNarrativeOption('teclat', dialog, 'casella3', 'c3_n')
})

options.casella3__c3_l.onChoose(() => {
  chooseNarrativeOption('teclat', dialog, 'casella3', 'c3_l')
})

options.casella4__c4_i.onChoose(() => {
  chooseNarrativeOption('teclat', dialog, 'casella4', 'c4_i')
})

options.casella4__c4_n.onChoose(() => {
  chooseNarrativeOption('teclat', dialog, 'casella4', 'c4_n')
})

options.casella4__c4_u.onChoose(() => {
  chooseNarrativeOption('teclat', dialog, 'casella4', 'c4_u')
})

options.casella4__c4_e.onChoose(() => {
  chooseNarrativeOption('teclat', dialog, 'casella4', 'c4_e')
})

options.casella5__c5_a.onChoose(() => {
  chooseNarrativeOption('teclat', dialog, 'casella5', 'c5_a')
})

options.casella5__c5_e.onChoose(() => {
  chooseNarrativeOption('teclat', dialog, 'casella5', 'c5_e')
})

options.casella5__c5_s.onChoose(() => {
  chooseNarrativeOption('teclat', dialog, 'casella5', 'c5_s')
})

options.casella5__c5_o.onChoose(() => {
  chooseNarrativeOption('teclat', dialog, 'casella5', 'c5_o')
})

options.comprova__accepta.onChoose(() => {
  chooseNarrativeOption('teclat', dialog, 'comprova', 'accepta')
})

options.comprova__accepta_no.onChoose(() => {
  chooseNarrativeOption('teclat', dialog, 'comprova', 'accepta_no')
})

options.comprova__esborra.onChoose(() => {
  chooseNarrativeOption('teclat', dialog, 'comprova', 'esborra')
})

options.comprova__deixa_comprova.onChoose(() => {
  chooseNarrativeOption('teclat', dialog, 'comprova', 'deixa_comprova')
})
