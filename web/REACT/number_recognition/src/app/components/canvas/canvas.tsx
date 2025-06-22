"use client";

import { useRef, useState } from "react";
import { useCanvasDraw } from "./canvasHooks";

export default function Canvas() {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const { clearCanvas, predictedNumber } = useCanvasDraw(canvasRef);

  return (
    <div>
      <canvas
        ref={canvasRef}
        width={400}
        height={400}
        className="border border-gray-600 rounded-md w-[400px] h-[400px]"
        id="canvas"
      ></canvas>

      <div className="flex mt-5 items-center justify-between">
        <p className="font-bold">Predicted Number: {predictedNumber}</p>
        <button
          onClick={clearCanvas}
          className="px-4 py-1 rounded-full bg-black text-white font-bold hover:cursor-pointer hover:bg-gray-600"
        >
          Clear
        </button>
      </div>
    </div>
  );
}
