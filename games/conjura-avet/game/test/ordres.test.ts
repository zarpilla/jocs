/**
 * La partida sencera en un altre ordre que el de `cami.ts`: el riu abans que la plaça, la Vet a l'apotecaria abans que
 * l'Iri a la bugaderia, la porta de l'arxiu abans del calc, els testimonis abans del segell, i el judici i l'epíleg amb
 * passos fora de lloc. Pel camí, coses fetes abans d'hora que han de dir el que toca.
 */
import { describe, expect, it } from 'vitest';
import { item, partida } from './partida.js';

const claus = (out: unknown) => (out as { key: string }[]).map((l) => l.key);

describe('ordres', () => {
  it('es juga sencera en un altre ordre, amb una pista a cada pas', () => {
    const { n, p } = partida({ checkHints: true });
    const canvia = (qui: string) => {
      expect(n.canSwitch(), `canviar a ${qui}`).toBe(true);
      p.switchTo(qui);
    };

    // Tutorial: l'ordre i el jutge abans que les branques.
    p.do('look', 'ordre');
    p.talk('ponc', 'culpa', 'adeu0');
    p.do('look', 'arrels');
    p.use('destral', 'branques');
    expect(n.flag('branques_apartades')).toBe(false);
    p.use('guants', 'branques');
    p.do('look', 'arrels');
    p.do('pickUp', 'cera');
    // L'Iri ha mirat el segell de l'ordre: sap que és d'ahir.
    expect(claus(p.talk('ponc'))).toContain('dlg.ponc.11');
    expect(n.getVar('fase')).toBe(1);

    // Acte 1: l'Iri va primer al riu, i la resina la va a buscar quan veu que la barca fa aigua.
    p.do('give', 'vet', 'cera');
    p.do('walkTo', 'cami_riu');
    p.talk('joanet', 'barca', 'comporta', 'adeu');
    expect(claus(p.do('use', 'comporta'))).toEqual(['sala.pont_ter.comporta_bull']);
    p.use('destral', 'sobreeixidor');
    p.do('walkTo', 'cami');
    p.use('olla', 'branca_trencada');
    p.do('walkTo', 'cami_riu');
    p.use('pot_resina', 'barca');
    p.use('salabre', 'comporta');
    expect(n.flag('serra_treta')).toBe(true);
    p.talk('joanet');
    expect(n.flag('joanet_fanal')).toBe(true);
    p.do('walkTo', 'cami');
    p.do('give', 'vet', 'serra');

    // La Vet: el claustre abans que l'ordre i la plaça.
    canvia('vet');
    p.do('walkTo', 'porta_monestir');
    expect(p.room).toBe('claustre');
    p.do('give', 'ingilberga', 'serra');
    expect(n.flag('prova_serra')).toBe(true);
    expect(claus(p.do('give', 'ingilberga', 'cera'))).toEqual(['sala.claustre.22b']);
    expect(claus(p.do('give', 'ingilberga', 'serra'))).toEqual(['sala.claustre.22']);
    p.talk('gueraula', 'canta', 'sencera', 'adeu');
    p.use('cera', 'pica');
    p.use('carbonet', item('cera'));
    p.do('use', 'pergami'); p.do('use', 'pergami'); p.do('use', 'pergami');
    expect(n.flag('segell_emma_vist')).toBe(true);
    p.talk('ingilberga', 'arxiu', 'entrar_no', 'adeu');
    p.do('walkTo', 'porta_monestir');
    p.talk('ponc', 'insistir', 'ell', 'privat');
    expect(n.flag('ordre_llegida')).toBe(true);

    // La plaça: la Vet primer, i l'Iri hi arriba quan ja hi ha cànem.
    p.do('walkTo', 'carrer');
    p.do('look', 'queixa');
    expect(n.flag('queixa_copiada')).toBe(false);
    p.do('look', 'campanar');
    p.talk('sanca', 'canem', 'tracte', 'adeu');
    canvia('iri');
    p.do('walkTo', 'carrer');
    expect(p.room).toBe('placa_sant_pol');
    canvia('vet');
    p.do('give', 'iri', 'canem');
    canvia('iri');
    p.use('canem', 'campanar');
    p.do('pull', 'campanar');
    canvia('vet');
    p.do('look', 'queixa');
    expect(n.flag('queixa_copiada')).toBe(true);
    // El riu ja és fet: la Sança no parla del rec sec.
    const noms = claus(p.talk('sanca', 'noms', 'adeu'));
    expect(noms).toContain('dlg.sanca.11b');
    expect(noms).not.toContain('dlg.sanca.11');
    p.do('walkTo', 'carrer');
    p.do('walkTo', 'porta_monestir');
    p.talk('ingilberga', 'signe', 'ordre', 'adeu');
    p.do('give', 'ingilberga', 'tauleta');
    p.talk('ingilberga', 'entrar', 'pare', 'emma', 'monges');
    expect(n.getVar('fase')).toBe(2);

    // Acte 2: la Vet comença sola a l'apotecaria, i la Gueraula li diu què falta.
    p.do('walkTo', 'porta_apotecaria');
    p.talk('gueraula', 'falta', 'barbes', 'veu', 'adeu2');
    p.use('cera', item('salconduit_brut'));
    p.do('use', 'flasco_sense_nom');
    p.use('ploma', item('pergamins'));
    p.do('pickUp', 'mel');
    p.do('pickUp', 'llar');
    p.use('carbo', item('mel'));
    p.do('pickUp', 'atramentum');
    p.do('pickUp', 'cardo');
    p.do('walkTo', 'porta');
    p.do('give', 'iri', 'caparros');
    // L'Iri: el bagul, les tisores i la tina, en desordre.
    canvia('iri');
    p.do('give', 'vet', 'pot_resina');
    p.do('walkTo', 'porta_bugaderia');
    p.do('pickUp', 'tisores');
    p.do('open', 'bagul');
    p.use('tuniques', 'tina');
    expect(n.flag('habits_tenyits')).toBe(false);
    p.use('clofolles', 'tina');
    p.use('caparros', 'tina');
    p.do('pickUp', 'llenya_alzina');
    p.use('alzina', 'fogo');
    p.use('pot_resina', 'fogo');
    p.use('tuniques', 'tina');
    p.use('tisores', item('habits'));
    p.do('walkTo', 'porta');
    p.do('give', 'vet', 'retalls');
    // Els hàbits a les mans de la Vet: la Gueraula ho veu, i la Vet els torna.
    p.do('give', 'vet', 'habits_curts');
    canvia('vet');
    p.do('walkTo', 'porta_apotecaria');
    p.use('pegot', item('salconduit_brut'));
    p.use('cera', item('salconduit_resina'));
    p.use('cardo', item('retalls'));
    p.use('pegot', item('llana'));
    expect(claus(p.talk('gueraula', 'falta', 'adeu2'))).toContain('dlg.gueraula.19b');
    p.do('walkTo', 'porta');
    p.do('give', 'iri', 'habits_curts');
    p.do('walkTo', 'porta_apotecaria');
    p.talk('gueraula', 'llest');
    expect(n.flag('disfressades')).toBe(true);
    expect(p.inventory('vet')).not.toContain('xarop');

    // La porteria: tots els sants i senyes abans del bo.
    expect(p.room).toBe('porteria');
    p.talk('bonfill', 'ora', 'pax', 'visca', 'tres', 'dona', 'dir', 'assenyala', 'tos');
    // La cuina: el vi abans de l'ofici, i la valeriana quan ell no mira.
    expect(p.room).toBe('cuina');
    p.talk('sunifred', 'vi', 'ofici', 'adeu_c');
    p.use('valeriana', 'copa');
    expect(n.flag('vi_drogat')).toBe(false);
    p.use('mocador', 'pila_olles');
    p.use('valeriana', 'gerra');
    p.do('use', 'gerra');
    p.talk('sunifred');
    p.talk('sunifred');
    p.use('ploma', 'sunifred');
    expect(p.room).toBe('scriptorium');

    // Acte 3: la porta de l'arxiu abans del calc.
    p.use('rascador', 'espelma_hores');
    expect(n.flag('canonges_fora')).toBe(false);
    p.use('tauleta', 'gombau');
    p.use('rascador', 'espelma_hores');
    p.use('claus', 'porta_capitular');
    expect(n.getVar('fase')).toBe(5);
    canvia('iri');
    // El fons i l'estendard abans del tapís.
    p.do('push', 'bagul_sunifred');
    expect(claus(p.do('push', 'estendard'))).toEqual(['sala.arxiu.estendard_aviat']);
    p.use('claus', 'bagul_sunifred');
    expect(claus(p.do('use', 'bagul_sunifred'))).toEqual(['sala.arxiu.fons_buit_altra']);
    p.do('pull', 'tapis');
    p.do('push', 'estendard');
    p.do('pull', 'contrapes');
    canvia('vet');
    p.use('tauleta', 'gombau');
    canvia('iri');
    p.do('open', 'bagul_sunifred');
    p.do('pickUp', 'cofre');
    expect(n.flag('cofre_agafat')).toBe(false);
    canvia('vet');
    p.use('carbonet', 'pergami');
    p.do('use', 'pergami'); p.do('use', 'pergami'); p.do('use', 'pergami');
    canvia('iri');
    p.do('pickUp', 'cofre');
    expect(n.getVar('fase')).toBe(6);
    p.do('push', 'banc_fons');
    p.do('use', 'trapa');

    // El molí: la pastera i la falca abans del pot.
    expect(p.room).toBe('moli');
    // Aquí no es pot canviar de germana: si l'Iri donés les cartes a la Vet, no les podria recuperar.
    expect(claus(p.do('give', 'vet', 'carta_calcada'))).toEqual(['donar.ara_no']);
    p.do('push', 'pastera');
    p.do('talkTo', 'finestra_dalt');
    p.use('destral', 'falca');
    p.do('push', 'pastera');
    p.do('talkTo', 'finestra_dalt');
    expect(n.getVar('fase')).toBe(6);
    p.use('carta_calcada', item('pot_apotecari'));
    p.use('pot_resina', item('pot_cartes'));
    p.do('talkTo', 'finestra_dalt');
    expect(n.getVar('fase')).toBe(7);

    // Acte 4: l'Iri al riu primer; la Vet, la Sança i el segell al final.
    p.talk('ponc', 'adeu7');
    p.do('walkTo', 'cami_riu');
    p.talk('ermessenda');
    expect(n.flag('testimoni_ermessenda')).toBe(false);
    expect(claus(p.do('look', 'barca'))).toEqual(['sala.pont_ter.barca_ronca']);
    p.do('push', 'barca');
    p.talk('joanet');
    p.do('push', 'comporta');
    p.talk('ermessenda');
    expect(n.flag('testimoni_ermessenda')).toBe(true);
    expect(n.flag('testimoni_joanet')).toBe(true);
    p.do('walkTo', 'cami');
    canvia('vet');
    p.do('walkTo', 'carrer');
    expect(claus(p.do('look', 'reixa'))).toEqual(['sala.placa_sant_pol.37b']);
    p.talk('sanca', 'creu');
    p.do('walkTo', 'carrer');
    p.talk('ponc', 'adeu7');
    p.do('give', 'ponc', 'tauleta');
    p.do('give', 'ponc', 'cera');
    expect(n.flag('segell_acceptat')).toBe(true);
    p.talk('ponc');

    // El judici: les cartes abans d'hora, i després en ordre.
    expect(p.room).toBe('judici');
    p.do('give', 'ponc', 'tauleta');
    p.do('give', 'ponc', 'serra');
    p.do('talkTo', 'ingilberga');
    p.do('give', 'ponc', 'tauleta');
    p.do('talkTo', 'iri');
    p.do('give', 'ponc', 'carta_calcada');
    expect(n.flag('judici_guanyat')).toBe(false);
    expect(claus(p.do('give', 'iri', 'carta_emma'))).toEqual(['donar.ara_no']);
    p.do('give', 'ponc', 'carta_emma');
    p.do('give', 'ponc', 'carta_calcada');
    expect(n.flag('judici_guanyat')).toBe(true);

    // L'epíleg: el plançó i el cofre abans del forat.
    expect(p.room).toBe('epileg');
    p.use('destral', 'forat_nou');
    p.use('cofre', 'forat_nou');
    p.do('pickUp', 'carretilla');
    p.use('planco', 'forat_nou');
    p.do('talkTo', 'sunifred');
    p.use('pala', 'forat_nou');
    p.use('planco', 'forat_nou');
    p.use('cofre', 'forat_nou');
    p.use('planco', 'forat_nou');
    p.do('look', 'rotul');
    expect(n.flag('final_avet')).toBe(true);
    expect(n.resolveEnding()).toBe('avet');
  });
});
