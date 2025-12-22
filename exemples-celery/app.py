# app.py
"""
Application Flask - Indépendant du code métier Celery
Importe UNIQUEMENT les tâches, pas la logique
"""
from flask import Flask, jsonify, render_template_string
from celery.result import AsyncResult

# Import de la tâche (pas de l'instance celery)
from tasks import compter_lentement, celery

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
    <title>Compteur Lent</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 600px;
            margin: 50px auto;
            padding: 20px;
            text-align: center;
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
            color: #667eea;
            margin-bottom: 10px;
        }
        .subtitle {
            color: #999;
            margin-bottom: 30px;
        }
        button {
            background: #667eea;
            color: white;
            border: none;
            padding: 15px 40px;
            font-size: 18px;
            border-radius: 50px;
            cursor: pointer;
            margin: 10px;
            transition: all 0.3s;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        }
        button:hover {
            background: #764ba2;
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(118, 75, 162, 0.4);
        }
        button:disabled {
            background: #ccc;
            cursor: not-allowed;
            transform: none;
        }
        #progress {
            margin: 30px 0;
            font-size: 72px;
            font-weight: bold;
            color: #667eea;
            min-height: 100px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        #status {
            font-size: 18px;
            color: #666;
            margin-top: 20px;
        }
        #result {
            margin-top: 30px;
            font-size: 24px;
            font-weight: bold;
            color: #28a745;
            padding: 20px;
            background: #d4edda;
            border-radius: 10px;
            display: none;
        }
        .logs {
            margin-top: 30px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 10px;
            max-height: 150px;
            overflow-y: auto;
            font-size: 14px;
            text-align: left;
            font-family: 'Courier New', monospace;
        }
        .log-entry {
            padding: 5px;
            border-bottom: 1px solid #dee2e6;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔢 Compteur Lent</h1>
        <p class="subtitle">Architecture séparée : Flask + Celery</p>
        
        <button id="btn5" onclick="lancerCompteur(5)">Compter jusqu'à 5</button>
        <button id="btn10" onclick="lancerCompteur(10)">Compter jusqu'à 10</button>
        <button id="btn20" onclick="lancerCompteur(20)">Compter jusqu'à 20</button>
        
        <div id="progress">🎯</div>
        <div id="status">Clique sur un bouton pour commencer</div>
        <div id="result"></div>
        
        <div class="logs" id="logs"></div>
    </div>

    <script>
        let taskId = null;
        
        function log(message) {
            const logsDiv = document.getElementById('logs');
            const time = new Date().toLocaleTimeString();
            const entry = document.createElement('div');
            entry.className = 'log-entry';
            entry.textContent = `[${time}] ${message}`;
            logsDiv.insertBefore(entry, logsDiv.firstChild);
        }
        
        async function lancerCompteur(jusqu_a) {
            // Désactive tous les boutons
            document.querySelectorAll('button').forEach(btn => btn.disabled = true);
            
            // Reset affichage
            document.getElementById('progress').textContent = '⏳';
            document.getElementById('status').textContent = 'Lancement...';
            document.getElementById('result').style.display = 'none';
            
            log(`🚀 Lancement compteur jusqu'à ${jusqu_a}`);
            
            try {
                // Lance le compteur
                const res = await fetch(`/compter/${jusqu_a}`);
                const data = await res.json();
                taskId = data.task_id;
                
                log(`✅ Task créée : ${taskId.substring(0, 8)}...`);
                
                // Vérifie la progression
                verifierProgression();
            } catch (error) {
                log(`❌ Erreur : ${error}`);
                document.querySelectorAll('button').forEach(btn => btn.disabled = false);
            }
        }
        
        async function verifierProgression() {
            try {
                const res = await fetch(`/status/${taskId}`);
                const data = await res.json();
                
                if (data.state === 'PROGRESS') {
                    // Affiche le nombre actuel
                    const current = data.current;
                    const total = data.total;
                    
                    document.getElementById('progress').textContent = current;
                    document.getElementById('status').textContent = 
                        `Comptage en cours : ${current} / ${total}`;
                    
                    log(`🔢 Compte : ${current}`);
                    
                    // Continue à vérifier
                    setTimeout(verifierProgression, 500);
                }
                else if (data.state === 'SUCCESS') {
                    // Terminé !
                    document.getElementById('progress').textContent = '✅';
                    document.getElementById('status').textContent = 'Terminé !';
                    document.getElementById('result').textContent = data.result;
                    document.getElementById('result').style.display = 'block';
                    
                    log(`🎉 ${data.result}`);
                    
                    // Réactive les boutons
                    document.querySelectorAll('button').forEach(btn => btn.disabled = false);
                }
                else if (data.state === 'FAILURE') {
                    document.getElementById('progress').textContent = '❌';
                    document.getElementById('status').textContent = 'Erreur !';
                    log(`❌ Échec : ${data.error}`);
                    document.querySelectorAll('button').forEach(btn => btn.disabled = false);
                }
                else {
                    // État inconnu, continue à vérifier
                    log(`ℹ️  État : ${data.state}`);
                    setTimeout(verifierProgression, 500);
                }
            } catch (error) {
                log(`❌ Erreur vérification : ${error}`);
                document.querySelectorAll('button').forEach(btn => btn.disabled = false);
            }
        }
        
        // Log initial
        log('✨ Interface prête');
    </script>
</body>
</html>
    ''')


@app.route('/compter/<int:jusqu_a>')
def lancer_compteur(jusqu_a):
    """
    Lance le compteur
    Flask ne fait QUE créer la tâche et retourner
    """
    print(f"📝 [FLASK] Création tâche : compter jusqu'à {jusqu_a}")
    
    # Lance la tâche Celery (importée depuis tasks.py)
    task = compter_lentement.delay(jusqu_a)
    
    print(f"🎫 [FLASK] Task ID : {task.id}")
    
    return jsonify({
        'message': 'Compteur lancé',
        'task_id': task.id
    })


@app.route('/status/<task_id>')
def status(task_id):
    """
    Vérifie le statut d'une tâche
    Flask ne fait QUE lire Redis
    """
    print(f"👀 [FLASK] Vérification statut : {task_id[:8]}...")
    
    # Utilise l'instance celery de tasks.py
    task = AsyncResult(task_id, app=celery)
    
    if task.state == 'PENDING':
        response = {
            'state': 'PENDING',
            'status': 'En attente...'
        }
    elif task.state == 'PROGRESS':
        response = {
            'state': 'PROGRESS',
            'current': task.info.get('current', 0),
            'total': task.info.get('total', 10)
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
    print("🔢 Compteur Lent - Flask (version séparée)")
    print("📍 Ouvre ton navigateur : http://localhost:5000")
    print("="*60)
    print("⚠️  N'oublie pas de lancer le worker dans un autre terminal :")
    print("   celery -A tasks worker --loglevel=info")
    print("="*60 + "\n")
    app.run(debug=True, port=5000)