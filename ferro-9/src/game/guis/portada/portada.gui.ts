// Creat per adapters/benne (benne-content.ts): els botons de la portada.
import { guis } from '@game';
import { comenca, carrega } from './portada.ids';
import { startFromCover } from '../../narrative/narrative.script';

comenca.onClick(() => startFromCover())
carrega.onClick(() => guis.loadMenu.show())
