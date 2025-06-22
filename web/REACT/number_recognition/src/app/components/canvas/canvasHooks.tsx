import { useEffect, useRef, useState } from "react";

export function useCanvasDraw(
  canvasRef: React.RefObject<HTMLCanvasElement | null>
) {
  const isDrawing = useRef(false);
  const lastPoint = useRef<{ x: number; y: number } | null>(null);
  const [predictedNumber, setPredictedNumber] = useState<number | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    // Set canvas size to match CSS size exactly
    const rect = canvas.getBoundingClientRect();
    canvas.width = rect.width;
    canvas.height = rect.height;

    // Configure drawing context
    ctx.lineWidth = 16;
    ctx.strokeStyle = "#000";
    ctx.lineCap = "round";
    ctx.lineJoin = "round";
    
    // Fill with white background (important for MNIST)
    ctx.fillStyle = "white";
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    const getMousePos = (e: MouseEvent | TouchEvent) => {
      const rect = canvas.getBoundingClientRect();
      const clientX = "touches" in e ? e.touches[0].clientX : e.clientX;
      const clientY = "touches" in e ? e.touches[0].clientY : e.clientY;
      return {
        x: clientX - rect.left,
        y: clientY - rect.top,
      };
    };

    const saveCanvas = async () => {
      if (!canvas) return;
      
      const ctx = canvas.getContext("2d");
      if (!ctx) return;

      // Check if there's any drawing on the canvas
      const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
      const hasDrawing = imageData.data.some((val, index) => {
        // Check if any pixel is not white (255, 255, 255, 255)
        if (index % 4 === 3) return false; // Skip alpha channel
        return val !== 255;
      });

      if (hasDrawing) {
        const dataUrl = canvas.toDataURL("image/png");
        await makePrediction(dataUrl);
      }
    };

    const startDrawing = (e: MouseEvent | TouchEvent) => {
      e.preventDefault();
      isDrawing.current = true;
      lastPoint.current = getMousePos(e);
    };

    const draw = (e: MouseEvent | TouchEvent) => {
      e.preventDefault();
      if (!isDrawing.current || !lastPoint.current) return;

      const newPoint = getMousePos(e);
      
      ctx.beginPath();
      ctx.moveTo(lastPoint.current.x, lastPoint.current.y);
      ctx.lineTo(newPoint.x, newPoint.y);
      ctx.stroke();
      
      lastPoint.current = newPoint;
    };

    const stopDrawing = async (e: MouseEvent | TouchEvent) => {
      e.preventDefault();
      if (!isDrawing.current) return;
      
      isDrawing.current = false;
      lastPoint.current = null;
      await saveCanvas();
    };

    // Add event listeners
    canvas.addEventListener("mousedown", startDrawing);
    canvas.addEventListener("mousemove", draw);
    canvas.addEventListener("mouseup", stopDrawing);
    canvas.addEventListener("mouseleave", stopDrawing);
    
    canvas.addEventListener("touchstart", startDrawing, { passive: false });
    canvas.addEventListener("touchmove", draw, { passive: false });
    canvas.addEventListener("touchend", stopDrawing, { passive: false });

    return () => {
      canvas.removeEventListener("mousedown", startDrawing);
      canvas.removeEventListener("mousemove", draw);
      canvas.removeEventListener("mouseup", stopDrawing);
      canvas.removeEventListener("mouseleave", stopDrawing);
      canvas.removeEventListener("touchstart", startDrawing);
      canvas.removeEventListener("touchmove", draw);
      canvas.removeEventListener("touchend", stopDrawing);
    };
  }, [canvasRef]);

  async function makePrediction(dataUrl: string) {
    setIsLoading(true);
    try {
      const res = await fetch("/api/mnist", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ image: dataUrl }),
      });

      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
      }

      const data = await res.json();
      console.log("Prediction:", data.result);
      
      // Parse the result to get just the number
      const match = data.result.match(/Predicted class: (\d+)/);
      if (match) {
        setPredictedNumber(parseInt(match[1]));
      }
    } catch (error) {
      console.error("Prediction error:", error);
    } finally {
      setIsLoading(false);
    }
  }

  function clearCanvas() {
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    
    // Clear and fill with white background
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = "white";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // Reset prediction
    setPredictedNumber(null);
  }

  return { 
    clearCanvas, 
    predictedNumber, 
    isLoading 
  };
}