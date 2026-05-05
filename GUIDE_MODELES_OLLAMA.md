# Guide : Ajouter des modèles à votre application Ollama

## 🚀 Installation d'Ollama

### Option 1 : Installation via snap (recommandée)
```bash
sudo snap install ollama
```

### Option 2 : Installation via le script officiel
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### Option 3 : Installation manuelle
```bash
# Télécharger et installer Ollama
curl -L https://ollama.com/download/ollama-linux-amd64 -o ollama
sudo mv ollama /usr/local/bin/
sudo chmod +x /usr/local/bin/ollama
```

## 🔧 Démarrage d'Ollama

Une fois installé, démarrez le service Ollama :

```bash
# Démarrer Ollama en arrière-plan
ollama serve
```

Ou pour un démarrage automatique au boot :
```bash
# Créer un service systemd
sudo systemctl enable ollama
sudo systemctl start ollama
```

## 📦 Installation de modèles

### Modèles populaires à installer

#### 1. Modèles généralistes
```bash
# Llama 3.1 (8B) - Excellent équilibre performance/vitesse
ollama pull llama3.1

# Llama 3.1 (70B) - Plus performant mais plus lourd
ollama pull llama3.1:70b

# Llama 3.2 (3B) - Très rapide, idéal pour les tâches simples
ollama pull llama3.2

# Mistral 7B - Excellent pour le français
ollama pull mistral

# Mixtral 8x7B - Très performant
ollama pull mixtral
```

#### 2. Modèles spécialisés
```bash
# Code Llama - Spécialisé en programmation
ollama pull codellama

# Phi-3 - Microsoft, compact et efficace
ollama pull phi3

# Gemma - Google, excellent pour les tâches de raisonnement
ollama pull gemma

# Neural Chat - Intel, optimisé pour les conversations
ollama pull neural-chat
```

#### 3. Modèles multimodaux
```bash
# LLaVA - Vision + langage
ollama pull llava

# Bakllava - Vision améliorée
ollama pull bakllava
```

## 🎯 Commandes utiles pour gérer les modèles

### Lister les modèles installés
```bash
ollama list
```

### Supprimer un modèle
```bash
ollama rm nom_du_modele
```

### Mettre à jour un modèle
```bash
ollama pull nom_du_modele
```

### Voir l'utilisation des ressources
```bash
ollama ps
```

## 🔍 Vérification que votre app détecte les modèles

Une fois les modèles installés, votre application les détectera automatiquement via l'endpoint `/api/models`. 

Vous pouvez tester avec :
```bash
# Vérifier qu'Ollama fonctionne
curl http://localhost:11434/api/tags

# Vérifier que votre app détecte les modèles
curl http://localhost:5000/api/models
```

## 📊 Recommandations par cas d'usage

### Pour un usage général
- **llama3.1** ou **mistral** (français excellent)

### Pour la programmation
- **codellama** ou **llama3.1** 

### Pour des ressources limitées
- **llama3.2** ou **phi3**

### Pour des tâches complexes
- **llama3.1:70b** ou **mixtral**

### Pour le traitement d'images
- **llava** ou **bakllava**

## ⚡ Script d'installation rapide

Voici un script pour installer automatiquement les modèles essentiels :

```bash
#!/bin/bash
echo "Installation des modèles Ollama essentiels..."

# Modèles de base
ollama pull llama3.1
ollama pull mistral
ollama pull codellama
ollama pull phi3

echo "Installation terminée !"
echo "Modèles installés :"
ollama list
```

## 🔧 Configuration avancée

### Personnaliser les paramètres des modèles

Vous pouvez créer des variants de modèles avec des paramètres personnalisés :

```bash
# Créer un fichier Modelfile
cat > Modelfile << EOF
FROM llama3.1

PARAMETER temperature 0.8
PARAMETER top_p 0.9
PARAMETER top_k 40

SYSTEM """
Vous êtes un assistant IA spécialisé en développement web français.
Répondez toujours en français et soyez précis dans vos explications.
"""
EOF

# Créer le modèle personnalisé
ollama create mon-llama-dev -f Modelfile
```

## 🎮 Utilisation dans votre application

Une fois les modèles installés :

1. **Redémarrez votre application** Flask si elle était déjà lancée
2. **Actualisez la page** web
3. **Sélectionnez le nouveau modèle** dans le menu déroulant
4. **Créez une nouvelle conversation** avec ce modèle

## 🐛 Dépannage

### Problèmes courants

#### Ollama ne démarre pas
```bash
# Vérifier le statut
systemctl status ollama

# Voir les logs
journalctl -u ollama -f
```

#### Modèle ne se charge pas
```bash
# Vérifier l'espace disque
df -h

# Vérifier la RAM disponible
free -h

# Redémarrer Ollama
sudo systemctl restart ollama
```

#### L'application ne voit pas les modèles
```bash
# Vérifier qu'Ollama écoute sur le bon port
netstat -tlnp | grep 11434

# Tester l'API directement
curl http://localhost:11434/api/tags
```

## 📈 Surveillance des performances

Pour surveiller l'utilisation des ressources :

```bash
# Voir les processus Ollama
ollama ps

# Surveiller l'utilisation système
htop

# Voir l'utilisation GPU (si disponible)
nvidia-smi
```

---

**Note importante** : Les modèles peuvent être volumineux (plusieurs GB). Assurez-vous d'avoir suffisamment d'espace disque et de RAM avant l'installation.