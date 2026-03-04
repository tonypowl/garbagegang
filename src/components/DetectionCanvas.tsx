// src/components/DetectionCanvas.tsx
import React, { useEffect, useRef } from "react";

export interface BoundingBox {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
  conf: number;
}

interface Props {
  imageFile: File;
  boxes: BoundingBox[];
  imageSize: { w: number; h: number };
}

const DetectionCanvas: React.FC<Props> = ({ imageFile, boxes, imageSize }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const objectUrl = URL.createObjectURL(imageFile);
    const img = new Image();

    img.onload = () => {
      // Scale canvas to fit container while preserving aspect ratio
      const maxWidth = 320;
      const scale = Math.min(maxWidth / img.width, 1);
      canvas.width = img.width * scale;
      canvas.height = img.height * scale;

      ctx.drawImage(img, 0, 0, canvas.width, canvas.height);

      // Draw each bounding box scaled to canvas size
      const scaleX = canvas.width / imageSize.w;
      const scaleY = canvas.height / imageSize.h;

      boxes.forEach((box) => {
        const x = box.x1 * scaleX;
        const y = box.y1 * scaleY;
        const w = (box.x2 - box.x1) * scaleX;
        const h = (box.y2 - box.y1) * scaleY;

        // Box fill
        ctx.fillStyle = "rgba(255, 51, 51, 0.15)";
        ctx.fillRect(x, y, w, h);

        // Box stroke
        ctx.strokeStyle = "#ff3333";
        ctx.lineWidth = 2;
        ctx.strokeRect(x, y, w, h);

        // Confidence label
        ctx.fillStyle = "#ff3333";
        ctx.font = "bold 11px monospace";
        ctx.fillText(`${Math.round(box.conf * 100)}%`, x + 4, y + 14);
      });

      URL.revokeObjectURL(objectUrl);
    };

    img.src = objectUrl;
  }, [imageFile, boxes, imageSize]);

  return (
    <canvas
      ref={canvasRef}
      style={{
        width: "100%",
        borderRadius: "8px",
        display: "block",
      }}
    />
  );
};

export default DetectionCanvas;
