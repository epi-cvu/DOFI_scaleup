# app_temp.py
"""
Application Flask - Convertisseur de température
"""
from flask import Flask, request, jsonify, render_template_string
from celery.result import AsyncResult

# Import de la tâche
from tasks_temp import convertir_temperature, celery

# ============================================
# CONFIGURATION FLASK
# ============================================

app = Flask(__name__)

# ============================================
# ROUTES FLASK
# ============================================

@app.route('/')
def home():
    """Page d'accueil avec interface"""
    return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>Convertisseur Température</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 600px;
            margin: 50px auto;
            padding: 20px;
            background: linear-gradient(135deg, #fc4a1a 0%, #f7b733 100%);
            min-height: 100vh;
        }
        .container {
            background: white;
            padding: 40px;
            border-radius: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
        }
        h1 {
            color: #fc4a1a;
            margin-bottom: 10px;
            text-align: center;
        }
        .subtitle {
            color: #999;
            margin-bottom: 30px;
            text-align: center;
        }
        .input-group {
            margin: 20px 0;
        }
        label {
            display: block;
            margin-bottom: 10px;
            color: #333;
            font-weight: bold;
        }
        input[type="number"] {
            width: 100%;
            padding: 15px;
            font-size: 18px;
            border: 2px solid #ddd;
            border-radius: 10px;
            box-sizing: border-box;
            transition: border 0.3s;
        }
        input[type="number"]:focus {
            border-color: #fc4a1a;
            outline: none;
        }
        button {
            width: 100%;
            background: #fc4a1a;
            color: white;
            border: none;
            padding: 15px 40px;
            font-size: 18px;
            border-radius: 50px;
            cursor: pointer;
            margin: 20px 0;
            transition: all 0.3s;
            box-shadow: 0 4px 15px rgba(252, 74, 26, 0.4);
        }
        button:hover {
            background: #f7b733;
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(247, 183, 51, 0.4);
        }
        button:disabled {
            background: #ccc;
            cursor: not-allowed;
            transform: none;
        }
        #loading {
            display: none;
            text-align: center;
            margin: 30px 0;
            color: #fc4a1a;
            font-size: 20px;
        }
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #fc4a1a;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 20px auto;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        #result {
            margin-top: 30px;
            padding: 30px;
            background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
            border-radius: 15px;
            display: none;
            text-align: center;
        }
        .result-value {
            font-size: 32px;
            font-weight: bold;
            margin: 15px 0;
            color: #155724;
        }
        .result-label {
            font-size: 14px;
            color: #666;
            margin-top: 5px;
        }
        .result-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
            margin-top: 20px;
        }
        .result-item {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .examples {
            margin-top: 30px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 10px;
        }
        .examples h3 {
            margin-top: 0;
            color: #333;
        }
        .example-btn {
            display: inline-block;
            background: #6c757d;
            color: white;
            padding: 8px 15px;
            margin: 5px;
            border-radius: 20px;
            cursor: pointer;
            font-size: 14px;
            border: none;
        }
        .example-btn:hover {
            background: #5a6268;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🌡️ Convertisseur de Température</h1>
        <p class="subtitle">Celsius → Fahrenheit & Kelvin</p>
        
        <div class="input-group">
            <label for="celsius">Température en Celsius (°C)</label>
            <input type="number" id="celsius" placeholder="Ex: 25" value="25" step="0.1">
        </div>
        
        <button id="convertBtn" onclick="convertir()">Convertir</button>
        
        <div id="loading">
            <div class="spinner"></div>
            <p>Calcul en cours...</p>
        </div>
        
        <div id="result">
            <h2>Résultat</h2>
            <div class="result-grid">
                <div class="result-item">
                    <div class="result-value" id="celsiusValue">--</div>
                    <div class="result-label">Celsius</div>
                </div>
                <div class="result-item">
                    <div class="result-value" id="fahrenheitValue">--</div>
                    <div class="result-label">Fahrenheit</div>
                </div>
                <div class="result-item">
                    <div class="result-value" id="kelvinValue">--</div>
                    <div class="result-label">Kelvin</div>
                </div>
            </div>
        </div>
        
        <div class="examples">
            <h3>Exemples rapides</h3>
            <button class="example-btn" onclick="setTemp(0)">0°C (Congélation)</button>
            <button class="example-btn" onclick="setTemp(25)">25°C (Température ambiante)</button>
            <button class="example-btn" onclick="setTemp(37)">37°C (Corps humain)</button>
            <button class="example-btn" onclick="setTemp(100)">100°C (Ébullition)</button>
            <button class="example-btn" onclick="setTemp(-40)">-40°C (Extrême froid)</button>
        </div>
    </div>

    <script>
        function setTemp(temp) {
            document.getElementById('celsius').value = temp;
        }
        
        async function convertir() {
            const celsius = parseFloat(document.getElementById('celsius').value);
            
            if (isNaN(celsius)) {
                alert('Entre un nombre valide !');
                return;
            }
            
            // Désactive le bouton et montre le loading
            document.getElementById('convertBtn').disabled = true;
            document.getElementById('loading').style.display = 'block';
            document.getElementById('result').style.display = 'none';
            
            try {
                // Lance la conversion
                const res = await fetch('/convertir', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({celsius: celsius})
                });
                
                const data = await res.json();
                const taskId = data.task_id;
                
                console.log('Task lancée:', taskId);
                
                // Attend le résultat
                attendreResultat(taskId);
            } catch (error) {
                console.error('Erreur:', error);
                alert('Erreur lors de la conversion');
                document.getElementById('convertBtn').disabled = false;
                document.getElementById('loading').style.display = 'none';
            }
        }
        
        async function attendreResultat(taskId) {
            try {
                const res = await fetch(`/status/${taskId}`);
                const data = await res.json();
                
                if (data.state === 'SUCCESS') {
                    // Affiche le résultat
                    const result = data.result;
                    
                    document.getElementById('celsiusValue').textContent = result.celsius + '°C';
                    document.getElementById('fahrenheitValue').textContent = result.fahrenheit + '°F';
                    document.getElementById('kelvinValue').textContent = result.kelvin + 'K';
                    
                    document.getElementById('loading').style.display = 'none';
                    document.getElementById('result').style.display = 'block';
                    document.getElementById('convertBtn').disabled = false;
                    
                    console.log('Conversion terminée:', result);
                } 
                else if (data.state === 'FAILURE') {
                    alert('Erreur lors du calcul');
                    document.getElementById('loading').style.display = 'none';
                    document.getElementById('convertBtn').disabled = false;
                } 
                else {
                    // Attend encore
                    setTimeout(() => attendreResultat(taskId), 500);
                }
            } catch (error) {
                console.error('Erreur:', error);
                document.getElementById('loading').style.display = 'none';
                document.getElementById('convertBtn').disabled = false;
            }
        }
    </script>
</body>
</html>
    ''')


@app.route('/convertir', methods=['POST'])
def convertir():
    """Lance la conversion"""
    data = request.json
    celsius = data.get('celsius', 0)
    
    print(f"📝 [FLASK] Demande de conversion : {celsius}°C")
    
    # Lance la tâche Celery
    task = convertir_temperature.delay(celsius)
    
    print(f"🎫 [FLASK] Task ID : {task.id}")
    
    return jsonify({
        'message': 'Conversion lancée',
        'task_id': task.id
    })


@app.route('/status/<task_id>')
def status(task_id):
    """Vérifie le statut d'une tâche"""
    task = AsyncResult(task_id, app=celery)
    
    if task.state == 'PENDING':
        response = {
            'state': 'PENDING',
            'status': 'En attente...'
        }
    elif task.state == 'SUCCESS':
        response = {
            'state': 'SUCCESS',
            'result': task.result
        }
    elif task.state == 'FAILURE':
        response = {
            'state': 'FAILURE',
            'error': str(task.info)
        }
    else:
        response = {
            'state': task.state
        }
    
    return jsonify(response)


# ============================================
# LANCEMENT
# ============================================

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🌡️  Convertisseur de Température - Flask")
    print("📍 Ouvre ton navigateur : http://localhost:5000")
    print("="*60)
    print("⚠️  N'oublie pas de lancer le worker :")
    print("   celery -A tasks_temp worker --loglevel=info")
    print("="*60 + "\n")
    app.run(debug=True, port=5000)