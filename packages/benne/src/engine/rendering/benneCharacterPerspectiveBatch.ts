import * as Phaser from 'phaser';

import {
  BENNE_MULTI_FRAG_SOURCE,
  BENNE_MULTI_VERT_SOURCE,
  benneMakeApplyLighting,
  benneMakeApplyTint,
  benneMakeDefineLights,
  benneMakeDefineTexCount,
  benneMakeGetNormalFromMap,
  benneMakeGetTexture1,
  benneMakeGetTexCoordOut,
  benneMakeGetTexRes,
  benneMakeOutInverseRotation,
  benneMakeRotationDatum,
  benneMakeSmoothPixelArt,
} from './phaserQuadStandardShaderInline.js';

type BenneQuadRenderOptions = { texRes?: boolean; [key: string]: unknown };

/** Same as stock {@link Phaser.Renderer.WebGL.RenderNodes.BatchHandlerQuad} name for `setRenderNodeRole`. */
export const BENNE_CHARACTER_BATCH_HANDLER_NAME = 'BatchHandlerBenneCharacterQuad';

/** Companion submitter that brackets each draw with {@link benneCharacterBatchObjectStack}. */
export const BENNE_CHARACTER_SUBMITTER_NAME = 'SubmitterBenneCharacterQuad';


/** `CharacterData.artScale` of the sprite being drawn (1 when it has none). */
function characterSheetArtScale(obj: object): number {
  const getData = (obj as { getData?: (key: string) => unknown }).getData;
  const data = typeof getData === 'function' ? (getData.call(obj, 'character') as { artScale?: number } | undefined) : undefined;
  const k = data?.artScale;
  return typeof k === 'number' && k > 0 ? k : 1;
}

const benneCharacterPerspectiveShaderAddition = {
  name: 'BenneCharacterPerspective',
  additions: {
    vertexDefine: 'attribute float inPerspMag;\n',
    outVariables: 'varying float outPerspMag;\n',
    vertexProcess: 'outPerspMag = inPerspMag;\n',
  },
  disable: false,
};

/**
 * Pixel art at a non-integer size. A character is drawn at whatever size its perspective scale and the screen give
 * (scale 0.37–1.25 in a deep room, × 2 to 3.7 screen px per room px), and with plain nearest sampling some texels
 * then cover one screen pixel and others two, or are skipped: the figure looks ragged, and blocky when it is small.
 * This samples by the texel footprint of each screen pixel (`fwidth`):
 * - **magnified** (a texel covers more than a pixel): "sharp bilinear" — each texel stays solid and only the one-pixel
 *   seam between two texels is blended, so every texel looks the same size;
 * - **minified** (several texels per pixel, a figure in the distance): the average of the footprint (up to 4×4
 *   samples), like a smaller drawing.
 * Colours are premultiplied, so averaging them blends the edges of the silhouette correctly.
 */
const benneCharacterPixelArtSamplingAddition = {
  name: 'BenneCharacterPixelArtSampling',
  additions: {
    extensions: '#extension GL_OES_standard_derivatives : enable',
    fragmentHeader: [
      'vec4 benneTexel(vec2 t, vec2 texWH) {',
      '    t = clamp(t, vec2(0.0), texWH - vec2(1.0));',
      '    return getTexture((t + vec2(0.5)) / texWH);',
      '}',
      'vec4 bennePixelArtSample(vec2 uv, vec2 texWH) {',
      '    vec2 px = uv * texWH;',
      '    vec2 fw = max(fwidth(px), vec2(1e-4));',
      '    float foot = max(fw.x, fw.y);',
      '    if (foot > 1.2) {',
      '        float n = min(4.0, ceil(foot));',
      '        vec4 acc = vec4(0.0);',
      '        float k = 0.0;',
      '        for (int j = 0; j < 4; j++) {',
      '            for (int i = 0; i < 4; i++) {',
      '                if (float(i) < n && float(j) < n) {',
      '                    vec2 o = (vec2(float(i), float(j)) + 0.5) / n - 0.5;',
      '                    acc += benneTexel(floor(px + o * fw), texWH);',
      '                    k += 1.0;',
      '                }',
      '            }',
      '        }',
      '        return acc / k;',
      '    }',
      '    vec2 p = px - 0.5;',
      '    vec2 i0 = floor(p);',
      '    vec2 f = p - i0;',
      '    vec2 w = clamp((f - 0.5) / fw + 0.5, 0.0, 1.0);',
      '    vec4 a = benneTexel(i0, texWH);',
      '    vec4 b = benneTexel(i0 + vec2(1.0, 0.0), texWH);',
      '    vec4 c = benneTexel(i0 + vec2(0.0, 1.0), texWH);',
      '    vec4 d = benneTexel(i0 + vec2(1.0, 1.0), texWH);',
      '    return mix(mix(a, b, w.x), mix(c, d, w.x), w.y);',
      '}',
    ].join('\n'),
    fragmentProcess: 'fragColor = bennePixelArtSample(outTexCoord, getTexRes());',
  },
  disable: false,
};

