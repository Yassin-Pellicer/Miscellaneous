import { NextRequest, NextResponse } from "next/server";
import { spawn } from "child_process";
import { writeFile, unlink } from "fs/promises";
import { v4 as uuidv4 } from "uuid";
import os from "os";
import path from "path";

// Force Node.js runtime
export const runtime = "nodejs";

export async function POST(req: NextRequest) {
  try {
    const { image } = await req.json();
    
    if (!image || typeof image !== "string") {
      return NextResponse.json({ error: "No image provided" }, { status: 400 });
    }

    // Remove the base64 prefix
    const base64Data = image.replace(/^data:image\/png;base64,/, "");
    
    // Write image to temp file
    const tempFilename = path.join(os.tmpdir(), `${uuidv4()}.png`);
    await writeFile(tempFilename, base64Data, "base64");

    // Get the absolute path to the Python script
    const scriptPath = path.join(process.cwd(), "src/app/mnist_predictor/use_trained_weights.py");

    // Call Python script with the image path
    const result = await new Promise<string>((resolve, reject) => {
      const py = spawn("python3", [scriptPath, tempFilename]);
      
      let output = "";
      let error = "";

      py.stdout.on("data", (data) => {
        output += data.toString();
      });

      py.stderr.on("data", (data) => {
        error += data.toString();
        console.error("Python error:", data.toString());
      });

      py.on("close", async (code) => {
        // Clean up temp file
        try {
          await unlink(tempFilename);
        } catch (cleanupError) {
          console.warn("Failed to cleanup temp file:", cleanupError);
        }

        if (code === 0) {
          resolve(output.trim());
        } else {
          reject(new Error(`Python script failed with code ${code}: ${error}`));
        }
      });

      py.on("error", (err) => {
        reject(new Error(`Failed to start Python process: ${err.message}`));
      });
    });

    return NextResponse.json({ result });
  } catch (err) {
    console.error("API error:", err);
    return NextResponse.json(
      { error: err instanceof Error ? err.message : String(err) },
      { status: 500 }
    );
  }
}