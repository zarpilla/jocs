/**
 * La marca del pilar 7 (guio/guio.md, Acte 2, pas 3b). L'Iri la grava al moll, i la Vet la veu en tornar a
 * l'hangar (`onEnter` de `gavina_hangar`). Però si el jugador continua amb l'Iri i envia els trossos de la biga,
 * la Vet els rep a la cel·la abans de passar per l'hangar, i el «rebut» arribaria tard. Per això el reajust ja es
 * nota en el primer moment que la Vet torna a jugar, sigui on sigui: mal de cap i el pilar 7 al cap. Quan després
 * entra a l'hangar, hi troba la marca sense repetir el mal de cap (`sala.gavina_hangar.marca_sabuda`).
 */
import type { ActionResult, Narrative } from '@aventura/narrative-core';

export const MARCA_TEXTS = ['marca.reajust1', 'marca.reajust2'];

const HANGAR = 'gavina_hangar';

export function installMarca(n: Narrative) {
  n.onEnterRoom((room): ActionResult | void => {
    if (n.world.activeProtagonist() !== 'vet' || room === HANGAR) return;
    if (!n.flag('marca_pilar') || n.flag('vet_ha_vist_marca') || n.flag('vet_intueix_marca')) return;
    n.apply({ setFlag: 'vet_intueix_marca' });
    return {
      lines: MARCA_TEXTS.map((text) => ({ who: 'player' as const, text })),
    };
  });
}
