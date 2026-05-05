# Ollama Multi-Chat Interface

Interface web moderne pour Ollama avec support des conversations multiples et historique persistant.

## ✨ Fonctionnalités

### 🗂️ Gestion Multi-Conversations
- **Historique persistant** : Toutes les conversations sont sauvegardées en base SQLite
- **Sidebar interactive** : Liste des conversations avec navigation facile
- **Titres intelligents** : Génération automatique de titres descriptifs basés sur la demande initiale
- **Gestion complète** : Créer, renommer, supprimer des conversations

### 🎯 Titres Intelligents
Le système génère automatiquement des titres pertinents basés sur votre première question :

**Exemples :**
- "Comment créer une API REST ?" → **"Comment créer API REST"**
- "Qu'est-ce que Python ?" → **"Qu'est-ce que Python"**
- "Aide-moi à déboguer ce code" → **"Aide pour déboguer code"**
- "Peux-tu expliquer les algorithmes ?" → **"Aide pour expliquer algorithmes"**

### 💻 Interface Moderne
- **Design responsive** : S'adapte aux écrans desktop et mobile
- **Sidebar rétractable** : Bouton toggle pour masquer/afficher
- **Menu contextuel** : Clic droit sur les conversations pour plus d'options
- **Streaming en temps réel** : Réponses affichées au fur et à mesure
- **Gestion d'erreurs** : Messages d'erreur clairs et informatifs

## 🚀 Installation et Utilisation

### Prérequis
- Python 3.7+
- Ollama installé et en fonctionnement sur `http://localhost:11434`

### Lancement
```bash
python3 app.py
```

Puis accédez à : **http://localhost:5000**

### Première utilisation
1. **Sélectionnez un modèle** dans le menu déroulant
2. **Cliquez sur "New Chat"** pour créer votre première conversation
3. **Tapez votre message** et appuyez sur Entrée
4. **Le titre se génère automatiquement** après votre première question

## 🎮 Utilisation

### Navigation
- **Nouvelle conversation** : Bouton "✨ New Chat" dans la sidebar
- **Changer de conversation** : Clic sur une conversation dans la liste
- **Masquer sidebar** : Bouton "◀" (desktop) ou "☰" (mobile)
- **Options de conversation** : Clic sur "⋯" pour renommer/supprimer

### Raccourcis Clavier
- **Envoyer message** : `Entrée`
- **Nouvelle ligne** : `Shift + Entrée`
- **Fermer modales** : `Échap`
- **Confirmer renommage** : `Entrée`

## 📊 Structure de la Base de Données

### Table `conversations`
- `id` : Identifiant unique
- `title` : Titre généré automatiquement
- `model` : Modèle Ollama utilisé
- `created_at` : Date de création
- `updated_at` : Dernière modification

### Table `messages`
- `id` : Identifiant unique
- `conversation_id` : Référence à la conversation
- `role` : `user` ou `assistant`
- `content` : Contenu du message
- `timestamp` : Horodatage

## 🔧 Architecture Technique

### Backend
- **Flask** : Serveur web avec API REST
- **Socket.IO** : Communication temps réel
- **SQLite** : Base de données embarquée
- **Threading** : Gestion des réponses streamées

### Frontend
- **HTML5/CSS3** : Interface moderne et responsive
- **JavaScript ES6** : Logique client avec classes
- **Socket.IO Client** : Communication bidirectionnelle
- **CSS Grid/Flexbox** : Layout adaptatif

### APIs Disponibles
- `GET /api/conversations` : Liste des conversations
- `POST /api/conversations` : Créer une nouvelle conversation
- `GET /api/conversations/{id}` : Détails d'une conversation
- `PUT /api/conversations/{id}` : Modifier une conversation
- `DELETE /api/conversations/{id}` : Supprimer une conversation
- `POST /api/conversations/{id}/clear` : Vider une conversation

## 🎨 Personnalisation

### Variables CSS
Le thème peut être personnalisé via les variables CSS dans `static/css/styles.css` :

```css
:root {
    --primary-color: #2563eb;
    --background-color: #f8fafc;
    --surface-color: #ffffff;
    --text-primary: #1e293b;
    /* ... */
}
```

### Génération de Titres
Les patterns de reconnaissance pour les titres sont dans `database.py`, méthode `_create_smart_title()`. Vous pouvez ajouter vos propres patterns :

```python
question_patterns = [
    (r'^(votre_pattern)', 'Préfixe Personnalisé'),
    # ...
]
```

## 🐛 Dépannage

### Problèmes Courants
1. **Port 5000 occupé** : Arrêtez les autres processus ou changez le port dans `app.py`
2. **Ollama non disponible** : Vérifiez que Ollama fonctionne sur le port 11434
3. **Base de données corrompue** : Supprimez `conversations.db` pour réinitialiser

### Logs
Le mode debug est activé par défaut. Les logs apparaissent dans le terminal.

---

## 📝 License

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou proposer une pull request.