const benneCharacterQuadConfig = {
  name: BENNE_CHARACTER_BATCH_HANDLER_NAME,
  verticesPerInstance: 4,
  indicesPerInstance: 6,
  shaderName: 'STANDARD',
  vertexSource: BENNE_MULTI_VERT_SOURCE,
  fragmentSource: BENNE_MULTI_FRAG_SOURCE,
  shaderAdditions: [
    benneMakeGetTexCoordOut(),
    benneMakeGetTexRes(),
    benneMakeSmoothPixelArt(true),
    benneCharacterPerspectiveShaderAddition,
    benneMakeDefineTexCount(1),
    benneMakeGetTexture1(),
    benneCharacterPixelArtSamplingAddition,
    benneMakeApplyTint(),
    benneMakeDefineLights(true),
    benneMakeRotationDatum(true),
    benneMakeOutInverseRotation(true),
    benneMakeGetNormalFromMap(true),
    benneMakeApplyLighting(true),
  ] as Phaser.Types.Renderer.WebGL.ShaderAdditionConfig[],
  vertexBufferLayout: {
    usage: 'DYNAMIC_DRAW',
    layout: [
      { name: 'inPosition', size: 2 },
      { name: 'inTexCoord', size: 2 },
      { name: 'inTexDatum' },
      { name: 'inTintEffect' },
      { name: 'inTint', size: 4, type: 'UNSIGNED_BYTE', normalized: true },
      { name: 'inPerspMag' },
    ],
  },
};

const registeredGames = new WeakSet<Phaser.Game>();

/** Stack of sprites/images currently inside Benne character submitter `run` (re-entrancy safe). */
const benneCharacterBatchObjectStack: Phaser.GameObjects.GameObject[] = [];

type BatchHandlerQuadClass = typeof Phaser.Renderer.WebGL.RenderNodes.BatchHandlerQuad;
type SubmitterQuadClass = typeof Phaser.Renderer.WebGL.RenderNodes.SubmitterQuad;

/**
 * Registers {@link BENNE_CHARACTER_BATCH_HANDLER_NAME} and {@link BENNE_CHARACTER_SUBMITTER_NAME}
 * on the game's WebGL render node manager. Safe to call multiple times per game instance.
 */
