import React from "react";
import { Composition } from "remotion";
import { Recap } from "./Recap";
import sampleData from "../../sample.json";

const FPS = 30;
const DURATION_SEC = 30;

export const Root: React.FC = () => {
  return (
    <>
      <Composition
        id="Recap"
        component={Recap as any}
        durationInFrames={FPS * DURATION_SEC}
        fps={FPS}
        width={1080}
        height={1920}
        defaultProps={{ data: sampleData }}
      />
    </>
  );
};
