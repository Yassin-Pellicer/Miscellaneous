import argparse
import cv2 # type: ignore
import numpy as np # type: ignore
import tensorflow as tf # type: ignore
import pandas as pd # type: ignore
from ultralytics import YOLO # type: ignore
import threading
import queue
import os

import os
os.environ["XLA_FLAGS"] = "--xla_gpu_cuda_data_dir=/usr/lib/cuda/"

dataset = "/media/yassin/Nuevo vol/Datasets/spanish_traffic/Classification/samples"
labelfile = pd.read_csv("/media/yassin/Nuevo vol/Datasets/spanish_traffic/Classification/gt_spanish_dataset.csv")

classes = sorted(os.listdir(dataset))
classDict = {}
for idx, c in enumerate(classes):
    selected_class_folder = os.path.join(dataset, c)
    img_sample = [img for img in os.listdir(selected_class_folder) if img.endswith(".jpg")][0]
    class_name = labelfile[labelfile["image"] == img_sample]["class_name"].values[0]
    classDict[idx] = class_name

def get_class_name_from_class_index(index):
    return classDict.get(index, f"Unknown-{index}")

def process_frame(frame, yolo, classifier, target_size=(128, 128), conf_threshold=0.5):
    results = yolo(frame, verbose=False, conf=conf_threshold, imgsz=640)
    annotations = []
    
    crops = []
    boxes = []

    for result in results:
        if result.boxes is not None and len(result.boxes) > 0:
            for box in result.boxes.xyxy:
                x1, y1, x2, y2 = map(int, box.cpu().numpy())
                
                if (x2 - x1) < 20 or (y2 - y1) < 20:
                    continue

                crop = frame[max(0,y1):y2, max(0,x1):x2]
                if crop.size == 0:
                    continue

                crop_resized = cv2.resize(crop, target_size)
                crop_rgb = cv2.cvtColor(crop_resized, cv2.COLOR_BGR2RGB)
                crops.append(crop_rgb)
                boxes.append((x1, y1, x2, y2))

    # Batch predict all crops at once (major speedup)
    if crops:
        crops_batch = np.array(crops)
        predictions = classifier.predict(crops_batch, verbose=0)
        
        for i, (x1, y1, x2, y2) in enumerate(boxes):
            predicted_class = np.argmax(predictions[i])
            confidence = predictions[i][predicted_class]
            
            # Only show high-confidence predictions
            if confidence > 0.3:  # Adjust threshold as needed
                label = f"{get_class_name_from_class_index(predicted_class)} ({confidence:.2f})"
                annotations.append((x1, y1, x2, y2, label))

    return annotations

def processing_worker(input_q, output_q, yolo, classifier):
    while True:
        item = input_q.get()
        if item is None:
            break
        
        frame, frame_id = item
        annotations = process_frame(frame.copy(), yolo, classifier)
        output_q.put((annotations, frame_id))
        input_q.task_done()

def process_video(video_path, yolo, classifier):
    cap = cv2.VideoCapture(video_path)
    window_name = "Traffic Sign Detection (Video)"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    fps = 30 
    frame_delay = int(1000 / fps)

    input_q = queue.Queue(maxsize=10)
    output_q = queue.Queue(maxsize=10)

    num_threads = 2
    threads = []
    for _ in range(num_threads):
        t = threading.Thread(target=processing_worker, args=(input_q, output_q, yolo, classifier), daemon=True)
        t.start()
        threads.append(t)

    annotations = []
    frame_count = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        input_q.put((frame, frame_count))

        while not output_q.empty():
            try:
                annotations, _ = output_q.get_nowait()
            except queue.Empty:
                break

        for (x1, y1, x2, y2, label) in annotations:
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0,255,0), 1)
            cv2.putText(frame, label, (x1, y1-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0,255,0), 1)

        cv2.imshow(window_name, frame)

        if cv2.waitKey(frame_delay) & 0xFF == ord("q"):
            break
        if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
            break

    cap.release()
    
    for _ in range(num_threads):
        input_q.put(None)
    for t in threads:
        t.join(timeout=1)
    
    cv2.destroyAllWindows()

def predict_traffic_signs(path, yolo, classifier):
    frame = cv2.imread(path)
    annotations = process_frame(frame, yolo, classifier)
    
    for (x1, y1, x2, y2, label) in annotations:
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0,255,0), 2)
        cv2.putText(frame, label, (x1, y1-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)
    
    cv2.imshow("Traffic Sign Detection (Image)", frame)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def optimize_models(yolo_path, classifier_path):
    yolo = YOLO(yolo_path)
    classifier = tf.keras.models.load_model(classifier_path)
    
    if tf.config.list_physical_devices('GPU'):
        tf.keras.mixed_precision.set_global_policy('mixed_float16')
    
    tf.config.optimizer.set_jit(True) 
    
    return yolo, classifier

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Traffic sign detection on video or image")
    parser.add_argument("--video", type=str, help="Path to input video")
    parser.add_argument("--image", type=str, help="Path to input image")
    parser.add_argument("--yolo", type=str, default="yolo/best.pt", help="Path to YOLO model")
    parser.add_argument("--classifier", type=str, default="keras/model.keras", help="Path to Keras classifier")
    args = parser.parse_args()

    try:
        yolo, classifier = optimize_models(args.yolo, args.classifier)
        print("Models loaded and optimized successfully")
    except Exception as e:
        print(f"Error loading models: {e}")
        exit(1)

    if args.video:
        process_video(args.video, yolo, classifier)
    elif args.image:
        predict_traffic_signs(args.image, yolo, classifier)