export function registerBenneCharacterPerspectiveBatch(game: Phaser.Game): void {
  if (registeredGames.has(game)) {
    return;
  }
  const renderer = game.renderer as Phaser.Renderer.WebGL.WebGLRenderer | null;
  if (!renderer?.renderNodes?.addNodeConstructor) {
    return;
  }
  const BaseBatch = Phaser.Renderer.WebGL.RenderNodes.BatchHandlerQuad as BatchHandlerQuadClass;
  const BaseSubmitter = Phaser.Renderer.WebGL.RenderNodes.SubmitterQuad as SubmitterQuadClass;

  class BatchHandlerBenneCharacterQuad extends BaseBatch {
    constructor(manager: Phaser.Renderer.WebGL.RenderNodes.RenderNodeManager) {
      super(manager, benneCharacterQuadConfig);
      const ro = this.renderOptions as BenneQuadRenderOptions;
      const nr = this.nextRenderOptions as BenneQuadRenderOptions;
      ro.texRes = true;
      nr.texRes = true;
    }

    /**
     * Keep {@link Phaser.Renderer.WebGL.RenderNodes.BatchHandlerQuad#renderOptions}.texRes true so
     * GetTexRes stays enabled and texture dimensions are uploaded, even when smooth pixel art is off.
     */
    updateRenderOptions(
      renderOptions?: Phaser.Types.Renderer.WebGL.RenderNodes.BatchHandlerQuadRenderOptions,
    ): void {
      super.updateRenderOptions(renderOptions ?? ({} as object));
      const next = this.nextRenderOptions as BenneQuadRenderOptions;
      if (next.texRes !== true) {
        next.texRes = true;
        (this as unknown as { _renderOptionsChanged: boolean })._renderOptionsChanged = true;
      }
    }

    batch(
      currentContext: Phaser.Renderer.WebGL.DrawingContext,
      glTexture: Phaser.Renderer.WebGL.Wrappers.WebGLTextureWrapper,
      x0: number,
      y0: number,
      x1: number,
      y1: number,
      x2: number,
      y2: number,
      x3: number,
      y3: number,
      texX: number,
      texY: number,
      texWidth: number,
      texHeight: number,
      tintMode: number,
      tintTL: number,
      tintBL: number,
      tintTR: number,
      tintBR: number,
      renderOptions: Phaser.Types.Renderer.WebGL.RenderNodes.BatchHandlerQuadRenderOptions,
    ): void {
      const top = benneCharacterBatchObjectStack[benneCharacterBatchObjectStack.length - 1];
      // The magnification in 1× frame units: a sheet drawn at `artScale`× is shown at 1/artScale on purpose (its
      // detail is denser, not something to bucket away), so only the perspective part of the scale counts.
      const mag =
        top && 'scaleX' in top && 'scaleY' in top
          ? Math.max(Math.abs(top.scaleX as number), Math.abs(top.scaleY as number)) * characterSheetArtScale(top)
          : 1;

      if (this.instanceCount === 0) {
        this.manager.setCurrentBatchNode(this, currentContext);
      }

      this.updateRenderOptions(renderOptions);
      if ((this as unknown as { _renderOptionsChanged: boolean })._renderOptionsChanged) {
        this.run(currentContext);
        this.updateShaderConfig();
      }

      const textureDatum = this.batchTextures(glTexture, renderOptions);

      let vo = this.instanceCount * this.floatsPerInstance;
      const vertexBuffer = this.vertexBufferLayout.buffer;
      const vertexViewF32 = vertexBuffer.viewF32!;
      const vertexViewU32 = vertexBuffer.viewU32!;

      // Bottom-left
      vertexViewF32[vo++] = x1;
      vertexViewF32[vo++] = y1;
      vertexViewF32[vo++] = texX;
      vertexViewF32[vo++] = texY + texHeight;
      vertexViewF32[vo++] = textureDatum;
      vertexViewF32[vo++] = tintMode;
      vertexViewU32[vo++] = tintBL;
      vertexViewF32[vo++] = mag;

      // Top-left
      vertexViewF32[vo++] = x0;
      vertexViewF32[vo++] = y0;
      vertexViewF32[vo++] = texX;
      vertexViewF32[vo++] = texY;
      vertexViewF32[vo++] = textureDatum;
      vertexViewF32[vo++] = tintMode;
      vertexViewU32[vo++] = tintTL;
      vertexViewF32[vo++] = mag;

      // Bottom-right
      vertexViewF32[vo++] = x3;
      vertexViewF32[vo++] = y3;
      vertexViewF32[vo++] = texX + texWidth;
      vertexViewF32[vo++] = texY + texHeight;
      vertexViewF32[vo++] = textureDatum;
      vertexViewF32[vo++] = tintMode;
      vertexViewU32[vo++] = tintBR;
      vertexViewF32[vo++] = mag;

      // Top-right
      vertexViewF32[vo++] = x2;
      vertexViewF32[vo++] = y2;
      vertexViewF32[vo++] = texX + texWidth;
      vertexViewF32[vo++] = texY;
      vertexViewF32[vo++] = textureDatum;
      vertexViewF32[vo++] = tintMode;
      vertexViewU32[vo++] = tintTR;
      vertexViewF32[vo++] = mag;

      this.instanceCount++;
      this.currentBatchEntry.count++;

      if (this.instanceCount === this.instancesPerBatch) {
        this.run(currentContext);
      }
    }
  }

  class SubmitterBenneCharacterQuad extends BaseSubmitter {
    constructor(manager: Phaser.Renderer.WebGL.RenderNodes.RenderNodeManager) {
      super(manager);
    }

    run(
      drawingContext: Phaser.Renderer.WebGL.DrawingContext,
      gameObject: Phaser.GameObjects.GameObject,
      parentMatrix: Phaser.GameObjects.Components.TransformMatrix,
      element: unknown,
      texturerNode: Phaser.Renderer.WebGL.RenderNodes.RenderNode,
      transformerNode: Phaser.Renderer.WebGL.RenderNodes.RenderNode | { quad: Float32Array },
      tinterNode?: Phaser.Renderer.WebGL.RenderNodes.RenderNode,
      normalMap?: Phaser.Renderer.WebGL.Wrappers.WebGLTextureWrapper,
      normalMapRotation?: number,
    ): void {
      benneCharacterBatchObjectStack.push(gameObject);
      try {
        BaseSubmitter.prototype.run.call(
          this,
          drawingContext,
          gameObject,
          parentMatrix,
          element as object,
          texturerNode,
          transformerNode as object,
          tinterNode,
          normalMap,
          normalMapRotation,
        );
      } finally {
        benneCharacterBatchObjectStack.pop();
      }
    }
  }

  renderer.renderNodes.addNodeConstructor(BENNE_CHARACTER_BATCH_HANDLER_NAME, BatchHandlerBenneCharacterQuad);
  renderer.renderNodes.addNodeConstructor(BENNE_CHARACTER_SUBMITTER_NAME, SubmitterBenneCharacterQuad);
  registeredGames.add(game);
}

/** Applies Benne character WebGL nodes after Phaser `initRenderNodes` (both roles required). */
export function attachBenneCharacterPerspectiveRenderNodes(
  sprite: Phaser.GameObjects.Image | Phaser.GameObjects.Sprite,
): void {
  sprite.setRenderNodeRole('Submitter', BENNE_CHARACTER_SUBMITTER_NAME);
  sprite.setRenderNodeRole('BatchHandler', BENNE_CHARACTER_BATCH_HANDLER_NAME);
}
