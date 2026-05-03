import React from "react";
import {
  AbsoluteFill,
  Img,
  Sequence,
  interpolate,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { loadFont as loadFraunces } from "@remotion/google-fonts/Fraunces";
import { loadFont as loadInter } from "@remotion/google-fonts/Inter";

const { fontFamily: FRAUNCES } = loadFraunces();
const { fontFamily: INTER } = loadInter();

const INK = "#F4EFE6";
const BG = "#0E0B08";
const ACCENT = "#F25C3D";
const MUTE = "#8C8579";
const HAIR = "#2A2520";

type Scene = {
  id: string;
  image: string;
  kicker: string;
  headline: string;
  caption: string;
  tone?: string;
  focus?: string; // CSS object-position value, e.g. "center top", "70% center"
};

type Stat = { value: string; label: string };

type Data = {
  title: string;
  subtitle: string;
  stats: Stat[];
  scenes: Scene[];
  closing_line: string;
  signature: string;
};

// ---------- helpers ----------

const easeOut = (t: number) => 1 - Math.pow(1 - t, 3);

const Kicker: React.FC<{
  children: React.ReactNode;
  color?: string;
  size?: number;
}> = ({ children, color = MUTE, size = 22 }) => (
  <div
    style={{
      fontFamily: INTER,
      fontWeight: 600,
      letterSpacing: "0.22em",
      textTransform: "uppercase",
      color,
      fontSize: size,
    }}
  >
    {children}
  </div>
);

const Hairline: React.FC<{ width?: string | number; color?: string }> = ({
  width = "100%",
  color = HAIR,
}) => (
  <div style={{ width, height: 1, background: color }} />
);

// Grain overlay
const Grain: React.FC = () => (
  <AbsoluteFill
    style={{
      pointerEvents: "none",
      backgroundImage:
        "radial-gradient(rgba(255,255,255,0.03) 1px, transparent 1px)",
      backgroundSize: "3px 3px",
      mixBlendMode: "overlay",
    }}
  />
);

// ---------- intro ----------

const Intro: React.FC<{ data: Data; heroImage: string }> = ({ data, heroImage }) => {
  const frame = useCurrentFrame();

  const imageOp = interpolate(frame, [0, 20], [0, 1], {
    extrapolateRight: "clamp",
    extrapolateLeft: "clamp",
  });
  const imageScale = interpolate(frame, [0, 60], [1.06, 1.12], {
    extrapolateRight: "clamp",
    extrapolateLeft: "clamp",
  });

  const kickerOp = interpolate(frame, [8, 24], [0, 1], {
    extrapolateRight: "clamp",
    extrapolateLeft: "clamp",
  });
  const titleOp = interpolate(frame, [20, 42], [0, 1], {
    extrapolateRight: "clamp",
    extrapolateLeft: "clamp",
  });
  const titleY = interpolate(frame, [20, 42], [0, 1], {
    extrapolateRight: "clamp",
    extrapolateLeft: "clamp",
  });

  return (
    <AbsoluteFill
      style={{
        background: BG,
        flexDirection: "column",
        justifyContent: "space-between",
      }}
    >
      <AbsoluteFill style={{ opacity: imageOp }}>
        <AbsoluteFill
          style={{
            transform: `scale(${imageScale})`,
            transformOrigin: "center",
          }}
        >
          <Img
            src={staticFile(heroImage)}
            style={{
              width: "100%",
              height: "100%",
              objectFit: "cover",
              filter: "saturate(0.95) contrast(1.04) brightness(0.45)",
            }}
          />
        </AbsoluteFill>
        <AbsoluteFill
          style={{
            background:
              "linear-gradient(180deg, rgba(14,11,8,0.65) 0%, rgba(14,11,8,0.3) 35%, rgba(14,11,8,0.15) 55%, rgba(14,11,8,0.85) 100%)",
          }}
        />
      </AbsoluteFill>

      <div
        style={{
          position: "absolute",
          top: 120,
          left: 80,
          right: 80,
          opacity: kickerOp,
        }}
      >
        <Kicker color={MUTE} size={26}>
          Hermes &nbsp;·&nbsp; Recap
        </Kicker>
        <div style={{ marginTop: 14 }}>
          <Hairline color="rgba(244,239,230,0.35)" />
        </div>
      </div>

      <div
        style={{
          position: "absolute",
          left: 80,
          right: 80,
          bottom: 180,
          opacity: titleOp,
          transform: `translateY(${(1 - easeOut(titleY)) * 40}px)`,
        }}
      >
        <div style={{ marginBottom: 30 }}>
          <Kicker color={ACCENT} size={26}>
            {data.subtitle}
          </Kicker>
        </div>
        <div
          style={{
            fontFamily: FRAUNCES,
            fontWeight: 360,
            fontStretch: "110%",
            color: INK,
            fontSize: 168,
            lineHeight: 0.95,
            letterSpacing: "-0.025em",
          }}
        >
          {data.title}
        </div>
      </div>

      <div
        style={{
          position: "absolute",
          bottom: 90,
          left: 80,
          right: 80,
          opacity: interpolate(frame, [38, 58], [0, 1], {
            extrapolateRight: "clamp",
            extrapolateLeft: "clamp",
          }),
        }}
      >
        <Hairline color="rgba(244,239,230,0.35)" />
        <div style={{ marginTop: 14, display: "flex", justifyContent: "space-between" }}>
          <Kicker>{data.signature}</Kicker>
          <Kicker>Vol. I &nbsp;/&nbsp; Edition of One</Kicker>
        </div>
      </div>
      <Grain />
    </AbsoluteFill>
  );
};

// ---------- scene ----------

const SceneCard: React.FC<{
  scene: Scene;
  index: number;
}> = ({ scene, index }) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();

  // Ken Burns — zoom OR pan per scene, never both
  const progress = frame / durationInFrames;
  const direction = index % 2 === 0 ? 1 : -1;
  const isZoom = index % 2 === 0;
  const scale = isZoom
    ? interpolate(progress, [0, 1], [1.04, 1.14])
    : 1.08;
  const tx = isZoom
    ? 0
    : interpolate(progress, [0, 1], [-11 * direction, 11 * direction]);
  const ty = 0;

  // Photo enter
  const photoOp = interpolate(frame, [0, 12], [0, 1], {
    extrapolateRight: "clamp",
    extrapolateLeft: "clamp",
  });
  // Photo out (fade tail for crossfade feel)
  const photoTail = interpolate(
    frame,
    [durationInFrames - 12, durationInFrames],
    [1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  // Headline fade-in
  const headlineOp = interpolate(frame, [22, 40], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const headlineY = interpolate(frame, [22, 40], [16, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const captionOp = interpolate(frame, [42, 60], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const captionY = interpolate(frame, [42, 60], [16, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const kickerOp = interpolate(frame, [6, 20], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill style={{ background: BG, opacity: photoTail }}>
      {/* Photo */}
      <AbsoluteFill style={{ opacity: photoOp }}>
        <AbsoluteFill
          style={{
            transform: `scale(${scale}) translate(${tx}px, ${ty}px)`,
            transformOrigin: "center",
          }}
        >
          <Img
            src={staticFile(scene.image)}
            style={{
              width: "100%",
              height: "100%",
              objectFit: "cover",
              objectPosition: scene.focus || "center center",
              filter: "saturate(0.95) contrast(1.04)",
            }}
          />
        </AbsoluteFill>
        {/* Bottom gradient for text legibility — compact lower third */}
        <AbsoluteFill
          style={{
            background:
              "linear-gradient(180deg, rgba(14,11,8,0.0) 0%, rgba(14,11,8,0.0) 55%, rgba(14,11,8,0.75) 72%, rgba(14,11,8,0.95) 100%)",
          }}
        />
      </AbsoluteFill>

      {/* Top kicker */}
      <div
        style={{
          position: "absolute",
          top: 100,
          left: 80,
          right: 80,
          opacity: kickerOp,
        }}
      >
        <Hairline color="rgba(244,239,230,0.35)" />
        <div style={{ display: "flex", justifyContent: "space-between", marginTop: 14 }}>
          <Kicker color={INK} size={24}>
            {scene.kicker}
          </Kicker>
          <Kicker color="rgba(244,239,230,0.55)" size={24}>
            № {String(index + 1).padStart(2, "0")}
          </Kicker>
        </div>
      </div>

      {/* Bottom text block — pushed low to avoid covering subjects */}
      <div
        style={{
          position: "absolute",
          left: 80,
          right: 80,
          bottom: 100,
        }}
      >
        <div
          style={{
            fontFamily: FRAUNCES,
            fontWeight: 380,
            color: INK,
            fontSize: 58,
            lineHeight: 1.08,
            letterSpacing: "-0.02em",
            opacity: headlineOp,
            transform: `translateY(${headlineY}px)`,
          }}
        >
          {scene.headline}
        </div>

        <div
          style={{
            opacity: captionOp,
            transform: `translateY(${captionY}px)`,
            marginTop: 24,
            fontFamily: INTER,
            fontWeight: 400,
            color: "rgba(244,239,230,0.78)",
            fontSize: 30,
            lineHeight: 1.4,
            maxWidth: 880,
          }}
        >
          {scene.caption}
        </div>
      </div>
      <Grain />
    </AbsoluteFill>
  );
};

// ---------- closing ----------

const Closing: React.FC<{ data: Data }> = ({ data }) => {
  const frame = useCurrentFrame();

  const lines = data.closing_line.split("\n");
  const op1 = interpolate(frame, [0, 18], [0, 1], { extrapolateRight: "clamp", extrapolateLeft: "clamp" });
  const op2 = interpolate(frame, [22, 40], [0, 1], { extrapolateRight: "clamp", extrapolateLeft: "clamp" });
  const sigOp = interpolate(frame, [50, 70], [0, 1], { extrapolateRight: "clamp", extrapolateLeft: "clamp" });

  return (
    <AbsoluteFill
      style={{
        background: BG,
        padding: "160px 80px",
        flexDirection: "column",
        justifyContent: "space-between",
      }}
    >
      <div>
        <Kicker color={MUTE}>In closing</Kicker>
        <div style={{ marginTop: 14 }}>
          <Hairline />
        </div>
      </div>

      <div>
        <div
          style={{
            fontFamily: FRAUNCES,
            fontWeight: 360,
            color: INK,
            fontSize: 96,
            lineHeight: 1.05,
            letterSpacing: "-0.02em",
          }}
        >
          <div style={{ opacity: op1 }}>{lines[0]}</div>
          {lines[1] && (
            <div style={{ opacity: op2, marginTop: 12 }}>{lines[1]}</div>
          )}
        </div>
      </div>

      <div style={{ opacity: sigOp }}>
        <Hairline />
        <div style={{ marginTop: 14, display: "flex", justifyContent: "space-between" }}>
          <Kicker color={ACCENT}>{data.signature}</Kicker>
          <Kicker>No. 001 &nbsp;/&nbsp; kept forever</Kicker>
        </div>
      </div>
      <Grain />
    </AbsoluteFill>
  );
};

// ---------- main ----------

const SCENE_DURS = [75, 105, 90, 120, 85]; // variable: 2.5s, 3.5s, 3s, 4s, ~2.8s

export const Recap: React.FC<{ data: Data }> = ({ data }) => {
  const heroImage = data.scenes[0]?.image || "";
  // Scene 0 is used as the intro background — remaining scenes get their own cards
  const body = data.scenes.slice(1);

  const INTRO_DUR = 90; // 3s
  const CLOSE_DUR = 90; // 3s
  const sceneDur = (i: number) => SCENE_DURS[i % SCENE_DURS.length];
  const sceneOffset = (i: number) => {
    let off = INTRO_DUR;
    for (let j = 0; j < i; j++) off += sceneDur(j);
    return off;
  };
  const totalScenes = body.reduce((s, _, i) => s + sceneDur(i), 0);

  return (
    <AbsoluteFill style={{ background: BG }}>
      <Sequence from={0} durationInFrames={INTRO_DUR}>
        <Intro data={data} heroImage={heroImage} />
      </Sequence>

      {body.map((scene, i) => (
        <Sequence
          key={scene.id}
          from={sceneOffset(i)}
          durationInFrames={sceneDur(i)}
        >
          <SceneCard scene={scene} index={i} />
        </Sequence>
      ))}

      <Sequence
        from={INTRO_DUR + totalScenes}
        durationInFrames={CLOSE_DUR}
      >
        <Closing data={data} />
      </Sequence>
    </AbsoluteFill>
  );
};
