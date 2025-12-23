# app_inv.py
from flask import Flask, request, jsonify, render_template_string
from celery.result import AsyncResult
from tasks_inv import inverser_texte, celery

app = Flask(__name__)

@app.route('/')
def home():
    return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>Inverseur de Texte</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 700px;
            margin: 50px auto;
            padding: 20px;
            background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
            min-height: 100vh;
        }
        .container {
            background: white;
            padding: 40px;
            border-radius: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
        }
        h1 {
            color: #667eea;
            text-align: center;
        }
        input[type="text"] {
            width: 100%;
            padding: 15px;
            font-size: 18px;
            border: 2px solid #ddd;
            border-radius: 10px;
            box-sizing: border-box;
            margin: 20px 0;
        }
        button {
            width: 100%;
            background: #667eea;
            color: white;
            border: none;
            padding: 15px;
            font-size: 18px;
            border-radius: 10px;
            cursor: pointer;
        }
        button:hover {
            background: #764ba2;
        }
        button:disabled {
            background: #ccc;
        }
        #result {
            margin-top: 30px;
            padding: 30px;
            background: #f8f9fa;
            border-radius: 15px;
            text-align: center;
            font-size: 32px;
            min-height: 60px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔄 Inverseur de Texte</h1>
        
        <input type="text" id="texte" placeholder="Tape du texte..." value="Bonjour">
        
        <button id="btn" onclick="inverser()">Inverser</button>
        
        <div id="result"></div>
    </div>

    <script>
        let taskId = null;
        
        function inverser() {
            const texte = document.getElementById('texte').value;
            
            if (!texte) {
                alert('Tape du texte !');
                return;
            }
            
            document.getElementById('btn').disabled = true;
            document.getElementById('result').textContent = '⏳ Chargement...';
            
            // Lance l'inversion
            fetch('/inverser', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({texte: texte})
            })
            .then(response => response.json())
            .then(data => {
                taskId = data.task_id;
                console.log('Task lancée:', taskId);
                verifier();
            })
            .catch(error => {
                console.error('Erreur:', error);
                document.getElementById('result').textContent = '❌ Erreur';
                document.getElementById('btn').disabled = false;
            });
        }
        
        function verifier() {
            fetch('/status/' + taskId)
            .then(response => response.json())
            .then(data => {
                console.log('Status:', data);
                
                if (data.state === 'PROGRESS') {
                    // Affiche le résultat partiel
                    document.getElementById('result').textContent = data.resultat_partiel || '...';
                    
                    // Continue à vérifier
                    setTimeout(verifier, 200);
                }
                else if (data.state === 'SUCCESS') {
                    // Terminé !
                    document.getElementById('result').textContent = data.result.texte_inverse;
                    document.getElementById('btn').disabled = false;
                    console.log('Terminé !');
                }
                else {
                    // Autre état
                    setTimeout(verifier, 200);
                }
            })
            .catch(error => {
                console.error('Erreur:', error);
                document.getElementById('btn').disabled = false;
            });
        }
    </script>
</body>
</html>
    ''')

@app.route('/inverser', methods=['POST'])
def inverser():
    data = request.json
    texte = data.get('texte', '')
    
    if not texte:
        return jsonify({'error': 'Texte vide'}), 400
    
    texte = texte[:100]
    
    print(f"📝 [FLASK] Demande d'inversion : '{texte}'")
    
    task = inverser_texte.delay(texte)
    
    print(f"🎫 [FLASK] Task ID : {task.id}")
    
    return jsonify({
        'message': 'Inversion lancée',
        'task_id': task.id
    })

@app.route('/status/<task_id>')
def status(task_id):
    task = AsyncResult(task_id, app=celery)
    
    if task.state == 'PENDING':
        response = {'state': 'PENDING'}
    elif task.state == 'PROGRESS':
        response = {
            'state': 'PROGRESS',
            'resultat_partiel': task.info.get('resultat_partiel', '')
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
        response = {'state': task.state}
    
    return jsonify(response)

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🔄 Inverseur de Texte - Flask")
    print("📍 Ouvre ton navigateur : http://localhost:5000")
    print("="*60 + "\n")
    app.run(debug=True, port=5000)