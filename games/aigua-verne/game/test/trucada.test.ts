/**
 * La trucada del Magnat (Escena 6, tasca 143): «Acceptem», «No» o «El pou ja és nostre». La Vet talla la comunicació
 * i el camí és el mateix, però la tria es recorda: a la mateixa trucada, a la Capitana aquella nit i al final.
 */
import { describe, expect, it } from 'vitest';
import type { ResolvedLine } from '@aventura/narrative-core';
import { partida } from './partida.js';

const textos = (lines: ResolvedLine[]) => lines.map((l) => l.text).join('\n');

function trucada(tria: 'si' | 'no' | 'pou') {
  const { n, p } = partida();
  n.apply([{ setVar: 'escena', value: 6 }]);
  p.goTo('cantimplora_pont');
  const dita = textos(p.talk('trucada', tria));
  const nit = textos(p.talk('capitana'));
  const altra = textos(p.talk('capitana'));
  const f = n.ending('plou');
  const final = [...f.scene, ...f.credits].map((l) => l.text).join('\n');
  return { n, dita, nit, altra, final };
}

describe('Aigua Verne: la trucada del Magnat', () => {
  it('«Acceptem»: la Vet talla, les germanes s\'hi enfaden i el Magnat s\'ha delatat («el vostre mecànic»)', () => {
    const { n, dita, nit, altra, final } = trucada('si');
    expect(dita).toMatch(/Envieu les claus amb el vostre mecànic[^]*Era per guanyar temps\.\nNo ho era\.[^]*mig got per cap/);
    expect(dita).toMatch(/I ha dit «el vostre mecànic»/);
    expect(n.flag('cal_espia')).toBe(true);
    expect(nit).toMatch(/Per un moment, jo també/);
    expect(altra).not.toMatch(/Per un moment/);
    expect(final).toMatch(/Ho tinc gravat\.\nVerbal\. No executat\. No consta\.\nJo soc el Magnat Verne/);
    expect(final).toMatch(/ella també hauria dit que sí/);
    expect(final).not.toMatch(/casella de l'ànima\.\n/);
  });

  it('«El pou ja és nostre»: el pou sí, l\'aigua no', () => {
    const { dita, nit, final } = trucada('pou');
    expect(dita).toMatch(/L'aigua, no\.\nLlegiu el contracte 7\.788[^]*mig got per cap/);
    expect(dita).not.toMatch(/guanyar temps|el vostre mecànic/);
    expect(nit).toMatch(/Jo també ho deia, de la nau/);
    expect(final).not.toMatch(/Ho tinc gravat|hauria dit que sí/);
    expect(final).toMatch(/Ratlla la casella de l'ànima\./);
  });

  it('«No»: com sempre, i la Capitana ho troba massa ràpid', () => {
    const { dita, nit, final } = trucada('no');
    expect(dita).not.toMatch(/L'aigua, no|guanyar temps|el vostre mecànic/);
    expect(nit).toMatch(/molt de pressa/);
    expect(final).not.toMatch(/Ho tinc gravat|hauria dit que sí/);
  });
});
