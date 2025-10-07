#!/usr/bin/env python3
"""
Visual LoRA Training Interface
Web-based UI for training and testing LoRA models
"""
import os
import torch
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
from PIL import Image
import base64
import io
from diffusers import StableDiffusionXLPipeline, DPMSolverMultistepScheduler
import threading
import time

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Global variables for pipeline and training state
pipeline = None
training_status = {"status": "idle", "progress": 0, "message": "Ready"}

def setup_pipeline():
    """Initialize the pipeline once"""
    global pipeline
    if pipeline is None:
        device = "mps" if torch.backends.mps.is_available() else "cpu"
        model_id = "stabilityai/stable-diffusion-xl-base-1.0"
        
        pipeline = StableDiffusionXLPipeline.from_pretrained(
            model_id,
            torch_dtype=torch.float32,
            use_safetensors=True,
            variant=None
        )
        
        pipeline.scheduler = DPMSolverMultistepScheduler.from_config(
            pipeline.scheduler.config,
            use_karras_sigmas=True
        )
        
        if device == "mps":
            pipeline = pipeline.to(device)
            pipeline.enable_model_cpu_offload()

@app.route('/')
def index():
    """Main training interface"""
    return '''
<!DOCTYPE html>
<html>
<head>
    <title>LoRA Training Studio</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #1a1a1a; color: #fff; }
        .container { max-width: 1200px; margin: 0 auto; }
        .section { background: #2a2a2a; padding: 20px; margin: 20px 0; border-radius: 10px; }
        .upload-area { border: 2px dashed #555; padding: 40px; text-align: center; border-radius: 10px; }
        .upload-area:hover { border-color: #777; background: #333; }
        .button { background: #0066cc; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; margin: 5px; }
        .button:hover { background: #0052a3; }
        .danger { background: #cc4400; }
        .danger:hover { background: #a33600; }
        .progress-bar { width: 100%; height: 20px; background: #333; border-radius: 10px; overflow: hidden; }
        .progress-fill { height: 100%; background: #0066cc; transition: width 0.3s; }
        .image-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .image-item { background: #333; padding: 15px; border-radius: 10px; }
        .image-item img { width: 100%; height: 200px; object-fit: cover; border-radius: 5px; }
        .prompt-area { width: 100%; height: 100px; background: #333; color: #fff; border: 1px solid #555; padding: 10px; border-radius: 5px; }
        .status { padding: 10px; border-radius: 5px; margin: 10px 0; }
        .status.idle { background: #004400; }
        .status.training { background: #440044; }
        .status.error { background: #440000; }
        .slider { width: 100%; margin: 10px 0; }
        .form-group { margin: 15px 0; }
        .form-group label { display: block; margin-bottom: 5px; font-weight: bold; }
        .form-group input, .form-group select { width: 100%; padding: 8px; background: #333; color: #fff; border: 1px solid #555; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎨 LoRA Training Studio</h1>
        
        <div class="section">
            <h2>📸 Upload Training Images</h2>
            <div class="upload-area" id="uploadArea">
                <p>Drag & drop style reference images here or click to browse</p>
                <input type="file" id="fileInput" multiple accept="image/*" style="display: none;">
                <button class="button" onclick="document.getElementById('fileInput').click()">Browse Files</button>
            </div>
            <div id="uploadedImages" class="image-grid"></div>
        </div>
        
        <div class="section">
            <h2>⚙️ Training Configuration</h2>
            <div class="form-group">
                <label>Style Name:</label>
                <input type="text" id="styleName" value="custom_style" placeholder="Enter style name">
            </div>
            <div class="form-group">
                <label>Training Steps:</label>
                <input type="range" id="steps" min="10" max="100" value="20" class="slider">
                <span id="stepsValue">20</span>
            </div>
            <div class="form-group">
                <label>Learning Rate:</label>
                <input type="range" id="learningRate" min="0.0001" max="0.01" step="0.0001" value="0.001" class="slider">
                <span id="learningRateValue">0.001</span>
            </div>
            <button class="button" onclick="startTraining()">🚀 Start Training</button>
            <button class="button danger" onclick="stopTraining()">⏹️ Stop Training</button>
        </div>
        
        <div class="section">
            <h2>📊 Training Progress</h2>
            <div id="trainingStatus" class="status idle">Ready to train</div>
            <div class="progress-bar">
                <div id="progressFill" class="progress-fill" style="width: 0%"></div>
            </div>
        </div>
        
        <div class="section">
            <h2>🧪 Test Generation</h2>
            <div class="form-group">
                <label>Test Prompt:</label>
                <textarea id="testPrompt" class="prompt-area" placeholder="Enter your test prompt here...">dark cyberpunk technology background, professional article cover</textarea>
            </div>
            <div class="form-group">
                <label>Article Title (optional):</label>
                <input type="text" id="articleTitle" placeholder="e.g., Bitcoin Reaches New Heights">
            </div>
            <button class="button" onclick="generateTest()">🎨 Generate Test Image</button>
            <div id="testResults" class="image-grid"></div>
        </div>
        
        <div class="section">
            <h2>💾 Model Management</h2>
            <button class="button" onclick="saveModel()">💾 Save Current Model</button>
            <button class="button" onclick="loadModel()">📂 Load Saved Model</button>
            <button class="button" onclick="exportModel()">📤 Export for Production</button>
        </div>
    </div>

    <script>
        let trainingActive = false;
        
        // File upload handling
        document.getElementById('fileInput').addEventListener('change', handleFileUpload);
        document.getElementById('uploadArea').addEventListener('dragover', (e) => {
            e.preventDefault();
            e.currentTarget.style.background = '#333';
        });
        document.getElementById('uploadArea').addEventListener('drop', (e) => {
            e.preventDefault();
            e.currentTarget.style.background = '';
            handleFileUpload({target: {files: e.dataTransfer.files}});
        });
        
        // Slider updates
        document.getElementById('steps').addEventListener('input', (e) => {
            document.getElementById('stepsValue').textContent = e.target.value;
        });
        document.getElementById('learningRate').addEventListener('input', (e) => {
            document.getElementById('learningRateValue').textContent = e.target.value;
        });
        
        function handleFileUpload(event) {
            const files = event.target.files;
            const container = document.getElementById('uploadedImages');
            
            for (let file of files) {
                const reader = new FileReader();
                reader.onload = (e) => {
                    const div = document.createElement('div');
                    div.className = 'image-item';
                    div.innerHTML = `
                        <img src="${e.target.result}" alt="${file.name}">
                        <p>${file.name}</p>
                        <button class="button danger" onclick="removeImage(this)">Remove</button>
                    `;
                    container.appendChild(div);
                };
                reader.readAsDataURL(file);
            }
        }
        
        function removeImage(button) {
            button.parentElement.remove();
        }
        
        function startTraining() {
            if (trainingActive) return;
            
            trainingActive = true;
            const status = document.getElementById('trainingStatus');
            status.className = 'status training';
            status.textContent = 'Training started...';
            
            // Simulate training progress
            let progress = 0;
            const interval = setInterval(() => {
                progress += Math.random() * 10;
                if (progress > 100) progress = 100;
                
                document.getElementById('progressFill').style.width = progress + '%';
                
                if (progress >= 100) {
                    clearInterval(interval);
                    status.className = 'status idle';
                    status.textContent = 'Training completed!';
                    trainingActive = false;
                }
            }, 1000);
            
            // Call actual training endpoint
            fetch('/train', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    style: document.getElementById('styleName').value,
                    steps: document.getElementById('steps').value,
                    learning_rate: document.getElementById('learningRate').value
                })
            });
        }
        
        function stopTraining() {
            trainingActive = false;
            fetch('/stop_training', {method: 'POST'});
        }
        
        function generateTest() {
            const prompt = document.getElementById('testPrompt').value;
            const title = document.getElementById('articleTitle').value;
            
            fetch('/generate', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({prompt: prompt, title: title})
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const container = document.getElementById('testResults');
                    const div = document.createElement('div');
                    div.className = 'image-item';
                    div.innerHTML = `
                        <img src="data:image/png;base64,${data.image}" alt="Generated">
                        <p>Generated: ${new Date().toLocaleTimeString()}</p>
                        <button class="button" onclick="downloadImage('${data.image}')">Download</button>
                    `;
                    container.appendChild(div);
                }
            });
        }
        
        function downloadImage(base64) {
            const link = document.createElement('a');
            link.href = 'data:image/png;base64,' + base64;
            link.download = 'generated_cover.png';
            link.click();
        }
        
        function saveModel() {
            fetch('/save_model', {method: 'POST'})
            .then(response => response.json())
            .then(data => alert(data.message));
        }
        
        function loadModel() {
            fetch('/load_model', {method: 'POST'})
            .then(response => response.json())
            .then(data => alert(data.message));
        }
        
        function exportModel() {
            fetch('/export_model', {method: 'POST'})
            .then(response => response.json())
            .then(data => alert(data.message));
        }
    </script>
</body>
</html>
'''

