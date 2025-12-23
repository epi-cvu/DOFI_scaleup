# app_des.py
from flask import Flask, jsonify, render_template_string
from celery.result import AsyncResult
from tasks_des import lancer_des, celery

app = Flask(__name__)

@app.route('/')
def home():
    return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>Lanceur de Dés</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: white;
        }
        .container {
            background: white;
            padding: 40px;
            border-radius: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
            color: #333;
        }
        h1 {
            color: #6f42c1;
            text-align: center;
        }
        .buttons {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
            margin: 30px 0;
        }
        button {
            background: #6f42c1;
            color: white;
            border: none;
            padding: 20px;
            font-size: 18px;
            border-radius: 15px;
            cursor: pointer;
            transition: all 0.3s;
        }
        button:hover {
            background: #5a32a3;
            transform: translateY(-2px);
        }
        button:disabled {
            background: #ccc;
            cursor: not-allowed;
            transform: none;
        }
        #des-container {
            display: none;
            margin: 30px 0;
        }
        #des {
            text-align: center;
            font-size: 60px;
            min-height: 100px;
            margin: 20px 0;
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 10px;
        }
        .de {
            animation: bounce 0.5s;
        }
        @keyframes bounce {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.3); }
        }
        #total-container {
            display: none;
            margin-top: 30px;
            padding: 30px;
            background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
            border-radius: 15px;
            text-align: center;
        }
        .total-number {
            font-size: 72px;
            font-weight: bold;
            color: #155724;
            margin: 20px 0;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 15px;
            margin-top: 20px;
        }
        .stat-item {
            background: white;
            padding: 15px;
            border-radius: 10px;
        }
        .stat-label {
            font-size: 12px;
            color: #666;
            text-transform: uppercase;
        }
        .stat-value {
            font-size: 24px;
            font-weight: bold;
            color: #6f42c1;
            margin-top: 5px;
        }
        .progress-bar {
            width: 100%;
            height: 10px;
            background: #e9ecef;
            border-radius: 5px;
            overflow: hidden;
            margin: 20px 0;
        }
        .progress-fill {
            height: 100%;
            background: #6f42c1;
            transition: width 0.3s;
        }
        .info-text {
            text-align: center;
            color: #666;
            margin: 10px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎲 Lanceur de Dés</h1>
        <p style="text-align: center; color: #999;">Teste ta chance !</p>
        
        <div class="buttons">
            <button onclick="lancer(1)">1 dé</button>
            <button onclick="lancer(3)">3 dés</button>
            <button onclick="lancer(5)">5 dés</button>
            <button onclick="lancer(10)">10 dés</button>
            <button onclick="lancer(20)">20 dés</button>
            <button onclick="lancer(50)">50 dés</button>
        </div>
        
        <div id="des-container">
            <div class="progress-bar">
                <div class="progress-fill" id="progressBar"></div>
            </div>
            <div class="info-text" id="infoText">Lancement des dés...</div>
            <div id="des"></div>
        </div>
        
        <div id="total-container">
            <h2>🎉 Résultat Final</h2>
            <div class="total-number" id="totalNumber"></div>
            <div class="stats">
                <div class="stat-item">
                    <div class="stat-label">Nombre de dés</div>
                    <div class="stat-value" id="statNombre"></div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">Moyenne</div>
                    <div class="stat-value" id="statMoyenne"></div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">Minimum</div>
                    <div class="stat-value" id="statMin"></div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">Maximum</div>
                    <div class="stat-value" id="statMax"></div>
                </div>
            </div>
        </div>
    </div>

    <script>
        const deFaces = ['⚀', '⚁', '⚂', '⚃', '⚄', '⚅'];
        let taskId = null;
        
        function lancer(nombre) {
            // Désactive les boutons
            document.querySelectorAll('button').forEach(btn => btn.disabled = true);
            
            // Reset affichage
            document.getElementById('des-container').style.display = 'block';
            document.getElementById('total-container').style.display = 'none';
            document.getElementById('des').innerHTML = '';
            document.getElementById('progressBar').style.width = '0%';
            document.getElementById('infoText').textContent = 'Lancement des dés...';
            
            // Lance les dés
            fetch('/lancer/' + nombre)
            .then(response => response.json())
            .then(data => {
                taskId = data.task_id;
                console.log('Task lancée:', taskId);
                verifier();
            })
            .catch(error => {
                console.error('Erreur:', error);
                document.querySelectorAll('button').forEach(btn => btn.disabled = false);
            });
        }
        
        function verifier() {
            fetch('/status/' + taskId)
            .then(response => response.json())
            .then(data => {
                console.log('Status:', data);
                
                if (data.state === 'PROGRESS') {
                    // Mise à jour progression
                    const progress = data.progress || 0;
                    document.getElementById('progressBar').style.width = progress + '%';
                    document.getElementById('infoText').textContent = 
                        `Dé ${data.current}/${data.total} - Total actuel: ${data.total_actuel}`;
                    
                    // Affiche les dés au fur et à mesure
                    const desHTML = data.resultats.map(n => 
                        '<span class="de">' + deFaces[n - 1] + '</span>'
                    ).join('');
                    document.getElementById('des').innerHTML = desHTML;
                    
                    // Continue à vérifier
                    setTimeout(verifier, 500);
                }
                else if (data.state === 'SUCCESS') {
                    // Terminé !
                    const result = data.result;
                    
                    document.getElementById('progressBar').style.width = '100%';
                    
                    // Affiche tous les dés
                    const desHTML = result.resultats.map(n => 
                        '<span class="de">' + deFaces[n - 1] + '</span>'
                    ).join('');
                    document.getElementById('des').innerHTML = desHTML;
                    
                    // Affiche les stats
                    document.getElementById('des-container').style.display = 'none';
                    document.getElementById('total-container').style.display = 'block';
                    
                    document.getElementById('totalNumber').textContent = result.total;
                    document.getElementById('statNombre').textContent = result.nombre_de_des;
                    document.getElementById('statMoyenne').textContent = result.moyenne;
                    document.getElementById('statMin').textContent = result.min;
                    document.getElementById('statMax').textContent = result.max;
                    
                    // Réactive les boutons
                    document.querySelectorAll('button').forEach(btn => btn.disabled = false);
                    
                    console.log('Terminé !', result);
                }
                else {
                    setTimeout(verifier, 200);
                }
            })
            .catch(error => {
                console.error('Erreur:', error);
                document.querySelectorAll('button').forEach(btn => btn.disabled = false);
            });
        }
    </script>
</body>
</html>
    ''')

@app.route('/lancer/<int:nombre>')
def lancer(nombre):
    if nombre < 1 or nombre > 100:
        return jsonify({'error': 'Entre 1 et 100 dés'}), 400
    
    print(f"📝 [FLASK] Lancement de {nombre} dés")
    
    task = lancer_des.delay(nombre)
    
    print(f"🎫 [FLASK] Task ID : {task.id}")
    
    return jsonify({
        'message': 'Dés lancés',
        'task_id': task.id
    })

@app.route('/status/<task_id>')
def status(task_id):
    """Vérifie le statut d'une tâche avec retry automatique"""
    import time
    
    max_retries = 3
    retry_delay = 0.1  # 100ms entre chaque retry
    
    for attempt in range(max_retries):
        try:
            task = AsyncResult(task_id, app=celery)
            
            # Accède au state (peut lever une exception)
            state = task.state
            
            if state == 'PENDING':
                response = {'state': 'PENDING'}
            elif state == 'PROGRESS':
                response = {
                    'state': 'PROGRESS',
                    'current': task.info.get('current', 0),
                    'total': task.info.get('total', 0),
                    'progress': task.info.get('progress', 0),
                    'resultats': task.info.get('resultats', []),
                    'total_actuel': task.info.get('total_actuel', 0)
                }
            elif state == 'SUCCESS':
                response = {
                    'state': 'SUCCESS',
                    'result': task.result
                }
            elif state == 'FAILURE':
                response = {
                    'state': 'FAILURE',
                    'error': str(task.info)
                }
            else:
                response = {'state': state}
            
            # Si on arrive ici, pas d'erreur
            return jsonify(response)
        
        except Exception as e:
            error_msg = str(e)
            print(f"⚠️  [FLASK] Erreur Redis (tentative {attempt + 1}/{max_retries}): {error_msg[:100]}")
            
            if attempt < max_retries - 1:
                # Pas la dernière tentative, on réessaie
                time.sleep(retry_delay)
                # Double le délai pour le prochain retry
                retry_delay *= 2
            else:
                # Dernière tentative échouée, on retourne une erreur
                print(f"❌ [FLASK] Échec après {max_retries} tentatives")
                return jsonify({
                    'state': 'PENDING',  # On retourne PENDING pour que le frontend continue
                    'error': 'Connexion temporaire perdue, réessai...'
                }), 200  # 200, pas 500, pour éviter que le JS s'arrête

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🎲 Lanceur de Dés - Flask")
    print("📍 Ouvre ton navigateur : http://localhost:5000")
    print("="*60 + "\n")
    app.run(debug=True, port=5000)