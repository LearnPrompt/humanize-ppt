import React from 'react';
import {
  AbsoluteFill,
  Composition,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';
import {registerRoot} from 'remotion';

const ink = '#0a0a0a';
const paper = '#f5f4ef';
const bg = '#ecece8';
const lemon = '#e6ff3d';
const grey = '#8a8a85';
const sans = 'Helvetica Neue, Arial, sans-serif';
const mono = 'Menlo, Monaco, ui-monospace, monospace';

const steps = [
  ['01', 'READ', 'load files and context'],
  ['02', 'ACT', 'run the bounded tool'],
  ['03', 'CHECK', 'make the result inspectable'],
  ['04', 'WRITE BACK', 'deliver the artifact'],
];

function Step({index, num, title, desc}: {index: number; num: string; title: string; desc: string}) {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const start = 18 + index * 24;
  const enter = spring({frame: frame - start, fps, config: {damping: 18, stiffness: 130}});
  const active = interpolate(frame, [start + 10, start + 32, start + 56], [0, 1, 0.25], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  return (
    <div
      style={{
        height: '100%',
        background: index === 1 ? lemon : index === 2 ? ink : paper,
        color: index === 2 ? paper : ink,
        padding: 34,
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'space-between',
        transform: `translateY(${(1 - enter) * 42}px)`,
        opacity: Math.min(1, enter),
        boxShadow: active > 0.7 ? `0 0 0 8px ${lemon}` : 'none',
      }}
    >
      <div style={{fontFamily: mono, fontSize: 24, letterSpacing: '0.12em'}}>{num}</div>
      <div>
        <div style={{fontFamily: sans, fontWeight: 900, fontSize: 58, lineHeight: 0.92}}>{title}</div>
        <div style={{fontFamily: sans, fontSize: 24, lineHeight: 1.25, marginTop: 16, color: index === 2 ? paper : '#222'}}>
          {desc}
        </div>
      </div>
    </div>
  );
}

function EntryLoop() {
  const frame = useCurrentFrame();
  const line = interpolate(frame, [18, 116], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const finalOpacity = interpolate(frame, [124, 152], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  return (
    <AbsoluteFill style={{backgroundColor: bg, color: ink, fontFamily: sans}}>
      <div
        style={{
          position: 'absolute',
          inset: 40,
          display: 'grid',
          gridTemplateColumns: 'repeat(12, 1fr)',
          gridTemplateRows: 'repeat(8, 1fr)',
          gap: 12,
        }}
      >
        <div style={{gridColumn: '1 / span 4', gridRow: '1 / span 8', background: lemon, padding: 38, display: 'flex', flexDirection: 'column', justifyContent: 'space-between'}}>
          <div style={{fontFamily: mono, fontSize: 20, letterSpacing: '0.12em'}}>REMOTION MATERIAL</div>
          <div style={{fontWeight: 700, fontSize: 110, lineHeight: 0.9, letterSpacing: '-0.03em'}}>ENTRY LOOP</div>
          <div style={{fontSize: 25, lineHeight: 1.25}}>A visible motion test for the Hermes execution cycle.</div>
        </div>
        <div style={{gridColumn: '5 / span 8', gridRow: '1 / span 5', background: ink, color: paper, padding: 38, position: 'relative'}}>
          <div style={{fontFamily: mono, fontSize: 18, letterSpacing: '0.12em', color: grey}}>{'READ -> ACT -> CHECK -> WRITE BACK'}</div>
          <div style={{position: 'absolute', left: 38, right: 38, top: 174, height: 10, background: '#333'}}>
            <div style={{height: '100%', width: `${line * 100}%`, background: lemon}} />
          </div>
          <div style={{position: 'absolute', left: 38, right: 38, bottom: 42, display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 12}}>
            {steps.map(([num, title, desc], i) => <Step key={num} index={i} num={num} title={title} desc={desc} />)}
          </div>
        </div>
        <div style={{gridColumn: '5 / span 8', gridRow: '6 / span 3', background: paper, padding: 36, display: 'flex', justifyContent: 'space-between', alignItems: 'end', opacity: finalOpacity}}>
          <div style={{fontWeight: 700, fontSize: 68, lineHeight: 0.95}}>FROM PROMPT TO ARTIFACT.</div>
          <div style={{fontFamily: mono, fontSize: 22, letterSpacing: '0.12em'}}>STATUS / PASS</div>
        </div>
      </div>
    </AbsoluteFill>
  );
}

export const RemotionRoot = () => (
  <Composition
    id="NeoGridEntryLoop"
    component={EntryLoop}
    durationInFrames={180}
    fps={30}
    width={1920}
    height={1080}
  />
);

registerRoot(RemotionRoot);
