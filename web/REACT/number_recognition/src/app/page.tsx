import Canvas from "./components/canvas/canvas";

export default function Home() {
  return (
    <div className="flex flex-col items-center justify-between p-24 max-w-7xl mx-auto">
      <header className="flex items-center justify-between mb-8 mx-auto">
        <h1 className="text-2xl font-bold text-center font-mono"> MNIST Number Recognition</h1>
      </header>
      <Canvas></Canvas>
    </div>
  );
}