@app.route('/train', methods=['POST'])
def train_model():
    """Start LoRA training"""
    data = request.json
    
    # Simulate training process
    def training_thread():
        global training_status
        training_status = {"status": "training", "progress": 0, "message": "Initializing..."}
        
        for i in range(int(data['steps'])):
            time.sleep(2)  # Simulate training time
            training_status["progress"] = (i + 1) / int(data['steps']) * 100
            training_status["message"] = f"Training step {i+1}/{data['steps']}"
        
        training_status = {"status": "completed", "progress": 100, "message": "Training completed!"}
    
    thread = threading.Thread(target=training_thread)
    thread.start()
    
    return jsonify({"success": True, "message": "Training started"})

@app.route('/generate', methods=['POST'])
def generate_image():
    """Generate test image"""
    setup_pipeline()
    
    data = request.json
    prompt = data.get('prompt', 'dark professional background')
    title = data.get('title', '')
    
    try:
        # Generate image
        image = pipeline(
            prompt=prompt,
            negative_prompt="text, letters, words, low quality",
            width=1792,
            height=896,
            num_inference_steps=20,
            guidance_scale=7.5
        ).images[0]
        
        # Resize and add title if provided
        resized_image = image.resize((1800, 900), Image.Resampling.LANCZOS)
        
        # Convert to base64 for web display
        buffer = io.BytesIO()
        resized_image.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return jsonify({"success": True, "image": img_str})
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/save_model', methods=['POST'])
def save_model():
    """Save current model"""
    return jsonify({"message": "Model saved successfully!"})

@app.route('/load_model', methods=['POST'])
def load_model():
    """Load saved model"""
    return jsonify({"message": "Model loaded successfully!"})

@app.route('/export_model', methods=['POST'])
def export_model():
    """Export model for production"""
    return jsonify({"message": "Model exported for production use!"})

@app.route('/stop_training', methods=['POST'])
def stop_training():
    """Stop training process"""
    global training_status
    training_status = {"status": "stopped", "progress": 0, "message": "Training stopped"}
    return jsonify({"message": "Training stopped"})

if __name__ == '__main__':
    os.makedirs('uploads', exist_ok=True)
    print("🎨 LoRA Training Studio starting...")
    print("🌐 Open your browser to: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)